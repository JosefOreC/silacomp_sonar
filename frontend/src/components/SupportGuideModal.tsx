import React, { useEffect, useRef, useState } from 'react';
import { CLASSIFICATIONS_ES, CORRECTIONS_ES } from '../utils/translations';

interface SupportGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type GuideSection = 'indicadores' | 'clasificaciones' | 'dictamen' | 'metodologia' | 'normativa';
const sections: { id: GuideSection; num: string; title: string }[] = [
  { id: 'indicadores', num: '1', title: 'Indicadores Principales' },
  { id: 'clasificaciones', num: '2', title: 'Niveles de Correspondencia' },
  { id: 'dictamen', num: '3', title: 'Dictamen y Calificación' },
  { id: 'metodologia', num: '4', title: 'Ponderación Multivariada' },
  { id: 'normativa', num: '5', title: 'Marco Institucional' },
];

export const SupportGuideModal: React.FC<SupportGuideModalProps> = ({ isOpen, onClose }) => {
  const [activeSection, setActiveSection] = useState<GuideSection>('indicadores');
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const previousFocus = document.activeElement;
    const dialog = dialogRef.current;
    dialog?.focus();
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
      if (event.key !== 'Tab' || !dialog) return;
      const controls = dialog.querySelectorAll<HTMLElement>('button:not(:disabled), a[href]');
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog)) {
        event.preventDefault();
        last?.focus();
      } else if (!event.shiftKey && (document.activeElement === last || document.activeElement === dialog)) {
        event.preventDefault();
        first?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus();
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const scrollToSection = (sectionId: GuideSection) => {
    setActiveSection(sectionId);
    const element = document.getElementById(`guide-sec-${sectionId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div ref={dialogRef} tabIndex={-1} className="guide-backdrop" role="dialog" aria-modal="true" aria-labelledby="guide-title" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(34, 7, 52, 0.55)',
      backdropFilter: 'blur(5px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000,
      padding: '20px'
    }}>
      <div className="guide-dialog" style={{
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        maxWidth: '1060px',
        width: '100%',
        height: '92vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: 'var(--shadow-lg)',
        color: 'var(--text-primary)'
      }}>
        {/* Encabezado Principal */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '18px 28px',
          borderBottom: '1px solid var(--border-color)',
          background: 'var(--bg-surface)'
        }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '4px' }}>
              Documento Técnico Institucional
            </div>
            <h2 id="guide-title" style={{ fontSize: '17px', fontWeight: 700, margin: 0, letterSpacing: '0.02em', color: 'var(--text-primary)' }}>
              Guía Metodológica de Criterios y Glosario de Indicadores
            </h2>
          </div>

          <button
            onClick={onClose}
            className="btn btn-secondary"
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              fontWeight: 600,
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer'
            }}
          >
            ✕ Cerrar Guía
          </button>
        </div>

        {/* Cuerpo con Diseño Vertical y Barra Lateral de Navegación */}
        <div className="guide-body">

          {/* Navegación Lateral Vertical */}
          <nav className="guide-navigation" aria-label="Secciones de la guía">
            <div style={{ fontSize: '10px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '8px', paddingLeft: '8px' }}>
              Secciones del Documento
            </div>

            {sections.map((item) => {
              const isActive = activeSection === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    width: '100%',
                    padding: '10px 12px',
                    background: isActive ? 'var(--violet-100)' : 'transparent',
                    border: 'none',
                    borderLeft: isActive ? '3px solid var(--violet-700)' : '3px solid transparent',
                    color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                    fontSize: '13px',
                    fontWeight: isActive ? 600 : 500,
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    borderRadius: 'var(--radius-md)'
                  }}
                >
                  <span style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    color: isActive ? 'var(--text-primary)' : 'var(--text-muted)',
                    background: isActive ? 'var(--violet-100)' : 'transparent',
                    border: '1px solid',
                    borderColor: isActive ? 'var(--text-secondary)' : 'var(--border-color)',
                    padding: '2px 6px',
                    borderRadius: 'var(--radius-md)',
                    minWidth: '20px',
                    textAlign: 'center'
                  }}>
                    {item.num}
                  </span>
                  <span>{item.title}</span>
                </button>
              );
            })}

            <div style={{ marginTop: 'auto', padding: '14px 10px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              <strong style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>Criterio de Aplicación:</strong>
              Use esta guía para justificar técnica y reglamentariamente los dictámenes en actas de convalidación.
            </div>
          </nav>

          {/* Panel Principal de Lectura Vertical */}
          <div className="guide-content">

            {/* SECCIÓN 1: INDICADORES PRINCIPALES */}
            <section id="guide-sec-indicadores" style={{ scrollMarginTop: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', background: 'var(--bg-elevated)', border: '1px solid var(--border-color)', padding: '2px 8px' }}>
                  PARTE 1
                </span>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', margin: 0, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Interpretación de los Indicadores Principales
                </h3>
              </div>
              <p style={{ margin: '0 0 20px 0', fontSize: '13px', color: 'var(--text-secondary)' }}>
                Los tres indicadores métricos reflejan dimensiones complementarias del expediente y deben ser valorados en su conjunto:
              </p>

              {/* Lista Vertical de Indicadores */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

                {/* 1.1 Exigencia Curricular Acreditada */}
                <div style={{
                  background: 'var(--bg-primary)',
                  border: '1px solid var(--border-color)',
                  borderLeft: '4px solid #34d399',
                  padding: '18px 20px',
                  borderRadius: 'var(--radius-md)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      Exigencia Curricular Acreditada
                    </div>
                    <span style={{ fontSize: '11px', fontWeight: 600, background: 'var(--match-bg)', color: 'var(--match-color)', border: '1px solid #059669', padding: '2px 8px' }}>
                      Métrica Decisoria Primaria
                    </span>
                  </div>

                  <p style={{ margin: '0 0 12px 0', fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    Porcentaje de unidades temáticas obligatorias del plan de estudios de destino que el estudiante ya cursó y demostró suficiencia formativa en su universidad de procedencia.
                  </p>

                  <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', padding: '12px 14px', fontSize: '12.5px', color: 'var(--text-secondary)' }}>
                    <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '4px' }}>Regla de Decisión Académica:</strong>
                    Si este indicador alcanza o supera el umbral reglamentario exigido por la institución (generalmente entre el 70% y el 80%), el expediente reúne el mérito académico suficiente para la convalidación o dispensa de la materia.
                  </div>
                </div>

                {/* 1.2 Aprovechamiento Curricular de Origen */}
                <div style={{
                  background: 'var(--bg-primary)',
                  border: '1px solid var(--border-color)',
                  borderLeft: '4px solid #CBD5E1',
                  padding: '18px 20px',
                  borderRadius: 'var(--radius-md)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      Aprovechamiento Curricular de Origen
                    </div>
                    <span style={{ fontSize: '11px', fontWeight: 600, background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)', padding: '2px 8px' }}>
                      Métrica de Transferencia
                    </span>
                  </div>

                  <p style={{ margin: '0 0 12px 0', fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    Proporción de contenidos cursados y aprobados por el estudiante en su institución de procedencia que son válidos y computables para la presente materia.
                  </p>

                  <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', padding: '12px 14px', fontSize: '12.5px', color: 'var(--text-secondary)' }}>
                    <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '4px' }}>Interpretación Práctica:</strong>
                    Un porcentaje menor al 100% no invalida la convalidación. Simplemente evidencia que la asignatura de origen abarcó temas adicionales o enfoques especializados no contemplados ni exigidos por el plan destino.
                  </div>
                </div>

                {/* 1.3 Afinidad Global de Contenidos */}
                <div style={{
                  background: 'var(--bg-primary)',
                  border: '1px solid var(--border-color)',
                  borderLeft: '4px solid #94A3B8',
                  padding: '18px 20px',
                  borderRadius: 'var(--radius-md)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      Afinidad Global de Contenidos
                    </div>
                    <span style={{ fontSize: '11px', fontWeight: 600, background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)', padding: '2px 8px' }}>
                      Promedio Ponderado
                    </span>
                  </div>

                  <p style={{ margin: '0 0 12px 0', fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    Promedio analítico de equivalencia semántica, concordancia léxica y vocabulario disciplinar entre las unidades comparadas.
                  </p>

                  <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', padding: '12px 14px', fontSize: '12.5px', color: 'var(--text-secondary)' }}>
                    <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '4px' }}>Estructura del Cálculo:</strong>
                    Suma ponderada determinista: Similitud Semántica (40%) + Concordancia Léxica (30%) + Vocabulario Disciplinar (15%) + Correspondencia Estructural (15%).
                  </div>
                </div>

              </div>
            </section>

            <hr style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: 0 }} />

            {/* SECCIÓN 2: NIVELES DE CORRESPONDENCIA TEMÁTICA */}
            <section id="guide-sec-clasificaciones" style={{ scrollMarginTop: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', background: 'var(--bg-elevated)', border: '1px solid var(--border-color)', padding: '2px 8px' }}>
                  PARTE 2
                </span>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', margin: 0, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Niveles de Correspondencia Temática
                </h3>
              </div>
              <p style={{ margin: '0 0 20px 0', fontSize: '13px', color: 'var(--text-secondary)' }}>
                Cada unidad temática es catalogada en un nivel de afinidad técnica objetivo:
              </p>

              {/* Lista Vertical de Niveles */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {Object.values(CLASSIFICATIONS_ES).map((cls) => (
                  <div
                    key={cls.code}
                    style={{
                      background: 'var(--bg-primary)',
                      border: '1px solid var(--border-color)',
                      padding: '16px 20px',
                      borderRadius: 'var(--radius-md)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                      <span className={`badge ${cls.badgeClass}`} style={{ fontSize: '12px', padding: '4px 10px', letterSpacing: '0.03em' }}>
                        {cls.label}
                      </span>
                      <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>
                        {cls.code === 'MATCH' && 'Afinidad ≥ 75%'}
                        {cls.code === 'PARTIAL_MATCH' && 'Afinidad entre 55% y 74%'}
                        {cls.code === 'UNCERTAIN' && 'Afinidad entre 40% y 54%'}
                        {cls.code === 'NO_MATCH' && 'Afinidad < 40%'}
                      </span>
                    </div>

                    <p style={{ margin: '0 0 8px 0', fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                      {cls.description}
                    </p>

                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      <strong style={{ color: 'var(--text-secondary)' }}>Acción sugerida para el evaluador: </strong>
                      {cls.code === 'MATCH' && 'Convalidación directa del contenido.'}
                      {cls.code === 'PARTIAL_MATCH' && 'Convalidable salvo que el tema sea troncal y requiera suficiencia complementaria.'}
                      {cls.code === 'UNCERTAIN' && 'Requiere inspección visual en el panel de evidencias para ratificar o descartar.'}
                      {cls.code === 'NO_MATCH' && 'Constituye una brecha formativa no subsanada por el curso de procedencia.'}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <hr style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: 0 }} />

            {/* SECCIÓN 3: DICTAMEN Y CALIFICACIÓN DOCENTE */}
            <section id="guide-sec-dictamen" style={{ scrollMarginTop: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', background: 'var(--bg-elevated)', border: '1px solid var(--border-color)', padding: '2px 8px' }}>
                  PARTE 3
                </span>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', margin: 0, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Opciones de Dictamen y Calificación Docente
                </h3>
              </div>
              <p style={{ margin: '0 0 20px 0', fontSize: '13px', color: 'var(--text-secondary)' }}>
                Al pulsar «Registrar Dictamen» en cualquier fila de la matriz, el docente puede registrar una decisión justificada:
              </p>

              {/* Lista Vertical de Opciones de Dictamen */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {Object.values(CORRECTIONS_ES).map((cor) => (
                  <div
                    key={cor.code}
                    style={{
                      background: 'var(--bg-primary)',
                      border: '1px solid var(--border-color)',
                      padding: '16px 20px',
                      borderRadius: 'var(--radius-md)'
                    }}
                  >
                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
                      {cor.label}
                    </div>
                    <p style={{ margin: '0 0 8px 0', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                      {cor.description}
                    </p>
                    <div style={{ fontSize: '11.5px', color: 'var(--text-muted)' }}>
                      Código de registro reglamentario: <code style={{ color: 'var(--text-secondary)', background: 'var(--bg-elevated)', padding: '2px 6px' }}>{cor.code}</code>
                    </div>
                  </div>
                ))}

                <div style={{ background: 'var(--bg-elevated)', borderLeft: '4px solid #CBD5E1', padding: '14px 18px', fontSize: '12.5px', color: 'var(--text-secondary)', marginTop: '6px' }}>
                  <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: '4px' }}>Garantía de Inmutabilidad y Trazabilidad Institucional:</strong>
                  La predicción original emitida por el algoritmo nunca es sobrescrita ni eliminada. La resolución docente se almacena en un registro independiente de auditoría con fecha, usuario y justificación académica, garantizando plena transparencia ante auditorías curriculares o apelaciones estudiantiles.
                </div>
              </div>
            </section>

            <hr style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: 0 }} />

            {/* SECCIÓN 4: PONDERACIÓN MULTIVARIADA */}
            <section id="guide-sec-metodologia" style={{ scrollMarginTop: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', background: 'var(--bg-elevated)', border: '1px solid var(--border-color)', padding: '2px 8px' }}>
                  PARTE 4
                </span>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', margin: 0, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Factores del Motor de Ponderación Multivariada
                </h3>
              </div>
              <p style={{ margin: '0 0 20px 0', fontSize: '13px', color: 'var(--text-secondary)' }}>
                El cálculo no depende de un único criterio arbitrario, sino de cuatro componentes analíticos complementarios:
              </p>

              {/* Lista Vertical de Factores */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>

                <div style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-color)', padding: '16px 20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <strong style={{ fontSize: '14px', color: 'var(--text-primary)' }}>1. Similitud Conceptual y Semántica</strong>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)', background: 'var(--violet-100)', padding: '2px 8px' }}>Ponderación 40%</span>
                  </div>
                  <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    Evalúa el significado conceptual profundo de los temas a través de modelos de lenguaje multilingües, reconociendo equivalencias sustanciales aun cuando los planes de estudio empleen redacciones, sinónimos o formulaciones pedagógicas diferentes.
                  </p>
                </div>

                <div style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-color)', padding: '16px 20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <strong style={{ fontSize: '14px', color: 'var(--text-primary)' }}>2. Concordancia Textual y Léxica</strong>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)', background: 'var(--violet-100)', padding: '2px 8px' }}>Ponderación 30%</span>
                  </div>
                  <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    Analiza la coincidencia léxica directa y términos exactos mediante ponderación de frecuencias textuales (TF-IDF y n-gramas), asegurando que el vocabulario canónico de la disciplina esté reflejado.
                  </p>
                </div>

                <div style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-color)', padding: '16px 20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <strong style={{ fontSize: '14px', color: 'var(--text-primary)' }}>3. Vocabulario Especializado Disciplinar</strong>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)', background: 'var(--violet-100)', padding: '2px 8px' }}>Ponderación 15%</span>
                  </div>
                  <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    Identifica y contabiliza términos técnicos indispensables y conceptos nucleares compartidos (p. ej. algoritmos, estándares, teoremas o herramientas especializadas).
                  </p>
                </div>

                <div style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-color)', padding: '16px 20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <strong style={{ fontSize: '14px', color: 'var(--text-primary)' }}>4. Correspondencia Estructural y Secuencia Curricular</strong>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)', background: 'var(--violet-100)', padding: '2px 8px' }}>Ponderación 15%</span>
                  </div>
                  <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    Examina el orden relativo y la pertenencia a unidades temáticas equivalentes dentro de la progresión temporal y formativa de la asignatura.
                  </p>
                </div>

              </div>
            </section>

            <hr style={{ border: 'none', borderTop: '1px solid var(--border-color)', margin: 0 }} />

            {/* SECCIÓN 5: MARCO NORMATIVO E INSTITUCIONAL */}
            <section id="guide-sec-normativa" style={{ scrollMarginTop: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', background: 'var(--bg-elevated)', border: '1px solid var(--border-color)', padding: '2px 8px' }}>
                  PARTE 5
                </span>
                <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', margin: 0, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Marco Institucional y Exención de Responsabilidad
                </h3>
              </div>

              <div style={{
                background: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                borderLeft: '4px solid #CBD5E1',
                padding: '20px 22px',
                borderRadius: 'var(--radius-md)'
              }}>
                <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
                  Principio de Apoyo Analítico No Vinculante
                </h4>
                <p style={{ margin: '0 0 12px 0', fontSize: '13.5px', color: 'var(--text-secondary)', lineHeight: 1.65 }}>
                  Este sistema constituye exclusivamente un instrumento computacional de pre-evaluación y apoyo técnico. Las métricas calculadas, sugerencias de correspondencia y clasificaciones automatizadas no poseen carácter resolutivo vinculante por sí mismas.
                </p>
                <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  La decisión final de homologación, convalidación o dispensa curricular recae de manera soberana y exclusiva en la <strong>Comisión Curricular Universitaria</strong> y en los docentes designados, con estricto apego al Reglamento de Convalidaciones y Régimen de Estudios de la institución.
                </p>
              </div>
            </section>

          </div>
        </div>

        {/* Pie del Modal */}
        <div style={{
          padding: '14px 28px',
          borderTop: '1px solid var(--border-color)',
          background: 'var(--bg-surface)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Documento de Referencia · Sistema de Convalidación Curricular
          </span>
          <button
            onClick={onClose}
            className="btn btn-primary"
            style={{
              fontSize: '12.5px',
              padding: '8px 20px',
              fontWeight: 600,
              borderRadius: 'var(--radius-md)',
              cursor: 'pointer'
            }}
          >
            Aceptar y Volver al Expediente
          </button>
        </div>
      </div>
    </div>
  );
};
