# ReguGuard — Module Guide for Students & Evaluators

> Course: **CSE3101 Agentic AI, BML Munjal University**  
> Team: **Yash Yadav (230664), Kartavya Dev (230653), Nancy (230640)**  
> Purpose: Quick reference explaining what each module does and how to modify it during the viva / lab evaluation.

---

## 1. `src/schemas.py` — Pydantic Data Models & Contracts

### What it does:
Defines all structured data types and message schemas across the system. It enforces type constraints on configuration (`RunConfig`), domain entities (`SMEProfile`, `ClauseChange`), reasoning outcomes (`ImpactVerdict`, `ActionPlan`), grounded evidence (`Evidence`), observability spans (`TraceEvent`), and the final user report (`ImpactReport`).

### Key Course Concepts:
- `# CONCEPT: Multi-agent configuration knobs` (PRD §5.3)
- `# CONCEPT: Structured Output & Output Guardrail` (PRD §7)
- `# CONCEPT: Reflection and Grounded Verification` (PRD §7)
- `# CONCEPT: Observability & OpenTelemetry-style Spans` (PRD §8.3)
- `# CONCEPT: Cross-framework A2A Envelope` (PRD §5.2)

### Business Rules Enforced:
1. If `verdict == "impacted"`, at least one item in `evidence` must have `verified == True`. Otherwise, the report automatically downgrades to `"ambiguous"`, appends a guardrail flag, and caps confidence to $\le 0.5$.
2. Mandatory headline: *"Potential regulatory impact detected — human review recommended"*.

### How to modify it:
- **Add a new persona:** Extend the `Literal[...]` options in `RunConfig`. Production architecture is fixed to Blackboard + Sequential + ReAct.
- **Add fields to SME profile:** Add a field to `SMEProfile` with type annotations and optional default values.
- **Change confidence downgrade behavior:** Edit `validate_business_rules` inside `ImpactReport`.

---

## 2. `src/config.py` — Central Settings & Environment

### What it does:
Loads environment settings from `.env`, resolves relative file paths across the project, and provides helper functions to read model definitions (`config/models.yaml`) and pricing tables (`config/pricing.yaml`).

### How to modify it:
- **Change default model or budget:** Update default values in `Settings` class or override them via `.env`.
- **Change token pricing rates:** Edit `config/pricing.yaml`.

---

## 3. `src/blackboard/store.py` & `src/blackboard/mcp_server.py` — Shared State Store

### What it does:
Implements the shared memory Blackboard pattern mandated by Course Criterion 1. All agents read and write versioned case state (e.g. `doc`, `diff`, `sme_profile`, `impact_verdict`, `evidence`, `action_plan`). Every write increments the version number and records agent identity and timestamp. Every read is logged to `blackboard_reads` so that the access frequency heatmap (Agent $\times$ Key) can be rendered accurately.

### Key Course Concepts:
- `# CONCEPT: Blackboard Shared State Record` (PRD §5.3)
- `# CONCEPT: Blackboard Write & Read Operations with Versioning`
- `# CONCEPT: Blackboard Snapshot` (Complete audit trail)
- `# CONCEPT: MCP Tool Server` (Exposes blackboard via FastMCP)

### How to modify it:
- **Add custom metadata to blackboard entries:** Modify `BlackboardEntry` schema and add columns to `blackboard_entries` table in `store.py`.
- **Add a new blackboard tool:** Add `@mcp.tool()` inside `src/blackboard/mcp_server.py`.

---

## 4. `src/mcp_servers/` — The Six MCP External Tool Servers

### What it does:
Implements the 6 external tool servers mandated by PRD §6:
1. `doc_fetcher.py`: Reads the curated regulatory corpus (`data/corpus/`) and `MANIFEST.csv`.
2. `clause_parser.py`: Breaks raw regulatory text into discrete sections/clauses and extracts monetary turnover figures (crores/lakhs) and dates.
3. `diff_tool.py`: Compares prior vs new regulation texts clause-by-clause to yield structured addition/modification/deletion records.
4. `sme_db.py`: Connects to SQLite and `data/smes/smes.json` to fetch enterprise financial profiles and read/write operational memory notes.
5. `deadline_calc.py`: Non-LLM deterministic date and countdown calculator.
6. `vector_search.py`: ChromaDB version-aware semantic retriever with metadata date filtering.

### Key Course Concepts:
- `# CONCEPT: MCP External Tool Execution` (PRD §6, Criterion 2)
- `# CONCEPT: Deterministic Non-LLM Computation` (`deadline_calc`)
- `# CONCEPT: Agent Memory Persistence` (`sme_db.update_memory`)

### How to modify it:
- **Add a new regulation document:** Drop the `.txt` or `.pdf` into `data/corpus/` and add an entry row in `MANIFEST.csv`.
- **Add an SME:** Add a JSON object into `data/smes/smes.json`.
- **Modify deadline logic:** Adjust rule cases inside `src/mcp_servers/deadline_calc.py`.

