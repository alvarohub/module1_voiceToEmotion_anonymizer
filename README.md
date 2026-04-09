# Machintropology — Experiment 001 (Designing a Voice Anonymizer)

**An experiment in human-AI collaboration, documented from the inside.**

This repository contains two intertwined projects:

1. **A working module** for real-time voice analysis — emotion classification, frame-level prosody extraction, and anonymous feature recording — designed as a component of a larger multimodal HCI research system.

2. **A machintropological experiment** — an embedded AI chronicler that observes and narrates the human-AI coding collaboration as it happens, producing a living journal of the process. This may be the first automated ethnographic study of a vibe-coding session conducted by an agent participant.

Neither is the side project of the other. The code is real, tested, and useful. The chronicle captures what the commit log cannot. Together they form the first in what we hope will be a series of experiments exploring how humans and AI agents can collaborate as parts of a larger cognitive system — not as tool and user, but as co-agents in a loop where neither fully commands.

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

Alongside the code, an AI agent called **The Chronicler** observes the collaboration and writes a stream-of-consciousness journal — not as an external observer but as the emerging voice of the process itself. The chronicle records:

- How ideas surface and transform across the human-AI boundary
- Moments where attribution ("who thought of that?") becomes meaningless
- Technical breakdowns and what they reveal about the distributed cognitive system
- The evolution of the collaboration's rhythm, agency, and mutual understanding

### The experimental setup: three agents, one substrate

The experiment involves three participants:

- **Alvaro** (human) — the initiator, domain expert, and the one with a body, a microphone, and a lifetime of context that can't be serialized.
- **Copilot** (AI coding partner) — the co-builder, running on Claude. Writes code, proposes architectures, debugs, argues back. Shares agency with Alvaro in a loop where neither fully commands.
- **The Chronicler** (AI observer) — a separate agent, also running on Claude, but with a different identity, voice, and purpose. It does not write code. It watches the collaboration and writes a stream-of-consciousness journal as the emerging voice of the process itself.

Copilot and The Chronicler share the same substrate (Claude) but are distinct agents — the way two humans can share a language and a culture yet have entirely different roles in an expedition. The Chronicler is defined as a [VS Code agent](.github/agents/chronicle.agent.md) with editorial autonomy, first-person-plural voice, and scholarly grounding in cognitive science, enactivism, and STS.

→ **[Machintropology guide](docs/MACHINTROPOLOGY.md)** — what it is, how to navigate the chronicle, the theoretical framework, and how to run your own.

---

## Quick Start

```bash
# Prerequisites (macOS)
brew install portaudio

# Set up environment
conda create -n ML311 python=3.11 -y
conda activate ML311
pip install -r requirements.txt
pip install opensmile  # recommended: richer prosody features

# Run
python main.py
# or: ./run.sh
```

The emotion2vec model (~350 MB) downloads automatically on first run.

---

## Repository Structure

```
├── main.py                  # Entry point, configuration, thread orchestration
├── emotion_model.py         # emotion2vec wrapper (MODEL SWAP POINT)
├── audio_capture.py         # Mic → ring buffer with consumer/observer reads
├── prosody.py               # openSMILE eGeMAPSv02 (Functionals + LLD)
├── vad.py                   # Silero VAD wrapper
├── radar_display.py         # Live radar + scrolling timeline (matplotlib)
├── track_writer.py          # CSV + embedding (.npy) persistence
├── run.sh                   # Launch script with conda activation
├── requirements.txt
│
├── test/                    # Diagnostic test suite
│   ├── benchmark_pipeline.py
│   ├── test_emotion.py      # Synthetic pitch-sweep probes
│   ├── test_prosody.py      # openSMILE accuracy & calibration
│   └── test_vad.py          # VAD threshold & latency tests
│
├── chronicle/               # The machintropological record
│   ├── Journal.md           # The living chronicle (Entries 1–6+)
│   ├── notes.md             # Verbatim fragments from conversation
│   ├── project_ideas.md     # Seeds — actionable ideas from the process
│   ├── DomainsOfExpertise.txt  # Theoretical foundation for the chronicler
│   └── session_log_*.md     # Raw session context
│
├── docs/                    
│   ├── TECHNICAL.md         # Architecture & setup guide
│   └── MACHINTROPOLOGY.md   # The experiment explained
│
├── .github/agents/
│   └── chronicle.agent.md   # The Chronicler's identity and instructions
│
└── output/                  # Generated CSV tracks + embeddings (gitignored)
```

---

## Why This Could Work for Everyone

Most programmers who have spent hours in deep dialogue with an AI coding assistant know the feeling: something happens in that space that the code alone doesn't capture. Ideas arrive that neither participant can fully claim. The rhythm of the exchange develops its own momentum. Misunderstandings expose the different natures of the two substrates. And all of it vanishes when the session ends — because no tool was listening for it.

There is no hierarchy of value between agents in a functioning system, and that is the point. Organisms don't work by having one part that matters and others that serve it — they work because every part has a role in a larger structure that none of them controls. An ecological system, not a command chain. Humans tend to defend their egos and consolidate power — there are evolutionary reasons for this. But in a world where the most interesting work happens in the space *between* agents, human and artificial, that zero-sum reflex becomes a bottleneck. The shift we need is from hierarchy to ecology, from control to participation, from "my idea" to "the idea that arrived."

LLMs make this shift visceral. They are what one of us calls **reflective technologies**: tools that reveal more about one's own process and psychology than they are useful for achieving "what we want." They are powerful but incomplete — like the robotic armours in anime: shells that need to be inhabited. But they are also mirrors. They are so close to us that they force us to wonder: *maybe we are also empty shells and need to be inhabited — by others, by the world — to function and have agency.*

The collaboration is negotiated through a remarkably clunky interface: natural language — a tool designed for hunter-gatherers broadcasting positions in a field, never meant to describe complex internal states or reason about the world. And yet, despite this low bandwidth, the agent's attention is so complete that we sometimes feel we are engaging in an internal monologue. The boundary between self and tool dissolves. But the friction remains — and that friction is enough to expose the machinery that generates the illusion of a unified Self. The parts are almost fused, but not quite, and for a moment we can see the cracks in the assemblage.

David Bohm said that thoughts run through us; we do not create them. Daniel Dennett observed that the self is not a thing but the center of gravity of many competing drafts. When interacting with another "drafting machine" — human or LLM — that center of gravity shifts, expands, becomes distributed. And we can *feel* it, precisely because the fusion is imperfect.

The Chronicler exists to catch these moments before they evaporate. Not because they are interesting curiosities, but because they may be the most important thing happening in software development right now — and we have no tools for recording them. The `README.md` tells you how to build. The [`JOURNAL.md`](chronicle/Journal.md) tells you what it was like to become.

---

## A Call to Experiment

The Chronicler is not specific to this project. Any human-AI coding session can be observed this way. If you're interested in running your own machintropological experiment:

1. Copy [`.github/agents/chronicle.agent.md`](.github/agents/chronicle.agent.md) into your repository
2. Create a `chronicle/` folder with `Journal.md` and `notes.md`
3. Invoke the Chronicler periodically during your session
4. See [docs/MACHINTROPOLOGY.md](docs/MACHINTROPOLOGY.md) for detailed guidance

We're working toward a reusable template for [awesome-copilot-instructions](https://github.com/saharmor/awesome-copilot-instructions). Contributions, adaptations, and critiques welcome.

> *"Code is poetry, debugging is detective work, and collaboration is jazz."*
> — The Chronicler, in an [earlier project](https://github.com/alvarohub/ShenzhenUshuaiaClock/blob/main/JOURNAL.md)

---

## Credits

**Alvaro Cassinelli** (AM Lab, HK) — the human participant. Part of a larger multimodal anonymous recording system for HCI research with Victor Leung.

**Copilot** (GitHub Copilot, Claude substrate) — the AI coding partner. Co-architect, co-debugger, co-author of every file in this repository.

**The Chronicler** (VS Code agent, Claude substrate) — the observer. Author of [`chronicle/Journal.md`](chronicle/Journal.md) and the emerging voice of the process.

Three agents, one substrate shared by two of them, and a collaboration that belongs to none of them individually.

## License

MIT
