import React from 'react';

interface Criterion {
  num: number;
  title: string;
  desc: string;
  status: 'MET' | 'PREPARED' | 'PARTIAL';
  evidence: string;
  test: string;
}

export const CoveragePage: React.FC = () => {
  const criteria: Criterion[] = [
    { num: 1, title: 'Blackboard Architecture', desc: 'Shared state mandatory; comparison against P2P messaging.', status: 'MET', evidence: 'src/blackboard/store.py', test: 'tests/test_blackboard.py' },
    { num: 2, title: 'External Tools via MCP', desc: '6 FastMCP tool servers + blackboard server.', status: 'MET', evidence: 'src/mcp_servers/', test: 'tests/test_mcp_tools.py' },
    { num: 3, title: 'Structured Output via Pydantic', desc: 'Pydantic v2 ImpactReport with deterministic business rules.', status: 'MET', evidence: 'src/schemas.py', test: 'tests/test_schemas.py' },
    { num: 4, title: 'Agentic Patterns Compared', desc: 'Sequential ReAct production pipeline compared offline with Parallel & P2P.', status: 'MET', evidence: 'src/adk_app/pipeline.py', test: 'tests/test_step9_topologies.py' },
    { num: 5, title: 'Callbacks & Heatmaps', desc: 'Lifecycle monitoring spans & agent access heatmaps.', status: 'MET', evidence: 'src/observability/callbacks.py', test: 'tests/test_step4_adk.py' },
    { num: 6, title: 'A2A Cross-Framework', desc: 'ADK remote client calling CrewAI Flow via Agent Card.', status: 'MET', evidence: 'src/crew_app/flow.py', test: 'tests/test_step5_a2a.py' },
    { num: 7, title: 'Framework Restrictions', desc: 'Google ADK + CrewAI only; no unauthorized frameworks.', status: 'MET', evidence: 'Architecture Audit', test: 'Full Repo Audit' },
    { num: 8, title: 'Guardrails & Safety', desc: '3-layer deterministic safety, PII masking (GSTIN/PAN).', status: 'MET', evidence: 'src/guardrails/engine.py', test: 'tests/test_step7_guardrails.py' },
    { num: 9, title: 'Observability & Provenance', desc: 'Trace IDs, DAG Provenance Graph, JSON/Markdown audit packs.', status: 'MET', evidence: 'src/observability/provenance.py', test: 'tests/test_steps11_12.py' },
    { num: 10, title: 'End-to-End Evaluation', desc: '48 labelled cases, 6 configs, 288 runs, boxplots & metrics.', status: 'MET', evidence: 'eval/run_benchmark.py', test: 'data/eval/' },
    { num: 11, title: 'Cloud Deployment', desc: 'Production Docker container with Supervisord for Google Cloud Run.', status: 'PREPARED', evidence: 'Dockerfile & cloudrun.sh', test: 'deploy/' }
  ];

  return (
    <main style={{ maxWidth: '1280px', margin: '0 auto', padding: '32px' }}>
      <div style={{ paddingBottom: '20px', borderBottom: 'var(--border-rule)', marginBottom: '28px' }}>
        <span className="small-caps" style={{ color: 'var(--color-accent)' }}>
          Rubric C8 Verification / 11 Criteria
        </span>
        <h1 style={{ fontSize: '32px', marginTop: '4px' }}>
          Professor Evaluation Matrix
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--color-muted)' }}>
          Comprehensive evidence mapping verifying each of the 11 course criteria.
        </p>
      </div>

      <div style={{
        backgroundColor: 'var(--color-surface)',
        border: 'var(--border-rule)',
        borderRadius: 'var(--radius-sm)',
        overflow: 'hidden',
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: 'var(--border-rule)', backgroundColor: 'var(--color-surface-hover)', textAlign: 'left' }}>
              <th style={{ padding: '12px 16px', width: '50px' }}>#</th>
              <th style={{ padding: '12px 16px' }}>Criterion</th>
              <th style={{ padding: '12px 16px' }}>Requirement & Implementation</th>
              <th style={{ padding: '12px 16px' }}>Status</th>
              <th style={{ padding: '12px 16px' }}>Code File</th>
              <th style={{ padding: '12px 16px' }}>Verification Test</th>
            </tr>
          </thead>
          <tbody>
            {criteria.map((c) => (
              <tr key={c.num} style={{ borderBottom: '1px solid var(--color-rule-light)' }}>
                <td className="mono" style={{ padding: '12px 16px', fontWeight: 600 }}>{c.num}</td>
                <td style={{ padding: '12px 16px', fontWeight: 500 }}>{c.title}</td>
                <td style={{ padding: '12px 16px', color: 'var(--color-muted)', fontSize: '12px' }}>{c.desc}</td>
                <td style={{ padding: '12px 16px' }}>
                  <span className="mono" style={{
                    fontSize: '11px',
                    padding: '3px 8px',
                    borderRadius: '2px',
                    fontWeight: 600,
                    backgroundColor: c.status === 'MET' ? 'var(--color-ok)' : 'var(--color-crewai)',
                    color: '#fff',
                  }}>
                    {c.status}
                  </span>
                </td>
                <td className="mono" style={{ padding: '12px 16px', fontSize: '11px' }}>{c.evidence}</td>
                <td className="mono" style={{ padding: '12px 16px', fontSize: '11px', color: 'var(--color-accent)' }}>{c.test}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
};

