#!/usr/bin/env python3
"""
YouTube Deep Analyzer (NotebookLM-style)
자막 추출 + MiniMax LLM 심층 분석 → HarnessOS 실험 인사이트 추출

Usage:
  python scripts/youtube_analyzer.py --url https://youtube.com/watch?v=...
  python scripts/youtube_analyzer.py --category agent_research --top 3
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.knowledge_collector import (
    RELEVANCE_KEYWORDS,
    extract_youtube_transcript,
    load_channels,
    fetch_channel,
)

MINIMAX_API_URL = "https://api.minimax.io/v1/text/chatcompletion_v2"
MINIMAX_MODEL   = "MiniMax-M2.5"

ANALYSIS_PROMPT = """You are a research assistant for HarnessOS.

HarnessOS is a Python-based AI AGENT EVALUATION FRAMEWORK (not a DevOps tool).
It runs controlled experiments on LLM agent behavior, specifically:
- Stuck agent escape: when LLM agents loop without progress, which strategies help them escape?
- Hypothesis-driven reasoning: does forming hypotheses improve agent problem-solving vs engineering-style debugging?
- Category-aware strategy selection: classifying stuck types and routing to best escape strategy
- Multi-agent feedback: when does verification help vs hurt agent performance?
- Autonomous outer loops: self-evolving agent architectures (omc-live, omc-autopilot)

YouTube transcript:
---
{transcript}
---

Provide:

**1. SUMMARY** (1 sentence)

**2. KEY INSIGHTS** (2-3 technical bullets)

**3. HARNESSOS RELEVANCE** (0-10)
Format exactly: "Score: X/10 — reason"
Rate high (7-10) if content covers: agent loops, LLM evaluation, stuck/escape behavior, multi-agent feedback, autonomous agents, self-improvement, reasoning strategies.
Rate medium (4-6) if: general LLM/AI research, evaluation methods, agent architectures.
Rate low (0-3) if: unrelated to AI agents or LLM research.

**4. EXPERIMENT IDEA**
If score >= 4: one concrete experiment for HarnessOS.
If score < 4: "Not applicable."

Response under 350 words."""


def analyze_video(video_id: str, title: str = "") -> dict:
    """단일 YouTube 영상 심층 분석."""
    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        return {"error": "MINIMAX_API_KEY not set"}

    focus_kws = [kw for kw, w in RELEVANCE_KEYWORDS.items() if w >= 1.0]
    transcript = extract_youtube_transcript(
        video_id, keywords=focus_kws, window_sec=60.0, max_chars=3000
    )

    if not transcript:
        return {"error": "No transcript available", "video_id": video_id}

    prompt = ANALYSIS_PROMPT.format(transcript=transcript)

    resp = requests.post(
        MINIMAX_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MINIMAX_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1500,  # <think> 블록 완료에 충분한 토큰
        },
        timeout=30,
    )

    if not resp.ok:
        return {"error": f"API error {resp.status_code}", "detail": resp.text[:200]}

    raw = resp.json()["choices"][0]["message"]["content"]
    # MiniMax <think> CoT 블록 제거
    analysis = re.sub(r"<think>.*?</think>\s*", "", raw, flags=re.DOTALL).strip()

    # relevance score 추출 — "Score: X/10" 또는 "(X/10)" 등 다양한 패턴 허용
    score_match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", analysis)
    score = float(score_match.group(1)) if score_match else 0.0

    return {
        "video_id": video_id,
        "title": title,
        "transcript_chars": len(transcript),
        "harnessos_score": score,
        "analysis": analysis,
    }


def analyze_from_url(youtube_url: str) -> dict:
    """YouTube URL에서 video_id 추출 후 분석."""
    m = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", youtube_url)
    if not m:
        return {"error": f"Cannot extract video ID from: {youtube_url}"}
    return analyze_video(m.group(1))


def analyze_category_top(category: str, top_n: int = 3) -> list[dict]:
    """카테고리에서 YouTube 영상 상위 N개 심층 분석."""
    data = load_channels()
    channels_flat = {
        ch["id"]: (cat, ch)
        for cat, ch_list in data.get("channels", {}).items()
        for ch in ch_list
    }

    focus_ids = data.get("category_focus_map", {}).get(category, [])
    yt_channels = [
        channels_flat[cid]
        for cid in focus_ids
        if cid in channels_flat and channels_flat[cid][1].get("type") == "youtube"
    ]

    all_items = []
    for cat, ch in yt_channels:
        items = fetch_channel(ch, cat)
        # YouTube items with video_id
        yt_items = [i for i in items if i.video_id]
        all_items.extend(yt_items)

    # relevance 순 정렬 후 상위 N개 분석
    all_items.sort(key=lambda x: x.relevance_score, reverse=True)
    results = []

    for item in all_items[:top_n]:
        print(f"  Analyzing: {item.title[:60]}...", file=sys.stderr)
        result = analyze_video(item.video_id, item.title)
        result["source"] = item.source_name
        result["url"] = item.url
        results.append(result)

    return results


def collect_and_rerank(
    category: str,
    top_n: int = 10,
    sort_by: str = "trending",
    min_relevance: float = 0.0,
    analyze_top_k: int = 5,
    alpha: float = 0.4,
) -> list:
    """1차 RSS 수집 + YouTube 상위 K개 LLM 분석 → 2차 re-ranking.

    Final score = alpha * normalized_trending + (1-alpha) * normalized_harnessos
    alpha=0.4: RSS 트렌딩 40% + LLM HarnessOS 관련도 60% 가중치.

    Args:
        analyze_top_k: 1차 정렬 후 LLM 분석할 YouTube 영상 수 (비용 제어)
        alpha: RSS trending 가중치 (1-alpha = LLM harnessos_score 가중치)
    Returns:
        FeedItem 리스트 (harnessos_score 필드 추가), re-ranking 순 정렬
    """
    from scripts.knowledge_collector import collect, FeedItem
    import dataclasses

    # 1차 수집
    items = collect(category, top_n=top_n * 2, sort_by=sort_by, min_relevance=min_relevance)

    # YouTube 영상만 LLM 분석 대상
    yt_items = [i for i in items if i.video_id]
    non_yt_items = [i for i in items if not i.video_id]

    if not yt_items:
        return items[:top_n]

    # 2차 LLM 분석 (상위 analyze_top_k만)
    yt_to_analyze = yt_items[:analyze_top_k]
    yt_scores: dict[str, float] = {}

    for item in yt_to_analyze:
        print(f"  [LLM rerank] {item.title[:55]}...", file=sys.stderr)
        result = analyze_video(item.video_id, item.title)
        if "harnessos_score" in result:
            yt_scores[item.video_id] = result["harnessos_score"]
        else:
            yt_scores[item.video_id] = 0.0

    # trending 정규화 (0~1)
    all_trends = [i.trending_score for i in items] or [1.0]
    max_trend = max(all_trends)
    min_trend = min(all_trends)
    trend_range = max(max_trend - min_trend, 1e-6)

    def final_score(item: FeedItem) -> float:
        norm_trend = (item.trending_score - min_trend) / trend_range
        llm_score = yt_scores.get(item.video_id, 0.0) / 10.0 if item.video_id else 0.0
        if item.video_id in yt_scores:
            return alpha * norm_trend + (1 - alpha) * llm_score
        return alpha * norm_trend  # 미분석 YouTube or 비YouTube

    # 통합 re-ranking: 모든 항목을 final_score로 정렬 (YouTube LLM 분석 여부 무관)
    reranked = sorted(items[:top_n * 2], key=final_score, reverse=True)
    return reranked[:top_n]


def print_analysis(result: dict) -> None:
    if "error" in result:
        print(f"[ERROR] {result['error']}")
        return
    score = result.get("harnessos_score", 0)
    bar = "█" * int(score) + "░" * (10 - int(score))
    print(f"\n{'='*60}")
    print(f"Video: {result.get('title','?')[:60]}")
    print(f"ID: {result.get('video_id','')} | Transcript: {result.get('transcript_chars',0)} chars")
    print(f"HarnessOS Score: {score:.1f}/10 [{bar}]")
    print(f"{'='*60}")
    print(result.get("analysis", ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Deep Analyzer (NotebookLM-style)")
    parser.add_argument("--url", help="YouTube URL to analyze")
    parser.add_argument("--category", help="Analyze top N YouTube videos from category")
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--output", choices=["text", "json"], default="text")
    parser.add_argument("--rerank", action="store_true",
                        help="LLM 2차 re-ranking (collect + analyze + blend scores)")
    parser.add_argument("--analyze-k", type=int, default=5,
                        help="rerank 모드: LLM 분석할 상위 YouTube 영상 수")
    args = parser.parse_args()

    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        print("[ERROR] Set MINIMAX_API_KEY environment variable")
        sys.exit(1)

    if args.url:
        result = analyze_from_url(args.url)
        if args.output == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_analysis(result)

    elif args.category and args.rerank:
        print(f"[RERANK] category={args.category} top={args.top} analyze_k={args.analyze_k}", file=sys.stderr)
        items = collect_and_rerank(args.category, top_n=args.top, analyze_top_k=args.analyze_k)
        if args.output == "json":
            def serialize(item):
                import dataclasses
                d = dataclasses.asdict(item)
                d["published"] = item.published.isoformat()
                return d
            print(json.dumps([serialize(i) for i in items], ensure_ascii=False, indent=2))
        else:
            for i, item in enumerate(items, 1):
                print(f"\n{i}. [{item.relevance_score:.1f}] {item.title}")
                print(f"   {item.url}")
                if item.video_id:
                    print(f"   [YouTube] video_id={item.video_id}")
                print(f"   {item.summary[:200]}")

    elif args.category:
        print(f"Analyzing top {args.top} YouTube videos from '{args.category}'...", file=sys.stderr)
        results = analyze_category_top(args.category, args.top)
        if args.output == "json":
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            for r in results:
                print_analysis(r)
    else:
        parser.print_help()
