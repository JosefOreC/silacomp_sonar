import React, { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import type { ModelVersion, TrainModelRequest } from '../types';

// ─── Utilidades de formato ────────────────────────────────────────────────────

const fmtPct = (v?: number) =>
  v !== undefined ? `${(v * 100).toFixed(1)}%` : '—';

const fmtNum = (v?: number, dec = 4) =>
  v !== undefined ? v.toFixed(dec) : '—';

const fmtDate = (iso?: string) => {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('es-PE', {
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit',
    });
  } catch {
    return iso;
  }
};

// ─── Sub-componente: Tarjeta de Versión de Modelo ────────────────────────────

interface ModelCardProps {
  model: ModelVersion;
  isSelected: boolean;
  onSelect: () => void;
  onActivate: () => void;
  activating: boolean;
}

const ModelCard: React.FC<ModelCardProps> = ({ model, isSelected, onSelect, onActivate, activating }) => {
  const isBaseline = model.metrics?.type === 'heuristic_baseline';
  const gain = model.metrics?.baseline_comparison?.f1_gain;

  return (
    <div
      id={`model-card-${model.version_id}`}
      onClick={onSelect}
      style={{
        border: `1px solid ${isSelected ? 'var(--accent)' : model.is_active ? '#22c55e44' : 'var(--border-color)'}`,
        borderRadius: '0px',
        padding: '16px',
        cursor: 'pointer',
        background: isSelected ? 'var(--bg-elevated)' : 'var(--bg-secondary)',
        transition: 'border-color 0.15s, background 0.15s',
        position: 'relative',
      }}
    >
      {/* Insignias */}
      <div style={{ display: 'flex', gap: '6px', marginBottom: '10px', flexWrap: 'wrap' }}>
        {model.is_active && (
          <span style={{
            fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em',
            textTransform: 'uppercase', color: '#22c55e',
            background: '#22c55e18', border: '1px solid #22c55e44',
            padding: '2px 8px',
          }}>
            ● Activo en Producción
          </span>
        )}
        {isBaseline && (
          <span style={{
            fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em',
            textTransform: 'uppercase', color: '#94a3b8',
            background: 'var(--bg-elevated)', border: '1px solid var(--border-color)',
            padding: '2px 8px',
          }}>
            Baseline Heurístico
          </span>
        )}
        {!isBaseline && gain !== undefined && (
          <span style={{
            fontSize: '10px', fontWeight: 700, letterSpacing: '0.05em',
            textTransform: 'uppercase',
            color: gain >= 0 ? '#4ade80' : '#f87171',
            background: gain >= 0 ? '#4ade8018' : '#f8717118',
            border: `1px solid ${gain >= 0 ? '#4ade8044' : '#f8717144'}`,
            padding: '2px 8px',
          }}>
            {gain >= 0 ? '↑' : '↓'} F₁ {gain >= 0 ? '+' : ''}{(gain * 100).toFixed(1)}% vs Baseline
          </span>
        )}
      </div>

      {/* Nombre del algoritmo */}
      <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px', fontFamily: 'monospace' }}>
        {model.algorithm_name}
      </div>
      <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '10px', fontFamily: 'monospace' }}>
        {model.version_id}
      </div>
      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px', lineHeight: 1.4 }}>
        {model.description}
      </div>

      {/* Métricas rápidas */}
      {!isBaseline && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginBottom: '12px' }}>
          {[
            { label: 'Exactitud', value: fmtPct(model.metrics?.accuracy) },
            { label: 'F₁ Macro', value: fmtNum(model.metrics?.f1_macro) },
            { label: 'Precisión', value: fmtPct(model.metrics?.precision_macro) },
          ].map(({ label, value }) => (
            <div key={label} style={{
              background: 'var(--bg-primary)', padding: '8px', textAlign: 'center',
              border: '1px solid var(--border-color)',
            }}>
              <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                {value}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
                {label}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Métricas baseline */}
      {isBaseline && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginBottom: '12px' }}>
          {[
            { label: 'Exactitud', value: fmtPct(model.metrics?.accuracy) },
            { label: 'F₁ Macro', value: fmtNum(model.metrics?.f1_macro) },
            { label: 'Tipo', value: 'Heurístico' },
          ].map(({ label, value }) => (
            <div key={label} style={{
              background: 'var(--bg-primary)', padding: '8px', textAlign: 'center',
              border: '1px solid var(--border-color)',
            }}>
              <div style={{ fontSize: '14px', fontWeight: 700, color: '#94a3b8', fontFamily: 'monospace' }}>
                {value}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
                {label}
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          {fmtDate(model.created_at)}
        </span>
        {!model.is_active && !isBaseline && (
          <button
            id={`activate-model-${model.version_id}`}
            onClick={(e) => { e.stopPropagation(); onActivate(); }}
            disabled={activating}
            className="btn btn-secondary"
            style={{ fontSize: '11px', padding: '4px 12px' }}
          >
            {activating ? 'Activando...' : 'Activar en Producción'}
          </button>
        )}
      </div>
    </div>
  );
};

// ─── Sub-componente: Matriz de Confusión ─────────────────────────────────────

const ConfusionMatrix: React.FC<{ matrix: number[][]; labels: string[] }> = ({ matrix, labels }) => {
  if (!matrix || matrix.length === 0) return null;
  const maxVal = Math.max(...matrix.flat());

  return (
    <div>
      <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
        Matriz de Confusión
      </div>
      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'collapse', fontSize: '12px', width: '100%' }}>
          <thead>
            <tr>
              <th style={{ padding: '6px 10px', color: 'var(--text-muted)', textAlign: 'left', fontSize: '10px', textTransform: 'uppercase' }}>
                Real ↓ / Pred →
              </th>
              {labels.map((l) => (
                <th key={l} style={{ padding: '6px 10px', color: 'var(--text-secondary)', textAlign: 'center', fontSize: '10px' }}>
                  {l}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {matrix.map((row, i) => (
              <tr key={i}>
                <td style={{ padding: '6px 10px', color: 'var(--text-secondary)', fontSize: '11px', fontWeight: 600, whiteSpace: 'nowrap' }}>
                  {labels[i] ?? `Clase ${i}`}
                </td>
                {row.map((val, j) => {
                  const isDiag = i === j;
                  const intensity = maxVal > 0 ? val / maxVal : 0;
                  return (
                    <td key={j} style={{
                      padding: '8px 10px', textAlign: 'center', fontFamily: 'monospace',
                      fontWeight: isDiag ? 700 : 400,
                      fontSize: '13px',
                      background: isDiag
                        ? `rgba(74, 222, 128, ${0.1 + intensity * 0.4})`
                        : val > 0 ? `rgba(248, 113, 113, ${0.08 + intensity * 0.25})` : 'transparent',
                      color: isDiag ? '#4ade80' : val > 0 ? '#f87171' : 'var(--text-muted)',
                      border: '1px solid var(--border-color)',
                    }}>
                      {val}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ─── Sub-componente: Panel de Métricas Detalladas ────────────────────────────

const MetricsPanel: React.FC<{ model: ModelVersion }> = ({ model }) => {
  const m = model.metrics;
  const bc = m?.baseline_comparison;
  const fi = m?.feature_importances;
  const cm = m?.confusion_matrix;
  const LABELS = ['NO_MATCH', 'PARTIAL', 'MATCH'];

  return (
    <div style={{ display: 'grid', gap: '20px' }}>
      {/* Métricas numéricas */}
      <div>
        <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          Métricas de Evaluación en Conjunto de Prueba
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: '8px' }}>
          {[
            { label: 'Exactitud', value: fmtPct(m?.accuracy), highlight: true },
            { label: 'F₁ Macro', value: fmtNum(m?.f1_macro), highlight: true },
            { label: 'F₁ Ponderado', value: fmtNum(m?.f1_weighted) },
            { label: 'Precisión Macro', value: fmtPct(m?.precision_macro) },
            { label: 'Recall Macro', value: fmtPct(m?.recall_macro) },
            { label: 'Muestras Train', value: m?.train_sample_count?.toString() ?? '—' },
            { label: 'Muestras Test', value: m?.test_sample_count?.toString() ?? '—' },
          ].map(({ label, value, highlight }) => (
            <div key={label} style={{ background: 'var(--bg-primary)', padding: '12px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: highlight ? '20px' : '16px', fontWeight: 700, fontFamily: 'monospace', color: highlight ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                {value}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.03em', marginTop: '2px' }}>
                {label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comparativa vs Baseline */}
      {bc && (
        <div>
          <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Benchmarking Frente al Baseline Heurístico
          </div>
          <div style={{
            padding: '14px 16px',
            background: bc.superior_to_baseline ? '#22c55e0a' : '#f871710a',
            border: `1px solid ${bc.superior_to_baseline ? '#22c55e33' : '#f8717133'}`,
          }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '12px' }}>
              {[
                { label: 'Exactitud Baseline', value: fmtPct(bc.baseline_accuracy) },
                { label: 'F₁ Macro Baseline', value: fmtNum(bc.baseline_f1_macro) },
                { label: 'Ganancia en Exactitud', value: (bc.accuracy_gain >= 0 ? '+' : '') + fmtPct(bc.accuracy_gain), positive: bc.accuracy_gain >= 0 },
                { label: 'Ganancia en F₁', value: (bc.f1_gain >= 0 ? '+' : '') + fmtNum(bc.f1_gain), positive: bc.f1_gain >= 0 },
              ].map(({ label, value, positive }) => (
                <div key={label}>
                  <div style={{ fontSize: '15px', fontWeight: 700, fontFamily: 'monospace', color: positive !== undefined ? (positive ? '#4ade80' : '#f87171') : 'var(--text-secondary)' }}>
                    {value}
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
                    {label}
                  </div>
                </div>
              ))}
            </div>
            <div style={{ marginTop: '10px', fontSize: '12px', fontWeight: 600, color: bc.superior_to_baseline ? '#4ade80' : '#f87171' }}>
              {bc.superior_to_baseline
                ? '✓ El modelo supervisado supera al baseline heurístico en las métricas de evaluación científica.'
                : '⚠ El modelo supervisado no ha superado al baseline heurístico. Se recomienda acumular más revisiones o ajustar hiperparámetros.'}
            </div>
          </div>
        </div>
      )}

      {/* Importancia de características */}
      {fi && Object.keys(fi).length > 0 && (
        <div>
          <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Importancia de Características
          </div>
          <div style={{ display: 'grid', gap: '6px' }}>
            {Object.entries(fi)
              .sort(([, a], [, b]) => b - a)
              .map(([name, importance]) => (
                <div key={name} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: '160px', fontSize: '11px', color: 'var(--text-secondary)', fontFamily: 'monospace', flexShrink: 0 }}>
                    {name}
                  </div>
                  <div style={{ flex: 1, height: '6px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', position: 'relative', overflow: 'hidden' }}>
                    <div style={{ position: 'absolute', inset: 0, width: `${importance * 100}%`, background: 'var(--accent)', transition: 'width 0.5s' }} />
                  </div>
                  <div style={{ width: '48px', textAlign: 'right', fontSize: '11px', fontFamily: 'monospace', color: 'var(--text-primary)' }}>
                    {(importance * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Matriz de confusión */}
      {cm && <ConfusionMatrix matrix={cm} labels={LABELS} />}
    </div>
  );
};

// ─── Componente Principal ─────────────────────────────────────────────────────

export const ModelManagementView: React.FC = () => {
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [selectedModel, setSelectedModel] = useState<ModelVersion | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [training, setTraining] = useState(false);
  const [trainError, setTrainError] = useState<string | null>(null);
  const [activatingId, setActivatingId] = useState<string | null>(null);
  const [trainForm, setTrainForm] = useState<TrainModelRequest>({
    algorithm: 'calibrated_logistic',
    test_size: 0.25,
    use_bootstrap: true,
    auto_activate: false,
  });
  const [datasetCount, setDatasetCount] = useState<number | null>(null);

  const loadModels = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [modelList, stats] = await Promise.all([
        api.listModels(),
        api.getDatasetStats(),
      ]);
      setModels(modelList);
      setDatasetCount(stats.total_examples);
      if (!selectedModel && modelList.length > 0) {
        setSelectedModel(modelList[0]);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al cargar los modelos');
    } finally {
      setLoading(false);
    }
  }, [selectedModel]);

  useEffect(() => {
    loadModels();
  }, []);

  const handleTrain = async () => {
    setTraining(true);
    setTrainError(null);
    try {
      const newModel = await api.trainModel(trainForm);
      await loadModels();
      setSelectedModel(newModel);
    } catch (err: unknown) {
      setTrainError(err instanceof Error ? err.message : 'Error durante el entrenamiento');
    } finally {
      setTraining(false);
    }
  };

  const handleActivate = async (versionId: string) => {
    setActivatingId(versionId);
    try {
      await api.activateModel(versionId);
      await loadModels();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al activar el modelo');
    } finally {
      setActivatingId(null);
    }
  };

  // ─── Render ──────────────────────────────────────────────────────────────────

  return (
    <div style={{ maxWidth: '1360px', margin: '24px auto', padding: '0 20px' }}>

      {/* Encabezado */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, margin: '0 0 4px 0', color: 'var(--text-primary)', letterSpacing: '0.02em', textTransform: 'uppercase' }}>
            Gestión de Modelos de Aprendizaje Supervisado
          </h2>
          <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-muted)' }}>
            Entrenamiento calibrado, versionado y ciclo de vida de modelos para comparación curricular (Fase 2.0)
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {datasetCount !== null && (
            <div style={{
              padding: '6px 12px', border: '1px solid var(--border-color)',
              background: 'var(--bg-elevated)', fontSize: '12px', color: 'var(--text-secondary)',
            }}>
              <span style={{ color: 'var(--text-muted)' }}>Observaciones:</span>{' '}
              <span style={{ fontWeight: 700, fontFamily: 'monospace', color: 'var(--text-primary)' }}>
                {datasetCount}
              </span>
            </div>
          )}
          <button
            onClick={loadModels}
            className="btn btn-secondary"
            style={{ fontSize: '12px', padding: '6px 14px' }}
          >
            ↻ Actualizar
          </button>
          <a
            href={api.getDatasetExportFormatUrl('csv')}
            download="dataset_convcomp.csv"
            className="btn btn-secondary"
            style={{ fontSize: '12px', padding: '6px 14px', textDecoration: 'none', color: 'var(--text-secondary)' }}
          >
            ↓ Exportar CSV
          </a>
        </div>
      </div>

      {error && (
        <div style={{ padding: '12px 16px', background: '#f871710a', border: '1px solid #f8717133', color: '#f87171', fontSize: '13px', marginBottom: '20px' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '380px 1fr', gap: '20px', alignItems: 'start' }}>

        {/* Panel izquierdo: lista de modelos + panel de entrenamiento */}
        <div style={{ display: 'grid', gap: '16px' }}>

          {/* Panel de Entrenamiento */}
          <div style={{ border: '1px solid var(--border-color)', background: 'var(--bg-secondary)', padding: '18px' }}>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Nuevo Ciclo de Entrenamiento
            </div>

            {/* Algoritmo */}
            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '5px' }}>
                Algoritmo
              </label>
              <select
                id="train-algorithm-select"
                value={trainForm.algorithm}
                onChange={(e) => setTrainForm((f) => ({ ...f, algorithm: e.target.value as TrainModelRequest['algorithm'] }))}
                style={{
                  width: '100%', padding: '8px 10px', fontSize: '12px',
                  background: 'var(--bg-primary)', border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)', borderRadius: '0px', fontFamily: 'monospace',
                }}
              >
                <option value="calibrated_logistic">Regresión Logística Calibrada (Platt Scaling)</option>
                <option value="random_forest">Random Forest Explicable</option>
              </select>
            </div>

            {/* Tamaño de prueba */}
            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '5px' }}>
                Partición de Evaluación: {Math.round(trainForm.test_size * 100)}%
              </label>
              <input
                id="train-test-size-slider"
                type="range" min="0.1" max="0.4" step="0.05"
                value={trainForm.test_size}
                onChange={(e) => setTrainForm((f) => ({ ...f, test_size: parseFloat(e.target.value) }))}
                style={{ width: '100%', accentColor: 'var(--accent)' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                <span>10%</span><span>40%</span>
              </div>
            </div>

            {/* Opciones */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '14px' }}>
              {[
                { key: 'use_bootstrap', label: 'Bootstrap sintético si datos escasos (<20 revisiones)' },
                { key: 'auto_activate', label: 'Activar automáticamente si supera al baseline' },
              ].map(({ key, label }) => (
                <label key={key} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', cursor: 'pointer', fontSize: '12px', color: 'var(--text-secondary)' }}>
                  <input
                    id={`train-option-${key}`}
                    type="checkbox"
                    checked={trainForm[key as keyof TrainModelRequest] as boolean}
                    onChange={(e) => setTrainForm((f) => ({ ...f, [key]: e.target.checked }))}
                    style={{ marginTop: '2px', accentColor: 'var(--accent)' }}
                  />
                  {label}
                </label>
              ))}
            </div>

            {trainError && (
              <div style={{ padding: '8px 12px', background: '#f871710a', border: '1px solid #f8717133', color: '#f87171', fontSize: '12px', marginBottom: '12px' }}>
                {trainError}
              </div>
            )}

            <button
              id="train-model-btn"
              onClick={handleTrain}
              disabled={training}
              className="btn btn-primary"
              style={{ width: '100%', fontSize: '13px', padding: '10px', fontWeight: 600 }}
            >
              {training ? (
                <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                  <span style={{ display: 'inline-block', width: '12px', height: '12px', border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
                  Entrenando modelo...
                </span>
              ) : 'Entrenar Nuevo Modelo'}
            </button>
          </div>

          {/* Lista de modelos */}
          {loading ? (
            <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
              Cargando versiones de modelos...
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '8px' }}>
              {models.map((model) => (
                <ModelCard
                  key={model.version_id}
                  model={model}
                  isSelected={selectedModel?.version_id === model.version_id}
                  onSelect={() => setSelectedModel(model)}
                  onActivate={() => handleActivate(model.version_id)}
                  activating={activatingId === model.version_id}
                />
              ))}
              {models.length === 0 && (
                <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px', border: '1px solid var(--border-color)' }}>
                  No hay versiones de modelos registradas aún.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Panel derecho: métricas detalladas */}
        <div>
          {selectedModel ? (
            <div style={{ border: '1px solid var(--border-color)', background: 'var(--bg-secondary)', padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
                <div>
                  <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '2px' }}>
                    {selectedModel.algorithm_name}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                    {selectedModel.version_id} · {fmtDate(selectedModel.created_at)}
                  </div>
                </div>
                {selectedModel.is_active && (
                  <span style={{
                    fontSize: '11px', fontWeight: 700, color: '#22c55e',
                    background: '#22c55e18', border: '1px solid #22c55e44',
                    padding: '4px 12px', letterSpacing: '0.04em', textTransform: 'uppercase',
                  }}>
                    ● Activo en Producción
                  </span>
                )}
              </div>

              {selectedModel.metrics?.type !== 'heuristic_baseline' ? (
                <MetricsPanel model={selectedModel} />
              ) : (
                <div style={{ padding: '24px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', textAlign: 'center' }}>
                  <div style={{ fontSize: '32px', marginBottom: '12px' }}>⚙</div>
                  <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px', fontWeight: 600 }}>
                    Motor Heurístico Bipartito-Adaptativo (Baseline)
                  </div>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)', maxWidth: '480px', margin: '0 auto', lineHeight: 1.6 }}>
                    Este es el algoritmo determinista de comparación curricular activo. Combina asignación global bipartita (Algoritmo Húngaro), pesos adaptativos y vocabulario canónico de acrónimos técnicos. Entrenar un modelo supervisado permite sustituirlo por un clasificador calibrado probabilísticamente.
                  </p>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', marginTop: '20px' }}>
                    {Object.entries(selectedModel.parameters ?? {}).slice(0, 4).map(([k, v]) => (
                      <div key={k} style={{ background: 'var(--bg-secondary)', padding: '10px', border: '1px solid var(--border-color)' }}>
                        <div style={{ fontSize: '13px', fontWeight: 700, fontFamily: 'monospace', color: 'var(--text-primary)' }}>
                          {typeof v === 'number' ? v.toFixed(2) : String(v)}
                        </div>
                        <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
                          {k.replace('w_', 'w. ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div style={{
              padding: '60px', textAlign: 'center', color: 'var(--text-muted)',
              border: '1px dashed var(--border-color)', background: 'var(--bg-secondary)',
              fontSize: '13px',
            }}>
              Selecciona un modelo de la lista para ver sus métricas detalladas.
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};
