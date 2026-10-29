import React from 'react';
import { UI_COPY } from '../copy';

export type ScreenId = 'flow' | 'board' | 'gates' | 'traces' | 'lab' | 'coverage' | 'concepts';

interface HeaderProps {
  activeScreen: ScreenId;
  onSelectScreen: (screen: ScreenId) => void;
  isRunning?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ activeScreen, onSelectScreen, isRunning }) => {
  const screens: { id: ScreenId; label: string }[] = [
    { id: 'flow', label: 'Flow' },
    { id: 'board', label: 'Board' },
    { id: 'gates', label: 'Gates' },
    { id: 'traces', label: 'Traces' },
    { id: 'lab', label: 'Lab' },
    { id: 'coverage', label: 'Coverage' },
    { id: 'concepts', label: 'Concepts' },
  ];

  return (
    <header style={{
      borderBottom: 'var(--border-rule)',
      backgroundColor: 'var(--color-surface)',
      padding: '12px 32px',
      display: 'flex',
      alignItems: 'baseline',
      justifyContent: 'space-between',
    }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span style={{
            fontFamily: 'var(--font-serif)',
            fontSize: '22px',
            fontWeight: 400,
            letterSpacing: '-0.02em',
          }}>
            {UI_COPY.appName}
          </span>
          <span className="small-caps" style={{ color: 'var(--color-muted)' }}>
            / Regulatory Impact
          </span>
        </div>

        <nav style={{ display: 'flex', gap: '18px' }}>
          {screens.map((s) => {
            const isActive = activeScreen === s.id;
            return (
              <button
                key={s.id}
                onClick={() => onSelectScreen(s.id)}
                style={{
                  fontSize: '13px',
                  fontFamily: 'var(--font-sans)',
                  fontWeight: isActive ? 600 : 400,
                  color: isActive ? 'var(--color-ink)' : 'var(--color-muted)',
                  borderBottom: isActive ? '2px solid var(--color-accent)' : '2px solid transparent',
                  paddingBottom: '2px',
                  transition: 'color var(--motion-fast) var(--ease-out)',
                }}
              >
                {s.label}
              </button>
            );
          })}
        </nav>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {isRunning && (
          <span className="small-caps mono" style={{ color: 'var(--color-accent)' }}>
            ● Pipeline Active
          </span>
        )}
        <span className="mono" style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
          {UI_COPY.courseTag}
        </span>
      </div>
    </header>
  );
};

