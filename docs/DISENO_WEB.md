# Rediseño web de ConvComp — Sesión 30

## Referencias y alcance

El usuario proporcionó dos capturas de la composición SaaS de Askai y una
captura adicional de una interfaz académica violeta. Estas imágenes, recibidas
en la conversación, son la referencia visual directa: navegación blanca,
titular central destacado, fondo degradado que se funde con el blanco,
panel de producto y tarjetas de funcionalidades con espacio entre elementos.

El enlace original de [Dribbble](https://dribbble.com/shots/27822756-SaaS-Landing-Page-AI-Search-Analytics-Platform)
respondió HTTP 202 sin contenido en este entorno. La implementación se basa
en las imágenes aportadas después por el usuario.

Se adapta la aplicación existente en el repositorio. La estructura muestra
los documentos y acciones reales de ConvComp; no incorpora precios,
testimonios, cifras comerciales ni una autenticación que no exista.

## Paleta y composición

| Uso | Color |
|---|---|
| Violeta profundo | `#300052` |
| Violeta principal | `#4B0082` |
| Acento y acciones | `#6500A8` |
| Acento luminoso del fondo | `#7300B9` |
| Lavanda de selección | `#F1E7FA` |
| Fondo general | `#FAF9FC` |
| Paneles | `#FFFFFF` |
| Texto principal | `#20162C` |
| Texto secundario | `#574B63` |

Los estados académicos conservan verde, ámbar, violeta y rojo diferenciados;
el violeta de marca no sustituye el significado de las clasificaciones.
La tipografía utiliza Inter con fuentes de sistema alternativas y monoespaciada
para valores técnicos. Los estilos compartidos están en `frontend/src/index.css`.

## Implementación

- Navegación blanca adaptable, marca de libro y favicon propio, sección activa,
  enlace para saltar al contenido y acceso a la guía.
- Inicio con titular, llamadas a evaluación/metodología y panel real de carga.
  La transición visual conduce al formulario, no a una captura ficticia.
- Un panel reutilizable por documento, con catálogo, archivo, institución,
  asignatura, estado de procesamiento y errores recuperables. Los documentos
  seleccionados se identifican como «Listo», sin implicar convalidación.
- Tarjetas informativas de evidencia, cobertura bidireccional, revisión humana
  y trazabilidad. Cada capacidad corresponde a funciones existentes.
- Tema claro aplicado al catálogo, resultados, auditoría, modelos y modales.
  El visor espacial conserva su contexto oscuro y la geometría de las regiones.
- Guía adaptable con navegación interna, foco contenido, cierre con Escape y
  restauración del foco. Se mantienen los contratos de API y las predicciones.
- Metadatos HTML en español y descargo institucional en todas las vistas,
  mediante el pie compartido.

## Validación ejecutada

El Paquete 33 de [TASKS.md](TASKS.md) registra el avance. Aprobaron **120 pruebas
Vitest** y **6 pruebas de navegador** en **42,7 s**. Se comprobó el flujo de
ambos documentos y sus metadatos, errores/reintentos y el teclado/foco de la guía.
Las pruebas de navegador cubren escritorio 1440 × 1050 y móvil 390 × 844,
incluyendo navegación, ausencia de desbordamiento y los experimentos existentes.
Se inspeccionaron las capturas de inicio, modelos y guía; los textos pequeños
de catálogo, estados y archivos se ajustaron a un contraste de al menos 4,5:1
en sus fondos claros correspondientes.

LCOV regenerado: **88,86%** de líneas, **75,77%** de ramas, **87,26%** de
sentencias y **78,93%** de funciones. Tipos, lint y build aprobados. El informe
de [SonarQube](RESULTADO_SONARQUBE.md) registra el análisis final y los criterios
para conservar la puntuación máxima.
El backend permanece sin cambios en esta sesión; su XML/JUnit proviene de la
validación de 137 pruebas de la sesión 29 sobre el mismo código de backend.

Análisis final `18cb74aa-78aa-4cac-ae4b-93d7dd9793a1`: **Quality Gate PASSED**,
**20/20 estimado localmente**, A/A/A, cero hallazgos, **85,6%** de cobertura global
y **0,8%** de duplicación. El verificador terminó con código 0 y `cumple: true`.

## Entorno local y evidencias

La web se publica con Docker en <http://localhost:5173>, manteniendo los
volúmenes de la aplicación. El frontend se compila con su Dockerfile normal.
Se detectaron cuatro fuentes antiguas en la imagen de API anterior; se actualizó
su capa de código desde `backend/app` sobre la imagen local de dependencias,
conservando la base anterior como `convcomp-backend:runtime-session30`.
La construcción completa sigue definida en `backend/Dockerfile`.
Se comprobó por SHA-256 que todas las fuentes Python en ejecución coinciden con
el repositorio; `pip check` no detectó incompatibilidades. API y catálogo HTTP
200, sin errores JavaScript ni desbordamiento horizontal móvil en la publicación.

Las evidencias locales, ignoradas por Git, incluyen:

- `.reports/session30-home-desktop.png` y `session30-home-mobile.png`.
- `.reports/session30-guide-desktop.png` y `session30-guide-mobile.png`.
- `.reports/session30-models-mobile.png`.
- `.reports/session30-docker-desktop.png` y `session30-docker-check.json`.
- `.reports/session30-frontend-tests.log`, `session30-frontend-checks.log`
  y `session30-browser-tests.log`.
- `.reports/session30-docker-final.log`, `session30-backend-refresh.log`
  y `Dockerfile-code-refresh`, que documentan la actualización local.

El rediseño no incluye una validación exhaustiva de WCAG, otros navegadores
ni experimentos científicos institucionales. Las pruebas visuales no modifican
la base de desarrollo ni entrenan/activan sus modelos.
