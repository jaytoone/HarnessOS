# TLDR AI Newsletter Submission

**To:** ai@tldr.tech
**Subject:** LLM agents don't degrade gradually — they cliff-edge. Built HarnessOS to survive it

**Body:**
```
Hi TLDR AI team,

I'd like to submit a link for consideration:

Title: Context degradation in LLM agents is a cliff-edge, not gradual — HarnessOS
URL: https://github.com/jaytoone/HarnessOS

Description:
I measured context degradation directly: agents perform normally up to ~70% context usage,
then fail silently and abruptly — not gradually. This "fuse" behavior, not gradual fade,
changed how HarnessOS was designed.
HarnessOS is infrastructure for running autonomous agents indefinitely: CTX (LLM-free context
precision, 5.2% token budget), omc-live (self-evolving outer loop), omc-live-infinite (context
rotation at 70% threshold + world model persistence, no iteration cap).
All design decisions are experiment-driven: hypothesis debugging -50% attempts; cliff-edge
context degradation; agent failures cluster in 3 classifiable patterns.
214 tests, 100% coverage.

GitHub: https://github.com/jaytoone/HarnessOS

Thanks,
Jay
```

---

## 발송 정보
- Gmail: be2jay67@gmail.com — session-3
- 수신: ai@tldr.tech

## Related
- [[projects/HarnessOS/research/20260326-omc-live-self-evolving-outer-loop|20260326-omc-live-self-evolving-outer-loop]]
- [[projects/HarnessOS/research/20260323-hypothesis-driven-agent-research|20260323-hypothesis-driven-agent-research]]
- [[projects/HarnessOS/research/20260327-omc-live-autonomous-ai-research-2025-2026|20260327-omc-live-autonomous-ai-research-2025-2026]]
- [[projects/HarnessOS/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/HarnessOS/research/20260327-omc-live-git-checkpoint-self-evolving-research|20260327-omc-live-git-checkpoint-self-evolving-research]]
- [[projects/HarnessOS/research/20260330-hypothesis-experiment-results|20260330-hypothesis-experiment-results]]
