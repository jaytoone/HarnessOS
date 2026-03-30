from dataclasses import dataclass, field
from typing import Any
from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
import time

console = Console()

@dataclass
class DashboardState:
    experiment: str = ""
    model: str = "MiniMax-M2.5"
    total_steps: int = 0
    current_step: int = 0
    results: list[dict[str, Any]] = field(default_factory=list)
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
    def __init__(self, state: DashboardState) -> None:
        self.state = state
        self._live = Live(render(state), refresh_per_second=1, console=console)

    def __enter__(self) -> 'Dashboard':
        self._live.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self._live.__exit__(*args)

    def update(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self.state, k, v)
        self._live.update(render(self.state))

    def add_result(self, result: dict[str, Any]) -> None:
        self.state.results.append(result)
        self.state.current_step = result.get("step", self.state.current_step)
        self._live.update(render(self.state))