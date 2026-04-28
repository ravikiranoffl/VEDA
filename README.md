
<div align="center">

# VEDA  
**Vast Electronic Data Archive**

*The Ultimate Autonomous OSINT Matrix*

[![License](https://img.shields.io/badge/License-MIT-emerald.svg?style=for-the-badge)](#)
[![Engine](https://img.shields.io/badge/Engine-Python_3.12-blue.svg?style=for-the-badge)](#)
[![Status](https://img.shields.io/badge/Status-Operational-success.svg?style=for-the-badge)](#)
[![Automation](https://img.shields.io/badge/Automation-GitHub_Actions-black.svg?style=for-the-badge&logo=github-actions)](#)

> *“In an era of fleeting digital information, stealth edits, and paywalls, VEDA ensures that every significant global shift is captured, organized, and archived forever.”*

</div>

---

## 🧠 The Vision: What is VEDA?

**VEDA (Vast Electronic Data Archive)** is a fully autonomous, serverless Open-Source Intelligence (**OSINT**) aggregation system designed to create a permanent, immutable record of global history as it unfolds.

Every day, the VEDA engine:
- Sweeps 30+ global and regional news sources  
- Extracts structured data from RSS/XML feeds  
- Deduplicates content using hashing  
- Archives results into lightweight, timestamped JSON  

The result: a **daily snapshot of the world’s information state**, preserved exactly as it appeared.

---

## ⚙️ Technical Architecture & Workflow

VEDA operates with a decoupled, serverless pipeline requiring zero human interaction.

```mermaid
graph TD
    A[Cron Trigger: Every 2 Hrs] -->|Wake Engine| B{VEDA Engine veda.py}
    
    subgraph Global Sweep
    B -->|Fetch XML/RSS| C[(Global Sources)]
    B -->|Fetch XML/RSS| D[(India National Sources)]
    B -->|Fetch XML/RSS| E[(Regional Telugu Sources)]
    end
    
    C & D & E --> F[Deduplication + Hashing]
    F --> G[Generate YYYY-MM-DD.json]
    
    subgraph Storage Layer
    G -->|Metadata| H[GitHub Repository]
    G -->|Full Articles| K[(HEDA: Hugging Face Vault)]
    end
    
    H --> I[GitHub Pages CDN]
    I --> J((Frontend UI))
    K -->|On Demand Fetch| J
    
    style B fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff
    style G fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style I fill:#312e81,stroke:#818cf8,stroke-width:2px,color:#fff
    style K fill:#9d174d,stroke:#f472b6,stroke-width:2px,color:#fff
````

---

## 🧬 Philosophy of Permanence

### Why Archive?

The modern internet is not stable:

* Articles get edited silently
* Headlines change without notice
* Content disappears behind paywalls

VEDA solves this by storing **raw, time-accurate snapshots**.

> Want to see what the world reported on a specific day?
> VEDA provides an unedited historical record.

---

### Why GitHub Pages?

VEDA deliberately avoids traditional backend infrastructure.

**Benefits:**

* 🟢 **Zero Cost Scaling** — Hosted on GitHub’s global CDN
* ⚡ **Blazing Fast UI** — Static JSON + client-side rendering
* 🔒 **Immutable Storage** — Git history ensures data integrity
* 🧩 **No Database Needed** — File system *is* the database

---

## 🧰 Core Toolstack

| Component     | Technology          | Purpose                                |
| ------------- | ------------------- | -------------------------------------- |
| Data Engine   | Python 3.12         | Fetching, parsing, hashing, extraction |
| Automation    | GitHub Actions      | Scheduled execution (cron jobs)        |
| Light Storage | JSON + Git          | Immutable structured archives          |
| Deep Storage  | Hugging Face (HEDA) | Long-form article storage              |
| Frontend UI   | HTML5 + Vanilla JS  | Fast, dynamic client rendering         |

---

## 🚀 System Strengths

### 1. Absolute Autonomy

* Fully automated pipeline
* No manual intervention required

### 2. Extreme Performance

* No backend latency
* Instant JSON fetch + render

### 3. Memory Efficiency

* Limits DOM rendering (100–250 entries)
* Prioritizes latest breaking content
* Prevents browser overload

---

## 🛣️ Engineering Roadmap

### 🔍 Q3 2026 — Master Indexer

**Problem:** Search limited to current day
**Solution:**

* Build `search-index.json`
* Enable cross-year instant search

---

### 🌐 Q4 2026 — Async Extraction Engine

**Problem:** Feed failures due to timeouts
**Solution:**

* Migrate to `aiohttp` + `asyncio`
* Implement exponential backoff
* Ensure zero data gaps

---

### 🤖 Q1 2027 — AI Semantic Clustering

**Problem:** Information overload (500+ headlines/day)
**Solution:**

* Integrate LLM (Gemini API)
* Merge duplicate stories
* Generate “Intelligence Briefing Cards”

---

## 🌍 Target Intelligence Matrix

### Global Sources

* NYT, Washington Post, BBC, France24, Al Jazeera

### India National

* The Hindu, Indian Express, NDTV, Times of India

### Financial Networks

* Moneycontrol, LiveMint, Economic Times

### Regional (Telugu)

* Namasthe Telangana, NTV, ABP Desam, V6 Velugu

---

## 🖥️ Local Deployment Guide

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/VEDA.git
cd VEDA
```

### 2. Install Dependencies

```bash
pip install aiohttp trafilatura huggingface_hub
```

### 3. Run Engine

```bash
python veda.py
```

> This generates today’s archive instantly.

---

### 4. Launch UI

Open:

```bash
index.html
```

in your browser to view the system locally.

---

<div align="center">

### ⚡ VEDA: Capturing History in Real-Time

<i>End of Line — VEDA Core Architecture</i>

</div>
