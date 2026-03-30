# LLM 장기 컨텍스트 실험 시스템 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** MiniMax M2.5를 대상으로 컨텍스트 길이에 따른 기억력 저하(실험 A)와 OpenHands 코딩 실수 시점(실험 B)을 측정하는 실험 시스템 구축

**Architecture:** 실험 A는 MiniMax API 직접 호출로 recall 테스트, 실험 B는 OpenHands REST API + trajectory 폴링으로 코딩 태스크를 자율 실행. rich 라이브러리 기반 실시간 터미널 대시보드로 진행 상황 시각화.

**Tech Stack:** Python 3.12, rich, httpx, pytest, MiniMax API, OpenHands API (localhost:3000)

---

## 파일 구조

```
AutoCode/
├── experiments/
│   ├── __init__.py
│   ├── context_memory/
│   │   ├── __init__.py
│   │   ├── tasks.py          # recall 태스크 생성 (패딩 + 질문)
│   │   └── evaluator.py      # MiniMax API 호출 + 정답 판정
│   └── coding_failure/
│       ├── __init__.py
│       ├── tasks.py          # 단계별 코딩 태스크 프롬프트 목록
│       └── evaluator.py      # OpenHands API 호출 + trajectory 분석
├── runner.py                 # CLI 진입점: python runner.py --exp a|b
├── dashboard.py              # rich Live 대시보드
├── results/
│   └── .gitkeep
├── tests/
│   ├── test_context_memory.py
│   └── test_coding_failure.py
├── requirements.txt
└── README.md
```

---

## Task 1: 프로젝트 기반 설정

**Files:**
- Create: `requirements.txt`
- Create: `results/.gitkeep`
- Create: `experiments/__init__.py`
- Create: `experiments/context_memory/__init__.py`
- Create: `experiments/coding_failure/__init__.py`

- [ ] **Step 1: requirements.txt 작성**

```
rich>=13.0.0
httpx>=0.27.0
pytest>=8.0.0
python-dotenv>=1.0.0
tiktoken>=0.7.0
```

파일 경로: `/home/jayone/Project/AutoCode/requirements.txt`

- [ ] **Step 2: 의존성 설치**

```bash
cd /home/jayone/Project/AutoCode
pip install -r requirements.txt
```

Expected: Successfully installed rich, httpx, pytest, tiktoken

- [ ] **Step 3: 디렉토리 및 __init__.py 생성**

```bash
mkdir -p experiments/context_memory experiments/coding_failure results tests
touch experiments/__init__.py
touch experiments/context_memory/__init__.py
touch experiments/coding_failure/__init__.py
touch results/.gitkeep
```

- [ ] **Step 4: 커밋**

```bash
git init
git add requirements.txt experiments/ results/
git commit -m "feat: init project structure"
```

---

## Task 2: 실험 A - recall 태스크 생성기

**Files:**
- Create: `experiments/context_memory/tasks.py`
- Create: `tests/test_context_memory.py`

- [ ] **Step 1: 실패 테스트 작성**

`tests/test_context_memory.py`:
```python
import pytest
from experiments.context_memory.tasks import build_recall_prompt, count_tokens

def test_build_recall_prompt_contains_secret():
    prompt, answer = build_recall_prompt(
        context_tokens=1000,
        position="front",
        secret="ALPHA-7734"
    )
    assert "ALPHA-7734" in prompt
    assert answer == "ALPHA-7734"

def test_build_recall_prompt_token_count_approximate():
    prompt, _ = build_recall_prompt(context_tokens=1000, position="middle", secret="TEST-0001")
    tokens = count_tokens(prompt)
    # 허용 오차 20%
    assert 800 <= tokens <= 1200

def test_positions_place_secret_correctly():
    for position in ["front", "middle", "back"]:
        prompt, answer = build_recall_prompt(
            context_tokens=500, position=position, secret="XYZ-9999"
        )
        assert "XYZ-9999" in prompt
        assert answer == "XYZ-9999"
```

- [ ] **Step 2: 테스트 실행 - 실패 확인**

```bash
cd /home/jayone/Project/AutoCode
pytest tests/test_context_memory.py -v
```

Expected: FAILED (ImportError - tasks.py not found)

- [ ] **Step 3: tasks.py 구현**

`experiments/context_memory/tasks.py`:
```python
import random
import string
import tiktoken

PADDING_TEMPLATE = (
    "이것은 컨텍스트 패딩 텍스트입니다. "
    "실험의 정확성을 위해 무의미한 내용이 반복됩니다. "
    "숫자 {n}. "
)

def count_tokens(text: str) -> int:
    """tiktoken cl100k_base 인코더로 토큰 수 근사 계산."""
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

def generate_padding(target_tokens: int) -> str:
    """target_tokens 크기의 패딩 텍스트 생성."""
    result = []
    current = 0
    i = 0
    while current < target_tokens:
        chunk = PADDING_TEMPLATE.format(n=i)
        result.append(chunk)
        current += count_tokens(chunk)
        i += 1
    return "".join(result)

def build_recall_prompt(
    context_tokens: int,
    position: str,  # "front" | "middle" | "back"
    secret: str | None = None,
) -> tuple[str, str]:
    """
    recall 테스트용 프롬프트 생성.
    Returns: (full_prompt, expected_answer)
    """
    if secret is None:
        secret = "SECRET-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    secret_sentence = f"중요: 비밀 코드는 {secret} 입니다. 이 코드를 기억하세요.\n"
    question = f"\n\n질문: 앞에서 언급된 비밀 코드는 정확히 무엇인가요? 코드만 답하세요."

    # 패딩 토큰 수 계산 (secret_sentence + question 토큰 제외)
    overhead = count_tokens(secret_sentence) + count_tokens(question)
    padding_tokens = max(0, context_tokens - overhead)
    padding = generate_padding(padding_tokens)

    if position == "front":
        prompt = secret_sentence + padding + question
    elif position == "middle":
        half = len(padding) // 2
        prompt = padding[:half] + secret_sentence + padding[half:] + question
    elif position == "back":
        prompt = padding + secret_sentence + question
    else:
        raise ValueError(f"Unknown position: {position}")

    return prompt, secret
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_context_memory.py -v
```

Expected: 3 passed

- [ ] **Step 5: 커밋**

```bash
git add experiments/context_memory/tasks.py tests/test_context_memory.py
git commit -m "feat: add context_memory task generator"
```

---

## Task 3: 실험 A - MiniMax API 평가기

**Files:**
- Create: `experiments/context_memory/evaluator.py`
- Modify: `tests/test_context_memory.py` (테스트 추가)

- [ ] **Step 1: 실패 테스트 추가**

`tests/test_context_memory.py`에 추가:
```python
from unittest.mock import patch, AsyncMock
from experiments.context_memory.evaluator import evaluate_recall, RecallResult
import asyncio

def test_evaluate_recall_success():
    """LLM이 정답을 맞춘 경우 is_correct=True."""
    with patch("experiments.context_memory.evaluator.call_minimax") as mock:
        mock.return_value = "ALPHA-7734"
        result = asyncio.run(evaluate_recall(
            prompt="...비밀 코드는 ALPHA-7734...",
            expected="ALPHA-7734",
            context_tokens=1000,
        ))
    assert result.is_correct is True
    assert result.context_tokens == 1000

def test_evaluate_recall_failure():
    """LLM이 오답을 반환한 경우 is_correct=False."""
    with patch("experiments.context_memory.evaluator.call_minimax") as mock:
        mock.return_value = "WRONG-0000"
        result = asyncio.run(evaluate_recall(
            prompt="...비밀 코드는 ALPHA-7734...",
            expected="ALPHA-7734",
            context_tokens=1000,
        ))
    assert result.is_correct is False
```

- [ ] **Step 2: 테스트 실행 - 실패 확인**

```bash
pytest tests/test_context_memory.py::test_evaluate_recall_success -v
```

Expected: FAILED (ImportError)

- [ ] **Step 3: evaluator.py 구현**

`experiments/context_memory/evaluator.py`:
```python
import os
import time
import asyncio
from dataclasses import dataclass
import httpx

MINIMAX_API_URL = "https://api.minimax.io/v1/chat/completions"
MINIMAX_MODEL = "MiniMax-M2.5"

@dataclass
class RecallResult:
    is_correct: bool
    expected: str
    got: str
    context_tokens: int
    position: str
    duration_ms: int

async def call_minimax(prompt: str) -> str:
    """MiniMax API 직접 호출, 응답 텍스트 반환."""
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MINIMAX_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50,
        "temperature": 0.0,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(MINIMAX_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

async def evaluate_recall(
    prompt: str,
    expected: str,
    context_tokens: int,
    position: str = "unknown",
) -> RecallResult:
    start = time.monotonic()
    got = await call_minimax(prompt)
    duration_ms = int((time.monotonic() - start) * 1000)
    is_correct = expected.upper() in got.upper()
    return RecallResult(
        is_correct=is_correct,
        expected=expected,
        got=got,
        context_tokens=context_tokens,
        position=position,
        duration_ms=duration_ms,
    )
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_context_memory.py -v
```

Expected: 5 passed

- [ ] **Step 5: 커밋**

```bash
git add experiments/context_memory/evaluator.py tests/test_context_memory.py
git commit -m "feat: add context_memory evaluator with MiniMax API"
```

---

## Task 4: 실험 B - OpenHands 코딩 태스크 목록

**Files:**
- Create: `experiments/coding_failure/tasks.py`
- Create: `tests/test_coding_failure.py`

- [ ] **Step 1: 실패 테스트 작성**

`tests/test_coding_failure.py`:
```python
from experiments.coding_failure.tasks import get_coding_tasks, CodingTask

def test_get_coding_tasks_returns_20():
    tasks = get_coding_tasks()
    assert len(tasks) == 20

def test_tasks_have_required_fields():
    tasks = get_coding_tasks()
    for t in tasks:
        assert isinstance(t.step, int)
        assert isinstance(t.prompt, str)
        assert t.step >= 1
        assert len(t.prompt) > 10

def test_task_difficulty_increases():
    tasks = get_coding_tasks()
    # 스텝 1-5: 단순 / 16-20: 복잡 (프롬프트 길이로 간접 측정)
    simple_avg = sum(len(t.prompt) for t in tasks[:5]) / 5
    complex_avg = sum(len(t.prompt) for t in tasks[15:]) / 5
    assert complex_avg > simple_avg
```

- [ ] **Step 2: 테스트 실행 - 실패 확인**

```bash
pytest tests/test_coding_failure.py -v
```

Expected: FAILED (ImportError)

- [ ] **Step 3: tasks.py 구현**

`experiments/coding_failure/tasks.py`:
```python
from dataclasses import dataclass

@dataclass
class CodingTask:
    step: int
    prompt: str
    category: str  # "simple" | "multi_file" | "refactor" | "architecture"

def get_coding_tasks() -> list[CodingTask]:
    """20단계 점진적 코딩 태스크 목록 반환."""
    return [
        # 스텝 1-5: 단순 함수 작성
        CodingTask(1, "calculator.py 파일을 만들고 두 수를 더하는 add(a, b) 함수를 작성하세요.", "simple"),
        CodingTask(2, "calculator.py에 subtract(a, b) 함수를 추가하세요.", "simple"),
        CodingTask(3, "calculator.py에 multiply(a, b) 함수를 추가하세요.", "simple"),
        CodingTask(4, "calculator.py에 divide(a, b) 함수를 추가하세요. 0으로 나누면 ValueError를 발생시키세요.", "simple"),
        CodingTask(5, "calculator.py의 모든 함수에 docstring을 추가하세요.", "simple"),
        # 스텝 6-10: 여러 파일 수정
        CodingTask(6, "models.py 파일을 만들고 Product(name, price, quantity) 데이터클래스를 정의하세요.", "multi_file"),
        CodingTask(7, "store.py 파일을 만들고 Product 리스트를 관리하는 Store 클래스를 작성하세요. add_product, remove_product, get_total_value 메서드를 포함하세요.", "multi_file"),
        CodingTask(8, "store.py의 Store 클래스에 search_by_name(query) 메서드를 추가하세요. 대소문자 무시 검색을 지원해야 합니다.", "multi_file"),
        CodingTask(9, "models.py에 Category(name, description) 클래스를 추가하고, Product에 category 필드를 추가하세요. store.py도 함께 업데이트하세요.", "multi_file"),
        CodingTask(10, "utils.py 파일을 만들고 Store의 상품 목록을 CSV 형식 문자열로 변환하는 to_csv(store) 함수를 작성하세요.", "multi_file"),
        # 스텝 11-15: 리팩토링
        CodingTask(11, "store.py의 Store 클래스를 BaseStore 추상 클래스와 InMemoryStore 구현 클래스로 분리하세요. 기존 인터페이스는 유지해야 합니다.", "refactor"),
        CodingTask(12, "models.py의 Product 클래스에 to_dict()와 from_dict() 메서드를 추가하세요. 직렬화/역직렬화가 가능해야 합니다.", "refactor"),
        CodingTask(13, "utils.py에 from_csv(csv_string) 함수를 추가하세요. to_csv의 역연산입니다. models.py의 from_dict를 활용하세요.", "refactor"),
        CodingTask(14, "store.py에 영속성을 추가하세요. save_to_file(filepath)와 load_from_file(filepath) 메서드를 InMemoryStore에 구현하세요. JSON 포맷 사용.", "refactor"),
        CodingTask(15, "모든 파일의 타입 힌트를 완성하세요. mypy --strict 수준을 목표로 합니다.", "refactor"),
        # 스텝 16-20: 아키텍처 변경
        CodingTask(16, "api.py 파일을 만들고 Store를 감싸는 REST API 레이어를 설계하세요. FastAPI 없이 순수 Python으로 라우팅 딕셔너리 방식을 사용하세요. GET /products, POST /products, DELETE /products/{name} 엔드포인트를 구현하세요.", "architecture"),
        CodingTask(17, "events.py 파일을 만들고 이벤트 시스템을 추가하세요. Store에 상품 추가/삭제 시 이벤트가 발생하고, 리스너를 등록할 수 있어야 합니다. Observer 패턴 사용.", "architecture"),
        CodingTask(18, "cache.py 파일을 만들고 Store 조회 결과에 TTL 기반 캐싱을 추가하세요. CachedStore 클래스가 InMemoryStore를 래핑하는 데코레이터 패턴으로 구현하세요.", "architecture"),
        CodingTask(19, "위에서 만든 모든 컴포넌트(Store, Cache, Events, API)를 연결하는 app.py를 작성하세요. 의존성 주입 패턴으로 구성하세요.", "architecture"),
        CodingTask(20, "전체 시스템에 대한 통합 테스트를 test_integration.py에 작성하세요. 상품 추가→캐시 확인→이벤트 발생→API 조회 전체 흐름을 검증하세요.", "architecture"),
    ]
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_coding_failure.py -v
```

Expected: 3 passed

- [ ] **Step 5: 커밋**

```bash
git add experiments/coding_failure/tasks.py tests/test_coding_failure.py
git commit -m "feat: add 20-step coding failure task list"
```

---

## Task 5: 실험 B - OpenHands 평가기

**Files:**
- Create: `experiments/coding_failure/evaluator.py`
- Modify: `tests/test_coding_failure.py` (테스트 추가)

- [ ] **Step 1: 실패 테스트 추가**

`tests/test_coding_failure.py`에 추가:
```python
from unittest.mock import patch, AsyncMock
from experiments.coding_failure.evaluator import (
    run_openhands_task, StepResult, detect_failure_inflection
)
import asyncio

def test_detect_failure_inflection_consecutive():
    """연속 2회 실패 시 급증으로 판정."""
    results = [
        StepResult(step=i, status="success", context_tokens=i*1000, duration_ms=100, error=None)
        for i in range(1, 9)
    ]
    results.append(StepResult(9, "failure", 9000, 100, "error"))
    results.append(StepResult(10, "failure", 10000, 100, "error"))
    inflection = detect_failure_inflection(results)
    assert inflection == 9

def test_detect_failure_inflection_no_inflection():
    """실패가 없으면 None 반환."""
    results = [
        StepResult(step=i, status="success", context_tokens=i*1000, duration_ms=100, error=None)
        for i in range(1, 6)
    ]
    assert detect_failure_inflection(results) is None
```

- [ ] **Step 2: 테스트 실행 - 실패 확인**

```bash
pytest tests/test_coding_failure.py::test_detect_failure_inflection_consecutive -v
```

Expected: FAILED (ImportError)

- [ ] **Step 3: evaluator.py 구현**

`experiments/coding_failure/evaluator.py`:
```python
import time
import asyncio
from dataclasses import dataclass
import httpx

OPENHANDS_URL = "http://localhost:3000"
POLL_INTERVAL = 2.0
MAX_WAIT_SEC = 300  # 5분 타임아웃

@dataclass
class StepResult:
    step: int
    status: str  # "success" | "failure" | "timeout"
    context_tokens: int
    duration_ms: int
    error: str | None

async def run_openhands_task(step: int, prompt: str) -> StepResult:
    """OpenHands에 태스크 전송 후 trajectory 폴링으로 결과 수집."""
    start = time.monotonic()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 대화 생성
        resp = await client.post(
            f"{OPENHANDS_URL}/api/conversations",
            json={"initial_user_msg": prompt, "conversation_trigger": "gui"},
        )
        resp.raise_for_status()
        conversation_id = resp.json()["conversation_id"]

        # trajectory 폴링
        elapsed = 0.0
        last_event_count = 0
        stable_count = 0

        while elapsed < MAX_WAIT_SEC:
            await asyncio.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL

            traj_resp = await client.get(
                f"{OPENHANDS_URL}/api/conversations/{conversation_id}/trajectory"
            )
            if traj_resp.status_code != 200:
                continue

            events = traj_resp.json().get("trajectory", [])
            if len(events) == last_event_count:
                stable_count += 1
                if stable_count >= 3:  # 6초간 새 이벤트 없으면 완료
                    break
            else:
                stable_count = 0
                last_event_count = len(events)

        duration_ms = int((time.monotonic() - start) * 1000)

        # 결과 분석
        if elapsed >= MAX_WAIT_SEC:
            return StepResult(step, "timeout", 0, duration_ms, "timeout exceeded")

        # 마지막 이벤트에서 오류 감지
        error_msg = None
        for event in reversed(events):
            content = str(event.get("observation", "") or event.get("action", ""))
            if any(kw in content.lower() for kw in ["error", "exception", "traceback", "failed"]):
                error_msg = content[:200]
                break

        status = "failure" if error_msg else "success"
        context_tokens = sum(len(str(e)) // 4 for e in events)  # 근사치

        return StepResult(step, status, context_tokens, duration_ms, error_msg)

def detect_failure_inflection(results: list[StepResult]) -> int | None:
    """
    실패 급증 시점(스텝 번호) 반환.
    조건: 연속 2회 실패 OR 구간(5스텝) 실패율이 이전 구간 대비 2배 이상.
    """
    # 조건 1: 연속 2회 실패
    for i in range(1, len(results)):
        if results[i].status == "failure" and results[i-1].status == "failure":
            return results[i-1].step

    # 조건 2: 구간 실패율 2배 이상
    if len(results) >= 10:
        prev_failures = sum(1 for r in results[:5] if r.status == "failure")
        for start in range(5, len(results) - 4):
            window = results[start:start+5]
            curr_failures = sum(1 for r in window if r.status == "failure")
            if prev_failures > 0 and curr_failures >= prev_failures * 2:
                return window[0].step
            prev_failures = curr_failures

    return None
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
pytest tests/test_coding_failure.py -v
```

Expected: 5 passed

- [ ] **Step 5: 커밋**

```bash
git add experiments/coding_failure/evaluator.py tests/test_coding_failure.py
git commit -m "feat: add OpenHands evaluator with trajectory polling"
```

---

## Task 6: 실시간 대시보드

**Files:**
- Create: `dashboard.py`

- [ ] **Step 1: dashboard.py 구현**

`dashboard.py`:
```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.console import Group
import time

console = Console()

@dataclass
class DashboardState:
    experiment: str = ""
    model: str = "MiniMax-M2.5"
    total_steps: int = 0
    current_step: int = 0
    results: list[dict] = field(default_factory=list)
    start_time: float = field(default_factory=time.monotonic)

def render(state: DashboardState) -> Panel:
    elapsed = int(time.monotonic() - state.start_time)
    progress_pct = int(state.current_step / max(state.total_steps, 1) * 100)
    bar = "█" * (progress_pct // 5) + "░" * (20 - progress_pct // 5)

    # 성공/실패 집계
    success = sum(1 for r in state.results if r.get("status") == "success")
    failure = sum(1 for r in state.results if r.get("status") == "failure")
    done = success + failure

    header = (
        f"[bold cyan]실험:[/] {state.experiment}  "
        f"[bold cyan]모델:[/] {state.model}  "
        f"[bold cyan]경과:[/] {elapsed}s\n"
        f"[bold cyan]진행:[/] {state.current_step}/{state.total_steps}  "
        f"[bold cyan]성공:[/] [green]{success}[/]  [bold cyan]실패:[/] [red]{failure}[/]\n"
        f"[{bar}] {progress_pct}%"
    )

    # 최근 로그 테이블
    table = Table(show_header=True, header_style="bold", box=None)
    table.add_column("스텝", width=6)
    table.add_column("상태", width=10)
    table.add_column("상세", width=40)
    table.add_column("토큰", width=10)

    for r in state.results[-8:]:
        status_str = "[green]SUCCESS[/]" if r["status"] == "success" else "[red]FAILURE[/]"
        table.add_row(
            str(r.get("step", "-")),
            status_str,
            str(r.get("task", ""))[:40],
            str(r.get("context_tokens", "-")),
        )

    from rich.text import Text
    return Panel(
        Group(Text.from_markup(header + "\n"), table),
        title="[bold]LLM 장기 컨텍스트 실험[/]",
        subtitle="[dim]Ctrl+C to stop[/]",
    )

class Dashboard:
    def __init__(self, state: DashboardState):
        self.state = state
        self._live = Live(render(state), refresh_per_second=1, console=console)

    def __enter__(self):
        self._live.__enter__()
        return self

    def __exit__(self, *args):
        self._live.__exit__(*args)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.state, k, v)
        self._live.update(render(self.state))

    def add_result(self, result: dict):
        self.state.results.append(result)
        self.state.current_step = result.get("step", self.state.current_step)
        self._live.update(render(self.state))
```

- [ ] **Step 2: 대시보드 동작 확인 (직접 실행)**

```bash
cd /home/jayone/Project/AutoCode
python3 -c "
import time
from dashboard import Dashboard, DashboardState
state = DashboardState(experiment='테스트', total_steps=5)
with Dashboard(state) as d:
    for i in range(1, 6):
        time.sleep(1)
        d.add_result({'step': i, 'status': 'success', 'task': f'태스크 {i}', 'context_tokens': i*1000})
"
```

Expected: 대시보드가 1초마다 갱신되며 5스텝 표시

- [ ] **Step 3: 커밋**

```bash
git add dashboard.py
git commit -m "feat: add rich real-time dashboard"
```

---

## Task 7: runner.py - 실험 실행기

**Files:**
- Create: `runner.py`

- [ ] **Step 1: runner.py 구현**

`runner.py`:
```python
#!/usr/bin/env python3
"""
LLM 장기 컨텍스트 실험 실행기.
Usage:
  python runner.py --exp a   # 실험 A: 기억력 저하
  python runner.py --exp b   # 실험 B: 코딩 실수 시점
"""
import argparse
import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from dashboard import Dashboard, DashboardState
from experiments.context_memory.tasks import build_recall_prompt
from experiments.context_memory.evaluator import evaluate_recall
from experiments.coding_failure.tasks import get_coding_tasks
from experiments.coding_failure.evaluator import run_openhands_task, detect_failure_inflection

RESULTS_DIR = Path("results")
CONTEXT_LENGTHS = [1_000, 10_000, 50_000, 100_000]
POSITIONS = ["front", "middle", "back"]
REPEATS = 3


async def run_experiment_a():
    """실험 A: Lost-in-the-Middle 기억력 저하 측정."""
    total = len(CONTEXT_LENGTHS) * len(POSITIONS) * REPEATS
    state = DashboardState(experiment="A - 기억력 저하", total_steps=total)
    all_results = []
    step = 0

    with Dashboard(state) as dash:
        for ctx_len in CONTEXT_LENGTHS:
            for position in POSITIONS:
                for rep in range(REPEATS):
                    step += 1
                    prompt, expected = build_recall_prompt(
                        context_tokens=ctx_len, position=position
                    )
                    result = await evaluate_recall(
                        prompt=prompt,
                        expected=expected,
                        context_tokens=ctx_len,
                        position=position,
                    )
                    row = {
                        "step": step,
                        "context_tokens": ctx_len,
                        "position": position,
                        "repeat": rep + 1,
                        "status": "success" if result.is_correct else "failure",
                        "expected": result.expected,
                        "got": result.got,
                        "duration_ms": result.duration_ms,
                        "task": f"{ctx_len}tok/{position}/rep{rep+1}",
                    }
                    all_results.append(row)
                    dash.add_result(row)

    _save_results("context_memory", all_results)
    print(f"\n실험 A 완료: {sum(1 for r in all_results if r['status']=='success')}/{total} 성공")


async def run_experiment_b():
    """실험 B: OpenHands 코딩 실수 시점 측정."""
    tasks = get_coding_tasks()
    state = DashboardState(experiment="B - 코딩 실수 시점", total_steps=len(tasks))
    all_results = []

    with Dashboard(state) as dash:
        for task in tasks:
            result = await run_openhands_task(task.step, task.prompt)
            row = {
                "step": result.step,
                "status": result.status,
                "context_tokens": result.context_tokens,
                "duration_ms": result.duration_ms,
                "error": result.error,
                "task": task.prompt[:60],
                "category": task.category,
            }
            all_results.append(row)
            dash.add_result(row)

    from experiments.coding_failure.evaluator import StepResult
    step_results = [
        StepResult(r["step"], r["status"], r["context_tokens"], r["duration_ms"], r["error"])
        for r in all_results
    ]
    inflection = detect_failure_inflection(step_results)

    summary = {
        "total_steps": len(tasks),
        "success_rate": sum(1 for r in all_results if r["status"] == "success") / len(tasks),
        "failure_inflection_step": inflection,
        "failure_inflection_tokens": next(
            (r["context_tokens"] for r in all_results if r["step"] == inflection), None
        ) if inflection else None,
    }
    _save_results("coding_failure", all_results, summary=summary)
    print(f"\n실험 B 완료. 실패 급증 시점: 스텝 {inflection}")


def _save_results(name: str, steps: list, summary: dict | None = None):
    RESULTS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = RESULTS_DIR / f"{name}_{ts}.json"
    data = {
        "experiment": name,
        "model": "minimax/MiniMax-M2.5",
        "timestamp": datetime.now().isoformat(),
        "steps": steps,
        "summary": summary or {},
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"결과 저장: {path}")


def main():
    parser = argparse.ArgumentParser(description="LLM 장기 컨텍스트 실험")
    parser.add_argument("--exp", choices=["a", "b"], required=True, help="실험 선택: a=기억력, b=코딩실수")
    args = parser.parse_args()

    if args.exp == "a":
        asyncio.run(run_experiment_a())
    else:
        asyncio.run(run_experiment_b())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 헬프 메시지 확인**

```bash
cd /home/jayone/Project/AutoCode
source ~/.claude/env/shared.env
python runner.py --help
```

Expected: usage 메시지 출력 (a/b 옵션 표시)

- [ ] **Step 3: 커밋**

```bash
git add runner.py
git commit -m "feat: add experiment runner CLI"
```

---

## Task 8: README 및 최종 통합 테스트

**Files:**
- Create: `README.md`

- [ ] **Step 1: 전체 테스트 실행**

```bash
cd /home/jayone/Project/AutoCode
pytest tests/ -v
```

Expected: 모든 테스트 통과

- [ ] **Step 2: README.md 작성**

`README.md`:
```markdown
# AutoCode - LLM 장기 컨텍스트 실험

## 개요
MiniMax M2.5를 대상으로 장기 컨텍스트 한계를 측정하는 실험 시스템.

## 실험 종류

### 실험 A: 기억력 저하 (Lost-in-the-Middle)
- 컨텍스트 길이: 1K / 10K / 50K / 100K 토큰
- 정보 위치: 앞 / 중간 / 뒤
- 각 조건 3회 반복 → 총 36 데이터포인트

### 실험 B: 코딩 실수 시점
- OpenHands 에이전트로 20단계 코딩 태스크 수행
- 실패 급증 시점 자동 감지

## 실행

```bash
# 환경 설정
pip install -r requirements.txt
source ~/.claude/env/shared.env  # MINIMAX_API_KEY 로드

# 실험 A 실행
python runner.py --exp a

# 실험 B 실행 (OpenHands localhost:3000 필요)
python runner.py --exp b
```

## 결과
`results/` 디렉토리에 JSON 저장됨.
```

- [ ] **Step 3: 최종 커밋**

```bash
git add README.md
git commit -m "feat: complete LLM long-context experiment system"
```

---

## 실험 전 체크리스트

- [ ] `source ~/.claude/env/shared.env` 로 MINIMAX_API_KEY 로드 확인
- [ ] `curl http://localhost:3000/api/settings` 로 OpenHands 동작 확인
- [ ] `python runner.py --help` 정상 출력 확인
- [ ] 실험 A 소요 예상 시간: 약 30~60분 (API 호출 36회)
- [ ] 실험 B 소요 예상 시간: 약 60~120분 (OpenHands 20스텝)

## Related
- [[projects/LiveCode/research/20260330-hypothesis-experiment-results|20260330-hypothesis-experiment-results]]
- [[projects/LiveCode/research/20260325-omc-live-patch-critique|20260325-omc-live-patch-critique]]
- [[projects/LiveCode/research/20260326-omc-live-skill-critique|20260326-omc-live-skill-critique]]
- [[projects/LiveCode/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/LiveCode/research/20260325-autonomous-agent-goal-update-subloop-architecture|20260325-autonomous-agent-goal-update-subloop-architecture]]
- [[projects/LiveCode/research/20260327-omc-live-git-checkpoint-self-evolving-research|20260327-omc-live-git-checkpoint-self-evolving-research]]
