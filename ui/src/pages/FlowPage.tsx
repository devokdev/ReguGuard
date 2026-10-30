import React, { useState, useEffect } from 'react';
import { FlowThread } from '../components/FlowThread';
import { BlackboardStrip, BlackboardNote } from '../components/BlackboardStrip';
import { ReportNote, ReportData } from '../components/ReportNote';
import { ExplainDrawer } from '../components/ExplainDrawer';
import { RegulatoryComparisonVisualizer } from '../components/RegulatoryComparisonVisualizer';

interface SME {
  sme_id: string;
  name: string;
  industry: string;
  aato_crore: number;
  einvoice_enabled: boolean;
  gst_registration: string;
}

interface Doc {
  doc_id: string;
  title: string;
  doc_date: string;
  effective_date?: string;
  synthetic?: boolean;
  description?: string;
}

export const FlowPage: React.FC = () => {
  const [smes, setSmes] = useState<SME[]>([]);
  const [docs, setDocs] = useState<Doc[]>([]);
  const [selectedSmeId, setSelectedSmeId] = useState<string>('SME-01');
  const [selectedDocId, setSelectedDocId] = useState<string>('notif_10_2023');

  const [selectedConcept, setSelectedConcept] = useState<string | null>(null);
  const [stageIndex, setStageIndex] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>('Select inputs and run the multi-agent pipeline.');
  const [notes, setNotes] = useState<BlackboardNote[]>([]);
  const [report, setReport] = useState<ReportData | null>(null);

  useEffect(() => {
    fetch('/api/smes')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setSmes(data);
          if (data.length > 0) setSelectedSmeId(data[0].sme_id);
        }
      })
      .catch((err) => console.error('Failed to load SMEs:', err));

    fetch('/api/documents')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setDocs(data);
          const viable = data.filter((d) => d.doc_id !== 'notif_13_2020');
          if (viable.length > 0) setSelectedDocId(viable[0].doc_id);
        }
      })
      .catch((err) => console.error('Failed to load Docs:', err));
  }, []);

  const handleRunPipeline = async () => {
    setIsRunning(true);
    setReport(null);
    setNotes([]);
    setStageIndex(0);
    setStatusMessage('Triggering ADK Manager & sequential agents...');

    const caseId = `CASE-${selectedDocId}-${selectedSmeId}-${Date.now().toString().slice(-4)}`;

    const eventSource = new EventSource(`/api/runs/${caseId}/events`);
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setStageIndex(data.index);
        setStatusMessage(data.label);

        const agentMap: Record<string, string> = {
          0: 'Monitor',
          1: 'Gate',
          2: 'Manager',
          3: 'ChangeDetection',
          4: 'SMEProfile',
          5: 'ImpactAnalysis',
          6: 'EvidenceCrew',
          7: 'ActionCrew'
        };
        const keyMap: Record<string, string> = {
          0: 'inbox_event',
          1: 'sanitized_query',
          2: 'run_plan',
          3: 'clause_diff',
          4: 'sme_financials',
          5: 'impact_verdict',
          6: 'verified_evidence',
          7: 'compliance_action'
        };

        if (data.index < 8) {
          setNotes((prev) => [
            ...prev,
            {
              id: `${data.index}-${Date.now()}`,
              key: keyMap[data.index] || 'entry',
              agent: agentMap[data.index] || 'Agent',
              version: 1,
              snippet: data.label.split(':')[1]?.trim() || 'Computed state'
            }
          ]);
        }
      } catch (err) {
        console.error('SSE parse error:', err);
      }
    };

    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: caseId,
          doc_id: selectedDocId,
          prior_doc_id: 'notif_13_2020',
          sme_id: selectedSmeId,
          config: {
            persona: 'owner'
          }
        })
      });

      if (!response.ok) throw new Error('API execution failed');
      const finalReport = await response.json();

      setTimeout(() => {
        setReport(finalReport);
        setStageIndex(8);
        setIsRunning(false);
        setStatusMessage('Sequential pipeline completed with verified citations.');
        eventSource.close();
      }, 3500);

    } catch (err) {
      console.error('Run failed:', err);
      setStatusMessage('Error executing pipeline.');
      setIsRunning(false);
      eventSource.close();
    }
  };

  const selectedSme = smes.find((s) => s.sme_id === selectedSmeId);

  return (
    <main style={{ maxWidth: '1280px', margin: '0 auto', padding: '32px' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        paddingBottom: '20px',
        borderBottom: 'var(--border-rule)',
        marginBottom: '28px',
      }}>
        <div>
          <span className="small-caps" style={{ color: 'var(--color-accent)' }}>
            Coursework Demonstration / CSE3101 Agentic AI
          </span>
          <h1 style={{ fontSize: '32px', marginTop: '4px' }}>
            ReguGuard Multi-Agent Impact Analyzer
          </h1>
          <p style={{ fontSize: '13px', color: 'var(--color-muted)', marginTop: '4px' }}>
            Status: <span className="mono" style={{ color: isRunning ? 'var(--color-accent)' : 'var(--color-ink)' }}>{statusMessage}</span>
          </p>
        </div>

        <button
          onClick={handleRunPipeline}
          disabled={isRunning}
          style={{
            padding: '10px 24px',
            backgroundColor: isRunning ? 'var(--color-muted)' : 'var(--color-ink)',
            color: 'var(--color-paper)',
            fontSize: '13px',
            fontFamily: 'var(--font-mono)',
            borderRadius: 'var(--radius-sm)',
            cursor: isRunning ? 'not-allowed' : 'pointer',
            boxShadow: '0 2px 6px rgba(0,0,0,0.06)',
            transition: 'background-color var(--motion-fast) var(--ease-out)',
          }}
        >
          {isRunning ? '⏳ Running Agents...' : '▶ Run Live Multi-Agent Pipeline'}
        </button>
      </div>

      {/* Simplified Inputs: Fixed Architecture */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1.2fr 1.2fr 2fr',
        gap: '24px',
        padding: '20px',
        backgroundColor: 'var(--color-surface)',
        border: 'var(--border-rule)',
        borderRadius: 'var(--radius-sm)',
        marginBottom: '32px',
      }}>
        <div>
          <label className="small-caps" style={{ display: 'block', marginBottom: '6px' }}>
            01. Select Indian SME
          </label>
          <select
            value={selectedSmeId}
            onChange={(e) => setSelectedSmeId(e.target.value)}
            disabled={isRunning}
            style={{
              width: '100%',
              padding: '8px 10px',
              backgroundColor: 'var(--color-paper)',
              border: 'var(--border-rule)',
              borderRadius: 'var(--radius-sm)',
              fontFamily: 'var(--font-sans)',
              fontSize: '13px',
            }}
          >
            {smes.map((s) => (
              <option key={s.sme_id} value={s.sme_id}>
                {s.sme_id}: {s.name} (₹{s.aato_crore} Cr)
              </option>
            ))}
          </select>
          {selectedSme && (
            <div className="mono" style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '6px' }}>
              Turnover: ₹{selectedSme.aato_crore} Cr · E-inv: {selectedSme.einvoice_enabled ? 'ON' : 'OFF'} · {selectedSme.gst_registration}
            </div>
          )}
        </div>

        <div>
          <label className="small-caps" style={{ display: 'block', marginBottom: '6px' }}>
            02. Target Notification
          </label>
          <select
            value={selectedDocId}
            onChange={(e) => setSelectedDocId(e.target.value)}
            disabled={isRunning}
            style={{
              width: '100%',
              padding: '8px 10px',
              backgroundColor: 'var(--color-paper)',
              border: 'var(--border-rule)',
              borderRadius: 'var(--radius-sm)',
              fontFamily: 'var(--font-sans)',
              fontSize: '13px',
            }}
          >
            {docs
              .filter((d) => d.doc_id !== 'notif_13_2020')
              .map((d) => (
                <option key={d.doc_id} value={d.doc_id}>
                  {d.title || d.doc_id}
                </option>
              ))}
          </select>
          {docs.find((d) => d.doc_id === selectedDocId)?.description && (
            <div className="mono" style={{ fontSize: '11px', color: 'var(--color-accent)', marginTop: '6px' }}>
              ℹ {docs.find((d) => d.doc_id === selectedDocId)?.description}
            </div>
          )}
          <div className="mono" style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '4px' }}>
            Base comparison law: notif_13_2020 (500 Cr base gazette)
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <span className="small-caps" style={{ display: 'block', marginBottom: '4px' }}>
            Fixed System Architecture (PRD §5.3)
          </span>
          <div style={{ fontSize: '12px', color: 'var(--color-muted)', lineHeight: 1.5 }}>
            <strong>Messaging:</strong> Blackboard (SQLite) · <strong>Topology:</strong> Fixed Sequential · <strong>Reasoning:</strong> ReAct
          </div>
          <div className="mono" style={{ fontSize: '10px', color: 'var(--color-accent)', marginTop: '4px' }}>
            Offline benchmark comparisons (P2P, Parallel, Single-shot) preserved in eval/
          </div>
        </div>
      </div>

      <FlowThread
        currentStageIndex={stageIndex}
        onSelectConcept={(conceptKey) => setSelectedConcept(conceptKey)}
        reflectionCount={stageIndex >= 6 ? 1 : 0}
      />

      <BlackboardStrip
        notes={notes}
      />

      {report && (
        <>
          <ReportNote report={report} />
          <RegulatoryComparisonVisualizer
            report={report}
            selectedSme={selectedSme}
            selectedDocId={selectedDocId}
            allSmes={smes}
          />
        </>
      )}

      <ExplainDrawer
        conceptKey={selectedConcept}
        onClose={() => setSelectedConcept(null)}
      />
    </main>
  );
};
