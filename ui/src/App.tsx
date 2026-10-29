import React, { useState } from 'react';
import { Header, ScreenId } from './components/Header';
import { Footer } from './components/Footer';
import { FlowPage } from './pages/FlowPage';
import { BoardPage } from './pages/BoardPage';
import { GatesPage } from './pages/GatesPage';
import { TracesPage } from './pages/TracesPage';
import { LabPage } from './pages/LabPage';
import { CoveragePage } from './pages/CoveragePage';
import { CONCEPTS } from './copy';

export const App: React.FC = () => {
  const [activeScreen, setActiveScreen] = useState<ScreenId>('flow');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header
        activeScreen={activeScreen}
        onSelectScreen={(screen) => setActiveScreen(screen)}
      />

      <div style={{ flex: 1 }}>
        {activeScreen === 'flow' && <FlowPage />}
        {activeScreen === 'board' && <BoardPage />}
        {activeScreen === 'gates' && <GatesPage />}
        {activeScreen === 'traces' && <TracesPage />}
        {activeScreen === 'lab' && <LabPage />}
        {activeScreen === 'coverage' && <CoveragePage />}

        {activeScreen === 'concepts' && (
          <div style={{ maxWidth: '1240px', margin: '0 auto', padding: '48px 32px' }}>
            <span className="small-caps" style={{ color: 'var(--color-accent)' }}>
              Course Syllabus Mapping / CSE3101 Handout
            </span>
            <h1 style={{ fontSize: '32px', marginTop: '6px', marginBottom: '24px' }}>
              Course Concepts Index
            </h1>
            <p style={{ color: 'var(--color-muted)', marginBottom: '32px', fontSize: '13px' }}>
              Every concept from the CSE3101 syllabus mapped to its plain English definition and exact code implementation.
            </p>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              gap: '20px',
            }}>
              {Object.entries(CONCEPTS).map(([key, c]) => (
                <div key={key} style={{
                  padding: '20px',
                  backgroundColor: 'var(--color-surface)',
                  border: 'var(--border-rule)',
                  borderRadius: 'var(--radius-sm)',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                    <span className="small-caps mono" style={{ color: 'var(--color-accent)' }}>
                      {c.tag}
                    </span>
                  </div>
                  <h3 style={{ fontSize: '18px', margin: '6px 0' }}>{c.title}</h3>
                  <p style={{ fontStyle: 'italic', color: 'var(--color-muted)', fontSize: '13px', marginBottom: '12px' }}>
                    "{c.oneLiner}"
                  </p>
                  <div style={{ borderTop: 'var(--border-rule)', paddingTop: '10px' }}>
                    <span className="small-caps" style={{ display: 'block', fontSize: '9px', marginBottom: '2px' }}>Code Location:</span>
                    <span className="mono" style={{ fontSize: '11px', color: 'var(--color-ink)' }}>
                      {c.codePath}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};
