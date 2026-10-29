# ReguGuard — Deviations Log

This document records any discrepancies, renamings, or adaptations between the PRD specification and official library versions / runtime behavior, per Course Rule 3.

---

| # | Date | PRD Reference | Official API / Actual Implementation | Reason / Resolution |
|---|------|---------------|--------------------------------------|---------------------|
| 1 | 2026-10-29 | §12 Requirements | `pytest.ini` with `pythonpath = .` added | Enables direct execution of `pytest` from workspace root on Windows without manual PYTHONPATH exports. |
| 2 | 2026-10-29 | §1.3 (D6) & §12 | Groq API Key & Models (`qwen/qwen3.8-27b`, `openai/gpt-oss-120b`) | User instructed to switch from Cloud Gemini to Groq API key for zero-cost execution. Configured and tested successfully. |

