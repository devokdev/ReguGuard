import React from 'react';
import { UI_COPY } from '../copy';

export const Footer: React.FC = () => {
  return (
    <footer style={{
      borderTop: 'var(--border-rule)',
      backgroundColor: 'var(--color-surface)',
      padding: '16px 32px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      fontSize: '12px',
      color: 'var(--color-muted)',
      marginTop: 'auto',
    }}>
      <div>
        <span>{UI_COPY.disclaimer}</span>
      </div>
      <div style={{ display: 'flex', gap: '20px' }}>
        <span className="mono">{UI_COPY.team}</span>
      </div>
    </footer>
  );
};

