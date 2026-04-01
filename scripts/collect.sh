#!/usr/bin/env bash
# HarnessOS Knowledge Collection CLI
# Usage: ./scripts/collect.sh [category] [top_n] [sort]
#
# Examples:
#   ./scripts/collect.sh                        # default: agent_research, 10, trending
#   ./scripts/collect.sh daily_digest 5 newest  # daily digest, top 5, newest
#   ./scripts/collect.sh ml_engineering 8 relevance
#   ./scripts/collect.sh --list                 # list categories
#
# Categories: agent_research | ml_engineering | product_growth |
#             system_design  | daily_digest   | trending_tools

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [[ "$1" == "--list" || "$1" == "-l" ]]; then
    python3 "$SCRIPT_DIR/knowledge_collector.py" --list-categories
    exit 0
fi

CATEGORY="${1:-agent_research}"
TOP="${2:-10}"
SORT="${3:-trending}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " HarnessOS Knowledge Pipeline"
echo " Category: $CATEGORY | Top: $TOP | Sort: $SORT"
echo " Date: $(date '+%Y-%m-%d %H:%M')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 "$SCRIPT_DIR/harness_updater.py" \
    --auto-collect \
    --category "$CATEGORY" \
    --top "$TOP" \
    --sort "$SORT"

echo ""
echo "Output: docs/research/digests/$(date +%Y%m%d)-${CATEGORY}.md"
