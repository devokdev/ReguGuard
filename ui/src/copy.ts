export interface ConceptDefinition {
  title: string;
  tag: string;
  oneLiner: string;
  explain: [string, string, string];
  codePath: string;
}

export const CONCEPTS: Record<string, ConceptDefinition> = {
  blackboard: {
    title: "Shared Board",
    tag: "Blackboard",
    oneLiner: "A shared whiteboard every agent writes on.",
    explain: [
      "Instead of sending giant files between agents, all agents read and write one shared record.",
      "Every change increments a version number and records who wrote it for complete auditing.",
      "If one agent fails, other agents can inspect the board state directly without starting over."
    ],
    codePath: "src/blackboard/store.py"
  },
  mcp: {
    title: "Tool Plug",
    tag: "MCP",
    oneLiner: "A standard plug so agents can use tools.",
    explain: [
      "The Model Context Protocol connects our agents to external calculators and databases safely.",
      "Each tool runs as its own service, so adding new legal rules won't break existing agent code.",
      "Every tool call is validated with strict type checks before the agent can use the answer."
    ],
    codePath: "src/mcp_servers/"
  },
  a2a: {
    title: "Cross Talk",
    tag: "A2A",
    oneLiner: "How two agents built with different frameworks talk.",
    explain: [
      "Google ADK agents and CrewAI agents speak different languages internally.",
      "The Agent-to-Agent protocol lets them exchange messages using standard cards and envelopes.",
      "Our system uses A2A to call the CrewAI verification flow right from the ADK pipeline."
    ],
    codePath: "src/crew_app/flow.py"
  },
  guardrail: {
    title: "Safety Gate",
    tag: "Guardrail",
    oneLiner: "A gate that checks what goes in and out.",
    explain: [
      "Rule-based filters block prompt injections and scrub sensitive details like GSTIN and PAN numbers.",
      "Tool guardrails stop unauthorized agents from running calculators or reading outside their lane.",
      "Output guardrails ensure every report contains mandatory disclaimers and verified quotes."
    ],
    codePath: "src/guardrails/engine.py"
  },
  react: {
    title: "Think & Act",
    tag: "ReAct",
    oneLiner: "The agent thinks, uses tools, and reasons step-by-step.",
    explain: [
      "Instead of guessing, the agent writes a thought, calls an MCP tool, and observes the answer.",
      "This loop repeats until the agent has verified every turnover number and effective date.",
      "Evaluators can inspect the exact thought chain on the Traces screen."
    ],
    codePath: "src/adk_app/pipeline.py"
  },
  reflection: {
    title: "Self Critique",
    tag: "Reflection",
    oneLiner: "The agent checks its own work and tries again.",
    explain: [
      "A Verifier agent extracts a quote from the law, and a Skeptic agent checks if it is verbatim.",
      "If the quote does not match the gazette text exactly, the system rejects it and loops back.",
      "This guarantees zero hallucinated citations in the final compliance report."
    ],
    codePath: "src/crew_app/flow.py"
  },
  rag: {
    title: "Agentic Search",
    tag: "Agentic RAG",
    oneLiner: "Look things up first, so answers quote real text.",
    explain: [
      "The system rewrites questions into search queries and filters laws by their effective date.",
      "Only clauses that are active as-of the query date are passed to the reasoning model.",
      "Inspect retrieved chunks and similarity grades on the Board screen."
    ],
    codePath: "src/mcp_servers/vector_search.py"
  },
  planning: {
    title: "Run Plan",
    tag: "Planning",
    oneLiner: "Manager plans stages before agents execute.",
    explain: [
      "The ADK Manager maps out which tools, profiles, and flows will run for the given notification.",
      "Delegations are posted to the blackboard so each agent knows its exact assignment.",
      "Prevents agents from repeating work or querying tools out of order."
    ],
    codePath: "src/adk_app/pipeline.py"
  }
};

export const UI_COPY = {
  appName: "ReguGuard",
  courseTag: "CSE3101 Agentic AI · BML Munjal University",
  team: "Yash Yadav (230664) · Kartavya Dev (230653) · Nancy (230640)",
  headlineDefault: "Potential regulatory impact detected — human review recommended",
  disclaimer: "Informational summary only. Does not constitute formal legal or tax counsel.",
  screens: {
    flow: { title: "The Flow", subtitle: "Sequential multi-agent pipeline thread." },
    board: { title: "The Board", subtitle: "Shared memory and vector retrieval." },
    gates: { title: "Safety Gates", subtitle: "Deterministic guardrails and attack presets." },
    traces: { title: "Audit Traces", subtitle: "Granular OpenTelemetry spans and provenance." },
    lab: { title: "Benchmark Lab", subtitle: "Hand-drawn SVG boxplots and comparisons." },
    coverage: { title: "Course Coverage", subtitle: "The 11 professor criteria status." },
    concepts: { title: "Concept Index", subtitle: "Plain definitions and source file links." }
  }
};
