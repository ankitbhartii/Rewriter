<div align="center">

# ⚡ Rewriter: AI Writing Assistant & Real-Time Grammar Platform

### An enterprise-grade, browser-based Grammarly & Superhuman Go clone built with reverse-engineered dual-layer canvas architecture and 21 specialized AI writing agents.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Superhuman Go](https://img.shields.io/badge/Superhuman_Go-21_Agents-6366F1?style=for-the-badge&logo=openai&logoColor=white)](https://go.superhuman.com/agent-directory)
[![LanguageTool](https://img.shields.io/badge/LanguageTool-Cloud_Engine-15C39A?style=for-the-badge)](https://languagetool.org)

<br/>

**[Features](#-key-features)** •
**[Reverse-Engineered Architecture](#-reverse-engineered-architecture)** •
**[Superhuman Go Agent Directory](#-superhuman-go-agent-directory-21-agents)** •
**[Quick Start](#-quick-start)** •
**[API Endpoints](#-rest-api-reference)** •
**[Configuration](#-configuration)**

<br/>

</div>

---

## 📖 Overview

**Rewriter** is an authentic, local-first web application that replicates the full feature set, typing fidelity, and visual aesthetics of **Grammarly** and **Superhuman Go**.

Built by reverse engineering the core engineering principles of official Grammarly open-source projects ([grammarly/contenteditable](https://github.com/grammarly/contenteditable), [grammarly/gector](https://github.com/grammarly/gector), [@grammarly/editor-sdk](https://www.npmjs.com/package/@grammarly/editor-sdk)) and integrating the complete suite of **21 specialized AI writing agents** from [Superhuman Go](https://go.superhuman.com/agent-directory).

```
                        ┌────────────────────────────────────────────────────────┐
                        │                     Rewriter UI                        │
                        │   ┌──────────────────────┐  ┌──────────────────────┐   │
                        │   │  Dual-Layer Canvas   │  │  Superhuman Go AI    │   │
                        │   │  • Transparent Text  │  │  • 21 Writing Agents │   │
                        │   │  • Squiggly Mirrors  │  │  • 1-Click Fix All   │   │
                        │   │  • Anchored Popups   │  │  • Document Score    │   │
                        │   └──────────┬───────────┘  └──────────┬───────────┘   │
                        └──────────────┼─────────────────────────┼───────────────┘
                                       │ HTTP /api/check         │ HTTP /api/agents
                                       ▼                         ▼
                        ┌────────────────────────────────────────────────────────┐
                        │                   FastAPI Backend                      │
                        │   ┌─────────────────────┐   ┌──────────────────────┐   │
                        │   │   LanguageTool API  │   │ Deterministic Rules  │   │
                        │   │   • Grammar & Spell │   │ • Oxford Comma       │   │
                        │   │   • Typography      │   │ • Compound Predicate │   │
                        │   └─────────────────────┘   │ • Verb Parallelism   │   │
                        │   ┌─────────────────────┐   │ • Passive Voice      │   │
                        │   │  AI Provider Engine │   └──────────────────────┘   │
                        │   │  • Ollama / OpenAI  │   ┌──────────────────────┐   │
                        │   │  • Local Heuristics │   │ Tone & Readability   │   │
                        │   └─────────────────────┘   └──────────────────────┘   │
                        └────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 1. 🎯 Pixel-Perfect Dual-Layer Synchronized Canvas

- **Native Typing Performance:** Uses a standard, transparent `<textarea>` in the foreground, guaranteeing native browser caret tracking, IME composition, undo/redo history, and zero latency on long documents.
- **Underlying Squiggly Highlights:** Character-matched background mirror layer that renders color-coded squigglies:
  - 🔴 **Red (Correctness):** Spelling, determiners, capitalization, subject-verb agreement, Oxford comma.
  - 🟡 **Yellow/Amber (Clarity):** Compound predicates, passive-to-active transformations, concise phrasing.
  - 🔵 **Blue (Style & Tone):** Formality adjustments, word choice, and readability improvements.

### 2. ⚡ Instant In-Place Rectification (Zero-Drift)

- **Offset-Preserving Delta Shifts:** When accepting a fix (via card, popup, or callout), the engine calculates character index deltas and shifts all downstream suggestion bounds immediately, eliminating drift or mismatched token replacements.
- **`[ ✓ Apply All ]` in 1 Click:** Resolves all detected errors in a single click, instantly updating the writing score to 100 with zero delay.
- **Anchored Contextual Popups:** Clicking or navigating the caret inside an underlined issue opens an anchored floating card directly below the error with instant **"✓ Accept"**, **"Ignore"**, and **"Add to Dictionary"** actions.
- **Floating Callout Bubble:** Interactive _"Fix grammar and consistency"_ speech bubble anchored to the text.

### 3. 🤖 Superhuman Go 21 AI Agents Suite

Full, real-time integration of all 21 specialized agents modeled from Superhuman Go's enterprise directory:

- Pinned shortcuts: **Reader Reactions**, **Executive Summarize**, **Shorten & Remove Jargon**, **Fix Consistency**.
- Searchable directory modal with category filtering and interactive chat integration.

### 4. 📊 Writing Score & Readability Metrics

- **Dynamic Radial SVG Gauge:** Smooth animated circle gauge (0–100) reflecting real-time grammatical health.
- **Tone & Readability Analysis:** Evaluates Flesch-Kincaid Reading Ease, sentence length, and tone indicators (Formal, Neutral, Casual).

### 5. 🌓 Dark & Light Mode

- Complete theme toggle with persistent `localStorage` preference, matching authentic Grammarly green (`#15C39A`) and Superhuman indigo (`#6366F1`) accents.

---

## 🔬 Reverse-Engineered Architecture

Our implementation is based directly on the technical discoveries from Grammarly's open-source repositories:

### Why `contenteditable` Fails for Production Grammar Checkers

According to Grammarly's official documentation in `grammarly/contenteditable`:

> _"Grammarly implements grammar-correcting-underlines via textarea + element on top (reasons: contenteditable is slow to render, no way to clean markup, hard to do proper selection/annotations)."_

1. **DOM Corruption:** Directly wrapping misspelled words in `<span>` tags inside a `contenteditable` container breaks browser undo/redo history, causes jumping carets, and corrupts multi-byte character inputs.
2. **Rewriter's Solution:** A synchronized coordinate system where both the `<textarea>` and the highlight mirror share identical `font-family`, `font-size`, `line-height`, `letter-spacing`, and `padding`, with scroll events locked 1:1.

### Deterministic GEC (Grammatical Error Correction)

From Grammarly's paper _"GECToR – Grammatical Error Correction: Tag, Not Rewrite"_:

- Rather than using generative LLMs that frequently hallucinate or alter intended meaning, grammar correction is modeled as localized transformations:
  - **Oxford Comma Rule:** Identifies serial conjunctions without preceding commas (`paid social and` → `paid social, and`).
  - **Temporal Idioms:** Injects missing grammatical articles (`through end of week` → `through the end of the week`).
  - **Compound Predicate Comma:** Eliminates unnecessary commas separating compound verbs (`parallel, and` → `parallel and`).
  - **Verb Tense Parallelism:** Aligns coordinated participle clauses (`are proceeding ... and escalated` → `escalating`).
  - **Passive Voice Restructuring:** Identifies by-phrases and re-casts into active voice (`A meeting was held by our team` → `Our team held a meeting`).

---

## 🗂 Superhuman Go Agent Directory (21 Agents)

| Agent Name                    | Category       | Primary Function                                                                  |
| :---------------------------- | :------------- | :-------------------------------------------------------------------------------- |
| **Reader Reactions**          | Tone & Clarity | Analyzes how the recipient is likely to interpret the tone and emotional weight   |
| **Executive Summary**         | Productivity   | Condenses multi-paragraph documents into high-impact executive bullet points      |
| **Shorten & Remove Jargon**   | Clarity        | Translates corporate buzzwords into crisp, plain English                          |
| **Grammar & Consistency**     | Correctness    | Rectifies all grammar, punctuation, and parallelism errors across the entire text |
| **AI Rewriter**               | Tone & Style   | Multi-mode rewriter: Polish, Formal, Concise, and Casual variants                 |
| **Email Reply Drafter**       | Productivity   | Generates contextually aware email responses tailored to message goals            |
| **Subject Line Generator**    | Marketing      | Produces 5 catchy, high-open-rate subject lines                                   |
| **Action Items Extractor**    | Productivity   | Extracts deliverables, owners, and due dates from correspondence                  |
| **Cold Outreach Specialist**  | Sales          | Formats hyper-personalized B2B outreach pitches                                   |
| **Meeting Recap Builder**     | Management     | Synthesizes meeting minutes into actionable recap messages                        |
| **Technical Simplifier**      | Technical      | Explains complex engineering architectures for non-technical stakeholders         |
| **Crisis Communications**     | PR & Comms     | Crafts measured, de-escalating communication during sensitive events              |
| **Customer Empathy Agent**    | Support        | Rewrites customer responses with supportive, resolution-focused empathy           |
| **SEO Meta Optimizer**        | Marketing      | Generates search-optimized titles and meta descriptions within character limits   |
| **Academic Polish**           | Academic       | Formalizes vocabulary and syntax for publications and academic papers             |
| **Cross-Cultural Adapter**    | Localization   | Neutralizes local idioms and slang for international audiences                    |
| **Legal Disclaimer Verifier** | Legal          | Checks for standard liability, privacy, and compliance disclaimers                |
| **Creative Storyteller**      | Creative       | Enhances narrative hooks, emotional resonance, and descriptive pacing             |
| **Bullet Point Distiller**    | Formatting     | Converts dense wall-of-text paragraphs into scannable hierarchical lists          |
| **Direct & Assertive Tone**   | Leadership     | Eliminates weak qualifiers ("I just wanted to", "maybe") for confident messaging  |
| **Multi-Language Translator** | Translation    | Context-aware translation preserving professional terminology and idioms          |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (Python 3.11, 3.12, or 3.13 supported)
- **Node.js 18+** & **npm**

### Installation

```bash
# Clone the repository
git clone https://github.com/ankitbhartii/Rewriter.git
cd Rewriter

# Install dependencies
npm install
pip install fastapi uvicorn pyspellchecker requests
```

### Launching the Application

#### Option 1: 1-Click Windows Launcher

Double-click:

```cmd
start_browser_app.bat
```

#### Option 2: Python Launcher (Cross-Platform)

```bash
python start_browser_app.py
```

#### Option 3: npm Script

```bash
npm run dev
```

Your browser will automatically open:

- **Web Editor:** [`http://localhost:8000`](http://localhost:8000)
- **Web Component & Extension Demo:** [`http://localhost:8000/extension`](http://localhost:8000/extension)
- **Interactive OpenAPI Docs:** [`http://localhost:8000/docs`](http://localhost:8000/docs)

---

## 📡 REST API Reference

| Endpoint          |     Method     | Description                                                                     | Payload Example                                         |
| :---------------- | :------------: | :------------------------------------------------------------------------------ | :------------------------------------------------------ |
| `/api/check`      |     `POST`     | Runs LanguageTool + deterministic rule checks, calculates score and suggestions | `{"text": "A meeting was held by our team..."}`         |
| `/api/rewrite`    |     `POST`     | Rewrites text across 4 styles (`polish`, `formal`, `concise`, `casual`)         | `{"text": "...", "mode": "formal"}`                     |
| `/api/agents`     |     `GET`      | Returns full catalog of 21 Superhuman Go agents with metadata                   | _None_                                                  |
| `/api/agents/run` |     `POST`     | Executes a specific agent on input text                                         | `{"agent_id": "reader_reactions", "text": "..."}`       |
| `/api/agent/chat` |     `POST`     | Interactive Superhuman Go conversational assistant                              | `{"text": "...", "action": "summarize", "query": ""}`   |
| `/api/config`     | `GET` / `POST` | Fetches or updates LLM providers (Ollama / OpenAI / Offline) and settings       | `{"ai_provider": "ollama", "ollama_model": "llama3.2"}` |
| `/api/dictionary` | `GET` / `POST` | Retrieves or adds custom personal vocabulary words                              | `{"word": "Zephyr"}`                                    |

---

## ⚙️ Configuration

Configure local AI providers via the **Settings (⚙️)** modal in the top header or via `/api/config`:

- **Offline Mode:** Uses built-in deterministic GEC heuristics + LanguageTool cloud checks (default, zero configuration required).
- **Ollama Mode:** Connect to your local Ollama instance (e.g. `http://localhost:11434` with `llama3.2` or `mistral`).
- **OpenAI Mode:** Connect using your OpenAI API key with `gpt-4o-mini` or custom models.

---

## 📁 Repository Structure

```
Rewriter/
├── web/
│   ├── index.html                 # Main Grammarly & Superhuman Go Web App
│   ├── extension_demo.html        # Floating Extension & Web Component Demo
│   └── static/
│       ├── css/
│       │   └── style.css          # Authentic Theme (Dual-layer, popups, agents drawer)
│       └── js/
│           ├── app.js             # Real-time synchronization & delta-shift engine
│           └── grammarly-plugin.js# Standalone <grammarly-editor-plugin> Web Component
├── grammarly_desktop/
│   ├── config.py                  # Settings & Personal Dictionary storage
│   └── engine/
│       ├── rules.py               # Deterministic GEC Rule Engine (Oxford comma, parallelism, etc.)
│       ├── spellcheck.py          # Typo correction & technical vocabulary
│       ├── languagetool.py        # Cloud LanguageTool API client
│       ├── agents.py              # 21 Superhuman Go Specialized AI Agents
│       ├── tone.py                # Flesch-Kincaid & Tone Analyzer
│       └── ai_provider.py         # AI Rewrite Engine (Offline / Ollama / OpenAI)
├── server.py                      # FastAPI Backend Server & Static Asset Host
├── start_browser_app.py           # Cross-platform Launcher (Auto browser launch)
├── start_browser_app.bat          # 1-Click Windows Launcher
├── package.json                   # Project scripts and dependencies
├── LICENSE                        # Apache 2.0 License
└── README.md                      # Complete Project Documentation
```

---

## 🛡️ License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
