import React from 'react';

interface HeaderProps {
  currentTab: 'upload' | 'dashboard' | 'results' | 'dataset' | 'models';
  onSelectTab: (tab: 'upload' | 'dashboard' | 'results' | 'dataset' | 'models') => void;
  hasActiveComparison: boolean;
  onOpenGuide?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ currentTab, onSelectTab, hasActiveComparison, onOpenGuide }) => {
  return (
    <header style={{ borderBottom: '1px solid var(--border-color)', background: 'var(--bg-secondary)', padding: '16px 24px' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div style={{ 
                width: '38px', 
                height: '38px', 
                borderRadius: '0px', 
                background: '#27272a', 
                border: '1px solid #3f3f46',
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                fontWeight: 700,
                color: '#f4f4f5',
                fontSize: '16px',
                letterSpacing: '0.05em'
              }}>
                CC
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <h1 style={{ fontSize: '18px', fontWeight: 700, margin: 0, letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--text-primary)' }}>
                    ConvComp
                  </h1>
                  <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-secondary)', background: 'var(--bg-elevated)', padding: '2px 8px', borderRadius: '0px', border: '1px solid var(--border-color)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                    Dictamen Técnico
                  </span>
                </div>
                <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: 'var(--text-muted)' }}>
                  Sistema Institucional de Análisis y Pre-Evaluación de Correspondencia Curricular
                </p>
              </div>
            </div>
          </div>

          <nav style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button
              onClick={() => onSelectTab('upload')}
              className={`btn ${currentTab === 'upload' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '12px', padding: '6px 14px' }}
            >
              Nueva Evaluación
            </button>
            <button
              onClick={() => onSelectTab('dashboard')}
              className={`btn ${currentTab === 'dashboard' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '12px', padding: '6px 14px' }}
            >
              Registro de Sílabos
            </button>
            {hasActiveComparison && (
              <button
                onClick={() => onSelectTab('results')}
                className={`btn ${currentTab === 'results' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ fontSize: '12px', padding: '6px 14px' }}
              >
                Informe Técnico
              </button>
            )}
            <button
              onClick={() => onSelectTab('dataset')}
              className={`btn ${currentTab === 'dataset' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '12px', padding: '6px 14px' }}
            >
              Registro de Auditoría
            </button>
            <button
              id="nav-tab-models"
              onClick={() => onSelectTab('models')}
              className={`btn ${currentTab === 'models' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '12px', padding: '6px 14px' }}
            >
              Modelos IA
            </button>
            {onOpenGuide && (
              <button
                onClick={onOpenGuide}
                className="btn btn-secondary"
                style={{
                  fontSize: '12px',
                  padding: '6px 14px',
                  borderColor: 'var(--border-color)',
                  color: 'var(--text-secondary)',
                  background: 'var(--bg-elevated)'
                }}
                title="Consultar Criterios Metodológicos y Glosario"
              >
                Guía Metodológica
              </button>
            )}
          </nav>
        </div>

        {/* Marco Institucional Obligatorio */}
        <div style={{
          marginTop: '14px',
          padding: '8px 14px',
          background: 'var(--bg-primary)',
          borderLeft: '3px solid #6b7280',
          borderRadius: '0px',
          fontSize: '12px',
          color: 'var(--text-secondary)',
          lineHeight: 1.4,
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style={{ color: '#d1d5db', fontWeight: 700, fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
            Aviso Institucional:
          </span>
          <span>
            Este sistema ejecuta un análisis computacional reproducible como herramienta de apoyo analítico. No reemplaza ni constituye una resolución de convalidación universitaria, la cual corresponde con exclusividad a las comisiones académicas competentes.
          </span>
        </div>
      </div>
    </header>
  );
};