# Reglas de Implementación y Guía del Proyecto (ConvComp)

Al trabajar en este repositorio, debes cumplir estrictamente las siguientes reglas definidas en [REGLAS_IMPLEMENTACION.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/REGLAS_IMPLEMENTACION.md):

1. **Clean Architecture / Monolito Modular:**
   - `backend/app/domain/`: Entidades puras y reglas de negocio sin dependencias externas (sin FastAPI, ORM, PyMuPDF, scikit-learn o PyTorch).
   - `backend/app/application/`: Casos de uso y puertos/interfaces.
   - `backend/app/infrastructure/`: Adaptadores técnicos (PDF, embeddings, persistencia, reportes).
   - `backend/app/api/`: Controladores FastAPI y esquemas Pydantic.
   - `frontend/`: React + TypeScript con Vite, separación estricta de componentes, páginas y servicios API. Prohibido el uso de `any`.

2. **Prohibiciones Clave:**
   - NO usar LLMs como jueces evaluadores automáticos o árbitros de convalidación.
   - NO sobreescribir las predicciones originales de la IA (`ContentMatch`) con las decisiones humanas (`Review`). Ambas deben coexistir de forma inmutable.
   - NO afirmar en informes ni pantallas que un curso está "oficialmente convalidado"; siempre indicar que es una "pre-evaluación computacional explicable de correspondencia académica".
   - NO implementar microservicios.

3. **Protocolo Obligatorio de Actualización de TASKS (`docs/TASKS.md`):**
   - Al iniciar cada sesión: revisar tareas pendientes en [TASKS.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/TASKS.md) y marcar en progreso `[/]` las que se vayan a abordar.
   - Al finalizar cada sesión:
     - Marcar como `[x]` las tareas completadas y probadas.
     - Actualizar la tabla del Resumen Ejecutivo de Avance con los porcentajes reales.
     - Redactar la entrada correspondiente en la **Bitácora de Sesiones de Trabajo** (fecha, objetivos, tareas completadas, decisiones técnicas, bloqueadores y próximas tareas).
