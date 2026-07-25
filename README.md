# NexusOps: Enterprise AI Operations & Data Integration Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js: 14](https://img.shields.io/badge/Next.js-14.1-black.svg)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docker.com)

**NexusOps** is an enterprise-grade Forward Deployed Engineering (FDE) platform built to solve customer data fragmentation, entity disambiguation across siloed systems, and safe Human-In-The-Loop (HITL) AI agent workflow automation.

Designed to demonstrate top-tier FDE competencies for roles at companies like **Palantir, Scale AI, Databricks, and OpenAI Enterprise**.

---

## 🌟 Key Architecture & Modules

```
                       +-------------------------------------------------------+
                       |             Next.js 14 Control Plane UI               |
                       | (TypeScript, Operational Dashboard, Agent Approvals) |
                       +---------------------------+---------------------------+
                                                   | REST / WebSocket
                                                   v
+--------------------------------------------------+--------------------------------------------------+
|                                    FastAPI Enterprise Backend                                       |
|                                                                                                     |
|  +---------------------------+   +-------------------------------+   +----------------------------+  |
|  | Multi-Source Ingestion    |   | Entity Resolution & Fusion    |   | AI Agent Workflow Engine   |  |
|  | Connector Engine          |-->| Engine (Graph & Normalization)|-->| (Tool Execution & HITL)    |  |
|  +---------------------------+   +-------------------------------+   +----------------------------+  |
|                                                                                    |                |
|  +---------------------------------------------------------------------------------+-------------+  |
|  | Audit Logging, RBAC & Telemetry Engine                                                         |  |
+---------------------------------------------------+-------------------------------------------------+
                                                    |
                                                    v
                     +------------------------------+------------------------------+
                     |  PostgreSQL (Relational + Entity Graph + Vector Metadata)   |
                     |  Redis (Task Queues & Agent Memory)                         |
                     +-------------------------------------------------------------+
```

### 1. Multi-Tenant Data Connector Engine
- Ingests customer data feeds from simulated Zendesk support tickets, HubSpot CRM company records, Jira engineering bugs, and PostgreSQL databases.
- Normalizes raw payloads into standardized entity schemas.

### 2. Fuzzy Entity Resolution & Fusion Engine
- Leverages Levenshtein distance metrics (`thefuzz`) and domain matching algorithms to group disparate customer records into a **Unified Customer Knowledge Graph**.
- Computes confidence scores for merged enterprise entities.

### 3. Human-In-The-Loop (HITL) AI Agent Workflow Engine
- Evaluates operational customer issues (SLA breaches, P0 escalations, credit refunds).
- Automated risk classification: Low-risk tasks run autonomously; high-risk actions (financial payouts, tier overrides) are placed into a live **Human-in-the-Loop Approval Queue**.
- Executes approved enterprise tool integrations (e.g. Jira escalation, billing credit issuance) with 1-click controls.

### 4. Immutable Audit Trail & Governance
- Logs every entity fusion, AI agent recommendation, and manual human override to an immutable audit record for enterprise compliance.

---

## 🚀 Quick Start (Local Development)

### Option 1: Docker Compose (Recommended)
```bash
docker compose up --build
```
- **Control Plane UI**: `http://localhost:3000`
- **FastAPI OpenAPI Docs**: `http://localhost:8000/docs`

### Option 2: Standalone Local Setup

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate | On Linux/macOS: source venv/bin/activate
pip install -e .
python scripts/seed.py
python main.py
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Vanilla CSS design system, Lucide Icons
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), AsyncPG
- **Storage & Queue**: PostgreSQL 16, Redis 7
- **Fuzzy Matching**: `thefuzz`, `Levenshtein`

---

## 📄 License
Licensed under the [MIT License](LICENSE).
