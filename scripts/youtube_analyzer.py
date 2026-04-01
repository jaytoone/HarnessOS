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

    prompt = ANALYSIS_PROMPT.format(transcript=transcript[:2500])

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
