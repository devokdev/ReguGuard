import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export interface BlackboardNote {
  id: string;
  key: string;
  agent: string;
  version: number;
  snippet?: string;
}

interface BlackboardStripProps {
  notes: BlackboardNote[];
}

// CONCEPT: Blackboard Shared State Record Strip (PRD §5.3)
export const BlackboardStrip: React.FC<BlackboardStripProps> = ({ notes }) => {
  return (
    <div style={{
      marginTop: '32px',
      padding: '16px 24px',
      backgroundColor: 'var(--color-surface)',
      border: 'var(--border-rule)',
      borderRadius: 'var(--radius-sm)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span className="small-caps" style={{ fontWeight: 600 }}>
            Shared Blackboard Record
          </span>
          <span className="mono" style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
            (SQLite Versioned State Store)
          </span>
        </div>
        <span className="mono" style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
          {notes.length} entries written
        </span>
      </div>

      <div style={{
        display: 'flex',
        gap: '12px',
        overflowX: 'auto',
        paddingBottom: '8px',
      }}>
        <AnimatePresence>
          {notes.map((note) => (
            <motion.div
              key={note.id}
              initial={{ opacity: 0, y: 8, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              style={{
                minWidth: '160px',
                maxWidth: '220px',
                backgroundColor: 'var(--color-paper)',
                border: 'var(--border-rule)',
                borderRadius: 'var(--radius-sm)',
                padding: '10px 12px',
                flexShrink: 0,
                boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span className="small-caps" style={{ color: 'var(--color-accent)' }}>
                  v{note.version}
                </span>
                <span className="mono" style={{ fontSize: '10px', color: 'var(--color-muted)' }}>
                  {note.agent}
                </span>
              </div>
              <div style={{ fontWeight: 500, fontSize: '12px', marginBottom: '4px' }}>
                {note.key}
              </div>
              {note.snippet && (
                <div style={{
                  fontSize: '11px',
                  color: 'var(--color-muted)',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}>
                  {note.snippet}
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};
