import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CONCEPTS, ConceptDefinition } from '../copy';

interface ExplainDrawerProps {
  conceptKey: string | null;
  onClose: () => void;
  stageData?: Record<string, any>;
}

export const ExplainDrawer: React.FC<ExplainDrawerProps> = ({ conceptKey, onClose, stageData }) => {
  const concept: ConceptDefinition | undefined = conceptKey ? CONCEPTS[conceptKey] : undefined;

  return (
    <AnimatePresence>
      {concept && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.25 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              inset: 0,
              backgroundColor: 'var(--color-ink)',
              zIndex: 100,
            }}
          />

          {/* Drawer Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
            style={{
              position: 'fixed',
              top: 0,
              right: 0,
              bottom: 0,
              width: '420px',
              maxWidth: '90vw',
              backgroundColor: 'var(--color-paper)',
              borderLeft: 'var(--border-rule)',
              boxShadow: '-4px 0 24px rgba(0,0,0,0.06)',
              zIndex: 101,
              padding: '32px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '24px' }}>
                <span className="small-caps" style={{ color: 'var(--color-accent)' }}>
                  Explain / Concept Note
                </span>
                <button
                  onClick={onClose}
                  style={{ fontSize: '13px', color: 'var(--color-muted)', padding: '4px 8px' }}
                >
                  [ Close ]
                </button>
              </div>

              <h2 style={{ fontSize: '28px', marginBottom: '8px' }}>
                {concept.title}
              </h2>

              <p style={{
                fontSize: '15px',
                fontStyle: 'italic',
                fontFamily: 'var(--font-serif)',
                color: 'var(--color-muted)',
                marginBottom: '24px',
                paddingBottom: '16px',
                borderBottom: 'var(--border-rule)',
              }}>
                "{concept.oneLiner}"
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '32px' }}>
                {concept.explain.map((sentence, idx) => (
                  <div key={idx} style={{ display: 'flex', gap: '12px' }}>
                    <span className="mono" style={{ fontSize: '12px', color: 'var(--color-accent)' }}>
                      0{idx + 1}
                    </span>
                    <p style={{ fontSize: '13px', lineHeight: 1.6 }}>{sentence}</p>
                  </div>
                ))}
              </div>

              {stageData && Object.keys(stageData).length > 0 && (
                <div style={{ marginTop: '24px' }}>
                  <span className="small-caps" style={{ display: 'block', marginBottom: '8px' }}>
                    Observed Stage Payload
                  </span>
                  <pre className="mono" style={{
                    fontSize: '11px',
                    backgroundColor: 'var(--color-surface)',
                    padding: '12px',
                    border: 'var(--border-rule)',
                    borderRadius: 'var(--radius-sm)',
                    overflowX: 'auto',
                    maxHeight: '180px',
                  }}>
                    {JSON.stringify(stageData, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div style={{
              paddingTop: '16px',
              borderTop: 'var(--border-rule)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
            }}>
              <span className="small-caps">Implementation File:</span>
              <span className="mono" style={{ fontSize: '12px', color: 'var(--color-ink)' }}>
                {concept.codePath}
              </span>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

