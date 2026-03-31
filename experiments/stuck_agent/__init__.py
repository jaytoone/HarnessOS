"""Stuck-Agent Escape Rate Experiment.

Experiment D: validates that hypothesis-driven rescue outperforms
continued engineering when an agent is stuck (has failed at least once).

Pipeline:
  Phase 1 — Engineering attempt → FAIL (defines "stuck" state)
  Phase 2a — Engineering rescue (control): retry with "try again" prompt
  Phase 2b — Hypothesis rescue (treatment): structured root-cause reasoning

Key metric: escape_rate_uplift = hyp_escape_rate - eng_escape_rate
Statistical test: McNemar's test (paired binary outcomes) + Cohen's d
"""
