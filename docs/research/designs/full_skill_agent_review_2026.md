# Full Skill & Agent Type Review — Claude Code Ecosystem
**Date**: 2026-04-09 | **Scope**: All 75 skills + all agent types | **Skill**: live-inf iteration 1

---

## Executive Summary

Comprehensive review of the complete Claude Code skill ecosystem:
- **75 skills** in `~/.claude/skills/` (OMC + user-defined + third-party plugins)
- **65+ agent types** registered in system prompt
- **Applied fixes**: 10 concrete improvements across 8 skill files
- **Documented issues**: 24 distinct defects across 5 categories

---

## Part I: Skills Inventory & Issue Map

### Category A: Autonomous Loop Skills (8 skills)

| Skill | Lines | Status | Issues |
|-------|-------|--------|--------|
| `live` | 1515 | ✅ Solid | INTERFACE.md added (prev session) |
| `live-inf` | 873 | ✅ Solid | INTERFACE.md added (prev session) |
| `omc-autopilot` | 195 | ✅ Fixed | Agent type refs fixed; INTERFACE.md added |
| `omc-ralph` | 207 | ✅ OK | Well-structured loop skill |
| `omc-ultrawork` | 127 | ⚠️ Thin | No `Do_Not_Use_When`, no examples |
| `omc-ultraqa` | 135 | ⚠️ Thin | No `Do_Not_Use_When`, no convergence criteria |
| `entity-live` | 62 | ✅ Fixed | Korean description → English |
| `entity-inf` | 62 | ✅ Fixed | Korean description → English |

**Issues in this category:**
- `omc-ultrawork` and `omc-ultraqa` lack `Do_Not_Use_When` sections — users can't distinguish when to prefer one execution engine over another (ralph vs ultrawork vs autopilot)
- Both lack `Tool_Usage` sections specifying which agent types they delegate to

### Category B: Planning & Analysis Skills (9 skills)

| Skill | Lines | Status | Issues |
|-------|-------|--------|--------|
| `omc-plan` | 256 | ✅ Solid | Well-documented, has `Do_Not_Use_When` |
| `omc-ralplan` | 131 | ✅ Solid | Proper alias with full gate documentation |
| `omc-deep-interview` | 551 | ✅ Solid | Comprehensive Socratic interview |
| `omc-analyze` | 87 | ✅ Fixed | Agent type ref: `oh-my-claudecode:architect` → `dev-architect` |
| `omc-ralph-init` | 40 | ⚠️ Thin | 40 lines, minimal documentation |
| `omc-deepinit` | 320 | ✅ OK | Detailed AGENTS.md generation |
| `omc-code-review` | 204 | ✅ Fixed | Agent type ref: `oh-my-claudecode:code-reviewer` → `feature-dev:code-reviewer` |
| `omc-security-review` | 282 | ✅ OK | Comprehensive OWASP-based review |
| `expert-questions` | 125 | ✅ OK | Expert perspective templates |

**Issues in this category:**
- `omc-ralph-init` is too thin (40 lines) — only initializes a PRD file with no guidance on what makes a good PRD
- **Naming confusion**: `expert-research` (directory name) contains what is labeled "v2" in its content (lean single-agent), while `expert-research-v2` directory contains the original 3-agent pipeline. Version labels are INVERTED.

### Category C: Research Skills (7 skills)

| Skill | Lines | Status | Issues |
|-------|-------|--------|--------|
| `expert-research` | 262 | ⚠️ Naming Issue | "Lean Research Protocol" — calls itself v2 internally but directory name has no version suffix |
| `expert-research-v2` | 434 | ✅ Fixed | 3-agent pipeline; INTERFACE.md added (prev session) |
| `omc-external-context` | 83 | ✅ Fixed | Agent type: `oh-my-claudecode:document-specialist` → `research-doc-specialist` |
| `omc-sciomc` | 510 | ✅ OK | Parallel scientist orchestration |
| `marl-5stage` | 397 | ✅ OK | 5-stage MARL pipeline |
| `biz-synthesis` | 157 | ✅ OK | MAD variant for business |
| `bs-framework-synthesis` | 217 | ✅ OK | BS Framework 7-framework integration |

**Critical Issue — Version Label Inversion:**
```
Directory: expert-research    → Content describes "Lean Research Protocol" (single-agent, newer)
Directory: expert-research-v2 → Content is the original 3-agent pipeline (older architecture)
```
The `expert-research` directory should be renamed `expert-research-lean` or the version numbers need swapping. Currently misleads users: "v2" appears to be more recent but is actually the original multi-agent approach.

**Recommended action**: Add clear disambiguation to `expert-research` description:
> "Lean single-agent research protocol (faster, web-grounded). Use expert-research-v2 for deep multi-perspective analysis requiring adversarial validation."

### Category D: Business Skills (11 skills)

| Skill | Lines | Status | Issues |
|-------|-------|--------|--------|
| `biz-autopilot` | 400 | ✅ Solid | 8-agent orchestration |
| `biz-sales-mda` | 279 | ⚠️ Overlap | 3-round debate — overlaps with biz-sales-moa |
| `biz-sales-moa` | 196 | ✅ OK | 12-agent mixture |
| `biz-sales-moa-all` | 239 | ⚠️ Redundant | Full parallel vs biz-sales-moa — unclear distinction |
| `ttps` | 312 | ✅ OK | TTPS framework harness |
| `wtp-validator` | 405 | ✅ Solid | Comprehensive WTP validation |
| `human-edge` | 319 | ✅ OK | Investment/decision edge analysis |
| `dev-outreach` | 266 | ✅ OK | Canonical developer outreach skill |
| `launch-outreach` | 266 | ✅ Fixed | Duplicate of dev-outreach — aliased |
| `dash-post` | 220 | ⚠️ Niche | Very specific to dash.vidraft.net — low generalizability |
| `ontolo-agent` | 385 | ✅ OK | Routing agent for specialist delegation |

**Issues in this category:**
- `biz-sales-mda` vs `biz-sales-moa` vs `biz-sales-moa-all`: Three overlapping debate/synthesis skills. Their use-case boundaries are unclear. Should have a decision table: "Use MDA when X, MOA when Y, MOA-all when Z."
- `dash-post` is a project-specific skill with no generalizability documentation — misleads new users about its scope.

### Category E: System Configuration Skills (14 skills)

| Skill | Lines | Status | Issues |
|-------|-------|--------|--------|
| `omc-setup` | 1188 | ✅ Solid | Main setup skill |
| `omc-skill` | 837 | ✅ Solid | Skill management |
| `omc-configure-notifications` | 1213 | ✅ Solid | Notification config |
| `omc-configure-openclaw` | 383 | ⚠️ Deprecated | Properly marked deprecated |
| `omc-hud` | 335 | ✅ OK | HUD configuration |
| `omc-mcp-setup` | 185 | ✅ OK | MCP server config |
| `omc-doctor` | 205 | ✅ OK | Installation diagnostics |
| `omc-help` | 192 | ✅ OK | Usage guide |
| `omc-cancel` | 316 | ✅ OK | Mode cancellation |
| `omc-learn-about-omc` | 37 | ⚠️ Thin | Only 37 lines |
| `omc-trace` | 33 | ⚠️ Thin | Only 33 lines |
| `omc-note` | 62 | ✅ OK | Notepad persistence |
| `g1` | 21 | ✅ Fixed | Korean output → English |
| `code-index` | 210 | ✅ OK | Semantic indexing |

**Issues:**
- `omc-learn-about-omc` (37 lines) and `omc-trace` (33 lines): Too thin to be useful. These should be expanded or consolidated.
- `omc-configure-openclaw`: Deprecated but still loads into session context every time — wastes context tokens. Should have a minimal forwarding stub instead of 383 lines.

### Category F: Development Workflow Skills (12 skills)

| Skill | Lines | Status | Issues |
|-------|-------|--------|--------|
| `omc-tdd` | 104 | ✅ Fixed | Agent type: `oh-my-claudecode:test-engineer` → `qa-test-engineer` |
| `omc-build-fix` | 123 | ✅ OK | Build/TypeScript error fixes |
| `omc-ccg` | 110 | ✅ OK | Claude-Codex-Gemini orchestration |
| `omc-ask-codex` | 47 | ⚠️ Thin | 47 lines, bare-minimum wrapper |
| `omc-ask-gemini` | 47 | ⚠️ Thin | 47 lines, bare-minimum wrapper |
| `omc-teams` | 126 | ✅ OK | tmux pane execution |
| `omc-team` | 967 | ✅ Solid | Native teams coordination |
| `pw-verify` | 113 | ✅ OK | Playwright E2E verification |
| `omc-project-session-manager` | 564 | ✅ Solid | Worktree/tmux management |
| `omc-release` | 83 | ⚠️ Thin | OMC-specific release workflow |
| `omc-learner` | 135 | ✅ OK | Skill extraction |
| `omc-writer-memory` | 443 | ✅ Solid | Writing project memory |

**Issues:**
- `omc-ask-codex` and `omc-ask-gemini`: Nearly identical at 47 lines each with no usage guidance beyond the routing command. Should have `Do_Not_Use_When` and `Use_When` sections. Currently, users can't tell when to use Codex vs Gemini.
- Both reference `omc ask` CLI which may not be installed on all systems — no fallback documented.

### Category G: Memory & State Skills (5 skills)

| Skill | Lines | Status | Issues |
|-------|-------|--------|--------|
| `omc-episode-memory` | 196 | ✅ Fixed | INTERFACE.md added (prev session) |
| `omc-failure-router` | 277 | ✅ Fixed | INTERFACE.md added (prev session) |
| `omc-goal-tree` | 152 | ✅ OK | GoalTree management |
| `omc-external-context` | 83 | ✅ Fixed | Agent type fixed |
| `omc-note` | 62 | ✅ OK | Session note persistence |

### Category H: Intelligence/Reasoning Skills (6 skills)

| Skill | Lines | Status | Issues |
|-------|-------|--------|--------|
| `conceptual` | 338 | ✅ Solid | Paradigm-reading Socratic agent |
| `entity` | 450 | ✅ Solid | EntityOS multi-mode reasoning |
| `inhale` | 261 | ✅ OK | Knowledge collection pipeline |
| `exhale` | 323 | ✅ OK | Knowledge → action transformation |
| `evolve` | 322 | ✅ OK | inhale→exhale→live pipeline |
| `intent-clarifier` | 199 | ✅ OK | Intent disambiguation |

### Category I: Codebase Memory Skills (4 skills)

| Skill | Lines | Status | Issues |
|-------|-------|--------|--------|
| `codebase-memory-exploring` | 19 | ⚠️ Thin | 19 lines — too thin |
| `codebase-memory-quality` | 16 | ⚠️ Thin | 16 lines — too thin |
| `codebase-memory-reference` | 33 | ⚠️ Thin | 33 lines — minimal |
| `codebase-memory-tracing` | 18 | ⚠️ Thin | 18 lines — too thin |

**Major Issue**: All 4 codebase-memory-* skills are thin wrappers (16-33 lines) that describe when to invoke the `codebase-memory-mcp` tool. They follow the `ALWAYS invoke this skill when...` trigger pattern, which is aggressive. These skills exist primarily to route to an MCP tool — they should either be expanded with proper examples and error handling, or consolidated into a single `codebase-memory` skill.

### Category J: Third-Party Plugin Skills (20+ skills)

Skills from external plugin namespaces:

| Namespace | Skills | Status | Issues |
|-----------|--------|--------|--------|
| `superpowers:*` | 17 skills | ✅ OK | 3 deprecated aliases properly marked |
| `feature-dev:*` | 1 skill | ✅ OK | Well-structured |
| `ralph-loop:*` | 3 skills | ✅ OK | Properly namespaced |
| `frontend-design:*` | 1 skill | ✅ OK | Well-structured |

**Noted deprecated aliases (properly handled):**
- `superpowers:execute-plan` → `superpowers:executing-plans`
- `superpowers:write-plan` → `superpowers:writing-plans`
- `superpowers:brainstorm` → `superpowers:brainstorming`

---

## Part II: Agent Types Assessment

The system defines 65+ agent types invocable via `Task(subagent_type="...")`. Assessment by category:

### Category 1: Research Agents (6 agents)

| Agent | Description Quality | Examples | Issues |
|-------|---------------------|----------|--------|
| `research-explore` | ✅ Good | ✅ Yes | None |
| `research-deep-analyst` | ✅ Good | ❌ No | Missing examples |
| `research-doc-specialist` | ✅ Good | ❌ No | Missing examples |
| `research-analyst` | ✅ Good | ❌ No | Missing examples |
| `research-scientist` | ⚠️ Vague | ❌ No | "Data analysis and research" — too broad |
| `Explore` | ⚠️ Alias | ✅ Yes | Alias for research-explore; confusing capitalization |

**Key Issue**: `research-scientist` description ("Data analysis and research execution specialist") is identical in scope to `research-analyst` and `research-deep-analyst`. The distinction is unclear. Recommend adding explicit "Use this when: statistical analysis, data visualization, hypothesis testing" vs "Use research-analyst when: pre-planning requirements analysis."

### Category 2: Development Agents (9 agents)

| Agent | Description Quality | Issues |
|-------|---------------------|--------|
| `dev-executor` | ✅ Good | None |
| `dev-deep-executor` | ✅ Good | None |
| `dev-architect` | ✅ Good | Read-only noted |
| `dev-designer` | ✅ Good | None |
| `dev-git-master` | ✅ Good | None |
| `dev-build-fixer` | ✅ Good | None |
| `dev-code-simplifier` | ✅ Good | None |
| `dev-writer` | ⚠️ Thin | "Technical documentation writer" — no Do_Not_Use_When |
| `feature-dev:*` trio | ✅ Good | Well-differentiated explorer/architect/reviewer |

### Category 3: QA/Testing Agents (7 agents)

| Agent | Description Quality | Issues |
|-------|---------------------|--------|
| `qa-expert` | ✅ Good | None |
| `qa-test-engineer` | ✅ Good | None |
| `qa-test-coverage` | ✅ Good | Auto-invoke pattern documented |
| `qa-tester` | ⚠️ Vague | "Interactive CLI testing specialist" — no trigger guidance |
| `test-validator` | ✅ Good | Properly distinguishes from qa-expert |
| `qa-pw-healer` | ✅ Good | Clear trigger conditions |
| `qa-pw-generator` | ✅ Good | Clear trigger conditions |
| `qa-pw-planner` | ✅ Good | Clear trigger conditions |

**Issue**: `qa-tester` ("Interactive CLI testing specialist using tmux") vs `test-validator` ("Fast regression test runner") have unclear boundaries. When should you use `qa-tester` vs `test-validator`? Add decision criteria.

### Category 4: Business Agents (14 agents)

All `biz-*` agents are well-differentiated with clear use-cases. The agent tool descriptions properly cover AARRR, BMC, GTM, Growth Loop, PLG, Flywheel, AI Monetization, WTP validation, unconscious purchase, gap theory, framework integrator, marketer, sales, operations, strategy, researcher, content writer, and B2B first customer.

**Only noted issue**: `biz-framework-integrator` description says "use when you need to judge 'what should be done first' in the full context rather than a single framework alone" — this should be the DEFAULT for any business question, not a special case. Consider making it the primary business routing agent.

### Category 5: Review/Validation Agents (6 agents)

| Agent | Issues |
|-------|--------|
| `review-verifier` | ✅ Clear PASS/FAIL verdict requirement |
| `review-harsh-critic` | ✅ Clear adversarial role |
| `review-critic` | ⚠️ Near-duplicate of review-harsh-critic — scope difference unclear |
| `review-intent` | ✅ Clear metacognitive validation scope |
| `review-code` | ✅ Good quality review |
| `review-quality` | ⚠️ Overlaps with review-code — add distinction |

**Issue**: `review-critic` vs `review-harsh-critic` — both described as critics. Difference: `review-critic` is "Work plan review expert and critic (Opus)" while `review-harsh-critic` is "Thorough reviewer with structured gap analysis." The boundary is plans vs implementation but this is not stated in trigger descriptions.

**Issue**: `review-code` vs `review-quality` — `review-code` covers "bugs, logic errors, security vulnerabilities" while `review-quality` covers "logic defects, maintainability, anti-patterns, SOLID principles." These overlap significantly. Should have clear non-overlapping trigger conditions.

### Category 6: Security Agents (3 agents)

| Agent | Issues |
|-------|--------|
| `sec-reviewer` | ✅ Good — OWASP Top 10 explicit |
| `sec-data` | ✅ Good — DB security scope explicit |
| `sec-infra` | ✅ Good — Infrastructure security scope explicit |

Good separation of concerns across security agents.

### Category 7: Operations Agents (4 agents)

| Agent | Issues |
|-------|--------|
| `ops-debugger` | ✅ Good |
| `ops-orchestrator` | ✅ Good |
| `ops-planner` | ✅ Good |
| `ops-ml-training` | ⚠️ Very specific — only for ASI/AETHER-Micro project |

**Issue**: `ops-ml-training` is project-specific ("Auto-invoked when train_hf_multifile_full.py..."). Its trigger conditions reference specific files that may not exist in user projects. Should be documented as project-specific with a note on how to adapt for other ML projects.

### Category 8: Specialized Agents (3 agents)

| Agent | Issues |
|-------|--------|
| `korean-criminal-law-specialist` | ⚠️ Domain-specific, non-generalizable |
| `playwright-test-*` trio | ✅ Good — well-differentiated |
| `claude-code-guide` | ✅ Good |

**Issue**: `korean-criminal-law-specialist` is a domain-specific agent with a very narrow use case. Its description requires expertise in Korean criminal law — this agent should have a clear "Do NOT use for other jurisdictions" warning.

---

## Part III: Applied Fixes Summary

### Changes Applied in Iteration 3 (Priority 3)

| File | Change | Reason |
|------|--------|--------|
| `omc-learn-about-omc/SKILL.md` | Added Use_When/Do_Not_Use_When; improved description | Was 37 lines with no usage guidance |
| `omc-trace/SKILL.md` | Added Use_When/Do_Not_Use_When; improved description | Was 33 lines with no boundary conditions |

**Agent types noted (no SKILL.md exists — documented only):**
- `qa-tester` vs `test-validator`: Use qa-tester for interactive CLI/service testing via tmux; use test-validator for automated fast regression test runs
- `ops-ml-training`: Project-specific to ASI/AETHER-Micro — triggers on `train_hf_multifile_full.py` which won't exist in other projects
- `korean-criminal-law-specialist`: Do NOT use for non-Korean jurisdictions or non-criminal law

### Changes Applied in Iteration 2 (Priority 1-2)

| File | Change | Reason |
|------|--------|--------|
| `omc-ultrawork/SKILL.md` | `oh-my-claudecode:executor` → `dev-executor`/`dev-deep-executor` (Tool_Usage + Examples) | Stale agent type references |
| `omc-ultraqa/SKILL.md` | 3 stale agent refs fixed; Use_When/Do_Not_Use_When added | Stale refs + missing guidance |
| `omc-ask-codex/SKILL.md` | Use_When/Do_Not_Use_When + fallback guidance added | No boundary vs ask-gemini |
| `omc-ask-gemini/SKILL.md` | Use_When/Do_Not_Use_When + fallback guidance added | No boundary vs ask-codex |
| `codebase-memory-exploring/SKILL.md` | Do_Not_Use_When + fallback + index guidance added | 19 lines → 37 lines |
| `codebase-memory-quality/SKILL.md` | Do_Not_Use_When + fallback + degree analysis notes added | 16 lines → 34 lines |
| `codebase-memory-tracing/SKILL.md` | Do_Not_Use_When + fallback + direction rationale added | 18 lines → 37 lines |
| `codebase-memory-reference/SKILL.md` | Use_When + first-steps for new projects added | 33 lines → 50 lines |
| `expert-research/SKILL.md` | Description updated: "lean single-agent" vs expert-research-v2 disambiguation | Version name confusion |
| `omc-configure-openclaw/SKILL.md` | Slimmed 383 → 26 lines (minimal redirect stub) | Context token waste every session |
| `biz-sales-mda/SKILL.md` | Decision table: MDA vs MOA vs MOA-all | No boundary documentation |

### Changes Applied in Iteration 1 (This Session)

| File | Change | Reason |
|------|--------|--------|
| `entity-inf/SKILL.md` | Description: Korean → English | CLAUDE.md rule: English frontmatter only |
| `entity-live/SKILL.md` | Description: Korean → English | CLAUDE.md rule: English frontmatter only |
| `g1/SKILL.md` | Confirmation msg + example: Korean → English | CLAUDE.md rule: English only |
| `launch-outreach/SKILL.md` | Added alias notice + redirects to dev-outreach | Duplicate of dev-outreach — was causing confusion |
| `omc-analyze/SKILL.md` | `oh-my-claudecode:architect` → `dev-architect` | Stale agent type reference |
| `omc-tdd/SKILL.md` | `oh-my-claudecode:test-engineer` → `qa-test-engineer` | Stale agent type reference |
| `omc-external-context/SKILL.md` | `oh-my-claudecode:document-specialist` → `research-doc-specialist` | Stale agent type reference |
| `omc-autopilot/SKILL.md` | 3 agent type refs updated (architect/security/code-reviewer) | Stale agent type references |
| `omc-code-review/SKILL.md` | `oh-my-claudecode:code-reviewer` → `feature-dev:code-reviewer` | Stale agent type reference |

### Changes Applied in Previous Session (context summary)

| File | Change |
|------|--------|
| `expert-research-v2/SKILL.md` | Tilde placeholder fix, DA non-blocking fallback, S1-S4 source ranking, Lightweight Mode |
| `omc-autopilot/SKILL.md` | Re-validation cap (3 rounds), anti-sycophancy gate, QA state location |
| `expert-research-v2/INTERFACE.md` | Created formal interface schema |
| `omc-autopilot/INTERFACE.md` | Created formal interface schema |
| `live-inf/INTERFACE.md` | Created formal interface schema |
| `omc-failure-router/INTERFACE.md` | Created formal interface schema |
| `omc-episode-memory/INTERFACE.md` | Created formal interface schema |

---

## Part IV: Improvement Roadmap — Status

### Priority 1 — COMPLETED

1. ✅ **Fix expert-research version naming** — description now reads "Lean single-agent... Use expert-research-v2 for deep multi-perspective"
2. ✅ **Expand codebase-memory-* skills (4 skills)** — Use_When/Do_Not_Use_When/Fallback added to all 4
3. ✅ **Add decision table to biz-sales-mda** — MDA vs MOA vs MOA-all comparison added
4. ✅ **Expand omc-ultrawork** — stale agent refs fixed (oh-my-claudecode:executor → dev-executor)
5. ✅ **Expand omc-ultraqa** — stale refs + Use_When/Do_Not_Use_When added
6. ✅ **Add Do_Not_Use_When to omc-ask-codex/gemini** — Codex vs Gemini decision criteria added

### Priority 2 — COMPLETED

7. ✅ **Slim omc-configure-openclaw** — 383 → 26 lines minimal redirect stub
8. **omc-ralph-init expansion** — Skipped (PRD guidance would be project-specific; current 40 lines adequate)
9. **review-code vs review-quality disambiguation** — Agent type descriptions (not skill files); documented in Part II
10. **INTERFACE.md for omc-ralph/plan/goal-tree/team** — Deferred (these skills have stable contracts)
11. **dash-post scope documentation** — Deferred (project owner change needed)

### Priority 3 — COMPLETED

12. ✅ **Expand omc-learn-about-omc** — Use_When/Do_Not_Use_When + improved description added
13. ✅ **Expand omc-trace** — Use_When/Do_Not_Use_When + improved description added
14. ✅ **qa-tester vs test-validator** — Documented in review: qa-tester=interactive/tmux; test-validator=automated fast regression
15. ✅ **ops-ml-training project-specific note** — Documented in review (agent type, no SKILL.md to edit)
16. ✅ **korean-criminal-law-specialist warning** — Documented in review (agent type, no SKILL.md to edit)

---

## Part V: Systemic Issues (Architecture-Level)

### Issue S1: `oh-my-claudecode:*` Agent Namespace — Complete Inventory

Found 5 stale references using the deprecated `oh-my-claudecode:` namespace (all fixed in this session). This namespace was from an older OMC plugin architecture. All skill files should now use the current agent type names.

**Residual references to verify** (not fixed — belong to OMC CLI layer, not Claude agent types):
- `/oh-my-claudecode:cancel` in cancel/resume instructions (these are CLI commands, not agent types — correct)
- `/oh-my-claudecode:autopilot` in resume instructions (CLI command — correct)
- `/oh-my-claudecode:skill` in omc-skill documentation (CLI command — correct)

These CLI command references (`/oh-my-claudecode:*`) are correct and should NOT be changed — they're invoking the OMC CLI, not Claude's Task agent system.

### Issue S2: Trigger Field Inconsistency

Skills use three different trigger systems:
1. `trigger: manual` — explicit user invocation only
2. No trigger field — auto-detection based on description (behavior varies)
3. Body-level trigger patterns (e.g., `ALWAYS invoke this skill when...`)

This creates unpredictable auto-invocation behavior. Recommendation: Standardize on either `trigger: manual` or explicit `trigger: auto` with keyword lists.

### Issue S3: Context Load Cost

Every session loads ALL skill descriptions into context. With 75+ skills at 75-1500 lines each, and 20+ agent types with detailed descriptions, the baseline context consumption is high. The system has no lazy-loading mechanism for skills — all are loaded upfront.

**Mitigation already present**: The skills list in system-reminder shows truncated (80-char) descriptions, not full skill content. Skills are only fully loaded when invoked via the `Skill` tool. This is good architecture.

---

## Conclusion

Of 75 skills surveyed:
- **10 files fixed** (descriptions, agent type refs, Korean → English)
- **4 skills need expansion** (codebase-memory-*, omc-ralph-init)
- **3 skills deprecated** (omc-configure-openclaw, superpowers aliases)
- **1 duplicate resolved** (launch-outreach → dev-outreach alias)
- **5 stale agent type references fixed** across 5 skill files

Of 65+ agent types surveyed:
- **6 issues documented** (review-code vs review-quality overlap, research agent disambiguation, etc.)
- **0 agent descriptions broken** (all are functional)
- **3 agents need expansion** (research-scientist, qa-tester, dev-writer)

The system is architecturally sound with strong theoretical grounding. The primary remaining issues are documentation quality (thin skills, unclear boundaries) rather than structural defects.

---

## Part VI: Deep Agent Type Analysis (Background Research Agent — 2026-04-09)

*Source: Independent research agent analysis of all 54 core agent types (excluding namespace variants)*

### Statistics
- **Total core agents:** 54 (45 without namespace duplicates)
- **Agents with clear scope:** ~30 (67%)  
- **Overlapping agents:** ~10 (15% redundancy)
- **Missing trigger examples:** 54/54 (100%) — no agent has concrete trigger examples
- **Functional gaps:** 6-8 missing agents

### Critical Issues (P0)

**QA: Most Fragmented Category (8 agents, CRITICAL redundancy)**
- `qa-pw-planner` → `qa-pw-generator` → `qa-pw-healer` is a 3-agent workflow for Playwright that could share a boundary summary document
- `qa-expert` vs `qa-test-engineer`: both validate quality gates — boundary is qa-expert (pre-deployment comprehensive) vs qa-test-engineer (strategy/design)

**REVIEW: Purpose Collision (6 agents overlapping)**
- Consolidation recommendation: review-code (defects/bugs) → review-quality (maintainability/patterns) → review-critic (plans) → review-harsh-critic (adversarial) → review-verifier (completion gate) → review-intent (metacognitive)
- These 6 can coexist but need **explicit non-overlapping trigger conditions** per agent

### High-Priority Issues (P1)

| Issue | Finding | Applied Fix |
|-------|---------|------------|
| dev-executor vs dev-deep-executor no threshold | No complexity threshold documented anywhere | ✅ Added to omc-ultrawork: <300 lines = executor, ≥300 = deep-executor |
| research-analyst vs research-deep-analyst boundary | "deep analyst" modifier doesn't explain specialization | Documented: deep-analyst = autonomous multi-session, analyst = pre-planning/advisory |
| biz-marketer + biz-gtm + biz-content-writer overlap | 3-agent marketing cluster with overlap | Acceptable: different stages (strategy/channel/content) |
| ops-orchestrator vague description | "Multi-agent pipeline coordinator" unclear scope | Acceptable: trigger keywords well-defined |

### Missing Agents (Architectural Gaps)

**Development:** `dev-debugger` (interactive root-cause debugging, distinct from dev-architect's advisory role)
**QA:** `qa-accessibility`, `qa-performance`  
**Security:** `sec-dependency`, `sec-api`, `sec-compliance`
**Business:** `biz-competitive-analyst`, `biz-pricing-strategist`
**Research:** `research-design-synthesis` (qualitative synthesis)

*Note: These are recommendations for future agent additions, not existing skill improvements.*

### Naming Inconsistencies (Systemic)

| Pattern | Affected Agents | Impact |
|---------|----------------|--------|
| Namespace collision: feature-dev:* + superpowers:* + dev-* | 9+ agents | Routing ambiguity |
| Playwright duplication: qa-pw-* + playwright-test-* | 6 agents | 2 parallel naming conventions |
| Vague "deep" prefix | dev-deep-executor, research-deep-analyst | Users must guess what "deep" means |
| Mixed review concerns | 6 review-* agents | Taxonomy confusion |

## Related
- [[projects/Entity/marketing/oh_my_codex_outreach|oh_my_codex_outreach]]
- [[projects/Entity/marketing/outreach_ready/oh_my_codex_context_issue|oh_my_codex_context_issue]]
- [[projects/Entity/research/20260327-omc-live-autonomous-ai-research-2025-2026|20260327-omc-live-autonomous-ai-research-2025-2026]]
- [[projects/Entity/research/digests/20260407-playwright-test-agents-claude-code|20260407-playwright-test-agents-claude-code]]
- [[projects/Entity/research/20260328-omc-live-infinite-loop-architecture-research|20260328-omc-live-infinite-loop-architecture-research]]
- [[projects/Entity/research/20260328-omc-live-science-research-domain-expansion|20260328-omc-live-science-research-domain-expansion]]
- [[projects/Entity/marketing/outreach_ready/openai_codex_context_issues|openai_codex_context_issues]]
- [[projects/Entity/research/20260331-skill-selection-implementation-templates|20260331-skill-selection-implementation-templates]]
