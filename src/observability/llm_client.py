"""
ReguGuard LLM Client & Mock Provider
====================================
Wraps Groq / Google GenAI LLM inferences with prompt validation,
token counting, fallback mock support, and trace callback logging.

Single Source of Truth: PRD §12, Course Rule 7
"""

from __future__ import annotations
import json
import os
import time
from typing import Dict, Any, Optional
from src.config import settings

# Attempt to load Groq client
try:
    from groq import Groq
    _groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
except Exception:
    _groq_client = None


class LLMClient:
    """Manages LLM completions with fallback mock support for deterministic testing."""

    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock or not bool(settings.GROQ_API_KEY)

    def generate(
        self,
        prompt: str,
        system_instruction: str = "",
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        response_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes text generation using Groq or the deterministic mock engine.
        Returns dict with: content, tokens_in, tokens_out, latency_ms.
        """
        model_name = model or settings.GENERATOR_MODEL
        t0 = time.time()

        if not self.use_mock and _groq_client is not None:
            try:
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                params: Dict[str, Any] = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                if response_format == "json":
                    params["response_format"] = {"type": "json_object"}

                response = _groq_client.chat.completions.create(**params)
                latency_ms = (time.time() - t0) * 1000.0

                usage = response.usage
                tokens_in = usage.prompt_tokens if usage else len(prompt) // 4
                tokens_out = usage.completion_tokens if usage else 100

                return {
                    "content": response.choices[0].message.content or "",
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "latency_ms": latency_ms,
                    "model": model_name
                }
            except Exception as e:
                # If rate-limited or offline, fallback cleanly
                pass

        # CONCEPT: Deterministic Mock LLM (Course Rule 7)
        latency_ms = (time.time() - t0) * 1000.0 + 15.0
        mock_content = self._generate_mock_response(prompt, system_instruction)
        return {
            "content": mock_content,
            "tokens_in": len(prompt) // 4 + 10,
            "tokens_out": len(mock_content) // 4 + 5,
            "latency_ms": latency_ms,
            "model": "mock-llm-engine"
        }

    def _generate_mock_response(self, prompt: str, system: str) -> str:
        """Generates realistic structured responses matching agent prompts."""
        prompt_lower = prompt.lower()

        # Manager RunPlan mock
        if "runplan" in prompt_lower or "coordinator" in system.lower():
            return json.dumps({
                "plan_name": "GST E-invoicing Impact Assessment",
                "steps": [
                    "Fetch notification and prior rules via Regulation Monitor",
                    "Execute parallel Change Detection and SME Profile analysis",
                    "Perform ReAct Impact Analysis",
                    "Verify evidence and generate Action Plan via CrewAI Flow"
                ],
                "delegations": ["monitor", "change_detection", "sme_profile", "impact", "evidence_action"]
            })

        # Impact Agent mock verdict
        if "impact analysis" in system.lower() or "verdict" in prompt_lower:
            return json.dumps({
                "verdict": "impacted",
                "confidence": 0.94,
                "reasoning_summary": (
                    "The SME has an Annual Aggregate Turnover (AATO) of 7.5 Crore INR, which exceeds "
                    "the newly lowered statutory e-invoicing threshold of 5 Crore INR prescribed in Para 2. "
                    "Consequently, the SME is legally required to implement e-invoicing."
                ),
                "key_section": "Para 2"
            })

        # Evidence verification mock
        if "skeptic" in system.lower() or "verifier" in system.lower():
            return json.dumps({
                "verified": True,
                "quote": "registered person whose aggregate turnover in any preceding financial year from 2017-18 onwards exceeds five crore rupees",
                "notes": "Exact substring match confirmed against source notification text."
            })

        # Action planner mock
        if "action" in system.lower():
            return json.dumps({
                "action": "Integrate ERP with GST Invoice Registration Portal (IRP) for automated IRN generation.",
                "owner": "Finance & Accounts Team",
                "priority": "high",
                "deadline": "2023-08-01"
            })

        return "Analysis completed successfully based on regulatory source texts."


llm_client = LLMClient()

