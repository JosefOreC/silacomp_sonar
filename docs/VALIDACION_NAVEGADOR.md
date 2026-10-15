# Validación integrada de evaluación científica

La suite usa Chromium real, el frontend de Vite y los endpoints FastAPI sobre una base temporal. Verifica la integración del panel de evaluación científica con la API. La extracción de PDFs y el rendimiento de embeddings quedan fuera de esta suite: las anotaciones, vectores y modelo son fixtures controlados reutilizados de las pruebas de integración.

## Preparación

Prepare `.venv` en la raíz con `backend/requirements.txt` y las dependencias de frontend del lockfile. Desde `frontend`, en PowerShell:

```powershell
npm.cmd ci
npx.cmd playwright install chromium
npm.cmd run test:browser
```

Si ya dispone de Chromium o Chrome instalado, puede evitar la descarga proporcionando la ruta al ejecutable:

```powershell
$env:CONVCOMP_BROWSER_EXECUTABLE = 'C:/ruta/a/chrome.exe'
npm.cmd run test:browser
```

La instalación normal usa la versión de Chromium correspondiente a Playwright. El override es opcional y permite usar una instalación local compatible. La sesión de validación utilizó Chromium disponible en la caché local; no descargó paquetes ni modelos por red.

## Aislamiento y ejecución

Los puertos locales `18765` (API) y `18766` (frontend) deben estar libres. La preparación no reutiliza servidores de desarrollo. Arranca procesos directamente y los cierra al terminar; en Windows evita depender de la enumeración de árboles de procesos con WMI/taskkill.

`tests/browser/serve.py` fija rutas temporales de datos e informes antes de importar la aplicación. Prepara dos comparaciones independientes con consenso exhaustivo, una comparación incompleta y un clasificador controlado; solo después habilita el servidor local. No agrega endpoints de preparación o borrado a la aplicación de producción. Se conservan la base de desarrollo, sus modelos y los informes existentes.

Las pruebas usan una sola ejecución concurrente para evitar escrituras superpuestas sobre el servidor temporal. Cada prueba crea los recursos que necesita y puede seleccionarse con `npm.cmd run test:browser -- --grep "fallo de consulta"`. Las respuestas simuladas se limitan a los casos de error de consulta y estado vacío; el flujo de reserva, ejecución, exportación y recuperación utiliza la API real.

## Casos cubiertos

1. Crear una reserva de dos comparaciones, impedir versiones iguales, ejecutar baseline contra candidato, comprobar F1, descargar el informe y recuperarlo tras una nueva carga. Verificar que el modelo activo conserva el baseline y que no hay excepciones JavaScript. Comprobar valores legibles de pesos y umbrales.
2. Intentar reservar una matriz incompleta, mostrar el conflicto de consenso y comprobar que no se guardó otra reserva.
3. Simular un fallo de consulta, reintentar y verificar que el conjunto disponible queda seleccionado y se elimina el error.
4. Mostrar instrucciones sin estudios y deshabilitar acciones cuyos datos todavía están incompletos.

## Evidencias y límites

El comando muestra el resultado de cada caso y genera `frontend/playwright-report/index.html`. Para abrirlo, ejecute `npm.cmd run test:browser:report`. Las trazas y capturas de fallos quedan en `frontend/test-results`; el primer caso guarda también `evaluacion-reservada.png` con el resultado completo. Estos archivos generados están excluidos de Git.

La suite verifica un viewport de escritorio de 1440 × 1000 en Chromium. No acredita compatibilidad móvil, otros navegadores, identidad real de revisores ni rendimiento científico con datos institucionales. Tampoco ejecuta entrenamiento real, OCR, revisión desde el visor o autenticación. La aceptación manual por usuarios sigue pendiente.
