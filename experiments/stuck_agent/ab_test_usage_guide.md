# A/B Test Usage Guide: Skill Patch Injection Experiment

## Experiment Goal
Validate: **orchestration prompts that evolve based on experience find better execution strategies**
- Source: arxiv:2604.00901 — Experience as a Compass
- Hypothesis: patched context primer → higher best_score at convergence (effect_size >= 0.05)

## Quick Start

```bash
# Check current condition
python3 scripts/ab_test_skill_patch.py status

# Switch to CONTROL condition (no patches)
python3 scripts/ab_test_skill_patch.py disable-patches
# → Run /live-inf with your goal
# → After convergence, check .omc/live-state.json for best_score

# Record control result
python3 scripts/ab_test_skill_patch.py record \
  --condition control \
  --score <best_score from live-state.json> \
  --iters <evolution_count from live-state.json> \
  --goal "<root_goal>"

# Switch to TREATMENT condition (patches active)
python3 scripts/ab_test_skill_patch.py enable-patches
# → Run /live-inf with SAME goal
# → After convergence, record result

python3 scripts/ab_test_skill_patch.py record \
  --condition treatment \
  --score <best_score> \
  --iters <iters> \
  --goal "<root_goal>"

# Analyze after 5 pairs
python3 scripts/ab_test_skill_patch.py analyze
```

## Design Notes
- **A (control)**: `.omc/skill-patches/` moved to `.omc/skill-patches.disabled/`
- **B (treatment)**: `.omc/skill-patches/` active → live Step 3d injects patch context
- **Paired**: same goal in both conditions to control for goal difficulty
- **5 pairs minimum**: statistical power for Wilcoxon signed-rank test
- **Auto-generate patches** before each treatment run:
  ```bash
  python3 -c "from scripts.skill_patcher import SkillPatcher; p=SkillPatcher.from_episodes('.omc/episodes.jsonl'); patch=p.generate_patch('live'); p.save_patch(patch)"
  ```

## Reading Results

```
Effect size: score improvement: +0.070 → hypothesis SUPPORTED
iter reduction: +1.2 fewer iterations → efficiency gain confirmed
```

- `+0.05` or more: hypothesis supported (practical significance)
- `< 0.05`: hypothesis not supported at this effect size

## Current Data

Existing records: **SIMULATED** (`data_type: "simulated"`)
Real validation requires:
1. Actual /live-inf convergence runs (not simulated)
2. Minimum 5 pairs per condition
3. Record immediately after each convergence

## Files
- `scripts/skill_patcher.py` — generates patches from episode history
- `scripts/ab_test_skill_patch.py` — records trials, analyzes results
- `.omc/skill-patches/` — active patches (treatment condition)
- `.omc/ab_test_results.jsonl` — trial records
