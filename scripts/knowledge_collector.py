#!/usr/bin/env python3
"""
Knowledge Collection Pipeline for HarnessOS
docs/knowledge-channels.yaml에 정의된 채널로부터 RSS를 수집하고
HarnessOS 관련성 기준으로 스코어링 후 상위 N개를 반환.

Usage:
  python scripts/knowledge_collector.py --category agent_research --top 10 --sort trending
  python scripts/knowledge_collector.py --category daily_digest --top 5 --sort newest
  python scripts/knowledge_collector.py --list-categories
"""

import argparse
import feedparser
import yaml
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

PROJECT_ROOT = Path(__file__).parent.parent
CHANNELS_FILE = PROJECT_ROOT / "docs" / "knowledge-channels.yaml"

# HarnessOS 관련성 키워드 (가중치)
# 제목 매칭 시 2배 부스트 적용
RELEVANCE_KEYWORDS = {
    # HarnessOS 핵심 개념 (4점 — 가장 높은 우선순위)
    "stuck agent": 4, "harness": 4, "agent harness": 4, "stuck loop": 4,
    "escape strategy": 4, "category-aware": 4,
    # 자율 에이전트 (3점)
    "autonomous agent": 3, "agent loop": 3, "self-improvement": 3,
    "hypothesis validation": 3, "hypothesis-driven": 3, "hypothesis": 3,
    "outer loop": 3, "inner loop": 3, "self-evolving": 3,
    # 평가/벤치마크 (2.5점)
    "llm evaluation": 2.5, "agent benchmark": 2.5, "agent evaluation": 2.5,
    "skill selection": 2.5, "strategy selection": 2.5,
    # 일반 에이전트 연구 (2점)
    "agentic": 2, "tool use": 2, "multi-agent": 2, "reward model": 2,
    "reinforcement": 2, "rlhf": 2, "rlaif": 2, "chain of thought": 2,
    "reasoning": 2, "planning": 2, "reflection": 2, "self-critique": 2,
    # 일반 LLM (1점)
    "language model": 1, "foundation model": 1, "fine-tuning": 1, "prompt": 1,
    "ai agent": 1, "llm": 1, "gpt": 1, "claude": 1, "gemini": 1,
    "transformer": 1, "attention": 1, "inference": 1,
    # 소프트웨어/시스템 (0.5점)
    "pipeline": 0.5, "automation": 0.5, "evaluation": 0.5, "testing": 0.5,
    "experiment": 0.5, "benchmark": 0.5,
}

# 제목에서만 추가 가중치 (제목 매칭 = 핵심 논문일 가능성 높음)
TITLE_BONUS_KEYWORDS = {
    "agent": 1.5, "llm": 1.0, "autonomous": 1.5, "self": 1.0,
    "stuck": 2.0, "harness": 2.0, "evaluation": 1.0, "benchmark": 1.0,
}

# 트렌딩 가중치 기준 (최근성)
TRENDING_DECAY_HOURS = 48  # 48시간 이내 = 최고 트렌딩


@dataclass
class FeedItem:
    title: str
    url: str
    summary: str
    published: datetime
    source_id: str
    source_name: str
    category: str
    relevance_score: float
    recency_hours: float
    trending_score: float
    tags: list


def load_channels() -> dict:
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_date(entry) -> datetime:
    """feedparser entry에서 datetime을 파싱."""
    for field in ["published_parsed", "updated_parsed", "created_parsed"]:
        parsed = getattr(entry, field, None)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def compute_relevance(title: str, summary: str) -> float:
    """HarnessOS 관련성 스코어 계산 (0~10).
    제목 매칭 시 추가 보너스 적용.
    """
    title_lower = title.lower()
    full_text = (title + " " + summary).lower()
    score = 0.0

    # 전체 텍스트 키워드 스코어
    for kw, weight in RELEVANCE_KEYWORDS.items():
        if kw in full_text:
            score += weight

    # 제목 전용 보너스 (핵심 논문 신호)
    for kw, bonus in TITLE_BONUS_KEYWORDS.items():
        if kw in title_lower:
            score += bonus

    return min(score, 10.0)


def compute_trending(published: datetime, relevance: float) -> float:
    """트렌딩 스코어 = 관련성 × 최근성 감쇄."""
    now = datetime.now(timezone.utc)
    age_hours = (now - published).total_seconds() / 3600
    recency = max(0, 1 - age_hours / (TRENDING_DECAY_HOURS * 7))  # 1주일 감쇄
    return relevance * (1 + recency * 2)  # 최신 글은 최대 3배 부스트


def fetch_channel(channel: dict, category: str) -> list[FeedItem]:
    """단일 채널 RSS를 파싱해서 FeedItem 리스트 반환."""
    rss_url = channel.get("rss", "")
    if not rss_url:
        return []

    try:
        feed = feedparser.parse(rss_url)
        items = []
        for entry in feed.entries[:30]:  # 최대 30개만 파싱
            title = entry.get("title", "No title")
            link = entry.get("link", "")
            summary_raw = entry.get("summary", entry.get("description", ""))
            # HTML 태그 제거
            summary = re.sub(r"<[^>]+>", " ", summary_raw)[:500]
            published = parse_date(entry)
            now = datetime.now(timezone.utc)
            age_hours = (now - published).total_seconds() / 3600

            rel = compute_relevance(title, summary)
            trend = compute_trending(published, rel)

            items.append(FeedItem(
                title=title,
                url=link,
                summary=summary.strip(),
                published=published,
                source_id=channel["id"],
                source_name=channel["name"],
                category=category,
                relevance_score=rel,
                recency_hours=age_hours,
                trending_score=trend,
                tags=channel.get("tags", []),
            ))
        return items
    except Exception as e:
        print(f"[WARN] {channel['id']}: {e}", file=sys.stderr)
        return []


def collect(
    focus_category: str,
    top_n: int = 10,
    sort_by: str = "trending",  # trending | newest | relevance
    min_relevance: float = 0.0,
) -> list[FeedItem]:
    """
    지정된 카테고리 포커스에서 채널들을 수집하고 상위 N개 반환.
    sort_by: trending | newest | relevance
    """
    data = load_channels()
    focus_map = data.get("category_focus_map", {})
    all_channels_flat = {}

    for cat, ch_list in data.get("channels", {}).items():
        for ch in ch_list:
            all_channels_flat[ch["id"]] = (cat, ch)

    target_ids = focus_map.get(focus_category, [])
    if not target_ids:
        print(f"[ERROR] Unknown category: {focus_category}", file=sys.stderr)
        print(f"Available: {list(focus_map.keys())}", file=sys.stderr)
        sys.exit(1)

    all_items: list[FeedItem] = []
    for ch_id in target_ids:
        if ch_id not in all_channels_flat:
            continue
        cat, channel = all_channels_flat[ch_id]
        print(f"  Fetching {channel['name']} ({channel['type']})...", file=sys.stderr)
        items = fetch_channel(channel, cat)
        all_items.extend(items)

    # 필터링
    filtered = [i for i in all_items if i.relevance_score >= min_relevance]

    # 정렬
    if sort_by == "trending":
        filtered.sort(key=lambda x: x.trending_score, reverse=True)
    elif sort_by == "newest":
        filtered.sort(key=lambda x: x.recency_hours)
    elif sort_by == "relevance":
        filtered.sort(key=lambda x: x.relevance_score, reverse=True)

    return filtered[:top_n]


def format_markdown(items: list[FeedItem], category: str, sort_by: str) -> str:
    """수집 결과를 마크다운으로 포맷."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"# Knowledge Digest — {date_str}",
        f"**Category**: `{category}` | **Sort**: `{sort_by}` | **Items**: {len(items)}",
        "",
    ]
    for i, item in enumerate(items, 1):
        pub = item.published.strftime("%Y-%m-%d %H:%M")
        age = f"{item.recency_hours:.0f}h ago"
        score_bar = "█" * min(int(item.relevance_score), 10)
        lines += [
            f"## {i}. {item.title}",
            f"- **Source**: {item.source_name} | **Published**: {pub} ({age})",
            f"- **Relevance**: {item.relevance_score:.1f}/10 `{score_bar}`",
            f"- **URL**: {item.url}",
            f"- **Summary**: {item.summary[:300]}..." if len(item.summary) > 300 else f"- **Summary**: {item.summary}",
            "",
        ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="HarnessOS Knowledge Collector")
    parser.add_argument("--category", "-c", default="agent_research",
                        help="Focus category from category_focus_map")
    parser.add_argument("--top", "-n", type=int, default=10, help="Top N items")
    parser.add_argument("--sort", "-s", choices=["trending", "newest", "relevance"],
                        default="trending", help="Sort order")
    parser.add_argument("--min-relevance", type=float, default=0.0,
                        help="Minimum relevance score (0~10)")
    parser.add_argument("--output", "-o", choices=["markdown", "json", "titles"],
                        default="markdown", help="Output format")
    parser.add_argument("--save", action="store_true",
                        help="Save to docs/research/ automatically")
    parser.add_argument("--list-categories", action="store_true",
                        help="List available categories and exit")
    args = parser.parse_args()

    if args.list_categories:
        data = load_channels()
        print("Available categories:")
        for cat, ids in data.get("category_focus_map", {}).items():
            print(f"  {cat}: {ids}")
        return

    print(f"[COLLECT] category={args.category} top={args.top} sort={args.sort}", file=sys.stderr)
    items = collect(args.category, args.top, args.sort, args.min_relevance)

    if args.output == "json":
        def serialize(item):
            d = asdict(item)
            d["published"] = item.published.isoformat()
            return d
        print(json.dumps([serialize(i) for i in items], ensure_ascii=False, indent=2))
    elif args.output == "titles":
        for i, item in enumerate(items, 1):
            print(f"{i}. [{item.relevance_score:.1f}] {item.title}")
    else:
        md = format_markdown(items, args.category, args.sort)
        print(md)

        if args.save:
            date_str = datetime.now().strftime("%Y%m%d")
            out_path = PROJECT_ROOT / "docs" / "research" / f"{date_str}-knowledge-digest-{args.category}.md"
            out_path.write_text(md, encoding="utf-8")
            print(f"\n[SAVED] {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
