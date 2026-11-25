import React, { useState, useEffect } from 'react';
import fallbackEntries from '../data/fallback_blackboard.json';
import fallbackMatrix from '../data/fallback_access_matrix.json';

interface BlackboardEntry {
  id: number;
  case_id: string;
  key: string;
  value: any;
  agent: string;
  version: number;
  ts: string;
  trace_id?: string;
}

export const BoardPage: React.FC = () => {
  const [caseId, setCaseId] = useState<string>('CASE-STEP5-A2A');
  const [entries, setEntries] = useState<BlackboardEntry[]>(fallbackEntries as BlackboardEntry[]);
  const [accessMatrix, setAccessMatrix] = useState<Record<string, Record<string, { reads: number; writes: number }>>>(fallbackMatrix as any);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchHistory = (id: string) => {
    setIsLoading(true);
    fetch(`/api/blackboard/${id}`)
      .then((res) => {
        const contentType = res.headers.get('content-type');
        if (res.ok && contentType && contentType.includes('application/json')) {
          return res.json();
        }
        return null;
      })
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) setEntries(data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.warn('Using fallback blackboard history:', err);
        setIsLoading(false);
      });
  };

  useEffect(() => {
    fetchHistory(caseId);
    fetch('/api/heatmaps/blackboard-access')
      .then((res) => {
        const contentType = res.headers.get('content-type');
        if (res.ok && contentType && contentType.includes('application/json')) {
          return res.json();
        }
        return null;
      })
      .then((data) => {
        if (data && Object.keys(data).length > 0) setAccessMatrix(data);
      })
      .catch((err) => console.warn('Using fallback matrix:', err));
  }, []);

  return (
    <main style={{ maxWidth: '1280px', margin: '0 auto', padding: '32px' }}>
      <div style={{ paddingBottom: '20px', borderBottom: 'var(--border-rule)', marginBottom: '28px' }}>
        <span className="small-caps" style={{ color: 'var(--color-accent)' }}>
          Shared State / Course Criterion 1
        </span>
        <h1 style={{ fontSize: '32px', marginTop: '4px' }}>
          Blackboard History & Access Matrix
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--color-muted)' }}>
          Every write increments versioning; reads are tracked across agents for full audit trails.
        </p>
      </div>

      {/* Case Query Input */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '32px' }}>
        <input
          type="text"
          value={caseId}
          onChange={(e) => setCaseId(e.target.value)}
          placeholder="Enter Case ID e.g., CASE-notif_10_2023-SME-01"
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
          onClick={() => fetchHistory(caseId)}
          style={{
            padding: '10px 20px',
            backgroundColor: 'var(--color-ink)',
            color: 'var(--color-paper)',
            borderRadius: 'var(--radius-sm)',
            fontSize: '13px',
            fontFamily: 'var(--font-mono)',
          }}
        >
          {isLoading ? 'Querying...' : 'Inspect Case History'}
        </button>
      </div>

      {/* Dual Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(360px, 1fr)', gap: '32px', alignItems: 'start' }}>
        {/* Versioned Entries List */}
        <div style={{ minWidth: 0 }}>
          <span className="small-caps" style={{ display: 'block', marginBottom: '12px' }}>
            Versioned Audit Timeline ({entries.length} Entries)
          </span>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {entries.length === 0 ? (
              <div style={{
                padding: '24px',
                textAlign: 'center',
                backgroundColor: 'var(--color-surface)',
                border: 'var(--border-rule)',
                color: 'var(--color-muted)',
              }}>
                No entries found for {caseId}. Run a pipeline from the Flow screen first!
              </div>
            ) : (
              entries.map((e) => (
                <div key={e.id} style={{
                  padding: '16px',
                  backgroundColor: 'var(--color-surface)',
                  border: 'var(--border-rule)',
                  borderRadius: 'var(--radius-sm)',
                  overflow: 'hidden',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'baseline' }}>
                      <span className="small-caps mono" style={{ color: 'var(--color-accent)' }}>
                        v{e.version}
                      </span>
                      <strong style={{ fontSize: '13px' }}>{e.key}</strong>
                    </div>
                    <span className="mono" style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
                      Written by: {e.agent}
                    </span>
                  </div>

                  <pre className="mono" style={{
                    fontSize: '11px',
                    backgroundColor: 'var(--color-paper)',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-sm)',
                    overflowX: 'auto',
                    overflowY: 'auto',
                    maxHeight: '180px',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    lineHeight: '1.45',
                    border: '1px solid var(--color-rule-light)',
                  }}>
                    {typeof e.value === 'object' ? JSON.stringify(e.value, null, 2) : String(e.value)}
                  </pre>
                  <div className="mono" style={{ fontSize: '10px', color: 'var(--color-muted)', marginTop: '8px' }}>
                    {e.ts}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Access Frequency Matrix (Sticky Sidebar with max-height scroll) */}
        <div style={{ position: 'sticky', top: '24px', minWidth: 0 }}>
          <span className="small-caps" style={{ display: 'block', marginBottom: '12px' }}>
            Agent Access Matrix (Criterion 5 Heatmap)
          </span>
          <div style={{
            backgroundColor: 'var(--color-surface)',
            border: 'var(--border-rule)',
            borderRadius: 'var(--radius-sm)',
            overflow: 'hidden',
          }}>
            <div style={{ maxHeight: 'calc(100vh - 180px)', overflowY: 'auto', padding: '12px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--color-ink)', textAlign: 'left', position: 'sticky', top: 0, backgroundColor: 'var(--color-surface)' }}>
                    <th style={{ padding: '8px 6px' }}>Agent</th>
                    <th style={{ padding: '8px 6px' }}>Key</th>
                    <th style={{ padding: '8px 6px', textAlign: 'right' }}>Reads</th>
                    <th style={{ padding: '8px 6px', textAlign: 'right' }}>Writes</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(accessMatrix).flatMap(([agent, keys]) =>
                    Object.entries(keys).map(([key, counts]) => (
                      <tr key={`${agent}-${key}`} style={{ borderBottom: '1px solid var(--color-rule-light)' }}>
                        <td className="mono" style={{ padding: '6px', color: 'var(--color-ink)', fontSize: '11px', whiteSpace: 'nowrap' }}>{agent}</td>
                        <td className="mono" style={{ padding: '6px', color: 'var(--color-muted)', fontSize: '11px' }}>{key}</td>
                        <td className="mono" style={{ padding: '6px', textAlign: 'right', fontSize: '11px' }}>{counts.reads}</td>
                        <td className="mono" style={{ padding: '6px', textAlign: 'right', fontWeight: 600, color: 'var(--color-accent)', fontSize: '11px' }}>{counts.writes}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
};

