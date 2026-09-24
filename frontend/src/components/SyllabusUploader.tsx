import React, { useState, useRef } from 'react';
import { api } from '../services/api';
import type { Syllabus, Comparison } from '../types';

interface SyllabusUploaderProps {
  onComparisonCreated: (comp: Comparison) => void;
  existingSyllabi: Syllabus[];
  onSyllabusUploaded: () => void;
}

export const SyllabusUploader: React.FC<SyllabusUploaderProps> = ({
  onComparisonCreated,
  existingSyllabi,
  onSyllabusUploaded,
}) => {
  // Estado para Sílabo Objetivo
  const [objFile, setObjFile] = useState<File | null>(null);
  const [objUniversity, setObjUniversity] = useState('');
  const [objCourseName, setObjCourseName] = useState('');
  const [uploadedObj, setUploadedObj] = useState<Syllabus | null>(null);
  const [selectedExistingObjId, setSelectedExistingObjId] = useState('');
  const [objLoading, setObjLoading] = useState(false);
  const [objError, setObjError] = useState<string | null>(null);

  // Estado para Sílabo Comparado
  const [cmpFile, setCmpFile] = useState<File | null>(null);
  const [cmpUniversity, setCmpUniversity] = useState('');
  const [cmpCourseName, setCmpCourseName] = useState('');
  const [uploadedCmp, setUploadedCmp] = useState<Syllabus | null>(null);
  const [selectedExistingCmpId, setSelectedExistingCmpId] = useState('');
  const [cmpLoading, setCmpLoading] = useState(false);
  const [cmpError, setCmpError] = useState<string | null>(null);

  // Estado general de comparación
  const [isComparing, setIsComparing] = useState(false);
  const [compareError, setCompareError] = useState<string | null>(null);

  const objInputRef = useRef<HTMLInputElement>(null);
  const cmpInputRef = useRef<HTMLInputElement>(null);

  const handleUploadObjective = async () => {
    if (!objFile) return;
    setObjLoading(true);
    setObjError(null);
    try {
      const syl = await api.uploadSyllabus(objFile, objUniversity, objCourseName);
      setUploadedObj(syl);
      setSelectedExistingObjId(syl.id);
      onSyllabusUploaded();
    } catch (err: any) {
      setObjError(err.message || 'Error al procesar el archivo');
    } finally {
      setObjLoading(false);
    }
  };

  const handleUploadCompared = async () => {
    if (!cmpFile) return;
    setCmpLoading(true);
    setCmpError(null);
    try {
      const syl = await api.uploadSyllabus(cmpFile, cmpUniversity, cmpCourseName);
      setUploadedCmp(syl);
      setSelectedExistingCmpId(syl.id);
      onSyllabusUploaded();
    } catch (err: any) {
      setCmpError(err.message || 'Error al procesar el archivo');
    } finally {
      setCmpLoading(false);
    }
  };

  const handleRunComparison = async () => {
    const finalObjId = selectedExistingObjId || uploadedObj?.id;
    const finalCmpId = selectedExistingCmpId || uploadedCmp?.id;

    if (!finalObjId || !finalCmpId) {
      setCompareError('Debe definir tanto el Sílabo Objetivo como el Sílabo Comparado.');
      return;
    }

    if (finalObjId === finalCmpId) {
      setCompareError('No es recomendable comparar un sílabo consigo mismo.');
      return;
    }

    setIsComparing(true);
    setCompareError(null);
    try {
      const comp = await api.createComparison(finalObjId, finalCmpId);
      onComparisonCreated(comp);
    } catch (err: any) {
      setCompareError(err.message || 'Fallo durante el procesamiento de la comparación');
    } finally {
      setIsComparing(false);
    }
  };

  const effectiveObjId = selectedExistingObjId || uploadedObj?.id;
  const effectiveCmpId = selectedExistingCmpId || uploadedCmp?.id;
  const canCompare = Boolean(effectiveObjId && effectiveCmpId && !isComparing);

  return (
    <div style={{ maxWidth: '1200px', margin: '30px auto', padding: '0 20px' }}>
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h2 style={{ fontSize: '22px', fontWeight: 700, margin: '0 0 6px 0', color: 'var(--text-primary)', letterSpacing: '0.02em', textTransform: 'uppercase' }}>
          Configuración y Carga de Expediente Curricular
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '13px', maxWidth: '700px', margin: '0 auto' }}>
          Ingrese los programas analíticos en formato PDF digital correspondiente al plan de estudios requerido y a los antecedentes académicos de origen.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '24px' }}>
        {/* Panel 1: Sílabo Objetivo */}
        <div className="card" style={{ borderTop: '3px solid #6b7280', borderRadius: '0px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ margin: 0, fontSize: '15px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
              <span style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-color)', padding: '2px 8px', borderRadius: '0px', fontSize: '11px', color: 'var(--text-secondary)' }}>1</span>
              Asignatura Requerida · Plan Destino
            </h3>
            {effectiveObjId && <span className="badge badge-match">Acreditado</span>}
          </div>

          {existingSyllabi.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                Seleccionar de asignaturas previamente registradas:
              </label>
              <select
                value={selectedExistingObjId}
                onChange={(e) => {
                  setSelectedExistingObjId(e.target.value);
                  if (e.target.value) setUploadedObj(null);
                }}
                style={{
                  width: '100%',
                  background: '#FFFFFF',
                  color: '#000000',
                  border: '1px solid #CBD5E1',
                  padding: '8px 12px',
                  borderRadius: '0px',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                <option value="" style={{ color: '#000000', background: '#FFFFFF' }}>
                  -- Cargar nuevo documento o seleccionar del catálogo --
                </option>
                {existingSyllabi.map((s) => (
                  <option key={s.id} value={s.id} style={{ color: '#000000', background: '#FFFFFF' }}>
                    {s.course_name || s.filename} · {s.university || 'Univ. no registrada'} · {s.total_pages} páginas
                  </option>
                ))}
              </select>
            </div>
          )}

          {!selectedExistingObjId && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div
                onClick={() => objInputRef.current?.click()}
                style={{
                  border: '2px dashed var(--border-color)',
                  borderRadius: '0px',
                  padding: '24px 16px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  background: objFile ? 'var(--bg-elevated)' : 'var(--bg-primary)',
                  transition: 'all 0.2s ease',
                }}
              >
                <input
                  ref={objInputRef}
                  type="file"
                  accept="application/pdf"
                  style={{ display: 'none' }}
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) setObjFile(f);
                  }}
                />
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '13px' }}>
                  {objFile ? objFile.name : 'Seleccionar documento PDF digital'}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {objFile ? `${(objFile.size / 1024).toFixed(1)} KB` : 'Archivos PDF con texto digital seleccionable'}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                    Universidad / Institución
                  </label>
                  <input
                    type="text"
                    placeholder="Ej. UNI, UNMSM, PUCP"
                    value={objUniversity}
                    onChange={(e) => setObjUniversity(e.target.value)}
                    style={{
                      width: '100%',
                      background: '#FFFFFF',
                      border: '1px solid #CBD5E1',
                      color: '#000000',
                      padding: '8px 10px',
                      borderRadius: '0px',
                      fontSize: '12px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                    Nombre de Asignatura
                  </label>
                  <input
                    type="text"
                    placeholder="Ej. Base de Datos I"
                    value={objCourseName}
                    onChange={(e) => setObjCourseName(e.target.value)}
                    style={{
                      width: '100%',
                      background: '#FFFFFF',
                      border: '1px solid #CBD5E1',
                      color: '#000000',
                      padding: '8px 10px',
                      borderRadius: '0px',
                      fontSize: '12px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
              </div>

              {objFile && !uploadedObj && (
                <button
                  onClick={handleUploadObjective}
                  disabled={objLoading}
                  className="btn btn-primary"
                  style={{ alignSelf: 'flex-start', fontSize: '12px' }}
                >
                  {objLoading ? 'Procesando texto digital...' : 'Cargar y Registrar Sílabo'}
                </button>
              )}

              {objError && (
                <div style={{ padding: '8px 12px', background: 'rgba(239, 68, 68, 0.1)', borderLeft: '3px solid #ef4444', borderRadius: '0px', fontSize: '12px', color: '#fca5a5' }}>
                  {objError}
                </div>
              )}

              {uploadedObj && (
                <div style={{ padding: '8px 12px', background: 'rgba(52, 211, 153, 0.1)', borderLeft: '3px solid #34d399', borderRadius: '0px', fontSize: '12px', color: '#6ee7b7' }}>
                  Documento procesado correctamente: {uploadedObj.total_pages} páginas y {uploadedObj.total_characters} caracteres de texto digital.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Panel 2: Sílabo Comparado */}
        <div className="card" style={{ borderTop: '3px solid #6b7280', borderRadius: '0px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ margin: 0, fontSize: '15px', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
              <span style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-color)', padding: '2px 8px', borderRadius: '0px', fontSize: '11px', color: 'var(--text-secondary)' }}>2</span>
              Asignatura Cursada · Institución de Origen
            </h3>
            {effectiveCmpId && <span className="badge badge-match">Acreditado</span>}
          </div>

          {existingSyllabi.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                Seleccionar de asignaturas previamente registradas:
              </label>
              <select
                value={selectedExistingCmpId}
                onChange={(e) => {
                  setSelectedExistingCmpId(e.target.value);
                  if (e.target.value) setUploadedCmp(null);
                }}
                style={{
                  width: '100%',
                  background: '#FFFFFF',
                  color: '#000000',
                  border: '1px solid #CBD5E1',
                  padding: '8px 12px',
                  borderRadius: '0px',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                <option value="" style={{ color: '#000000', background: '#FFFFFF' }}>
                  -- Cargar nuevo documento o seleccionar del catálogo --
                </option>
                {existingSyllabi.map((s) => (
                  <option key={s.id} value={s.id} style={{ color: '#000000', background: '#FFFFFF' }}>
                    {s.course_name || s.filename} · {s.university || 'Univ. no registrada'} · {s.total_pages} páginas
                  </option>
                ))}
              </select>
            </div>
          )}

          {!selectedExistingCmpId && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div
                onClick={() => cmpInputRef.current?.click()}
                style={{
                  border: '2px dashed var(--border-color)',
                  borderRadius: '0px',
                  padding: '24px 16px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  background: cmpFile ? 'var(--bg-elevated)' : 'var(--bg-primary)',
                  transition: 'all 0.2s ease',
                }}
              >
                <input
                  ref={cmpInputRef}
                  type="file"
                  accept="application/pdf"
                  style={{ display: 'none' }}
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) setCmpFile(f);
                  }}
                />
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '13px' }}>
                  {cmpFile ? cmpFile.name : 'Seleccionar documento PDF digital'}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {cmpFile ? `${(cmpFile.size / 1024).toFixed(1)} KB` : 'Archivos PDF con texto digital seleccionable'}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                    Universidad / Institución
                  </label>
                  <input
                    type="text"
                    placeholder="Ej. U. de Buenos Aires, UNAM"
                    value={cmpUniversity}
                    onChange={(e) => setCmpUniversity(e.target.value)}
                    style={{
                      width: '100%',
                      background: '#FFFFFF',
                      border: '1px solid #CBD5E1',
                      color: '#000000',
                      padding: '8px 10px',
                      borderRadius: '0px',
                      fontSize: '12px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                    Nombre de Asignatura
                  </label>
                  <input
                    type="text"
                    placeholder="Ej. Sistemas de Bases de Datos"
                    value={cmpCourseName}
                    onChange={(e) => setCmpCourseName(e.target.value)}
                    style={{
                      width: '100%',
                      background: '#FFFFFF',
                      border: '1px solid #CBD5E1',
                      color: '#000000',
                      padding: '8px 10px',
                      borderRadius: '0px',
                      fontSize: '12px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
              </div>

              {cmpFile && !uploadedCmp && (
                <button
                  onClick={handleUploadCompared}
                  disabled={cmpLoading}
                  className="btn btn-secondary"
                  style={{ alignSelf: 'flex-start', fontSize: '12px' }}
                >
                  {cmpLoading ? 'Procesando texto digital...' : 'Cargar y Registrar Sílabo'}
                </button>
              )}

              {cmpError && (
                <div style={{ padding: '8px 12px', background: 'rgba(239, 68, 68, 0.1)', borderLeft: '3px solid #ef4444', borderRadius: '0px', fontSize: '12px', color: '#fca5a5' }}>
                  {cmpError}
                </div>
              )}

              {uploadedCmp && (
                <div style={{ padding: '8px 12px', background: 'rgba(52, 211, 153, 0.1)', borderLeft: '3px solid #34d399', borderRadius: '0px', fontSize: '12px', color: '#6ee7b7' }}>
                  Documento procesado correctamente: {uploadedCmp.total_pages} páginas y {uploadedCmp.total_characters} caracteres de texto digital.
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Botón de Ejecución de Comparación */}
      <div style={{ marginTop: '32px', textAlign: 'center' }}>
        {compareError && (
          <div style={{ maxWidth: '600px', margin: '0 auto 16px', padding: '10px 16px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: '0px', color: '#fca5a5', fontSize: '12px' }}>
            {compareError}
          </div>
        )}

        <button
          onClick={handleRunComparison}
          disabled={!canCompare}
          className="btn btn-primary"
          style={{
            padding: '12px 36px',
            fontSize: '14px',
            fontWeight: 700,
            opacity: canCompare ? 1 : 0.5,
            cursor: canCompare ? 'pointer' : 'not-allowed',
            textTransform: 'uppercase',
            letterSpacing: '0.04em'
          }}
        >
          {isComparing ? 'Ejecutando Evaluación Curricular...' : 'Generar Dictamen de Correspondencia'}
        </button>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
          La evaluación computacional analiza correspondencia conceptual, léxica y de vocabulario disciplinar.
        </p>
      </div>
    </div>
  );
};