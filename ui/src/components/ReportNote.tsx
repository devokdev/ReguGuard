import React from 'react';
import { UI_COPY } from '../copy';

export interface ReportData {
  case_id: string;
  trace_id: string;
  sme_id: string;
  headline: string;
  verdict: {
    verdict: string;
    confidence: number;
    reasoning_summary: string;
  };
  evidence: Array<{
    section: string;
    quote: string;
    source_doc_id: string;
    verified: boolean;
  }>;
  action?: {
    action: string;
    owner: string;
    deadline?: string;
    priority: string;
  };
  metrics: {
    total_latency_s: number;
    total_tokens: number;
  };
}

interface ReportNoteProps {
  report: ReportData;
}

export const ReportNote: React.FC<ReportNoteProps> = ({ report }) => {
  const isImpacted = report.verdict.verdict === 'impacted';

  return (
    <div style={{
      marginTop: '40px',
      backgroundColor: 'var(--color-surface)',
      border: 'var(--border-rule)',
      borderRadius: 'var(--radius-sm)',
      padding: '32px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.03)',
    }}>
      {/* Top Banner Notice */}
      <div style={{
        paddingBottom: '16px',
        borderBottom: 'var(--border-rule)',
        marginBottom: '24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'baseline',
      }}>
        <span className="small-caps" style={{ color: 'var(--color-accent)', fontWeight: 600 }}>
          {report.headline}
        </span>
        <span className="mono" style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
          Trace: {report.trace_id}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
        {/* Left Column: Verdict & Narrative */}
        <div>
          <span className="small-caps">Assessed Verdict</span>
          <div style={{
            fontSize: '44px',
            fontFamily: 'var(--font-serif)',
            color: isImpacted ? 'var(--color-accent)' : 'var(--color-ink)',
            textTransform: 'capitalize',
            lineHeight: 1.1,
            margin: '8px 0 16px',
          }}>
            {report.verdict.verdict.replace('_', ' ')}
          </div>

          <p style={{ fontSize: '14px', lineHeight: 1.6, marginBottom: '24px' }}>
            {report.verdict.reasoning_summary}
          </p>

          {/* Evidence Quotes */}
          {report.evidence.length > 0 && (
            <div>
              <span className="small-caps" style={{ display: 'block', marginBottom: '8px' }}>
                Grounded Citations (Substring Verified)
              </span>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {report.evidence.map((ev, i) => (
                  <div key={i} style={{
                    borderLeft: '2px solid var(--color-ok)',
                    paddingLeft: '12px',
                    fontStyle: 'italic',
                    fontFamily: 'var(--font-serif)',
                    fontSize: '13px',
                  }}>
                    "{ev.quote}"
                    <span className="mono" style={{
                      display: 'block',
                      fontStyle: 'normal',
                      fontSize: '11px',
                      color: 'var(--color-muted)',
                      marginTop: '4px',
                    }}>
                      — {ev.section} ({ev.source_doc_id}) · Verified Substring
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Prescription & Metrics */}
        <div style={{
          borderLeft: 'var(--border-rule)',
          paddingLeft: '24px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
        }}>
          {report.action && (
            <div>
              <span className="small-caps">Recommended Action</span>
              <p style={{ fontWeight: 500, fontSize: '13px', marginTop: '6px', marginBottom: '12px' }}>
                {report.action.action}
              </p>
              <div style={{ fontSize: '12px', color: 'var(--color-muted)', lineHeight: 1.8 }}>
                <div><strong>Owner:</strong> {report.action.owner}</div>
                <div><strong>Deadline:</strong> {report.action.deadline || 'Immediate'}</div>
                <div><strong>Priority:</strong> {report.action.priority.toUpperCase()}</div>
              </div>
            </div>
          )}

          <div style={{
            paddingTop: '20px',
            borderTop: 'var(--border-rule)',
            marginTop: '20px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span className="small-caps">Confidence</span>
              <span className="mono" style={{ fontSize: '12px' }}>
                {(report.verdict.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div style={{
              width: '100%',
              height: '3px',
              backgroundColor: 'var(--color-rule)',
              borderRadius: '2px',
              overflow: 'hidden',
              marginBottom: '16px',
            }}>
              <div style={{
                width: `${report.verdict.confidence * 100}%`,
                height: '100%',
                backgroundColor: 'var(--color-accent)',
              }} />
            </div>

            <div className="mono" style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
              Latency: {report.metrics.total_latency_s.toFixed(2)}s · Tokens: {report.metrics.total_tokens}
            </div>
          </div>
        </div>
      </div>

      {/* Legal Disclaimer */}
      <div style={{
        marginTop: '24px',
        paddingTop: '16px',
        borderTop: 'var(--border-rule)',
        fontSize: '11px',
        color: 'var(--color-muted)',
      }}>
        {UI_COPY.disclaimer}
      </div>
    </div>
  );
};

