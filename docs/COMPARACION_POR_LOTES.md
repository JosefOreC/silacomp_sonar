# Comparación por lotes — versión 3.3.0

La vista **Por lotes** compara un sílabo objetivo con entre uno y cinco
candidatos del catálogo. Cada pareja produce una comparación independiente,
con sus evidencias, revisión humana e informe PDF habituales. Es una
pre-evaluación computacional explicable de correspondencia académica; la
decisión de convalidación corresponde a las autoridades universitarias.

## Uso en la interfaz

1. Registre los documentos desde Evaluar si todavía no están en el catálogo.
2. Abra **Por lotes**, seleccione el objetivo y marque hasta cinco candidatos.
   La búsqueda admite asignatura, universidad y archivo, sin distinguir tildes.
3. Pulse **Comparar candidatos seleccionados**. Los resultados muestran ambas
   coberturas, afinidad global y acceso al análisis y PDF de cada candidato.
4. Descargue el resumen mediante **Exportar lote JSON**. **Lotes guardados**
   permite recuperar los últimos veinte lotes después de recargar la página.
5. Use **Preparar otro lote** para iniciar otra ejecución explícita.

El orden se determina por cobertura del objetivo descendente, después por
afinidad global descendente y finalmente por identificador de candidato
ascendente. Las coberturas de distintos candidatos **no se suman**: pueden
cubrir los mismos temas. Los contadores del lote describen su ejecución y
no representan cobertura curricular conjunta ni calidad científica.

## Alcance y límites

- Se reutiliza el motor existente de comparación de pares. No cambia su
  algoritmo, sus predicciones originales ni las revisiones humanas.
- Todo el lote usa una versión fija del modelo y copias de los pesos y umbrales
  de referencia. Si hay un modelo activo, se carga en una instancia propia;
  un cambio de activación durante el lote no altera los candidatos siguientes.
  Si ese modelo no puede cargarse, se devuelve 409 sin sustituirlo por baseline.
  Cuando no hay modelo activo se usa `bipartite-adaptive-002`.
- El objetivo y los candidatos deben existir y ser distintos; no se permiten
  candidatos repetidos. El objetivo debe contener temas identificables.
- Antes de crear el lote se limita la suma de
  `temas_objetivo × temas_candidato` a **20 000 pares**, además del máximo de
  cinco candidatos. No se aceptan pesos o umbrales personalizados en esta API.
- Un candidato sin temas guarda `NO_CONTENT`; un fallo al comparar guarda
  `COMPARISON_FAILED` con un mensaje público genérico. Los candidatos restantes
  continúan. Los fallidos no reciben puntuaciones artificiales ni informe PDF.
- La ejecución es síncrona y secuencial. No incorpora colas, cancelación,
  reanudación automática, autenticación ni gestión de usuarios de Fase 4.

## API e idempotencia

```http
POST /api/comparison-batches
Content-Type: application/json

{
  "request_id": "1dc72f46-6ba1-4219-bbfa-1334bda6a14a",
  "objective_syllabus_id": "SYL-objetivo",
  "compared_syllabus_ids": ["SYL-candidato-a", "SYL-candidato-b"]
}
```

El UUID obligatorio identifica una solicitud. El ID persistido es
`CB-` seguido de sus 32 caracteres hexadecimales sin guiones.

| Operación | Resultado |
|---|---|
| POST nuevo | 201 con resultados y estado del lote |
| POST con mismo UUID, objetivo y candidatos en el mismo orden | 200; consulta lo guardado sin ejecutar otra vez |
| POST con UUID existente y otros documentos u orden | 409; requiere otra solicitud |
| Documentos inexistentes | 404 antes de guardar el lote |
| Selección, UUID, campos o presupuesto inválidos | 422 antes de guardar el lote |
| `GET /api/comparison-batches?limit=20` | Historial reciente; admite de 1 a 50 |
| `GET /api/comparison-batches/{id}` | Estado y resultados persistidos; 404 si no existe |
| `GET /api/comparison-batches/{id}/export` | Descarga JSON con el mismo contrato |

La respuesta conserva objetivo, candidatos, fecha, modelo, pesos, umbrales,
regla de ranking, IDs ordenados y resultados individuales. `global_score` de
cada resultado está entre 0 y 1; sus coberturas, entre 0 y 100. No existe una
puntuación global del conjunto. Los enlaces individuales siguen usando las
API de comparaciones e informes existentes.

## Persistencia y recuperación

SQLite incorpora tres tablas aditivas: `comparison_batches`,
`comparison_batch_results` y `comparison_batch_completions`. El UUID se reclama
atómicamente; cada resultado y el cierre se insertan sin sobreescribirlos.
El historial conserva los títulos y universidades observados al crear el lote.

| Estado | Significado |
|---|---|
| `RUNNING` | Todavía no se ha guardado un cierre; puede estar ejecutándose o haberse interrumpido |
| `COMPLETED` | Todos los candidatos tienen comparación guardada |
| `PARTIAL` | El lote terminó con al menos una comparación válida y al menos un error |
| `FAILED` | El lote terminó sin comparaciones válidas |

La interfaz conserva el UUID al reintentar una petición fallida y ofrece
**Consultar solicitud guardada** cuando se pierde su respuesta. También permite
actualizar el historial y un resultado. Una recarga recupera los lotes que ya
alcanzaron la persistencia; no conserva selecciones que no se enviaron.

Si el proceso se interrumpe, los resultados ya insertados permanecen disponibles.
Repetir el UUID consulta el avance y **no reanuda** la ejecución. Para continuar,
cree otro lote solo con los candidatos pendientes. La comparación individual
y su resultado en el lote no comparten una transacción: una interrupción entre
ambos guardados puede dejar un análisis accesible en el registro individual,
aunque todavía no figure en el lote. Consulte ese registro antes de repetirlo.

## Validación

Las pruebas de dominio y API cubren límites, ranking, idempotencia, persistencia,
interrupciones, errores por candidato y modelo fijo durante la ejecución. Las
pruebas UI cubren selección, búsqueda, reintentos e historial. Dos flujos de
Chrome verifican API real aislada, descarga JSON/PDF, acceso al análisis,
recarga y resultados parciales en móvil. Los datos controlados de esas pruebas
no demuestran rendimiento científico sobre sílabos institucionales.

Resultados de calidad y despliegue: [RESULTADO_SONARQUBE.md](RESULTADO_SONARQUBE.md).
Instrucciones de navegador: [VALIDACION_NAVEGADOR.md](VALIDACION_NAVEGADOR.md).
