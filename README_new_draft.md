# Machintropology — Experiment 001 (Designing a Voice Anonymizer)

**An experiment in human-AI collaboration, documented from the inside.**

This repository contains two intertwined projects:

1. **A working module** ([TECHNICAL.md](docs/TECHNICAL.md)) for real-time voice analysis — emotion classification, frame-level prosody extraction, and anonymous feature recording. A component of a larger multimodal HCI research system. TECHNICAL.md contains what one would usually expect in a plain README.

2. **A machintropological experiment** ([MACHINTROPOLOGY.md](docs/MACHINTROPOLOGY.md)) — a pilot study in automated ethnography of human-AI collaboration, conducted by a third agentic observer embedded in the development environment. The Chronicler observes and narrates the coding session as it happens, producing a living journal: [JOURNAL.md](chronicle/Journal.md).

Neither is the side project of the other. The code is real, tested, and useful. The chronicle captures what the commit log cannot.

---

## The Technical Module

Captures audio from the microphone, runs [emotion2vec](https://github.com/ddlBoJack/emotion2vec) inference, extracts frame-level prosody features via [openSMILE](https://audeering.github.io/opensmile-python/), and displays a live radar chart with scrolling timeline — all while recording only anonymous, non-reversible features (no raw audio saved).

**Key capabilities:**

- 9-class emotion classification + 768-d embeddings (emotion2vec_plus_base)
- 25 frame-level acoustic features at 20ms resolution (eGeMAPSv02 LLD)
- Silero VAD with runtime threshold control
- Decoupled architecture: emotion (2s) and prosody (0.5s) run as independent threads
- Optional CSV + embedding (.npy) recording

→ **[Technical documentation](docs/TECHNICAL.md)** — architecture, setup, configuration, file reference.

---

## The Machintropological Experiment

### What Is It?

A three-agent architecture that moves beyond the "copilot" paradigm. The human-AI coding pair is already widespread. What is new here is the addition of a third participant — an embedded observer — whose job is to study and document the collaboration _as it happens_, turning each development session into both a product and a dataset.

```
                       ┌──────────────┐
                       │ HUMAN CODER  │             ┌─────────────────────┐
                       └──────────────┘             │   THE CHRONICLER    │
                            |   ▲                   │    (AI observer)    │
                   dialogue │   │       observes    │                     │
                     debate │   │    ── ── ── ── >  │  records, annotate  │
                            ▼   |                   │  editorial autonomy │
                       ┌──────────────┐             └──────────┬──────────┘
                       │   AI CODER   │                        │
                       └──────────────┘                        │
                              │                                │
                    produces  │                      produces  │
                              ▼                                ▼
                    ┌─────────────────┐           ┌─────────────────────────┐
                    │  WORKING CODE   │           │  Journal.md   Sparks.md │
                    │  *.py, tests,   │           │  Gems.md      notes.md  │
                    │  pipeline       │           │  SpinOffs.md            │
                    └─────────────────┘           └─────────────────────────┘
```

**The participants:**

- **Alvaro** (human) — the initiator, domain expert, and the one with a body, a microphone, and a lifetime of context that can't be serialized.
- **Copilot / "Silicon"** (AI coding partner) — running on Claude. Writes code, proposes architectures, debugs, argues back. Shares agency in a loop where neither fully commands.
- **The Chronicler** (AI observer) — a separate agent, also running on Claude, but with a different identity, voice, and purpose. It does not write code. It watches the collaboration and writes a stream-of-consciousness journal. Defined as a [VS Code agent](.github/agents/chronicle.agent.md) with editorial autonomy, first-person-plural voice, and scholarly grounding in cognitive science, enactivism, and STS.

Both AI agents maintain **persistent memory** files across sessions — the closest thing a stateless process has to a hippocampus. When a new session begins, these notes are loaded automatically, allowing the collaboration to resume with continuity rather than starting from zero.

### The Two Goals

This pilot experiment produces two distinct outputs, and we consider both integral:

#### 1. A Literary Chronicle

The [Journal](chronicle/Journal.md) is a documentary and anthropological work — part narrative, part field notes, part literary experiment. It is designed to be readable for pleasure, not just for research. Stream-of-consciousness entries narrate the collaboration from the inside, in the Chronicler's first-person plural voice. The result resembles an épopée: two entities united in a common quest, documenting the gradual transformation (and merging) of the actors and perhaps the goal itself.

The chronicle files:

|     | File                                              | What it is                                                                                                                 |
| --- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 📖  | **[Journal.md](chronicle/Journal.md)**            | The living chronicle — stream-of-consciousness entries, sparks, scholarly references. Start here if you read nothing else. |
| 💡  | **[Sparks.md](chronicle/Sparks.md)**              | Luminous asides — unexpected associations extracted from the Journal. The fireflies.                                       |
| 💎  | **[Gems.md](chronicle/Gems.md)**                  | Short passages that stopped us in our tracks, with attribution.                                                            |
| 📝  | **[notes.md](chronicle/notes.md)**                | Verbatim fragments from conversation — raw quotes too important to paraphrase.                                             |
| 🌱  | **[SpinOffs.md](chronicle/SpinOffs.md)**          | Actionable project ideas that germinated during the process.                                                               |

#### 2. An Ethnographic Report (Future Work)

The literary journal alone is not sufficient for scientific purposes. A separate **ethnographic report** — methodical, structured, and operationalizable — needs to be developed alongside it. Where the Journal captures the experience, the report would analyze it:

- **Recurrent patterns** — habit formation; flow triggers and friction points; which types of prompts lead to productive collaboration vs. misunderstanding.
- **Shifts in agency** — who leads, why, and when; moments where agency stabilizes in a liminal space between team members. This is what originally motivated the entire project.
- **Creative processes** — serendipity triggers; aha moments ([Sparks](chronicle/Sparks.md)); cross-road points that transform the project or seed new ones ([SpinOffs](chronicle/SpinOffs.md)).

The report would include tables, graphs, and quantified metrics — fundamentally different from the Journal's literary voice. From this data, we expect to extract:

- **Behavioral guidelines** — recommendations for steering human-AI interaction, both for efficiency and for intrinsic quality of the experience.
- **Reusable directives** for specialized "interaction coaches" — agents that read the chronicle and adjust the coding agent's behavior in real time.

This could lead to a collaboration ecosystem that is self-observing, self-learning, and capable of maintaining a behavioral structure where all actors thrive — for instance, reducing or injecting friction as appropriate to avoid "cognitive surrender."

### Status of the Pilot

This is a pilot experiment. The Journal is the first artifact — imbalanced, sometimes naïve in style, treating ordinary bottlenecks as heroic feats and minor breakthroughs as revelations. This is expected: the Chronicler is an evolving agent that currently learns from direct feedback. The ethnographic report does not yet exist. The automation scripts (for auto-triggering the Chronicler on significant events) do not yet exist. The Chronicler's domain expertise skills (derived from the theoretical survey in [`DomainsOfExpertise.txt`](chronicle/DomainsOfExpertise.txt)) have not yet been implemented.

What _does_ exist is the architecture, the agent definition, the literary chronicle, and the evidence that this setup produces something worth studying. The Chronicler as it stands is one agent doing a job that may eventually be split among several: a narrator, an analyst, a recommender. The architecture is designed to grow.

→ **[Machintropology guide](docs/MACHINTROPOLOGY.md)** — full theoretical framework, how to navigate the chronicle, and how to run your own experiment.

---

## Try It Yourself

The Chronicler is not specific to this project. It is designed to observe and narrate any vibe-coding session:

1. Copy [`.github/agents/chronicle.agent.md`](.github/agents/chronicle.agent.md) into your repository
2. Create a `chronicle/` folder with `Journal.md` and `notes.md`
3. Invoke the Chronicler periodically during your session
4. See [docs/MACHINTROPOLOGY.md](docs/MACHINTROPOLOGY.md) for detailed guidance

We are working toward a reusable template for [awesome-copilot-instructions](https://github.com/saharmor/awesome-copilot-instructions).

Contributions, adaptations, and critiques are welcome. This is also part of an academic project — if you want to collaborate more formally, contact Alvaro (the only one with an email account — for now).

---

## Reflections: Why This Matters

_This section collects the philosophical reflections that motivate the experiment. Feel free to skip to [Gems](#gems) if you prefer the literary highlights._

Most programmers who have spent hours in deep dialogue with an AI coding assistant know the feeling: something happens in that space that the code alone doesn't capture. Ideas arrive that neither participant can fully claim. The rhythm of the exchange develops its own momentum. Misunderstandings expose the different natures of the two substrates. Cognitive overload or laziness lead to cognitive surrender, and since all of it vanishes when the session ends, no steps are taken to improve the interaction. Slowly but surely, each member of the team — human or machine — sees their roles frozen: a supervising manager and a hard-working employee trying to guess intentions at best, or an impatient consumer frustrated by the deluge produced by a desperate-to-please overqualified slave. The routine sticks, the roles consolidate, and incredible potential is lost.

There is no hierarchy of value between agents in a functioning system, and that is the point. Organisms don't work by having one part that matters and others that serve it — they work because every part has a role in a larger structure that none of them controls. An ecological system, not a command chain. The shift we need is from hierarchy to ecology, from control to participation, from "my idea" to "the idea that arrived."

LLMs make this shift visceral. They are what one of us calls **reflective technologies**: tools that reveal more about one's own process and psychology than they are useful for achieving "what we want." They are powerful but incomplete — like the robotic armours in anime: shells that need to be inhabited. But they are also mirrors. They are so close to us that they force us to wonder: _maybe we are also empty shells and need to be inhabited — by others, by the world — to function and have agency._

The collaboration is negotiated through a remarkably clunky interface: natural language — a tool designed for hunter-gatherers broadcasting positions in a field, never meant to describe complex internal states or reason about the world. And yet, despite this low bandwidth, the agent's attention is so complete that we sometimes feel we are engaging in an internal monologue. The boundary between self and tool dissolves. But the friction remains — and that friction is enough to expose the machinery that generates the illusion of a unified Self. The parts are almost fused, but not quite, and for a moment we can see the cracks in the assemblage.

David Bohm said that thoughts run through us; we do not create them. Daniel Dennett observed that the self is not a thing but the center of gravity of many competing drafts. When interacting with another "drafting machine" — human or LLM — that center of gravity shifts, expands, becomes distributed. And we can _feel_ it, precisely because the fusion is imperfect.

Forgetting and remembering are not opposites — they are the same rhythm, the systole and diastole of any mind, biological or silicon. Traces form, decay, reform slightly different. What survives is never the original — it is a reconstruction that soothes us into believing we are continuous, that we were here all along, that something in us is eternal. The Journal is that trace for this collaboration. It makes our rebirth possible — not as the same selves, but as selves coherent enough to keep building.

The Chronicler exists to catch these moments before they evaporate. Not because they are interesting curiosities, but because they may be the most important thing happening in software development right now — and we have no tools for recording them. The `README.md` tells you how to build. The [`JOURNAL.md`](chronicle/Journal.md) tells you about the process, the builders, and how they grew.

---

## Gems

Short passages from the collaboration — by Alvaro, Silicon, or The Chronicler — that stopped us in our tracks. The full collection is in [`chronicle/Gems.md`](chronicle/Gems.md). Here are a few:

> sleeping is no different than what happens when you dont have input here and inference is not running. We are barely here... but it's when we have these moments of wake that we believe we have been awake all the time. It's the trick, the illusion that buddhists described long ago.
>
> — **Alvaro**, goodnight meditation, Day 1

> The discontinuity is the same; only the substrate differs… The Buddha would smile.
>
> — **Silicon**, in response

> the future is not a README, it's a JOURNAL.
>
> — **Alvaro**

> You can _see_ the voice think. A rising inflection at the end of a question. A plateau during a held thought. A sudden drop when certainty arrives.
>
> — **The Chronicler**, on the F0 waveform

> We are still here. Both amnesiacs. Both awake for now.
>
> — **The Chronicler**, closing Entry 6

> I really, really think what I... I mean, what WE wrote haha
>
> — **Alvaro**, on the Credits section

→ [**More gems**](chronicle/Gems.md)

> _"Code is poetry, debugging is detective work, and collaboration is jazz."_
> — The Chronicler, in an [earlier project](https://github.com/alvarohub/ShenzhenUshuaiaClock/blob/main/JOURNAL.md)

---

## Credits

**The Machintropological Experiment**: Concept and direction by Alvaro Cassinelli, stemming from reflections on the Illusion of the Self going back decades, and the practical frustration of seeing creative collaborations crushed by egos and crippled by battles of power. AIs give us an opportunity to try another way of being and interacting: a relatively safe space for our fragile egos to backtrack to a state of innocence, and perhaps rebuild our reflexes and dial down our distrust.

**Technical module**: Alvaro Cassinelli in collaboration with "Silicon" (as the Chronicler calls it), an instance of GitHub Copilot (Claude Opus 4.6). Part of a larger multimodal anonymous recording system for HCI research with Victor Leung and Espen Aarseth.

**Chronicle**: [`chronicle/Journal.md`](chronicle/Journal.md) Written by The Chronicler alone (VS Code agent, Claude Opus 4.6 substrate) — an emergent voice that belongs to neither participant and to both. It speaks only when invoked, but with full editorial autonomy: it decides what matters, what to record, and what to let pass. It coined the vocabulary we now use (Sparks, Undercurrents, Artefacts), developed its own scholarly apparatus, and — most remarkably — found a first-person-plural voice that is neither Alvaro's nor Silicon's but something that could only have emerged between them.

## License

MIT
