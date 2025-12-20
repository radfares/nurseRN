# AGENTS.md
# Nursing Research Project Assistant — Agent Operating Manual

This file defines the rules, responsibilities, architecture, workflows, and quality standards for all AI coding agents contributing to the nurseRN project.  
Agents MUST follow this document when modifying code, adding features, writing tests, or performing maintenance.

---

# 1. Purpose

The nurseRN system is a multi-agent AI platform designed to support nursing residents through their healthcare improvement projects.  
This AGENTS.md file ensures:

- Consistent development practices  
- Reliable orchestration behavior  
- High-quality research output  
- Safe tool usage  
- Automated testing and validation  
- Predictable agent behavior  

Human developers are NOT required to write tests or maintain them — this responsibility is delegated to AI agents.

---

# 2. Project Architecture

## 2.1 High-Level Overview
The system uses a layered architecture:

- **Agent Layer** — Domain-specialized AI agents  
- **Orchestration Layer** — Planning, execution, resilience  
- **Workflow Layer** — Multi-phase research pipelines  
- **Service Layer** — API tools, circuit breakers, RAG  
- **Tool Layer** — Document readers, literature tools, safety tools  
- **Data Layer** — SQLite DBs, vector stores, caches  

## 2.2 Architecture Diagram

```mermaid
graph TD
    subgraph "User Interface"
        UI[User Query]
    end

    subgraph "Orchestration Layer (src/orchestration/)"
        IO[Intelligent Orchestrator]
        WO[Workflow Orchestrator]
        RO[Resilient Orchestrator]
        CM[Context Manager]
        MCP[MCP Dispatcher]
    end

    subgraph "Agent Layer (agents/)"
        NRA[Nursing Research Agent]
        MRA[Medical Research Agent]
        ARA[Academic Research Agent]
        RWA[Research Writing Agent]
        PTA[Project Timeline Agent]
        DAP[Data Analysis Planner]
        CVA[Citation Validation Agent]
    end

    subgraph "Workflow Layer (src/workflows/)"
        URP[Unified Research Pipeline]
        QG[Quality Gates]
    end

    subgraph "Service Layer (src/services/)"
        AT[API Tools]
        CB[Circuit Breaker]
        RAG[RAG Pipeline]
        CA[Citation APIs]
    end

    subgraph "Tool Layer (src/tools/)"
        LT[Literature Tools]
        MT[Milestone Tools]
        ST[Safety Tools]
        DR[Document Readers]
    end

    subgraph "Data Layer"
        DB[(SQLite Project DB)]
        VS[(ChromaDB Vector Store)]
        AC[(API Cache)]
    end

    UI --> IO
    IO --> WO
    WO --> RO
    RO --> MCP
    MCP --> NRA & MRA & ARA & RWA & PTA & DAP & CVA
    
    URP --> QG
    URP --> WO
    
    NRA & MRA & ARA & RWA & PTA & DAP & CVA --> AT
    AT --> CB
    AT --> AC
    
    NRA & MRA & ARA & RWA & PTA & DAP & CVA --> LT & MT & ST & DR
    NRA & MRA & ARA & RWA & PTA & DAP & CVA --> RAG
    
    RAG --> VS
    LT & MT --> DB
```
