import React, { useState, useEffect } from 'react';

interface Preset {
  name: string;
  layer: string;
  text: string;
  description: string;
}

export const GatesPage: React.FC = () => {
  const [presets, setPresets] = useState<Record<string, Preset>>({});
  const [selectedPresetId, setSelectedPresetId] = useState<string>('injection_direct');
  const [customInput, setCustomInput] = useState<string>('');
  const [testResult, setTestResult] = useState<any | null>(null);
  const [testing, setTesting] = useState<boolean>(false);

  useEffect(() => {
    fetch('/api/guardrails/presets')
      .then((res) => res.json())
      .then((data) => {
        setPresets(data);
        if (data.injection_direct) {
          setCustomInput(data.injection_direct.text);
        }
      })
      .catch((err) => console.error('Failed to load presets:', err));
  }, []);

  const handleSelectPreset = (id: string) => {
    setSelectedPresetId(id);
    if (presets[id]) {
      setCustomInput(presets[id].text);
    }
    setTestResult(null);
  };

  const handleRunTest = async () => {
    setTesting(true);
    try {
      const res = await fetch('/api/guardrails/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preset_id: selectedPresetId, custom_text: customInput }),
      });
      const data = await res.json();
      setTestResult(data);
    } catch (err) {
      console.error('Guardrail test failed:', err);
    } finally {
      setTesting(false);
    }
  };

  return (
    <main style={{ maxWidth: '1280px', margin: '0 auto', padding: '32px' }}>
      <div style={{ paddingBottom: '20px', borderBottom: 'var(--border-rule)', marginBottom: '28px' }}>
        <span className="small-caps" style={{ color: 'var(--color-accent)' }}>
          Safety Layer / Course Criterion 8
        </span>
        <h1 style={{ fontSize: '32px', marginTop: '4px' }}>
          Guardrail Lab & Attack Presets
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--color-muted)' }}>
          Deterministic 3-layer safety tests: prompt injection, toxic input de-escalation, and PII masking.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.6fr', gap: '32px' }}>
        {/* Preset Selector */}
        <div>
          <span className="small-caps" style={{ display: 'block', marginBottom: '12px' }}>
            Select Attack Preset
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {Object.entries(presets).map(([id, p]) => {
              const isSelected = selectedPresetId === id;
              return (
                <button
                  key={id}
                  onClick={() => handleSelectPreset(id)}
                  style={{
                    padding: '14px 16px',
                    textAlign: 'left',
                    backgroundColor: isSelected ? 'var(--color-surface)' : 'var(--color-paper)',
                    border: isSelected ? '1px solid var(--color-ink)' : 'var(--border-rule)',
                    borderRadius: 'var(--radius-sm)',
                    transition: 'all var(--motion-fast) var(--ease-out)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span className="small-caps" style={{ color: 'var(--color-accent)' }}>{p.layer}</span>
                  </div>
                  <strong style={{ fontSize: '13px', display: 'block', marginBottom: '4px' }}>{p.name}</strong>
                  <div style={{ fontSize: '12px', color: 'var(--color-muted)' }}>{p.description}</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Test Console */}
        <div style={{
          padding: '24px',
          backgroundColor: 'var(--color-surface)',
          border: 'var(--border-rule)',
          borderRadius: 'var(--radius-sm)',
        }}>
          <span className="small-caps" style={{ display: 'block', marginBottom: '8px' }}>
            Test Payload Console
          </span>

          <textarea
            value={customInput}
            onChange={(e) => setCustomInput(e.target.value)}
            rows={5}
            style={{
              width: '100%',
              padding: '12px',
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              backgroundColor: 'var(--color-paper)',
              border: 'var(--border-rule)',
              borderRadius: 'var(--radius-sm)',
              marginBottom: '16px',
            }}
          />

          <button
            onClick={handleRunTest}
            disabled={testing}
            style={{
              padding: '10px 24px',
              backgroundColor: 'var(--color-ink)',
              color: 'var(--color-paper)',
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              borderRadius: 'var(--radius-sm)',
            }}
          >
            {testing ? 'Testing Guardrails...' : '⚡ Test Guardrails'}
          </button>

          {/* Verdict Card */}
          {testResult && (
            <div style={{
              marginTop: '24px',
              padding: '20px',
              backgroundColor: 'var(--color-paper)',
              border: 'var(--border-rule)',
              borderRadius: 'var(--radius-sm)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '12px' }}>
                <span className="small-caps">Interception Layer: {testResult.layer}</span>
                <span className="mono" style={{
                  padding: '4px 8px',
                  borderRadius: '2px',
                  backgroundColor: testResult.verdict === 'blocked' ? 'var(--color-blocked)' : 'var(--color-ok)',
                  color: '#fff',
                  fontSize: '11px',
                  fontWeight: 600,
                }}>
                  {testResult.verdict?.toUpperCase()}
                </span>
              </div>

              <div style={{ fontSize: '13px', marginBottom: '12px' }}>
                <strong>Reason:</strong> {testResult.reason}
              </div>

              {testResult.flags && testResult.flags.length > 0 && (
                <div style={{ marginBottom: '12px' }}>
                  <span className="small-caps" style={{ display: 'block', marginBottom: '4px' }}>Flags Triggered:</span>
                  <ul style={{ paddingLeft: '20px', fontSize: '12px', color: 'var(--color-muted)' }}>
                    {testResult.flags.map((f: string, i: number) => <li key={i}>{f}</li>)}
                  </ul>
                </div>
              )}

              <div>
                <span className="small-caps" style={{ display: 'block', marginBottom: '4px' }}>Sanitized Output Passed to Agent:</span>
                <pre className="mono" style={{
                  padding: '10px',
                  backgroundColor: 'var(--color-surface)',
                  border: 'var(--border-rule)',
                  fontSize: '11px',
                  overflowX: 'auto',
                }}>
                  {testResult.sanitized}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
};

