# Despliegue Docker y análisis SonarQube

Ejecutar los comandos desde la raíz del repositorio. Requiere Docker Engine
con contenedores Linux y Docker Compose v2 o superior. En Windows, iniciar
Docker Desktop y comprobar `docker version` antes de continuar.

## Instancia local preparada el 2026-10-15

La aplicación de este equipo utiliza <http://localhost:5173>. Se unificó este
puerto en `.env`, `.env.example` y el valor predeterminado de Compose para
coincidir con la dirección de acceso del usuario. La primera validación usó
18080; la instancia actual publica 5173 y Nginx escucha internamente en 8080.

SonarQube está en <http://localhost:9000>, con el proyecto `convcomp` creado.
El usuario es `admin` y su contraseña aleatoria está en `SONAR_ADMIN_PASSWORD`
dentro de `.env`. `SONAR_TOKEN` contiene el token de análisis del proyecto;
`SONAR_DB_PASSWORD` corresponde a PostgreSQL. La contraseña inicial `admin`
ya fue reemplazada. Estos valores locales están excluidos de Git.

La prueba de persistencia dejó un PDF llamado
`validacion_docker_sintetica.pdf` en la instancia Docker. El almacenamiento de
desarrollo del repositorio se conserva independiente.

## Aplicación

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 180
docker compose ps
Invoke-RestMethod http://localhost:5173/api/health
```

En Linux/macOS, crear `.env` si no existe con `[ -f .env ] || cp .env.example .env`
y consultar salud con `curl -f http://localhost:5173/api/health`. La aplicación
está disponible en <http://localhost:5173>. `APP_PORT` cambia el puerto publicado.
Docker y el servidor Vite de desarrollo deben usar puertos distintos cuando
se ejecutan al mismo tiempo; para esta instancia Docker ocupa 5173.

El frontend se compila con Node 24 y se sirve con Nginx sin privilegios en
el puerto 8080. Usa `/api` como URL de API, de modo que el navegador contacta
al mismo origen. Nginx reenvía `/api/` al backend dentro de la red Docker y
conserva la ruta completa, incluidos parámetros y descargas PDF.
`VITE_API_URL` se incorpora durante la compilación; cambiar una variable del
contenedor Nginx después de construir la imagen no modifica esa URL.

El backend usa Python 3.11, PyTorch CPU y Uvicorn con un trabajador, sin
recarga de desarrollo. Ejecuta como usuario 10001 y mantiene la base SQLite.
PostgreSQL en el archivo de calidad pertenece exclusivamente a SonarQube.

Los volúmenes `app_data`, `app_reports` y `huggingface_cache` conservan la
base SQLite, PDF cargados, modelos supervisados, reportes y caché de embeddings.
La instancia empieza con almacenamiento nuevo; no importa datos de desarrollo.
Las imágenes excluyen datos, modelos locales, entornos y credenciales.
Sentence Transformers descarga su modelo al primer uso si hay conexión;
si falla, la aplicación utiliza su respaldo determinista existente. La
comprobación de salud de la API no acredita que el modelo se haya descargado.

```powershell
docker compose logs --tail 100 backend frontend
docker compose down
docker compose up -d --wait
```

`down` conserva los volúmenes. No utilizar `down -v` cuando se desee conservar
la información. Para comprobar persistencia, cargar un PDF, recrear los
contenedores con `docker compose up -d --force-recreate --wait` y verificar
que sigue listado y se puede descargar. Para respaldar SQLite junto con los
PDF y modelos de forma consistente, detener el backend antes de copiar sus
volúmenes y conservar las mismas rutas al restaurar.

Por defecto el puerto se publica en `127.0.0.1`. Para acceso desde otros
equipos, configurar `APP_BIND_ADDRESS` y colocar el servicio detrás del proxy
HTTPS y del control de acceso de la institución. La versión actual de la
aplicación conserva sus revisores declarados sin autenticación.

## Servidor SonarQube

Editar `.env` y asignar una contraseña propia no vacía a `SONAR_DB_PASSWORD`.
No es la contraseña del usuario administrador de SonarQube. El archivo `.env`
está excluido de Git; `.env.example` no contiene secretos.

SonarQube requiere recursos adicionales para Java y Elasticsearch. Comprobar
en el host Linux de Docker `vm.max_map_count >= 524288` y
`fs.file-max >= 131072`. Compose configura los límites del contenedor de
131072 descriptores y 8192 procesos. En Docker Desktop estos parámetros
corresponden a su máquina Linux. Consultar los pasos según el host en la
[documentación oficial de requisitos Linux](https://docs.sonarsource.com/sonarqube-community-build/server-installation/pre-installation/linux).

```powershell
docker compose -f compose.sonarqube.yaml config --quiet
docker compose -f compose.sonarqube.yaml up -d --wait --wait-timeout 900
```

Abrir <http://localhost:9000> (`SONAR_PORT` permite cambiar el puerto). En una
instancia nueva, iniciar con `admin` / `admin`, cambiar la contraseña y crear
el proyecto manualmente con clave `convcomp`. Generar un token de análisis de
ese proyecto y guardarlo en `SONAR_TOKEN` dentro de `.env`. El token necesita
permiso para ejecutar análisis. No se envían credenciales a Git ni se crea
automáticamente un administrador.

SonarQube usa PostgreSQL 17, volúmenes propios y una red independiente de la
aplicación. Las etiquetas predeterminadas `community`, `latest` y las de las
imágenes de aplicación reciben actualizaciones. Para despliegues repetibles,
fijar etiquetas concretas o digest revisados antes de construir; las imágenes
de calidad se pueden seleccionar con `SONARQUBE_IMAGE` y `SONAR_SCANNER_IMAGE`.
Consultar las notas de actualización de SonarQube antes de cambiar su imagen
sobre una base existente.

## Cobertura y análisis

Generar los reportes con la suite Python dentro de Docker:

```powershell
docker compose -f compose.sonarqube.yaml --profile tools run --rm --build backend-tests
```

El comando debe terminar con código 0 antes de ejecutar el escáner. Produce
`.reports/coverage.xml` (Cobertura), `.reports/pytest.xml` (JUnit) y el resumen
de cobertura por consola. La etapa Docker `test` descarga previamente el modelo
`paraphrase-multilingual-MiniLM-L12-v2`, necesario para la prueba de paráfrasis.
La construcción requiere acceso a Hugging Face; después las pruebas usan ese
modelo en modo offline y almacenamiento temporal. Esta caché pertenece solo
a la imagen de pruebas. No ejecuta Playwright ni acredita rendimiento científico
institucional.

El montaje del repositorio permite conservar los reportes en el host. En
Linux, ajustar `LOCAL_UID` y `LOCAL_GID` en `.env` a los valores de `id -u` e
`id -g`, para que el servicio de pruebas pueda escribirlos. El escáner utiliza
el usuario de su imagen; necesita lectura del repositorio y reportes. Su
directorio de trabajo está en `/tmp/sonar-work` y su caché en un volumen.

Alternativamente, generar cobertura en el entorno Python local:

```powershell
.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt
.venv/Scripts/python.exe -m pytest tests --cov --cov-report=term-missing --cov-report=xml:.reports/coverage.xml --junitxml=.reports/pytest.xml
```

En Linux/macOS usar `.venv/bin/python`. `.coveragerc` guarda rutas relativas
para importar reportes aunque las pruebas y el escáner usen directorios
distintos, conforme a la [guía de cobertura Python de SonarQube](https://docs.sonarsource.com/sonarqube-server/analyzing-source-code/test-coverage/python-test-coverage).

Ejecutar el análisis después de generar los reportes correctamente:

```powershell
docker compose -f compose.sonarqube.yaml --profile tools run --rm sonar-scanner
```

`sonar-project.properties` incluye el backend Python y el frontend
TypeScript/React, e identifica las pruebas Python, Vitest y Playwright. Antes
del análisis, ejecutar también `npm.cmd run test:coverage` desde `frontend`.
Importa cobertura Python y `frontend/coverage/lcov.info`, sin exclusiones de
carpetas de fuentes. Los XML Python y LCOV deben versionarse para la entrega
académica; los demás artefactos de `.reports` permanecen ignorados. Consulte
[EVALUACION_CALIDAD.md](EVALUACION_CALIDAD.md) para el gate de 20 puntos,
los metadatos de entrega y la verificación reproducible.

El escáner recibe `SONAR_TOKEN` por entorno y se conecta internamente a
`http://sonarqube:9000`, según la [guía oficial del escáner Docker](https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/scanners/sonarscanner).
Espera el resultado del Quality Gate hasta 600 segundos y devuelve un error
si el gate falla o vence el plazo. Los hallazgos, métricas y condiciones se
consultan en <http://localhost:9000/dashboard?id=convcomp>. Un análisis enviado
correctamente no implica que el proyecto supere el Quality Gate.

```powershell
docker compose -f compose.sonarqube.yaml logs --tail 100 sonarqube sonar-db
docker compose -f compose.sonarqube.yaml down
```

## Validación realizada

El 2026-10-15 se construyeron y arrancaron las imágenes, se verificó la
persistencia tras recrear los contenedores y se ejecutaron las 99 pruebas con
cobertura y el análisis real de SonarQube. Consulte
[RESULTADO_SONARQUBE.md](RESULTADO_SONARQUBE.md) para las métricas, los hallazgos
y el alcance del Quality Gate. La bitácora se conserva en `docs/TASKS.md`.

