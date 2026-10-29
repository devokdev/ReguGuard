import React, { useState, useEffect } from 'react';

interface TraceSpan {
  trace_id: string;
  span_id: string;
  parent_span_id?: string;
  agent: string;
  framework: string;
  kind: string;
  latency_ms: number;
  tokens_in: number;
  tokens_out: number;
  cost_usd: number;
  payload_preview: string;
  status: string;
  ts_start: string;
}

export const TracesPage: React.FC = () => {
  const [traceId, setTraceId] = useState<string>('trace-test-564d7c');
  const [spans, setSpans] = useState<TraceSpan[]>([]);
  const [selectedSpan, setSelectedSpan] = useState<TraceSpan | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchSpans = (id: string) => {
    setLoading(true);
    fetch(`/api/traces/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setSpans(data);
          if (data.length > 0) setSelectedSpan(data[0]);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load spans:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchSpans(traceId);
  }, []);

  const maxLatency = Math.max(...spans.map((s) => s.latency_ms), 10);

  return (
    <main style={{ maxWidth: '1280px', margin: '0 auto', padding: '32px' }}>
      <div style={{ paddingBottom: '20px', borderBottom: 'var(--border-rule)', marginBottom: '28px' }}>
        <span className="small-caps" style={{ color: 'var(--color-accent)' }}>
          Observability / Course Criterion 5 & 9
        </span>
        <h1 style={{ fontSize: '32px', marginTop: '4px' }}>
          Trace Explorer & Span Waterfall
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--color-muted)' }}>
          OpenTelemetry-style execution spans tracking agent latencies and tool boundaries.
        </p>
      </div>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '32px' }}>
        <input
          type="text"
          value={traceId}
          onChange={(e) => setTraceId(e.target.value)}
          placeholder="Enter Trace ID"
          style={{
            flex: 1,
            padding: '10px 14px',
            backgroundColor: 'var(--color-surface)',
            border: 'var(--border-rule)',
            borderRadius: 'var(--radius-sm)',
            fontFamily: 'var(--font-mono)',
            fontSize: '13px',
          }}
        />
        <button
          onClick={() => fetchSpans(traceId)}
          style={{
            padding: '10px 20px',
            backgroundColor: 'var(--color-ink)',
            color: 'var(--color-paper)',
            borderRadius: 'var(--radius-sm)',
            fontSize: '13px',
            fontFamily: 'var(--font-mono)',
          }}
        >
          {loading ? 'Fetching...' : 'Load Spans'}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '32px' }}>
        {/* Waterfall List */}
        <div>
          <span className="small-caps" style={{ display: 'block', marginBottom: '12px' }}>
            Span Waterfall ({spans.length} Recorded Spans)
          </span>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {spans.map((s) => {
              const barWidth = Math.max((s.latency_ms / maxLatency) * 100, 4);
              const isSelected = selectedSpan?.span_id === s.span_id;

              return (
                <div
                  key={s.span_id}
                  onClick={() => setSelectedSpan(s)}
                  style={{
                    padding: '10px 14px',
                    backgroundColor: isSelected ? 'var(--color-surface)' : 'var(--color-paper)',
                    border: isSelected ? '1px solid var(--color-ink)' : 'var(--border-rule)',
                    borderRadius: 'var(--radius-sm)',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'baseline' }}>
                      <span className="mono" style={{ fontSize: '11px', color: 'var(--color-accent)' }}>
                        {s.agent}
                      </span>
                      <span className="small-caps mono" style={{ fontSize: '10px' }}>
                        [{s.kind}]
                      </span>
                    </div>
                    <span className="mono" style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
                      {s.latency_ms.toFixed(1)} ms
                    </span>
                  </div>

                  {/* Latency Bar */}
                  <div style={{
                    width: '100%',
                    height: '4px',
                    backgroundColor: 'var(--color-rule-light)',
                    borderRadius: '2px',
                    overflow: 'hidden',
                  }}>
                    <div style={{
                      width: `${barWidth}%`,
                      height: '100%',
                      backgroundColor: s.framework === 'crewai' ? 'var(--color-crewai)' : 'var(--color-adk)',
                    }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Span Details */}
        <div>
          <span className="small-caps" style={{ display: 'block', marginBottom: '12px' }}>
            Span Detail Inspector
          </span>

          {selectedSpan ? (
            <div style={{
              padding: '24px',
              backgroundColor: 'var(--color-surface)',
              border: 'var(--border-rule)',
              borderRadius: 'var(--radius-sm)',
            }}>
              <h3 style={{ fontSize: '20px', marginBottom: '8px' }}>
                {selectedSpan.agent}
              </h3>
              <div className="mono" style={{ fontSize: '12px', color: 'var(--color-muted)', marginBottom: '16px' }}>
                Span: {selectedSpan.span_id} · Framework: {selectedSpan.framework.toUpperCase()}
              </div>

              <div style={{ fontSize: '13px', lineHeight: 1.8, marginBottom: '16px' }}>
                <div><strong>Kind:</strong> {selectedSpan.kind}</div>
                <div><strong>Latency:</strong> {selectedSpan.latency_ms.toFixed(2)} ms</div>
                <div><strong>Tokens:</strong> In {selectedSpan.tokens_in} / Out {selectedSpan.tokens_out}</div>
                <div><strong>Status:</strong> {selectedSpan.status.toUpperCase()}</div>
              </div>

              <span className="small-caps" style={{ display: 'block', marginBottom: '6px' }}>Payload Preview</span>
              <pre className="mono" style={{
                fontSize: '11px',
                padding: '10px',
                backgroundColor: 'var(--color-paper)',
                border: 'var(--border-rule)',
                borderRadius: 'var(--radius-sm)',
                overflowX: 'auto',
                maxHeight: '180px',
              }}>
                {selectedSpan.payload_preview}
              </pre>
            </div>
          ) : (
            <div style={{
              padding: '24px',
              backgroundColor: 'var(--color-surface)',
              border: 'var(--border-rule)',
              color: 'var(--color-muted)',
              textAlign: 'center',
            }}>
              Select a span from the waterfall to inspect telemetry.
            </div>
          )}
        </div>
      </div>
    </main>
  );
};

