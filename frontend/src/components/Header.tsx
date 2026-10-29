import { ArrowUpRight, BookOpenCheck } from 'lucide-react';
import type { AppTab } from '../types';

interface HeaderProps {
  currentTab: AppTab;
  onSelectTab: (tab: HeaderProps['currentTab']) => void;
  hasActiveComparison: boolean;
  onOpenGuide?: () => void;
}

const navigation: { tab: HeaderProps['currentTab']; label: string; name: string }[] = [
  { tab: 'upload', label: 'Evaluar', name: 'Nueva Evaluación' },
  { tab: 'batches', label: 'Por lotes', name: 'Comparación por lotes' },
  { tab: 'dashboard', label: 'Sílabos', name: 'Registro de Sílabos' },
  { tab: 'results', label: 'Resultados', name: 'Informe Técnico' },
  { tab: 'dataset', label: 'Auditoría', name: 'Registro de Auditoría' },
  { tab: 'models', label: 'Modelos IA', name: 'Modelos IA' },
];

export const Header = ({ currentTab, onSelectTab, hasActiveComparison, onOpenGuide }: HeaderProps) => (
  <header className="site-header">
    <a className="skip-link" href="#main-content">Ir al contenido</a>
    <div className="navigation-shell">
      <button className="brand" type="button" onClick={() => onSelectTab('upload')} aria-label="ConvComp, inicio">
        <span className="brand-mark"><BookOpenCheck size={23} strokeWidth={1.8} /></span>
        <span>ConvComp<span className="brand-dot">.</span></span>
      </button>
      <nav className="primary-navigation" aria-label="Navegación principal">
        {navigation.filter(item => item.tab !== 'results' || hasActiveComparison).map(item => (
          <button key={item.tab} type="button" aria-label={item.name}
            id={item.tab === 'models' ? 'nav-tab-models' : undefined}
            aria-current={currentTab === item.tab ? 'page' : undefined}
            className={`navigation-link${currentTab === item.tab ? ' is-active' : ''}`}
            onClick={() => onSelectTab(item.tab)}>
            {item.label}
          </button>
        ))}
      </nav>
      {onOpenGuide && <button className="btn btn-primary navigation-guide" type="button" onClick={onOpenGuide}
        title="Consultar Criterios Metodológicos y Glosario">
        Guía Metodológica <ArrowUpRight size={15} aria-hidden="true" />
      </button>}
    </div>
  </header>
);
