"""Coding-failure task definitions: 20-step progressive coding challenges."""
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class CodingTask:
    """A single progressive coding challenge step."""

    step: int
    prompt: str
    category: Literal["simple", "multi_file", "refactor", "architecture"]

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