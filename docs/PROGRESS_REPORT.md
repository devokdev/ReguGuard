# ReguGuard — Coursework Progress Report (Phase 2 & Phase 3)

> Course: **CSE3101 Agentic AI, BML Munjal University**  
> Team: **Yash Yadav (230664), Kartavya Dev (230653), Nancy (230640)**  
> Reference: PRD §15 (Part-2 & Part-3 Submission Support)

---

## 1. Progress vs Plan Summary

| Stage / Component | Evaluation-1 Planned Target | Evaluation-2 / Phase 3 Actual Status | Variance Explanation |
|---|---|---|---|
| **System Scope** | Regulation Monitor + Change Detection | **Full vertical slice implemented** (All 7 agents + Guardrails + A2A + Web UI) | Exceeded plan to achieve full Rubric C8 marks |
| **Agent Frameworks** | Exploratory | **Google ADK + CrewAI Flow** | Locked per Professor criterion |
| **Shared State** | Conceptual Blackboard | **SQLite `BlackboardStore` + FastMCP server** | Fully operational with access heatmaps |
| **Cross-Framework** | Not specified | **Agent-to-Agent (A2A) protocol** | Implemented with official Agent Card |
| **External Tools** | Standard functions | **6 FastMCP microservices** | Standards-compliant tool execution |
| **Guardrails** | Basic prompt rules | **3-Layer Deterministic + PII Masking** | Defends against injection, toxic, & data leaks |
| **Evaluation** | Small sample checks | **48 labelled cases, 6 configs, 288-run grid** | Reproducible with metrics & boxplots |
| **Deployment** | Local only | **Google Cloud Run containerized deployment** | Docker + Supervisord multi-process architecture |

---

## 2. Approach Changes from Evaluation 1 to Evaluation 2 (D1–D16)
*Refer to [`docs/EVAL1_TO_EVAL2_CHANGES.md`](file:///c:/Users/karta/Desktop/projects/agentic_ai/docs/EVAL1_TO_EVAL2_CHANGES.md) for the itemized decision audit table.*

---

## 3. Rubric Coverage Self-Assessment
- **C6 (Progress vs Plan - 5/5):** Completed all P0 vertical slice deliverables and all P1 phase 3 targets ahead of schedule.
- **C7 (Technical Understanding - 5/5):** Clear demarcation between ADK coordinator patterns, ReAct loops, Reflection critique in CrewAI, and FastMCP tool boundaries.
- **C8 (Requirements Met - 10/10):** All 11 professor criteria demonstrably met with automated test proofs.
- **C9 (Documentation - 5/5):** Comprehensive `MODULE_GUIDE.md`, `ARCHITECTURE.md`, `COVERAGE.md`, `VIVA_QA.md`, and `DEVIATIONS.md`.
- **C10 (Viva & Individual Contribution - 5/5):** Every team member equipped with viva questions, answers, and modification exercises.

