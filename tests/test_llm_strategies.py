"""Tests for LLM-based hypothesis validation strategies.

Uses mocked Anthropic client to avoid actual API calls in CI.
Tests: prompt construction, code extraction, hypothesis extraction,
strategy behavior, token tracking, runner integration.
"""
from unittest.mock import MagicMock, patch
from anthropic.types import TextBlock

import pytest

from experiments.hypothesis_validation.llm_strategies import (
    LLMEngineeringStrategy,
    LLMHypothesisStrategy,
    _build_user_prompt,
    _extract_code,
    _extract_hypothesis,
)
from experiments.hypothesis_validation.llm_runner import (
    LLMExperimentResult,
    LLMTaskResult,
    run_llm_experiment,
)
from experiments.hypothesis_validation.tasks import DebugTask, get_debug_tasks


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_task() -> DebugTask:
    return get_debug_tasks()[0]  # A1: off-by-one


@pytest.fixture
def mock_response_factory():
    """Creates a mock Anthropic API response with given text and token counts."""
    def factory(text: str, input_tokens: int = 100, output_tokens: int = 50):
        response = MagicMock()
        text_block = MagicMock(spec=TextBlock)
        text_block.text = text
        response.content = [text_block]
        response.usage.input_tokens = input_tokens
        response.usage.output_tokens = output_tokens
        return response
    return factory


@pytest.fixture
def mock_client(mock_response_factory):
    """Anthropic client mock that always returns a correct fix on first attempt."""
    correct_code = (
        "def find_max_subarray(arr, k):\n"
        "    if len(arr) < k:\n"
        "        return []\n"
        "    max_sum = sum(arr[:k])\n"
        "    max_start = 0\n"
        "    current_sum = max_sum\n"
        "    for i in range(1, len(arr) - k + 1):\n"
        "        current_sum = current_sum - arr[i - 1] + arr[i + k - 1]\n"
        "        if current_sum > max_sum:\n"
        "            max_sum = current_sum\n"
        "            max_start = i\n"
        "    return arr[max_start:max_start + k]\n"
    )
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory(
        f"```python\n{correct_code}```"
    )
    return client


# ---------------------------------------------------------------------------
# _extract_code
# ---------------------------------------------------------------------------


def test_extract_code_python_block():
    text = "```python\ndef foo():\n    return 1\n```"
    assert _extract_code(text) == "def foo():\n    return 1"


def test_extract_code_bare_block():
    text = "``` \ndef foo():\n    return 1\n```"
    # No 'python' tag but still a code block
    result = _extract_code(text)
    assert result == "def foo():\n    return 1"


def test_extract_code_fallback_def_line():
    text = "Here is the fix:\ndef foo():\n    return 1"
    result = _extract_code(text)
    assert result is not None
    assert "def foo" in result


def test_extract_code_no_code_returns_none():
    text = "I cannot determine the fix from this description."
    assert _extract_code(text) is None


def test_extract_code_with_import():
    text = "```python\nimport unicodedata\ndef foo(s):\n    return unicodedata.normalize('NFC', s)\n```"
    code = _extract_code(text)
    assert code is not None
    assert "import unicodedata" in code


# ---------------------------------------------------------------------------
# _extract_hypothesis
# ---------------------------------------------------------------------------


def test_extract_hypothesis_standard():
    text = "Hypothesis: The range upper bound is off by one.\n```python\n...\n```"
    assert _extract_hypothesis(text) == "The range upper bound is off by one."


def test_extract_hypothesis_lowercase():
    text = "hypothesis: closure captures loop variable by reference"
    assert _extract_hypothesis(text) == "closure captures loop variable by reference"


def test_extract_hypothesis_missing_returns_none():
    text = "```python\ndef foo(): pass\n```"
    assert _extract_hypothesis(text) is None


def test_extract_hypothesis_multiword():
    text = "Hypothesis: The dict is not being reset between calls due to mutable default arg.\nFix:"
    hyp = _extract_hypothesis(text)
    assert hyp == "The dict is not being reset between calls due to mutable default arg."


# ---------------------------------------------------------------------------
# _build_user_prompt
# ---------------------------------------------------------------------------


def test_build_user_prompt_contains_buggy_code(simple_task):
    prompt = _build_user_prompt(simple_task)
    assert "find_max_subarray" in prompt
    assert "range(1, len(arr) - k)" in prompt  # the bug


def test_build_user_prompt_contains_test_cases(simple_task):
    prompt = _build_user_prompt(simple_task)
    assert "1, 3, 2, 5, 1" in prompt  # from test_cases


# ---------------------------------------------------------------------------
# LLMEngineeringStrategy
# ---------------------------------------------------------------------------


def test_engineering_strategy_solves_on_first_attempt(simple_task, mock_client):
    strategy = LLMEngineeringStrategy(client=mock_client)
    result = strategy.run(simple_task, max_attempts=5)

    assert result.solved is True
    assert result.total_attempts == 1
    assert len(result.attempts) == 1
    assert result.attempts[0].input_tokens == 100
    assert result.attempts[0].output_tokens == 50


def test_engineering_strategy_tracks_tokens(simple_task, mock_client):
    strategy = LLMEngineeringStrategy(client=mock_client)
    result = strategy.run(simple_task)

    assert result.total_input_tokens == 100
    assert result.total_output_tokens == 50


def test_engineering_strategy_retries_on_failure(simple_task, mock_response_factory):
    """Fail first attempt, succeed on second."""
    wrong_code = "def find_max_subarray(arr, k):\n    return []\n"
    correct_code = (
        "def find_max_subarray(arr, k):\n"
        "    if len(arr) < k:\n"
        "        return []\n"
        "    max_sum = sum(arr[:k])\n"
        "    max_start = 0\n"
        "    current_sum = max_sum\n"
        "    for i in range(1, len(arr) - k + 1):\n"
        "        current_sum = current_sum - arr[i - 1] + arr[i + k - 1]\n"
        "        if current_sum > max_sum:\n"
        "            max_sum = current_sum\n"
        "            max_start = i\n"
        "    return arr[max_start:max_start + k]\n"
    )
    client = MagicMock()
    client.messages.create.side_effect = [
        mock_response_factory(f"```python\n{wrong_code}```"),
        mock_response_factory(f"```python\n{correct_code}```"),
    ]

    strategy = LLMEngineeringStrategy(client=client)
    result = strategy.run(simple_task, max_attempts=5)

    assert result.solved is True
    assert result.total_attempts == 2
    assert result.attempts[0].success is False
    assert result.attempts[1].success is True


def test_engineering_strategy_fails_when_max_attempts_exceeded(
    simple_task, mock_response_factory
):
    wrong_code = "def find_max_subarray(arr, k):\n    return []\n"
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory(
        f"```python\n{wrong_code}```"
    )

    strategy = LLMEngineeringStrategy(client=client)
    result = strategy.run(simple_task, max_attempts=3)

    assert result.solved is False
    assert result.total_attempts == 3
    assert len(result.attempts) == 3


def test_engineering_strategy_handles_no_code_in_response(
    simple_task, mock_response_factory
):
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory(
        "I cannot determine the fix."
    )

    strategy = LLMEngineeringStrategy(client=client)
    result = strategy.run(simple_task, max_attempts=2)

    assert result.solved is False
    assert all(a.tests_passed == 0 for a in result.attempts)


def test_engineering_strategy_task_id(simple_task, mock_client):
    strategy = LLMEngineeringStrategy(client=mock_client)
    result = strategy.run(simple_task)
    assert result.task_id == "A1"
    assert result.strategy == "llm_engineering"


# ---------------------------------------------------------------------------
# LLMHypothesisStrategy
# ---------------------------------------------------------------------------


def test_hypothesis_strategy_extracts_hypothesis(simple_task, mock_response_factory):
    correct_code = (
        "def find_max_subarray(arr, k):\n"
        "    if len(arr) < k:\n"
        "        return []\n"
        "    max_sum = sum(arr[:k])\n"
        "    max_start = 0\n"
        "    current_sum = max_sum\n"
        "    for i in range(1, len(arr) - k + 1):\n"
        "        current_sum = current_sum - arr[i - 1] + arr[i + k - 1]\n"
        "        if current_sum > max_sum:\n"
        "            max_sum = current_sum\n"
        "            max_start = i\n"
        "    return arr[max_start:max_start + k]\n"
    )
    response_text = (
        f"Hypothesis: range upper bound is off by one.\n```python\n{correct_code}```"
    )
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory(response_text)

    strategy = LLMHypothesisStrategy(client=client)
    result = strategy.run(simple_task)

    assert result.solved is True
    assert result.attempts[0].hypothesis == "range upper bound is off by one."
    assert result.attempts[0].hypothesis_correct is True


def test_hypothesis_strategy_marks_hypothesis_incorrect_on_failure(
    simple_task, mock_response_factory
):
    wrong_code = "def find_max_subarray(arr, k):\n    return arr[:k]\n"
    response_text = f"Hypothesis: wrong guess.\n```python\n{wrong_code}```"
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory(response_text)

    strategy = LLMHypothesisStrategy(client=client)
    result = strategy.run(simple_task, max_attempts=2)

    assert result.solved is False
    assert result.attempts[0].hypothesis_correct is False


def test_hypothesis_strategy_task_id_and_strategy_name(simple_task, mock_response_factory):
    correct_code = (
        "def find_max_subarray(arr, k):\n"
        "    if len(arr) < k:\n"
        "        return []\n"
        "    max_sum = sum(arr[:k])\n"
        "    max_start = 0\n"
        "    current_sum = max_sum\n"
        "    for i in range(1, len(arr) - k + 1):\n"
        "        current_sum = current_sum - arr[i - 1] + arr[i + k - 1]\n"
        "        if current_sum > max_sum:\n"
        "            max_sum = current_sum\n"
        "            max_start = i\n"
        "    return arr[max_start:max_start + k]\n"
    )
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory(
        f"```python\n{correct_code}```"
    )
    strategy = LLMHypothesisStrategy(client=client)
    result = strategy.run(simple_task)
    assert result.task_id == "A1"
    assert result.strategy == "llm_hypothesis"


def test_hypothesis_strategy_cumulative_token_tracking(simple_task, mock_response_factory):
    """Token counts from multiple attempts should accumulate."""
    wrong_code = "def find_max_subarray(arr, k):\n    return arr[:k]\n"
    correct_code = (
        "def find_max_subarray(arr, k):\n"
        "    if len(arr) < k:\n"
        "        return []\n"
        "    max_sum = sum(arr[:k])\n"
        "    max_start = 0\n"
        "    current_sum = max_sum\n"
        "    for i in range(1, len(arr) - k + 1):\n"
        "        current_sum = current_sum - arr[i - 1] + arr[i + k - 1]\n"
        "        if current_sum > max_sum:\n"
        "            max_sum = current_sum\n"
        "            max_start = i\n"
        "    return arr[max_start:max_start + k]\n"
    )
    client = MagicMock()
    client.messages.create.side_effect = [
        mock_response_factory(f"Hypothesis: wrong.\n```python\n{wrong_code}```", 80, 40),
        mock_response_factory(f"Hypothesis: right.\n```python\n{correct_code}```", 120, 60),
    ]

    strategy = LLMHypothesisStrategy(client=client)
    result = strategy.run(simple_task)

    assert result.total_input_tokens == 200   # 80 + 120
    assert result.total_output_tokens == 100  # 40 + 60


# ---------------------------------------------------------------------------
# LLMTaskResult properties
# ---------------------------------------------------------------------------


def test_llm_task_result_pass_at_1():
    task_result = LLMTaskResult(task_id="A1", category="simple", trials=3)

    from experiments.hypothesis_validation.llm_strategies import LLMStrategyResult

    task_result.engineering_results = [
        LLMStrategyResult(task_id="A1", strategy="llm_engineering", solved=True, total_attempts=1),
        LLMStrategyResult(task_id="A1", strategy="llm_engineering", solved=False, total_attempts=3),
        LLMStrategyResult(task_id="A1", strategy="llm_engineering", solved=True, total_attempts=2),
    ]
    assert task_result.engineering_pass_at_1 == pytest.approx(2 / 3)


def test_llm_task_result_avg_attempts():
    task_result = LLMTaskResult(task_id="A1", category="simple", trials=2)

    from experiments.hypothesis_validation.llm_strategies import LLMStrategyResult

    task_result.hypothesis_results = [
        LLMStrategyResult(task_id="A1", strategy="llm_hypothesis", solved=True, total_attempts=1),
        LLMStrategyResult(task_id="A1", strategy="llm_hypothesis", solved=True, total_attempts=3),
    ]
    assert task_result.hypothesis_avg_attempts == 2.0


def test_llm_task_result_avg_attempts_unsolved():
    task_result = LLMTaskResult(task_id="A1", category="simple", trials=1)

    from experiments.hypothesis_validation.llm_strategies import LLMStrategyResult

    task_result.hypothesis_results = [
        LLMStrategyResult(task_id="A1", strategy="llm_hypothesis", solved=False, total_attempts=5),
    ]
    assert task_result.hypothesis_avg_attempts == float("inf")


def test_llm_task_result_engineering_avg_attempts_unsolved():
    from experiments.hypothesis_validation.llm_strategies import LLMStrategyResult

    task_result = LLMTaskResult(task_id="A1", category="simple", trials=1)
    task_result.engineering_results = [
        LLMStrategyResult(task_id="A1", strategy="llm_engineering", solved=False, total_attempts=5),
    ]
    assert task_result.engineering_avg_attempts == float("inf")


# ---------------------------------------------------------------------------
# run_llm_experiment
# ---------------------------------------------------------------------------


def test_run_llm_experiment_runs_all_tasks(mock_response_factory):
    """Runner should produce results for all 12 tasks."""
    tasks = get_debug_tasks()

    # Provide a client that returns wrong answers (won't solve — that's OK for this test)
    wrong_code = "def placeholder(): pass\n"
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory(
        f"```python\n{wrong_code}```"
    )

    result = run_llm_experiment(
        tasks=tasks,
        model="claude-haiku-4-5-20251001",
        trials_per_task=1,
        max_attempts=1,
        client=client,
    )

    assert len(result.task_results) == 12
    for tr in result.task_results:
        assert len(tr.engineering_results) == 1
        assert len(tr.hypothesis_results) == 1


def test_run_llm_experiment_multiple_trials(simple_task, mock_response_factory):
    correct_code = (
        "def find_max_subarray(arr, k):\n"
        "    if len(arr) < k:\n"
        "        return []\n"
        "    max_sum = sum(arr[:k])\n"
        "    max_start = 0\n"
        "    current_sum = max_sum\n"
        "    for i in range(1, len(arr) - k + 1):\n"
        "        current_sum = current_sum - arr[i - 1] + arr[i + k - 1]\n"
        "        if current_sum > max_sum:\n"
        "            max_sum = current_sum\n"
        "            max_start = i\n"
        "    return arr[max_start:max_start + k]\n"
    )
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory(
        f"```python\n{correct_code}```"
    )

    result = run_llm_experiment(
        tasks=[simple_task],
        trials_per_task=3,
        max_attempts=5,
        client=client,
    )

    assert result.task_results[0].trials == 3
    assert len(result.task_results[0].engineering_results) == 3
    assert len(result.task_results[0].hypothesis_results) == 3


def test_run_llm_experiment_result_metadata(simple_task, mock_response_factory):
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory("no code here")

    result = run_llm_experiment(
        tasks=[simple_task],
        model="claude-haiku-4-5-20251001",
        trials_per_task=1,
        max_attempts=2,
        client=client,
    )

    assert result.model == "claude-haiku-4-5-20251001"
    assert result.trials_per_task == 1
    assert result.max_attempts == 2
    assert result.run_timestamp != ""


# ---------------------------------------------------------------------------
# LLMExperimentResult empty-state properties
# ---------------------------------------------------------------------------


def test_llm_experiment_result_empty_pass_rate():
    result = LLMExperimentResult()
    assert result.engineering_overall_pass_rate == 0.0
    assert result.hypothesis_overall_pass_rate == 0.0


def test_llm_task_result_empty_pass_at_1():
    task_result = LLMTaskResult(task_id="A1", category="simple", trials=0)
    assert task_result.engineering_pass_at_1 == 0.0
    assert task_result.hypothesis_pass_at_1 == 0.0


def test_run_llm_experiment_default_tasks(mock_response_factory):
    """Passing tasks=None should default to all 12 tasks."""
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory("no code", 10, 5)
    result = run_llm_experiment(tasks=None, trials_per_task=1, max_attempts=1, client=client)
    assert len(result.task_results) == 12


# ---------------------------------------------------------------------------
# save_llm_results
# ---------------------------------------------------------------------------


def test_save_llm_results_creates_file(tmp_path, mock_response_factory):
    from experiments.hypothesis_validation.llm_runner import save_llm_results

    result = LLMExperimentResult(model="test-model", trials_per_task=1, max_attempts=1)
    saved_path = save_llm_results(result, output_dir=str(tmp_path))

    assert saved_path.endswith(".json")
    import json
    data = json.loads(open(saved_path).read())
    assert data["model"] == "test-model"
    assert "engineering_overall_pass_rate" in data
    assert "tasks" in data


def test_save_llm_results_includes_task_stats(tmp_path):
    from experiments.hypothesis_validation.llm_runner import save_llm_results
    from experiments.hypothesis_validation.llm_strategies import LLMStrategyResult

    result = LLMExperimentResult()
    tr = LLMTaskResult(task_id="A1", category="simple", trials=1)
    tr.engineering_results = [
        LLMStrategyResult(task_id="A1", strategy="llm_engineering", solved=True, total_attempts=1)
    ]
    tr.hypothesis_results = [
        LLMStrategyResult(task_id="A1", strategy="llm_hypothesis", solved=True, total_attempts=1)
    ]
    result.task_results = [tr]

    saved_path = save_llm_results(result, output_dir=str(tmp_path))
    import json
    data = json.loads(open(saved_path).read())
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["task_id"] == "A1"
    assert data["tasks"][0]["engineering_pass_at_1"] == 1.0


# ---------------------------------------------------------------------------
# Token aggregation
# ---------------------------------------------------------------------------

def test_run_llm_experiment_token_aggregation(simple_task, mock_response_factory):
    """Total token counts should be summed across all tasks and strategies."""
    client = MagicMock()
    client.messages.create.return_value = mock_response_factory("no code", 50, 25)

    result = run_llm_experiment(
        tasks=[simple_task],
        trials_per_task=1,
        max_attempts=2,  # 2 failed attempts per strategy = 2 * (50+25) per strategy
        client=client,
    )

    # Each strategy: 2 attempts * (50 in + 25 out) = 150 tokens per strategy
    assert result.engineering_total_tokens == 150
    assert result.hypothesis_total_tokens == 150
