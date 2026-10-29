import React, { useState, useEffect } from 'react';

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
  const [entries, setEntries] = useState<BlackboardEntry[]>([]);
  const [accessMatrix, setAccessMatrix] = useState<Record<string, Record<string, { reads: number; writes: number }>>>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchHistory = (id: string) => {
    setIsLoading(true);
    fetch(`/api/blackboard/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setEntries(data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch blackboard:', err);
        setIsLoading(false);
      });
  };

  useEffect(() => {
    fetchHistory(caseId);
    fetch('/api/heatmaps/blackboard-access')
      .then((res) => res.json())
      .then((data) => setAccessMatrix(data))
      .catch((err) => console.error('Failed to load matrix:', err));
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
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '32px' }}>
        {/* Versioned Entries List */}
        <div>
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
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
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
                    padding: '8px 10px',
                    borderRadius: 'var(--radius-sm)',
                    overflowX: 'auto',
                    maxHeight: '120px',
                  }}>
                    {typeof e.value === 'object' ? JSON.stringify(e.value, null, 2) : String(e.value)}
                  </pre>
                  <div className="mono" style={{ fontSize: '10px', color: 'var(--color-muted)', marginTop: '6px' }}>
                    {e.ts}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Access Frequency Matrix */}
        <div>
          <span className="small-caps" style={{ display: 'block', marginBottom: '12px' }}>
            Agent Access Matrix (Criterion 5 Heatmap)
          </span>
          <div style={{
            padding: '16px',
            backgroundColor: 'var(--color-surface)',
            border: 'var(--border-rule)',
            borderRadius: 'var(--radius-sm)',
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ borderBottom: 'var(--border-rule)', textAlign: 'left' }}>
                  <th style={{ padding: '8px' }}>Agent</th>
                  <th style={{ padding: '8px' }}>Key</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>Reads</th>
                  <th style={{ padding: '8px', textAlign: 'right' }}>Writes</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(accessMatrix).flatMap(([agent, keys]) =>
                  Object.entries(keys).map(([key, counts]) => (
                    <tr key={`${agent}-${key}`} style={{ borderBottom: '1px solid var(--color-rule-light)' }}>
                      <td className="mono" style={{ padding: '6px 8px', color: 'var(--color-ink)' }}>{agent}</td>
                      <td className="mono" style={{ padding: '6px 8px', color: 'var(--color-muted)' }}>{key}</td>
                      <td className="mono" style={{ padding: '6px 8px', textAlign: 'right' }}>{counts.reads}</td>
                      <td className="mono" style={{ padding: '6px 8px', textAlign: 'right', fontWeight: 600, color: 'var(--color-accent)' }}>{counts.writes}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
};

