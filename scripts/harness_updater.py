#!/usr/bin/env python3
"""
HarnessOS Knowledge Updater
knowledge_collector.py 결과를 받아 HarnessOS 실험/연구에 반영.

Usage:
  # 파이프 사용
  python scripts/knowledge_collector.py --category agent_research --output json | \
    python scripts/harness_updater.py --mode reflect

  # 직접 실행 (수집+반영 한번에)
  python scripts/harness_updater.py --category agent_research --top 5 --auto-collect
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
RESEARCH_DIR = PROJECT_ROOT / "docs" / "research"
DIGEST_DIR = RESEARCH_DIR / "digests"


def load_items_from_stdin() -> list[dict]:
    return json.load(sys.stdin)


def extract_harness_insights(items: list[dict]) -> list[dict]:
    """
    HarnessOS에 직접 반영 가능한 인사이트 추출.
    relevance_score >= 2.0 인 항목만 선별.
    """
    insights = []
    for item in items:
        if item.get("relevance_score", 0) < 2.0:
            continue
        # 키워드 기반 반영 유형 판단
        text = (item["title"] + " " + item.get("summary", "")).lower()
        reflect_type = "general"
        if any(k in text for k in ["stuck", "loop", "plateau", "escape"]):
            reflect_type = "stuck_agent"
        elif any(k in text for k in ["hypothesis", "experiment", "validation", "benchmark"]):
            reflect_type = "hypothesis_validation"
        elif any(k in text for k in ["skill", "tool use", "routing", "agent"]):
            reflect_type = "skill_selection"
        elif any(k in text for k in ["evaluation", "scoring", "metric", "reward"]):
            reflect_type = "evaluation"

        insights.append({**item, "reflect_type": reflect_type})
    return insights


def save_digest(items: list[dict], category: str) -> Path:
    """수집 결과를 날짜별 마크다운으로 저장."""
    DIGEST_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    out_path = DIGEST_DIR / f"{date_str}-{category}.md"

    insights = extract_harness_insights(items)
    lines = [
        f"# Knowledge Digest — {date_str}",
        f"Category: `{category}` | Total items: {len(items)} | HarnessOS-relevant: {len(insights)}",
        "",
        "## HarnessOS Relevant Items",
        "",
    ]

    type_groups: dict[str, list] = {}
    for ins in insights:
        t = ins["reflect_type"]
        type_groups.setdefault(t, []).append(ins)

    for rtype, group in sorted(type_groups.items()):
        lines.append(f"### {rtype.replace('_', ' ').title()}")
        for item in group:
            pub = item.get("published", "")[:10]
            lines += [
                f"- **[{item['source_name']}]** [{item['title']}]({item['url']})",
                f"  - Relevance: {item.get('relevance_score', 0):.1f}/10 | Published: {pub}",
                f"  - {item.get('summary', '')[:200]}",
                "",
            ]

    if not insights:
        lines.append("_No high-relevance items found for this run._\n")

    lines += [
        "## All Items",
        "",
    ]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. [{item['title']}]({item['url']}) — {item['source_name']} (rel={item.get('relevance_score', 0):.1f})")

    content = "\n".join(lines)
    out_path.write_text(content, encoding="utf-8")
    return out_path


def auto_collect_and_reflect(category: str, top: int | None, sort: str) -> None:
    """knowledge_collector를 subprocess로 호출 후 반영."""
    collector = PROJECT_ROOT / "scripts" / "knowledge_collector.py"
    cmd = [
        sys.executable, str(collector),
        "--category", category,
        "--sort", sort,
        "--output", "json",
    ]
    if top is not None:
        cmd.extend(["--top", str(top)])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Collector failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    items = json.loads(result.stdout)
    out_path = save_digest(items, category)
    print(f"[REFLECT] Saved {len(items)} items → {out_path}", file=sys.stderr)

    # 인사이트 요약 출력
    insights = extract_harness_insights(items)
    if insights:
        print(f"\n[INSIGHTS] {len(insights)} HarnessOS-relevant items found:")
        for ins in insights[:5]:
            print(f"  [{ins['reflect_type']}] {ins['title'][:70]}")
    else:
        print("[INSIGHTS] No high-relevance items this run.")


def main():
    parser = argparse.ArgumentParser(description="HarnessOS Knowledge Updater")
    parser.add_argument("--mode", choices=["reflect", "digest"], default="reflect")
    parser.add_argument("--category", "-c", default="agent_research")
    parser.add_argument("--top", "-n", type=int, default=None,
                        help="Top N items (default: adaptive per category)")
    parser.add_argument("--sort", "-s", choices=["trending", "newest", "relevance"],
                        default="trending")
    parser.add_argument("--auto-collect", action="store_true",
                        help="Auto-run collector instead of reading stdin")
    args = parser.parse_args()

    if args.auto_collect:
        auto_collect_and_reflect(args.category, args.top, args.sort)
    else:
        items = load_items_from_stdin()
        out_path = save_digest(items, args.category)
        insights = extract_harness_insights(items)
        print(f"[REFLECT] {len(items)} items → {len(insights)} insights → {out_path}")


if __name__ == "__main__":
    main()
