import React from 'react';
import { motion } from 'framer-motion';

export interface StageNode {
  id: string;
  num: string;
  title: string;
  sub: string;
  tag: string;
  framework: 'adk' | 'crewai' | 'guardrail' | 'system';
  conceptKey: string;
}

interface FlowThreadProps {
  currentStageIndex: number;
  onSelectConcept: (conceptKey: string) => void;
  gateBlocked?: boolean;
  gateReason?: string;
  reflectionCount?: number;
}

// CONCEPT: Fixed Sequential Pipeline Thread (PRD §5.3)
export const STAGES: StageNode[] = [
  { id: 'inbox', num: '01', title: 'Inbox', sub: 'Receive notification', tag: 'Trigger', framework: 'system', conceptKey: 'planning' },
  { id: 'gate', num: '02', title: 'Gate', sub: 'Mask PII & injections', tag: 'Guardrail', framework: 'guardrail', conceptKey: 'guardrail' },
  { id: 'plan', num: '03', title: 'Plan', sub: 'Manager RunPlan', tag: 'Planning', framework: 'adk', conceptKey: 'planning' },
  { id: 'diff', num: '04', title: 'Diff Laws', sub: 'Clause diffing', tag: 'MCP: diff', framework: 'adk', conceptKey: 'mcp' },
  { id: 'profile', num: '05', title: 'SME Profile', sub: 'Financial memory', tag: 'MCP: sme_db', framework: 'adk', conceptKey: 'blackboard' },
  { id: 'judge', num: '06', title: 'Judge Impact', sub: 'ReAct reasoning', tag: 'ReAct', framework: 'adk', conceptKey: 'react' },
  { id: 'check', num: '07', title: 'Check Quotes', sub: 'Skeptic critique', tag: 'Reflection', framework: 'crewai', conceptKey: 'reflection' },
  { id: 'act', num: '08', title: 'Plan Action', sub: 'Remediation dates', tag: 'Crew Flow', framework: 'crewai', conceptKey: 'a2a' },
  { id: 'report', num: '09', title: 'Report', sub: 'Grounded output', tag: 'Output Lock', framework: 'system', conceptKey: 'guardrail' },
];

export const FlowThread: React.FC<FlowThreadProps> = ({
  currentStageIndex,
  onSelectConcept,
  gateBlocked,
  gateReason,
  reflectionCount = 0,
}) => {
  return (
    <div style={{ position: 'relative', padding: '40px 0', overflowX: 'auto' }}>
      {/* SVG Connecting Thread */}
      <svg
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
        }}
      >
        <line
          x1="50"
          y1="85"
          x2="95%"
          y2="85"
          stroke="var(--color-rule)"
          strokeWidth="1.5"
          strokeDasharray="4 4"
        />
      </svg>

      {/* Nodes Track */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        position: 'relative',
        zIndex: 2,
        minWidth: '950px',
      }}>
        {STAGES.map((stage, idx) => {
          const isActive = idx === currentStageIndex;
          const isDone = idx < currentStageIndex;
          const isBlocked = stage.id === 'gate' && gateBlocked;

          let laneColor = 'var(--color-muted)';
          if (stage.framework === 'adk') laneColor = 'var(--color-adk)';
          if (stage.framework === 'crewai') laneColor = 'var(--color-crewai)';
          if (stage.framework === 'guardrail') laneColor = 'var(--color-accent)';

          return (
            <motion.div
              key={stage.id}
              onClick={() => onSelectConcept(stage.conceptKey)}
              whileHover={{ y: -2 }}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                width: '95px',
                cursor: 'pointer',
                opacity: isDone ? 0.6 : 1,
                position: 'relative',
              }}
            >
              {/* Concept Pill Tag */}
              <span className="small-caps mono" style={{
                fontSize: '9px',
                color: laneColor,
                marginBottom: '4px',
              }}>
                {stage.tag}
              </span>

              {/* Node Marker */}
              <div style={{
                width: '100%',
                borderTop: `2px solid ${isActive ? 'var(--color-accent)' : isBlocked ? 'var(--color-blocked)' : laneColor}`,
                paddingTop: '8px',
                marginBottom: '6px',
              }}>
                <span className="mono" style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  color: isActive ? 'var(--color-accent)' : 'var(--color-muted)',
                }}>
                  {stage.num}
                </span>
              </div>

              {/* Stage Typography */}
              <h3 style={{
                fontSize: '14px',
                fontWeight: isActive ? 600 : 400,
                color: isActive ? 'var(--color-ink)' : 'var(--color-muted)',
                marginBottom: '2px',
              }}>
                {stage.title}
              </h3>

              <span style={{ fontSize: '11px', color: 'var(--color-muted)', lineHeight: 1.3 }}>
                {stage.sub}
              </span>

              {/* Gate Blocked Indicator */}
              {isBlocked && (
                <div style={{
                  marginTop: '8px',
                  fontSize: '10px',
                  color: 'var(--color-blocked)',
                  borderTop: '1px solid var(--color-blocked)',
                  paddingTop: '4px',
                }}>
                  Blocked: {gateReason || 'Rejected'}
                </div>
              )}

              {/* Reflection Loop Counter */}
              {stage.id === 'check' && reflectionCount > 0 && (
                <span className="mono" style={{
                  marginTop: '6px',
                  fontSize: '10px',
                  color: 'var(--color-crewai)',
                }}>
                  ↺ Retry: {reflectionCount}
                </span>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};
