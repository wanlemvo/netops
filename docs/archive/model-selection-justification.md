# Model Selection Justification

## Context

This project used a spec-driven agentic workflow to plan and implement a local-first NetOps CLI/TUI feature set. The work required requirements interpretation, task decomposition, code implementation, debugging, and validation through tests.

## GPT/Codex

**Strengths**
- Strong fit for repository-aware implementation, debugging, and iterative test repair.
- Effective at following existing project structure and making scoped code changes across Python modules, tests, and SpecKit artifacts.
- Good at maintaining traceability between `spec.md`, `plan.md`, `tasks.md`, implementation files, and test coverage.

**Weaknesses**
- Can over-implement if task scope is not constrained.
- Requires validation through tests because plausible code can still miss edge cases or local conventions.

**Reasoning, Coding, and Research Fit**
- Best fit for coding and debugging inside an existing codebase.
- Good fit for structured reasoning when supported by project artifacts.
- Research use should be paired with official documentation or explicit source checks.

**Latency/Cost Tradeoffs**
- Higher-capability coding models can be more expensive than lightweight models, but reduce rework when changes span architecture, tests, and implementation.
- Latency is acceptable for implementation because tool use and test execution dominate the workflow.

**Safety Behavior Observations**
- Strong at preserving user changes when instructed and avoiding destructive Git operations.
- Still requires human review for privacy-sensitive logs, generated documentation, and source claims.

**Benchmark/Tradeoff Discussion**
- Public coding and reasoning benchmarks generally show frontier GPT/Codex-class models as strong choices for code generation, debugging, and tool-using workflows. The practical tradeoff is cost versus fewer failed implementation loops.

## Claude Sonnet

**Strengths**
- Strong reasoning, planning, and long-context synthesis.
- Useful for evaluating requirements, identifying ambiguity, and producing readable design documents.
- Often good at explaining tradeoffs in a balanced way.

**Weaknesses**
- May be less directly integrated with local coding tools depending on environment.
- Can produce polished plans that still need verification against the actual repository.

**Reasoning, Coding, and Research Fit**
- Best fit for planning, architecture review, requirements analysis, and reasoning-heavy decomposition.
- Good coding support, especially for design-sensitive refactors, but still needs test-backed validation.

**Latency/Cost Tradeoffs**
- Usually a good middle ground for planning quality versus cost.
- May be less efficient than a coding-specialized agent when many file edits and test iterations are required.

**Safety Behavior Observations**
- Generally cautious and good at surfacing uncertainty.
- Summaries can still omit operational details, so important claims should be checked against source artifacts.

**Benchmark/Tradeoff Discussion**
- Claude Sonnet-class models are commonly competitive on reasoning, writing, and code understanding benchmarks. The practical advantage is thoughtful planning; the tradeoff is that execution still benefits from a tool-integrated coding agent.

## Gemini

**Strengths**
- Strong research and broad information synthesis capabilities.
- Useful for comparing documentation, generating alternative approaches, and quickly exploring unfamiliar topics.
- Can be helpful when the task requires current ecosystem context.

**Weaknesses**
- Research summaries can hide source quality differences.
- Implementation output may need more adaptation to local project conventions.

**Reasoning, Coding, and Research Fit**
- Best fit for research, source comparison, and broad technical option discovery.
- Useful as an input to planning, but not the final authority for implementation decisions.

**Latency/Cost Tradeoffs**
- Can be efficient for broad research passes.
- Additional verification time is needed when outputs depend on source quality or current facts.

**Safety Behavior Observations**
- Helpful for summarization, but summarized claims should be traced back to sources.
- Risk of over-compressing uncertainty if prompts ask for short answers.

**Benchmark/Tradeoff Discussion**
- Gemini-class models are strong in multimodal and research-oriented tasks. The tradeoff is that research breadth does not replace repository-specific implementation validation.

## Recommended Hybrid Workflow

Use a hybrid workflow rather than relying on a single model for the full assessment:

- **Gemini for research**: gather current ecosystem context, compare official documentation, and identify options.
- **Claude Sonnet for planning/reasoning**: refine requirements, challenge assumptions, and structure the implementation plan.
- **GPT/Codex for implementation/debugging**: edit the repository, run tests, fix failures, and keep tasks synchronized with code.

This balances breadth, reasoning quality, and practical implementation capability while reducing the risk of overreliance on one model’s blind spots.
