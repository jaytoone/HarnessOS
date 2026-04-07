# Ready-to-Post: google/adk-python#4178

## Posting Instructions

- **URL**: https://github.com/google/adk-python/issues/4178
- **Action**: Post the comment below as a reply
- **Verify before posting**: Issue is still open and accepting comments
- **Tone**: Technical peer sharing experience, zero self-promotion
- **Word count**: ~130 words

## Comment

```
The state corruption after 429/503 is more dangerous than the rate-limiting itself. What's happening: the agent's execution context (internal state, tool call history, partial results) persists across the failure boundary, so the next query inherits a half-completed workflow state.

This is a state isolation problem, not a retry problem. RetryConfig handles the HTTP layer but doesn't reset the agent's cognitive state after a failed workflow step.

What works: checkpoint-based state management where each agent turn is atomic. Before every LLM call, snapshot the current state. On 429/503, restore to the last clean checkpoint rather than continuing from the corrupted mid-execution state.

For the immediate workaround: the suggestion to use the native Gemini adapter instead of LiteLLM is correct — it handles retry + state reset more cleanly because it doesn't add an extra abstraction layer where state can leak.
```
