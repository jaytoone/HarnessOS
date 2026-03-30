"""Context-memory task builders: padding generation and recall prompt construction."""
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