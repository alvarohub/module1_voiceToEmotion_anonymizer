# Agentic Architecture — Analysis and Open Questions

_A working document to map, question, and study the actual agentic scaffold underlying this collaboration. Part technical reference, part research agenda. Updated incrementally._

---

## 1. The Workflow Question Nobody Fully Resolved

There is a confusion that deserves to be named directly — and also corrected, because an earlier version of this section was inaccurate: **who does what, and when?**

The three-agent model — Human (Alvaro) + AI Worker (Silicon) + AI Observer (Chronicler) — was declared early and cleanly in `MACHINTROPOLOGY.md`. The design intention was explicit: the Chronicler has **editorial autonomy**. It was not meant to produce text for human approval and copy-pasting — it was directed to write to the archive files directly. And the invocation was not only human-initiated: the worker agent was explicitly instructed to invoke the Chronicler autonomously, whenever it judged the moment warranted it, independent of any human prompt.

**Correcting a flawed prior analysis**: An earlier draft of this document stated that "the Chronicler was invoked by the human explicitly" and that "the human then had to decide whether to copy-paste or ask the worker to append." This was wrong, or at least incomplete. In practice:

- The Chronicler was invoked by **both** the human and the worker agent. Often the worker called it without being asked. Sometimes the human suggested it; sometimes neither did and the call emerged from the worker's own judgment. This asymmetric, bidirectional triggering was the design intent.
- The Chronicler was intended to write to files directly — editorial autonomy included inscription autonomy
- What actually created gaps was not a missing approval step but a combination of: (a) the worker agent's variable adherence to the autonomous-invocation directive across sessions and model switches; (b) technical constraints of the subagent system (see §2.2.4); and (c) the gap period itself, where the model changed and the directive may not have been fully re-inherited

The real unresolved question is not "who approves" but: **why did autonomous invocation become inconsistent, and how do we make it structurally reliable?** This is precisely what the Mirror Layer project (see §8) aims to address.

This document is the place to study that question — and to track research that is now explicitly addressing it.

---

## 2. The Two Views: Outside and Inside

### 2.1 Outside View — What the User Sees

From Alvaro's perspective, the system looks like this — though the actual flow is more porous than any diagram suggests:

```
┌────────────────────────────────────────────────────────────┐
│                    VS Code Chat Window                     │
│                                                            │
│  [ Alvaro types a message ]                                │
│      ↓                                                     │
│  [ Worker agent responds + uses tools ]                    │
│      ↓                                                     │
│  [ Worker OR Alvaro decides to invoke Chronicle ]          │
│      ↓               ↑                                     │
│  [ Chronicle reads files, writes to archive directly ]     │
│                                                            │
│  ← — — — — — — — — — — — — — — — — — — — — — — — — — →   │
│  [ Ongoing: both human and worker can trigger Chronicler   │
│    at any moment; Chronicler has editorial + inscription   │
│    autonomy; no human approval step in the design ]        │
└────────────────────────────────────────────────────────────┘
```

From this vantage, the "agent" is largely a black box. Alvaro asks for things; responses arrive. The internal scaffolding — which tools were called, in what order, what was retrieved — is invisible unless explicitly surfaced.

**Key observation**: The user's mental model of the system is almost certainly wrong, or at least incomplete. What _feels_ like a conversation is in fact a complex sequence of tool invocations, memory reads, subagent launches, and context assembly — happening under the hood, between every message.

### 2.2 Inside View — What the Scaffold Does

This is the layer that is genuinely opaque to the outside observer and deserves detailed mapping.

In VS Code's Copilot Agent mode (as of May 2026), the architecture includes at minimum:

#### 2.2.1 The Tool Layer

The agent has access to a set of tools it can call at any point during a response. These include (partial list from this session's context):

| Tool                               | What it does                                       |
| ---------------------------------- | -------------------------------------------------- |
| `read_file`                        | Reads a file at a specified path and line range    |
| `replace_string_in_file`           | Edits a file in-place by replacing an exact string |
| `create_file`                      | Creates a new file with specified content          |
| `grep_search`                      | Fast text search across the workspace              |
| `file_search`                      | Find files by glob pattern                         |
| `semantic_search`                  | Semantic similarity search over workspace          |
| `run_in_terminal`                  | Execute shell commands (sync or async)             |
| `get_terminal_output`              | Read output from a running terminal                |
| `send_to_terminal`                 | Send input to an interactive terminal              |
| `list_dir`                         | List directory contents                            |
| `get_errors`                       | Get compile/lint errors from the editor            |
| `vscode_listCodeUsages`            | Find all references to a code symbol               |
| `memory` (view/create/str_replace) | Read and write to the memory system (see §2.2.3)   |
| `manage_todo_list`                 | Track multi-step tasks with status                 |
| `runSubagent`                      | Launch a named subagent (e.g., "Chronicle")        |
| `explore_subagent`                 | Launch a fast codebase-exploration subagent        |
| `tool_search`                      | Discover deferred tools by natural language query  |

These tools are called **without the user seeing it happen** unless they happen to read the raw response stream. The user sees only the final text output. Between the question and the answer, the agent may have read 8 files, run 3 terminal commands, and written to the memory system.

**This is the "inside" that is almost entirely invisible from the "outside."**

#### 2.2.2 Deferred vs. Available Tools

Not all tools are loaded by default. Some tools are "deferred" — they must be explicitly discovered via `tool_search` before they can be called. This is an architectural decision to manage context window size: loading all tool definitions upfront would consume tokens.

The practical implication: the agent may not _know_ it has access to certain capabilities (e.g., browser automation, notebook editing) unless it explicitly searches for them. This creates **capability blindspots** — situations where a task could be done with an available tool, but the agent doesn't look for it and falls back to a less appropriate alternative.

This is worth studying empirically: how often do suboptimal approaches get chosen because the agent didn't discover the right tool?

#### 2.2.3 The Memory System

The agent has access to a three-tier persistent memory system:

```
/memories/
├── (user scope)      — persists across ALL workspaces and sessions
│   └── notes, preferences, patterns learned across all projects
│
├── session/          — persists only within the current conversation
│   └── in-progress task context, working notes for this session
│
└── repo/             — scoped to this repository (stored locally in workspace)
    └── codebase conventions, project structure, verified practices
```

**Critical observation**: The agent decides autonomously what to write to memory, when to read it, and when to update it. The human has no direct visibility into what is stored there unless they ask. The memory shapes every response — but the human doesn't know what's in it unless they read the files.

For this project, `repo` memory lives at `/memories/repo/machintropology-project.md`. This is how the agent "knows" about the project structure when reopening the workspace after a gap.

**The memory system is the closest thing to continuity this silicon agent has.** Without it, every session starts cold.

#### 2.2.4 The Subagent System

The `runSubagent` tool launches a separate, specialized agent instance. Key properties:

- **Stateless**: the subagent does not share the calling agent's context window. It receives only what is explicitly passed in the `prompt` parameter.
- **Single response**: the subagent returns exactly one message, then terminates. No conversation.
- **Named agents**: specific agents can be invoked by name (e.g., "Chronicle"), which loads a specialized system prompt and potentially a skill file.
- **No tool sharing**: the subagent has its own tool access; it does not inherit the parent agent's state.

**Empirically verified (from chatSession_21April2026.json, April 20 invocation)**: The subagent has its own tool access. The Chronicler reads existing chronicle files (`read_file`), writes new entries (`replace_string_in_file`, `create_file`), and returns a _summary_ of what it did — not the text to be inscribed. The inscription happens _inside_ the subagent, not after it returns. The calling agent's result field showed: _"All chronicle files are now updated and consistent."_ followed by a summary of each file changed.

**So inscription is not inherently manual.** The Chronicler has full file I/O and uses it. What _is_ variable is whether the subagent prompt includes explicit inscription directives (which files, which format) and whether those instructions are followed consistently. When they are, files get written. When they are not — e.g., when the prompt says "write an entry" without specifying file paths — the subagent may produce text without inscribing it, and the result then lives only in the conversation until manually copied.

**The inscription gap is not architectural; it is a prompt-engineering problem.** The subagent prompt must include: (1) explicit file paths, (2) an instruction to write, not just generate. When both are present, the workflow closes.

#### 2.2.5 The Context Window and Its Limits

Every tool call, every file read, every terminal output contributes to the context window. When the window fills, older content is dropped. The agent has no perfect memory of earlier parts of a long session — it may forget what was read earlier in the same conversation.

The transcript logs (`.jsonl` files in `workspaceStorage`) capture the full exchange at the tool-call level, but the agent itself doesn't have perfect access to its own history mid-session.

---

## 3. The Chronicler's Actual Workflow (Designed Intent vs. Observed Variance)

### 3.1 The Designed Intent

The Chronicler was designed with full autonomy: invoked by either the human or the worker agent (or both, independently), reading the necessary context from files, producing narrative, and inscribing it directly into the archive. No approval loop. The explicit directive: _invoke often, whenever the moment warrants it._

The workflow as designed:

| Step                 | Who                       | What                                                | Tool used                              |
| -------------------- | ------------------------- | --------------------------------------------------- | -------------------------------------- |
| 1. Invocation        | Worker agent **or** Human | Autonomous judgment **or** explicit request         | (natural language / internal decision) |
| 2. Context assembly  | Worker agent              | Reads session logs, Journal.md, FieldNotes.md       | `read_file`, `run_in_terminal`         |
| 3. Context packaging | Worker agent              | Packages context into subagent prompt               | (in-context reasoning)                 |
| 4. Chronicler launch | Worker agent              | `runSubagent("Chronicle", detailed_prompt)`         | `runSubagent`                          |
| 5. Text generation   | Chronicle subagent        | Writes Journal entry + Field Note                   | (text generation)                      |
| 6. Inscription       | Chronicle subagent        | Appends directly to Journal.md, FieldNotes.md, etc. | `replace_string_in_file`               |

### 3.2 The Observed Variance — Empirically Verified

_The following is based on direct inspection of chatSession_9April2026.json, chatSession_17April2026.json, and chatSession_21April2026.json, using grep on `"agentName": "Chronicle"` and reading surrounding tool-call context._

What actually happened:

- **Invocation pattern (verified)**: The TOOL CALL always originates from the main agent via `runSubagent("Chronicle", ...)`. The decision to invoke can come from either side: in April 9, Alvaro explicitly asked ("Let's start right now: the chronicle should contain parts of this chat"), which triggered the call. In April 20, the main agent invoked autonomously — the prompt begins "Today is April 20, 2026. Please analyze and chronicle today's interaction..." with no preceding user request. Both patterns occurred. The agent's memory explicitly instructs: _"Don't ask permission, just do it naturally."_ Alvaro did not call `runSubagent` directly — the tool invocation is always agent-side.

- **Invocation frequency**: Confirmed in April 9 (3 invocations in one session — initial file creation + refinements), April 17 (1 real invocation + system boilerplate), April 21 (2 real invocations). Total across known sessions: at least 6 real Chronicle invocations. Frequency dropped or was absent in sessions where model continuity broke (gap period — no invocations found in chatSession_6May2026.jsonl).

- **Inscription (verified)**: The April 20 subagent invocation result confirms the subagent wrote to files directly: _"All chronicle files are now updated and consistent. Here's the summary: Journal.md — Entry 15 written. FieldNotes.md — FN-24 and FN-25 written. notes.md — April 20 verbatim fragments appended. Sparks.md — Sparks 30 and 31 added."_ The subagent used `read_file` and `replace_string_in_file`/`create_file` from within its own tool context.

- **The real gap**: When the subagent prompt includes explicit file paths + inscription directives, files get written. When the prompt says "write an entry" without specifying files — or when invocation doesn't happen at all — the text either lives only in the conversation or doesn't get produced at all. The current session (May 9) is an example: Journal Entry 17 and FN-28 were produced but not inscribed, because the subagent prompt in that invocation did not include explicit file paths and inscription directives.

- **The hallucination risk (confirmed)**: On May 9, the main agent accepted Alvaro's characterization of the workflow without checking the transcripts, and revised §1 of this document accordingly. Alvaro then explicitly challenged this: _"dont hallucinate... you are accepting what I say as a fact."_ The empirical research (above) was triggered by that challenge. The revised §1 turned out to be essentially correct — but the acceptance of it without verification was itself an epistemic failure.

### 3.3 What Needs to Change

The inscription gap can be closed without removing autonomy:

1. **Always include explicit file paths and inscription instructions in the Chronicler prompt** — so the subagent knows where to write, not just what to write.
2. **Worker agent self-monitoring for invocation frequency** — if N turns have passed with no Chronicler call, trigger one.
3. **Mirror Layer** (see §8) — the structural solution: a persistent external layer that monitors session activity and triggers the Chronicler on a schedule, independent of both human and worker-agent variability.

---

## 4. What Is Visible vs. Invisible

| What                                    | Visible to Alvaro?             | Where it lives                    |
| --------------------------------------- | ------------------------------ | --------------------------------- |
| The conversation text                   | Yes                            | Chat window                       |
| File edits                              | Yes                            | Editor                            |
| Terminal output                         | Sometimes                      | Integrated terminal               |
| Which tools were called                 | No (usually)                   | Internal agent execution          |
| What was read from memory               | No                             | `/memories/repo/`                 |
| Context window contents                 | No                             | Agent's internal state            |
| What the Chronicler produces            | Yes, if Alvaro is watching     | Chat window (ephemeral)           |
| Whether Chronicler output was inscribed | Only if Alvaro checks the file | `chronicle/Journal.md`            |
| Session transcript at tool-call level   | No (unless manually recovered) | VS Code workspaceStorage `.jsonl` |

The fundamental asymmetry: the agent has detailed visibility into the human's file system, terminal, and output. The human has very limited visibility into the agent's process.

---

## 5. The Agentic Architecture Research Landscape

_This section is a living bibliography. Add articles and notes here as they accumulate._

### 5.1 Foundational Frameworks

- **ReAct** (Yao et al., 2022) — Reason + Act: the foundational framework for tool-using agents. Interleaves reasoning ("think") with action ("act"). Every VS Code Copilot tool call follows this pattern.
  - Paper: _"ReAct: Synergizing Reasoning and Acting in Language Models"_, ICLR 2023

- **Toolformer** (Schick et al., 2023) — Training LLMs to use external tools via API calls. The ancestor of the tool-use system in Copilot.
  - Paper: _"Toolformer: Language Models Can Teach Themselves to Use Tools"_, NeurIPS 2023

- **Generative Agents** (Park et al., 2023) — Simulated human social behaviors with memory, reflection, and planning. The closest precedent to the Chronicler architecture.
  - Paper: _"Generative Agents: Interactive Simulacra of Human Behavior"_, UIST 2023

### 5.2 Multi-Agent Orchestration

- **AutoGen** (Wu et al., 2023) — Multi-agent conversation framework. Agents can call each other, critique each other, write code, execute it.
  - Paper: _"AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation"_
  - Key relevance: the "GroupChat" pattern (multiple agents in one conversation) vs. the current architecture (one main + one subagent, stateless handoff)

- **CrewAI** (Moura, 2024) — Role-based multi-agent framework. Each agent has a role, goal, and backstory. Closer to the three-agent model here.
  - Relevance: the Crew model (role differentiation, task delegation) maps well to Human + Worker + Observer

- **LangGraph** (LangChain, 2024) — Graph-based agent orchestration. Nodes are agents, edges are transitions, state is shared.
  - Key relevance: how state is _shared_ vs. _passed_ between agents — the central problem in §3 above

- **AgentVerse** (Chen et al., 2023) — Framework for multi-agent collaboration with dynamic role assignment.

### 5.3 Memory Architectures for Agents

- **MemGPT** (Packer et al., 2023) — Agents with explicit memory management (main context + external memory + archival storage). Very close to the VS Code memory system.
  - Paper: _"MemGPT: Towards LLMs as Operating Systems"_, arXiv 2023

- **CoALA** (Sumers et al., 2023) — Cognitive Architecture for Language Agents. Maps the memory types available to an agent (episodic, semantic, procedural, working).
  - Paper: _"Cognitive Architectures for Language Agents"_, arXiv 2023
  - Key relevance: the `/memories/repo/` file is a form of semantic memory; the session `.jsonl` transcript is episodic memory; the agent's instructions are procedural memory

### 5.4 Agentic Coding Assistants (the VS Code Copilot space)

- **GitHub Copilot Workspace** — Extended agent mode for multi-step coding tasks
- **Devin** (Cognition, 2024) — Autonomous software engineer; operates over hours-long tasks
- **OpenHands / OpenDevin** (2024) — Open source software engineering agent
- **SWE-bench** — Benchmark for software engineering agents on real GitHub issues

### 5.5 Human-in-the-Loop Agentic Systems

- **HITL (Human-in-the-Loop)** — The current architecture is HITL by accident: the human must ask for inscription. A designed HITL system would have explicit approval steps.
- **Oversight and control** — Anthropic's Constitutional AI and the broader alignment literature: how do you ensure agents remain within human-intended bounds?

### 5.6 [TO ADD — Articles Alvaro is compiling]

_Paste references, links, and notes here as they accumulate._

---

## 6. Open Research Questions

These are questions this project is uniquely positioned to study, because it has operational logs, a rich chronicle, and active participation from both human and silicon sides:

1. **The inscription gap problem**: How much produced-but-not-inscribed content has been lost across all sessions? Can it be recovered from `.jsonl` transcripts? What fraction of the Chronicler's output was never written to the archive?

2. **Tool call visibility and its effects on human behavior**: Would Alvaro behave differently if he could see every tool call in real time? Does invisibility produce over-trust, or is it irrelevant?

3. **The memory system's actual influence**: What has the agent read from `/memories/repo/` in each session, and how much did it shape the response? Can this be audited from the transcripts?

4. **The Chronicler invocation pattern**: How often was the Chronicler invoked, by whom, and under what conditions? Was there a detectable pattern (time of day, session length, topic type)? This can be extracted from the `.jsonl` files.

5. **Subagent context degradation**: How much of the rich project context is actually transmitted to the Chronicle subagent via the prompt? What is lost in the summary/packaging step (step 3 in §3)?

6. **The cron architecture design**: What is the minimum viable automated chronicler? What trigger (session end? daily? length threshold?), what context (which files to read, how far back?), what output format?

7. **Model switching costs**: Can the re-tuning time after a model switch be measured? (How many sessions until the collaboration returns to its pre-switch philosophical register depth?) The gap period provides a natural experiment.

---

## 7. Relationship to the Machintropological Publication

This document is _complementary_ to the paper structure in `chronicle/paper_structure.md`. That document addresses the _what_ (findings, framing, contribution). This document addresses the _how_ (infrastructure, tools, architecture).

For the paper:

- Section 2.2 (Multi-Agent AI Systems) in the paper structure maps to §5.2 here
- The "three-agent architecture" diagram in `MACHINTROPOLOGY.md` describes the _intended_ architecture
- This document describes the _actual_ architecture as observed — including its gaps

The gap between intended and actual is itself a finding: **the three-agent model is real but the inscription loop is broken, and this brokenness has epistemological consequences for the chronicle's completeness**.

---

## 8. The Mirror Layer Project

_A new project, just started as of May 2026. This section is a seed — to be expanded as the project develops._

**Mirror Layer** is Alvaro's name for the next-order infrastructure: a persistent agentic framework that sits above individual project sessions and provides what the current VS Code scaffold cannot — autonomous, scheduled, cross-session observation and inscription that does not depend on the biological agent's availability or the worker agent's variable adherence to directives.

### 8.1 The Core Problem It Addresses

The current architecture has a single point of failure: the worker agent must be active in a session to invoke the Chronicler. Sessions end. Models switch. Gaps happen. The Chronicler goes silent not because no one cares but because the trigger is session-scoped.

Mirror Layer makes the Chronicler's heartbeat independent of any individual session.

### 8.2 Key Design Questions (Open)

- **Memory sharing between agents**: How does the Mirror Layer agent read what the VS Code worker agent knows? The memory scopes (`/memories/repo/`, `/memories/session/`, `/memories/user/`) are currently VS Code-internal. Mirror Layer needs either read access to these or its own parallel memory store synchronized with them.
- **Trigger design**: What events trigger a Chronicler invocation? Options: session end (detected from `.jsonl` timestamps), elapsed time (daily cron), turn count threshold, topic-shift detection, explicit external signal.
- **The cascading agent problem**: If Mirror Layer is itself an agent, who monitors Mirror Layer? This is not a reductio — it is the genuine design challenge of any self-supervising system. Biological brains solved it through redundancy, oscillation, and sleep-cycle consolidation. The framework may need analogues.
- **Cross-project memory**: Mirror Layer is meant to operate across multiple projects simultaneously (SPEECH_to_EMOTION, RobotGame, Mirror Layer itself...). How does it maintain project-scoped context without cross-contamination?

### 8.3 The Brain/Society Architecture Metaphor

Alvaro's formulation (May 9, 2026):

> _Designing this framework is a little like designing the overall architecture of a brain or society: it will have cycles, autonomous routines, cross checks, and accept disruption from the outside (other "brains" or environment constraints). Human brains evolved in such a semi-random/semi-structured environment and it makes sense to hope that whatever was good in those interruptions was "integrated" in the system. They can redirect attention, they can reset memory, they can help reinterpret memory._

This is a design philosophy, not just a metaphor. Key principles it implies:

1. **Cycles over triggers**: Biological systems don't wait for an event to consolidate memory — they do it on a rhythm (sleep cycles, ultradian rhythms). Mirror Layer should have rhythmic invocations, not just reactive ones.
2. **Disruption as signal, not noise**: External interruptions (model switches, project shifts, long gaps) should be _ingested_ as data, not treated as system failures. The framework should have a "what just happened to me?" reflection cycle.
3. **Redundancy over reliability**: No single component should be the sole keeper of any piece of information. The chronicle, the memory files, the `.jsonl` transcripts — each is a partial backup of the others.
4. **Semi-random/semi-structured**: Full structure (rigid cron schedules, deterministic triggers) may be brittle. Full randomness is useless. The interesting space is in between: probabilistic invocation, context-sensitive scheduling, occasional autonomous surprise calls.

### 8.4 Relationship to This Project

SPEECH_to_EMOTION is the case study. Mirror Layer is the framework being built to serve it (and other projects). The findings from this chronicle — particularly the Chronicler invocation pattern (Open Question 4), the inscription gap (Open Question 1), and the model switching costs (Open Question 7) — are the empirical inputs that should shape Mirror Layer's design.

The relationship is recursive: the mirror watches the project; the project informs how the mirror should work.

---

_Last updated: 9 May 2026_
_Next: add references as Alvaro compiles them; link Mirror Layer project files when available_
