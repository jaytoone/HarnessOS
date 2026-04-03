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
    "agent scaffold": 3, "agent orchestration": 3,
    # 평가/벤치마크 (2.5점)
    "llm evaluation": 2.5, "agent benchmark": 2.5, "agent evaluation": 2.5,
    "skill selection": 2.5, "strategy selection": 2.5,
    "agentic rag": 2.5, "mcp": 2.5, "model context protocol": 2.5,
    # 일반 에이전트 연구 (2점)
    "agentic": 2, "tool use": 2, "multi-agent": 2, "reward model": 2,
    "reinforcement": 2, "rlhf": 2, "rlaif": 2, "chain of thought": 2,
    "reasoning": 2, "planning": 2, "reflection": 2, "self-critique": 2,
    "tool call": 2, "tool calling": 2, "function calling": 2,
    "react agent": 2, "react pattern": 2, "agent framework": 2,
    "code agent": 2, "memory agent": 2, "computer use": 2,
    # 일반 LLM (1점)
    "language model": 1, "foundation model": 1, "fine-tuning": 1, "prompt": 1,
    "ai agent": 1, "llm": 1, "gpt": 1, "claude": 1, "gemini": 1,
    "transformer": 1, "attention": 1, "inference": 1,
    "context window": 1.5, "swarm": 1.5, "agent swarm": 2,
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
    transcript: str | None = None      # YouTube 자막 (video 타입만)
    video_id: str | None = None        # YouTube video ID


def extract_youtube_transcript(
    video_id: str,
    keywords: list[str] | None = None,
    window_sec: float = 45.0,
    max_chars: int = 3000,
) -> str | None:
    """YouTube 영상에서 자막 추출.

    keywords 지정 시: 키워드 주변 ±window_sec 구간만 추출 (관련 구간 집중).
    keywords 없으면: 전체 자막 텍스트 반환 (max_chars 제한).

    Returns:
        str: 자막 텍스트 (관련 구간 or 전체)
        None: 자막 없음
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id)
        snippets = fetched.snippets

        if not keywords:
            # 전체 자막 반환
            return " ".join(s.text for s in snippets)[:max_chars]

        # 키워드 히트 타임스탬프 수집
        kw_lower = [k.lower() for k in keywords]
        hit_times: list[float] = []
        for s in snippets:
            if any(kw in s.text.lower() for kw in kw_lower):
                hit_times.append(s.start)

        if not hit_times:
            # 키워드 없으면 전체 앞부분 반환
            return " ".join(s.text for s in snippets)[:max_chars]

        # 히트 타임스탬프 주변 구간 병합 (겹치는 구간 union)
        intervals: list[tuple[float, float]] = [
            (max(0, t - window_sec), t + window_sec) for t in hit_times
        ]
        # 정렬 후 겹치는 구간 병합
        intervals.sort()
        merged: list[tuple[float, float]] = [intervals[0]]
        for start, end in intervals[1:]:
            if start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))

        # 해당 구간의 snippet만 추출
        relevant_texts: list[str] = []
        for seg_start, seg_end in merged:
            seg_snippets = [s for s in snippets if seg_start <= s.start <= seg_end]
            if seg_snippets:
                chunk = " ".join(s.text for s in seg_snippets)
                ts = f"[{int(seg_start//60)}:{int(seg_start%60):02d}]"
                relevant_texts.append(f"{ts} {chunk}")

        result = " | ".join(relevant_texts)
        return result[:max_chars]

    except Exception:
        return None


def extract_video_id_from_entry(entry) -> str | None:
    """feedparser YouTube entry에서 video ID 추출."""
    # YouTube RSS entries: yt_videoid 필드 또는 id 필드
    vid = getattr(entry, "yt_videoid", None)
    if vid:
        return vid
    entry_id = entry.get("id", "")
    # format: "yt:video:VIDEO_ID"
    if ":" in entry_id:
        return entry_id.split(":")[-1]
    return None


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

    is_youtube = channel.get("type") == "youtube"

    try:
        feed = feedparser.parse(rss_url)
        items = []
        for entry in feed.entries[:30]:  # 최대 30개만 파싱
            title = entry.get("title", "No title")
            link = entry.get("link", "")
            summary_raw = entry.get("summary", entry.get("description", ""))
            # HTML 태그 제거
            summary = re.sub(r"<[^>]+>", " ", summary_raw)[:2000]
            published = parse_date(entry)
            now = datetime.now(timezone.utc)
            age_hours = (now - published).total_seconds() / 3600

            # YouTube: 자막 추출 (관련성 높은 영상만 — 비용 절감)
            video_id = None
            transcript = None
            if is_youtube:
                video_id = extract_video_id_from_entry(entry)

            # 1차 관련성 (제목+설명 기반)
            rel = compute_relevance(title, summary)

            # YouTube: rel >= 0.5 이면 자막 추출 + 키워드 구간 집중
            if is_youtube and video_id and rel >= 0.5:
                # 고가중치 키워드만 추출 대상으로 사용 (가중치 >= 2.0)
                focus_kws = [kw for kw, w in RELEVANCE_KEYWORDS.items() if w >= 2.0]
                transcript = extract_youtube_transcript(
                    video_id,
                    keywords=focus_kws,
                    window_sec=45.0,
                    max_chars=3000,
                )
                if transcript:
                    rel = compute_relevance(title, summary + " " + transcript)
                    # summary에 타임스탬프 구간 포함
                    preview = transcript[:500]
                    summary = f"[transcript segments] {preview}"

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
                transcript=transcript,
                video_id=video_id,
            ))
        return items
    except Exception as e:
        print(f"[WARN] {channel['id']}: {e}", file=sys.stderr)
        return []


def _compute_adaptive_top_n(
    pool_size: int,
    relevant_count: int,
    source_count: int,
) -> int:
    """Adaptive top-N 계산.

    Research basis: RAG top-k 연구 (arXiv:2501.01880) + DynamicRAG (2025)
    - K=5-10 최적, >20 성능 저하 (RAG)
    - 하지만 inhale은 buffer (evolve가 3-5개만 소비) → 상한 50까지 허용
    - 카테고리별 관련 항목 비율이 0~36%로 10배 차이 → 고정 K 부적합

    Formula: K = min(max(relevant*0.8, sources*2), cap)
    """
    if relevant_count == 0:
        return min(5, pool_size)  # 세렌디피티 샘플
    recall_target = int(relevant_count * 0.8)  # 관련 항목 80% 캡처
    min_per_source = source_count * 2          # 소스 다양성 보장
    max_cap = min(50, pool_size)               # RAG 연구 기반 상한
    return min(max(recall_target, min_per_source), max_cap)


def collect(
    focus_category: str,
    top_n: int | None = None,  # None = adaptive (권장)
    sort_by: str = "trending",  # trending | newest | relevance
    min_relevance: float = 0.0,
) -> list[FeedItem]:
    """
    지정된 카테고리 포커스에서 채널들을 수집하고 상위 N개 반환.
    top_n=None이면 adaptive K 사용 (카테고리별 최적 자동 계산).
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

    # Adaptive top_n 계산 (top_n=None일 때)
    if top_n is None:
        relevant_count = sum(1 for i in filtered if i.relevance_score >= 3.0)
        source_count = len(set(i.source_id for i in filtered))
        top_n = _compute_adaptive_top_n(len(filtered), relevant_count, source_count)
        print(f"  [ADAPTIVE] pool={len(filtered)} relevant={relevant_count} "
              f"sources={source_count} → top_n={top_n}", file=sys.stderr)

    # 정렬
    if sort_by == "trending":
        filtered.sort(key=lambda x: x.trending_score, reverse=True)
    elif sort_by == "newest":
        filtered.sort(key=lambda x: x.recency_hours)
    elif sort_by == "relevance":
        filtered.sort(key=lambda x: x.relevance_score, reverse=True)

    # Source diversity 재랭킹: 같은 source_id 반복 시 감쇠 적용
    return _diversity_rerank(filtered, top_n)


def _diversity_rerank(
    items: list[FeedItem],
    top_n: int,
    decay: float = 0.7,
) -> list[FeedItem]:
    """Source diversity 재랭킹.

    같은 source_id에서 이미 선택된 항목이 있으면 후속 항목의
    effective score에 decay^count 감쇠를 적용.
    이를 통해 다양한 소스가 top_n에 포함되도록 함.

    Args:
        items: 이미 정렬된 FeedItem 리스트
        top_n: 반환할 최대 항목 수
        decay: 같은 소스 반복 시 감쇠 계수 (0.7 = 30% 감쇠/중복)
    """
    if not items:
        return []

    selected: list[FeedItem] = []
    source_counts: dict[str, int] = {}
    remaining = list(items)

    for _ in range(min(top_n, len(remaining))):
        # 각 후보의 effective score 계산 (source 중복 감쇠 적용)
        best_idx = 0
        best_effective = -1.0
        for idx, item in enumerate(remaining):
            count = source_counts.get(item.source_id, 0)
            effective = item.trending_score * (decay ** count)
            if effective > best_effective:
                best_effective = effective
                best_idx = idx

        chosen = remaining.pop(best_idx)
        selected.append(chosen)
        source_counts[chosen.source_id] = source_counts.get(chosen.source_id, 0) + 1

    return selected


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
    parser.add_argument("--top", "-n", type=int, default=None,
                        help="Top N items (default: adaptive per category)")
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
