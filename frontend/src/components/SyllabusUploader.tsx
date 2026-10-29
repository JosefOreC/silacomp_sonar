import { useRef, useState } from 'react';
import { ArrowDown, ArrowRight, BookOpen, Check, FileCheck2, FileText, Fingerprint, GitCompareArrows,
  Layers, LoaderCircle, ScanLine, ShieldCheck, Upload } from 'lucide-react';
import { api } from '../services/api';
import type { Syllabus, Comparison } from '../types';

interface SyllabusUploaderProps {
  onComparisonCreated: (comp: Comparison) => void;
  existingSyllabi: Syllabus[];
  onSyllabusUploaded: () => void;
  onOpenGuide?: () => void;
  onOpenBatch?: () => void;
}

interface DocumentState {
  file: File | null;
  university: string;
  courseName: string;
  uploaded: Syllabus | null;
  selectedId: string;
  loading: boolean;
  error: string | null;
}

function useSyllabusDocument(onUploaded: () => void) {
  const [state, setState] = useState<DocumentState>({ file: null, university: '', courseName: '',
    uploaded: null, selectedId: '', loading: false, error: null });
  const inputRef = useRef<HTMLInputElement>(null);
  const update = (changes: Partial<DocumentState>) => setState(previous => ({ ...previous, ...changes }));
  const upload = async () => {
    if (!state.file) return;
    update({ loading: true, error: null });
    try {
      const syllabus = await api.uploadSyllabus(state.file, state.university, state.courseName);
      update({ uploaded: syllabus, selectedId: syllabus.id });
      onUploaded();
    } catch (error: unknown) {
      update({ error: error instanceof Error ? error.message : 'Error al procesar el archivo' });
    } finally {
      update({ loading: false });
    }
  };
  return { state, update, upload, inputRef, id: state.selectedId || state.uploaded?.id };
}

type DocumentInput = ReturnType<typeof useSyllabusDocument>;

const DocumentPanel = ({ document, syllabi, objective }: {
  document: DocumentInput; syllabi: Syllabus[]; objective: boolean;
}) => {
  const { state, update, upload, inputRef, id } = document;
  const prefix = objective ? 'objective' : 'compared';
  const selected = syllabi.find(syllabus => syllabus.id === state.selectedId) ?? state.uploaded;
  return (
    <section className={`document-panel${id ? ' has-document' : ''}`} aria-labelledby={`${prefix}-title`}>
      <div className="document-heading">
        <span className="document-icon"><FileText size={22} strokeWidth={1.6} aria-hidden="true" /></span>
        <div>
          <span className="document-kicker">{objective ? '01 · PLAN DESTINO' : '02 · INSTITUCIÓN DE ORIGEN'}</span>
          <h3 id={`${prefix}-title`}>{objective ? 'Sílabo objetivo' : 'Sílabo comparado'}</h3>
        </div>
        {id && <span className="document-ready"><Check size={13} /> Listo</span>}
      </div>
      <p className="document-description">{objective ? 'La asignatura cuyos contenidos necesitas acreditar.' : 'La asignatura cursada que deseas contrastar.'}</p>
      {syllabi.length > 0 && <div className="field-group">
        <label htmlFor={`${prefix}-catalog`}>Seleccionar del catálogo</label>
        <select id={`${prefix}-catalog`} value={state.selectedId} disabled={state.loading}
          onChange={event => update({ selectedId: event.target.value, uploaded: null, error: null })}>
          <option value="">Cargar nuevo documento o elegir un sílabo</option>
          {syllabi.map(syllabus => <option key={syllabus.id} value={syllabus.id}>
            {syllabus.course_name || syllabus.filename} · {syllabus.university || 'Universidad no registrada'} · {syllabus.total_pages} páginas
          </option>)}
        </select>
      </div>}
      {!state.selectedId && <>
        <input ref={inputRef} hidden type="file" accept="application/pdf"
          aria-label={`Documento PDF ${objective ? 'objetivo' : 'comparado'}`} disabled={state.loading}
          onChange={event => {
            const file = event.target.files?.[0];
            if (file) update({ file, uploaded: null, error: null });
          }} />
        <button className={`upload-zone${state.file ? ' has-file' : ''}`} type="button"
          disabled={state.loading} onClick={() => inputRef.current?.click()}>
          <span className="upload-icon"><Upload size={22} strokeWidth={1.7} /></span>
          <strong>{state.file ? state.file.name : 'Seleccionar documento PDF'}</strong>
          <span>{state.file ? `${(state.file.size / 1024).toFixed(1)} KB · Listo para registrar` : 'Texto digital u OCR para documentos escaneados'}</span>
          <span className="upload-browse">Explorar archivos <ArrowRight size={13} /></span>
        </button>
        <div className="document-fields">
          <div className="field-group">
            <label htmlFor={`${prefix}-university`}>Universidad / Institución</label>
            <input id={`${prefix}-university`} value={state.university} disabled={state.loading}
              placeholder={objective ? 'Ej. UNI, UNMSM, PUCP' : 'Ej. U. de Buenos Aires, UNAM'}
              onChange={event => update({ university: event.target.value })} />
          </div>
          <div className="field-group">
            <label htmlFor={`${prefix}-course`}>Nombre de Asignatura</label>
            <input id={`${prefix}-course`} value={state.courseName} disabled={state.loading}
              placeholder={objective ? 'Ej. Base de Datos I' : 'Ej. Sistemas de Bases de Datos'}
              onChange={event => update({ courseName: event.target.value })} />
          </div>
        </div>
        {state.file && <button type="button" className="btn btn-primary document-submit" disabled={state.loading}
          onClick={upload}>{state.loading ? <><LoaderCircle size={16} className="spin" /> Procesando documento...</> : 'Cargar y Registrar Sílabo'}</button>}
      </>}
      {id && selected && <div className="selected-document">
        <FileCheck2 size={26} strokeWidth={1.5} />
        <div><strong>{selected.course_name || selected.filename}</strong>
          <span>{selected.total_pages} páginas · {selected.university || 'Universidad no registrada'}</span></div>
      </div>}
      {state.error && <p className="feedback feedback-error" role="alert">{state.error}</p>}
    </section>
  );
};

const features = [
  { icon: ScanLine, title: 'Evidencia, página por página', text: 'Vuelve al texto original de ambos PDF y localiza cada correspondencia.' },
  { icon: GitCompareArrows, title: 'Una mirada en ambos sentidos', text: 'Consulta lo que cubre cada asignatura y los contenidos que quedan pendientes.' },
  { icon: ShieldCheck, title: 'Tu criterio tiene la última palabra', text: 'Registra una revisión humana sin reemplazar la predicción original.' },
  { icon: Fingerprint, title: 'Un proceso que puedes auditar', text: 'Conserva parámetros, decisiones y versiones para seguir cada evaluación.' },
];

export const SyllabusUploader = ({ onComparisonCreated, existingSyllabi, onSyllabusUploaded, onOpenGuide, onOpenBatch }: SyllabusUploaderProps) => {
  const objective = useSyllabusDocument(onSyllabusUploaded);
  const compared = useSyllabusDocument(onSyllabusUploaded);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const canCompare = Boolean(objective.id && compared.id && !comparing);
  const runComparison = async () => {
    if (!objective.id || !compared.id) return;
    if (objective.id === compared.id) {
      setError('No es recomendable comparar un sílabo consigo mismo.');
      return;
    }
    setComparing(true);
    setError(null);
    try {
      onComparisonCreated(await api.createComparison(objective.id, compared.id));
    } catch (failure: unknown) {
      setError(failure instanceof Error ? failure.message : 'Fallo durante el procesamiento de la comparación');
    } finally {
      setComparing(false);
    }
  };
  return (
    <div className="evaluation-page">
      <section className="evaluation-hero" aria-labelledby="evaluation-title">
        <span className="hero-orbit hero-orbit-left" aria-hidden="true"><FileText /></span>
        <span className="hero-orbit hero-orbit-right" aria-hidden="true"><BookOpen /></span>
        <span className="hero-eyebrow"><span /> INTELIGENCIA ACADÉMICA, CON EVIDENCIA</span>
        <h1 id="evaluation-title">Dos sílabos.<br /><span>Una mirada más clara.</span></h1>
        <p>Descubre cómo se conectan los contenidos de dos asignaturas.<br className="desktop-break" /> Compara, explora la evidencia y aporta tu criterio académico.</p>
        <div className="hero-actions">
          <a className="btn btn-hero" href="#comparison-workspace">Comenzar evaluación <ArrowDown size={16} /></a>
          {onOpenGuide && <button className="btn btn-hero-outline" type="button" onClick={onOpenGuide}>Conocer la metodología <ArrowRight size={15} /></button>}
        </div>
        <div className="hero-assurance"><ShieldCheck size={15} /> Análisis explicable <span>·</span> Evidencia verificable <span>·</span> Decisión humana</div>
      </section>
      <section id="comparison-workspace" className="comparison-workspace" aria-labelledby="workspace-title">
        <div className="workspace-topbar"><span><span className="workspace-status-dot" /> ESPACIO DE EVALUACIÓN</span><span><ShieldCheck size={13} /> Trazabilidad de principio a fin</span></div>
        <div className="workspace-heading">
          <div><span className="section-eyebrow">NUEVA EVALUACIÓN</span><h2 id="workspace-title">Empieza con tus documentos</h2><p>Carga dos PDF o selecciona sílabos de tu catálogo.</p>
            {onOpenBatch && <button type="button" className="text-button" onClick={onOpenBatch}>¿Varios candidatos? Comparar por lotes <ArrowRight size={13} /></button>}
          </div>
          <ol className="workflow-steps" aria-label="Etapas de la evaluación">
            <li aria-current="step"><span>1</span> Documentos</li><li><span>2</span> Análisis</li><li><span>3</span> Revisión</li>
          </ol>
        </div>
        <div className="document-grid">
          <DocumentPanel document={objective} syllabi={existingSyllabi} objective />
          <div className="document-connection" aria-hidden="true"><GitCompareArrows size={20} /></div>
          <DocumentPanel document={compared} syllabi={existingSyllabi} objective={false} />
        </div>
        <div className="workspace-actionbar">
          <p><Layers size={16} /> Correspondencia conceptual, léxica y disciplinar.</p>
          <button type="button" className="btn btn-primary compare-button" onClick={runComparison} disabled={!canCompare}>
            {comparing ? <><LoaderCircle size={17} className="spin" /> Ejecutando Evaluación Curricular...</> : <>Generar Dictamen de Correspondencia <ArrowRight size={17} /></>}
          </button>
        </div>
        {error && <p className="feedback feedback-error comparison-error" role="alert">{error}</p>}
      </section>
      <section className="evaluation-features" aria-labelledby="features-title">
        <div className="features-heading"><div><span className="section-eyebrow">MÁS CONTEXTO. MEJORES DECISIONES.</span><h2 id="features-title">Cada coincidencia,<br /><span>un argumento verificable.</span></h2></div><p>La IA propone una correspondencia. La plataforma te muestra por qué. La evaluación académica sigue en tus manos.</p></div>
        <div className="feature-grid">{features.map(({ icon: Icon, title, text }) => <article className="feature-card" key={title}><span className="feature-icon"><Icon size={21} strokeWidth={1.7} /></span><h3>{title}</h3><p>{text}</p></article>)}</div>
      </section>
    </div>
  );
};
