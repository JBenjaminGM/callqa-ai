# 📋 Requerimientos Funcionales y No Funcionales

**Proyecto:** CallQA AI — Plataforma de QA para Call Center
**Versión:** 1.0 — Vista previa para evaluación

---

## 1. Requerimientos Funcionales (RF)

Los requerimientos funcionales describen **qué debe hacer** el sistema. Cada uno incluye su criterio de aceptación.

### Módulo: Autenticación, Usuarios y Roles

#### RF-01: Login

**Descripción:** El sistema debe permitir el inicio de sesión mediante email y contraseña.

**Criterio de aceptación:**

- Dado un email y contraseña válidos, el usuario accede según su rol (asesor → `/mi-panel`; admin/jefe → `/dashboard`)
- El endpoint `POST /auth/login` tiene rate limit de 5 intentos / 15 minutos
- El sistema genera un JWT firmado para gestionar la sesión (con refresh y logout)
- `GET /auth/me` devuelve el `role` y el `agent_id` del usuario
- El login **ya no muestra credenciales demo** en pantalla

**Prioridad:** Alta

---

#### RF-02: Roles y control de acceso

**Descripción:** El sistema debe diferenciar tres roles: `admin`, `jefe` y `asesor`.

**Criterio de aceptación:**

- `admin` y `jefe` comparten los mismos permisos por ahora (gestión + analítica global), resueltos por el helper `is_manager`; el rol por defecto es `jefe`
- `asesor` solo accede a su ficha, sus llamadas y su panel "Mi rendimiento"; está vinculado a su ficha de ejecutivo vía `User.agent_id`
- La dependencia `require_manager` protege los endpoints de gestión
- El asesor recibe **403** al intentar el dashboard global, subir/asignar/reintentar/eliminar llamadas, la configuración o la gestión de ejecutivos
- El frontend aplica navegación, guard y redirección por rol

**Prioridad:** Alta

---

#### RF-03: Crear login de asesor

**Descripción:** Un manager debe poder crear la cuenta de acceso de un ejecutivo.

**Criterio de aceptación:**

- `POST /agents/{id}/login` (solo manager) crea el `User` con rol `asesor` y lo vincula al `Agent`
- El email del asesor corresponde al del ejecutivo
- El seed crea las cuentas: `admin@callqa.com` (admin), `jefe@callqa.com` (jefe) y un asesor por cada ejecutivo demo
- El seed **ya no imprime contraseñas** por consola

**Prioridad:** Alta

---

### Módulo: Gestión de Ejecutivos

#### RF-04: Crear ejecutivo

**Descripción:** El manager debe poder registrar ejecutivos en el sistema.

**Criterio de aceptación:**

- Campos requeridos: nombre, email; opcional: campaña asignada
- El email debe ser único en el sistema
- `POST /agents` requiere rol manager

**Prioridad:** Alta

---

#### RF-05: Editar ejecutivo

**Descripción:** El manager debe poder modificar datos de ejecutivos existentes.

**Criterio de aceptación:**

- `PUT /agents/{id}` (solo manager)
- Los cambios se reflejan inmediatamente

**Prioridad:** Alta

---

#### RF-06: Desactivar ejecutivo

**Descripción:** El manager debe poder desactivar (no eliminar) ejecutivos.

**Criterio de aceptación:**

- `DELETE /agents/{id}` (solo manager) marca el ejecutivo como inactivo
- Un ejecutivo desactivado no aparece en los formularios de subida
- Su historial de llamadas permanece accesible

**Prioridad:** Media

---

### Módulo: Campañas y Nota de Producto

#### RF-07: Gestionar campañas

**Descripción:** El manager debe poder crear, editar y eliminar campañas.

**Criterio de aceptación:**

- CRUD vía `GET/POST /campaigns`, `GET/PUT/DELETE /campaigns/{id}`
- Cada campaña tiene una **nota de producto de 9 campos**: producto/servicio, descripción de la oferta, beneficios clave, precio/condiciones, requisitos del cliente, frases obligatorias, claims prohibidos, público objetivo, notas
- El seed trae 3 campañas de ejemplo con su nota

**Prioridad:** Alta

---

#### RF-08: Crear campaña desde PDF o con asistente IA

**Descripción:** El sistema debe poder autocompletar la nota de producto.

**Criterio de aceptación:**

- `POST /campaigns/extract` recibe un PDF, lo parsea (pypdf + LLM) y autocompleta los campos que detecte; lo que no encuentre se completa en el formulario
- `POST /campaigns/assist` apoya el llenado del formulario con IA
- El módulo frontend `/campaigns` permite crear vía PDF/IA/formulario y editar

**Prioridad:** Media

---

#### RF-09: Inyección de la nota de producto en el análisis

**Descripción:** La oferta de la campaña debe evaluarse en el análisis IA.

**Criterio de aceptación:**

- La nota de producto se inyecta en el prompt de análisis
- La IA evalúa si el ejecutivo ofreció la oferta correcta, respetó las frases obligatorias y evitó los claims prohibidos
- Se integra en los criterios existentes de promociones/cumplimiento

**Prioridad:** Alta

---

### Módulo: Subida y Procesamiento de Llamadas

#### RF-10: Subir archivo de audio individual

**Descripción:** El manager debe poder subir un archivo de audio.

**Criterio de aceptación:**

- Formatos aceptados: MP3, WAV, M4A, OGG, FLAC
- Tamaño máximo: 100 MB
- Validación del formato antes de la subida
- Asignación a un ejecutivo y a una campaña
- `POST /calls` (manager)

**Prioridad:** Alta

---

#### RF-11: Subida en lote (batch upload)

**Descripción:** El manager debe poder subir múltiples archivos de una vez.

**Criterio de aceptación:**

- `POST /calls/batch` (solo manager)
- Procesamiento asíncrono (Celery en local, inline vía BackgroundTasks en el despliegue)
- Indicador de progreso por archivo

**Prioridad:** Media

---

#### RF-12: Transcripción automática

**Descripción:** El sistema debe transcribir el audio automáticamente.

**Criterio de aceptación:**

- Usa Groq Whisper large v3 (proveedor portable vía configuración)
- Genera transcripción con timestamps por segmento
- Detecta automáticamente quién habla (diarización por contenido vía LLM: ejecutivo vs cliente; la heurística de pausas es solo fallback)
- Enmascara *best-effort* la PII antes del análisis
- Idioma según configuración global (español por defecto)

**Prioridad:** Alta

---

#### RF-13: Análisis automático con IA

**Descripción:** El sistema debe analizar la transcripción y generar scores.

**Criterio de aceptación:**

- Usa Groq (Llama 3.3 70B) por defecto; Claude/OpenAI/Azure configurables vía patrón factory (solo configuración)
- Evalúa las dimensiones activas de la rúbrica dinámica (7 por defecto)
- Inyecta la nota de producto de la campaña asociada
- Genera score 0-100 por dimensión y score global ponderado
- Genera recomendaciones accionables priorizadas

**Prioridad:** Alta

---

#### RF-14: Estados del procesamiento

**Descripción:** El sistema debe mostrar el estado en tiempo real.

**Criterio de aceptación:**

- Estados: `En cola → Transcribiendo → Analizando → Listo` / `Error`
- Consulta vía `GET /calls/{id}/status` (polling)
- Notificación visual cuando una llamada esté lista

**Prioridad:** Alta

---

#### RF-15: Reintento en caso de error

**Descripción:** El sistema debe permitir reintentar llamadas con error.

**Criterio de aceptación:**

- `POST /calls/{id}/retry` (solo manager) sobre llamadas en estado `Error`
- El reintento es idempotente
- Detalle del error visible para troubleshooting

**Prioridad:** Media

---

### Módulo: Consulta de Resultados

#### RF-16: Listado de llamadas

**Descripción:** Los usuarios deben ver las llamadas según su rol.

**Criterio de aceptación:**

- `GET /calls`: admin/jefe ven todas; el asesor solo las suyas
- Columnas: fecha, ejecutivo, campaña, duración, score global, estado
- Filtros: ejecutivo, fecha (rango), score (rango), estado

**Prioridad:** Alta

---

#### RF-17: Detalle de llamada

**Descripción:** El usuario debe ver el análisis completo de una llamada.

**Criterio de aceptación:**

- `GET /calls/{id}` con scoping por rol (el asesor solo las suyas)
- Metadata: ejecutivo, campaña, fecha, duración
- Score global con clasificación visual según los umbrales QA
- Score por cada dimensión con barra de progreso
- Sección de recomendaciones accionables
- Transcripción expandible con timestamps
- Descarga del reporte: `GET /calls/{id}/report.pdf` (scoped)

**Prioridad:** Alta

---

#### RF-18: Dashboard del equipo

**Descripción:** El manager debe ver KPIs agregados del equipo.

**Criterio de aceptación:**

- `GET /dashboard/summary` (solo manager) con filtros de campaña, `agent_id`, fechas y periodo
- `GET /dashboard/campaigns` (solo manager)
- KPIs principales: total llamadas, score promedio, tendencia
- Gráfico de distribución de scores
- Mejor performance / oportunidad de mejora
- Listado de últimas llamadas procesadas
- Tiempo de carga ≤ 2 segundos

**Prioridad:** Alta

---

#### RF-19: Rendimiento del ejecutivo / "Mi rendimiento"

**Descripción:** Ver el detalle de rendimiento de un ejecutivo.

**Criterio de aceptación:**

- `GET /dashboard/agents/{id}` con scoping: el asesor solo accede al suyo
- Score promedio histórico y reciente, tendencia temporal
- Fortalezas y áreas de mejora
- El asesor accede a través de la página "Mi rendimiento"

**Prioridad:** Alta

---

### Módulo: Configuración

#### RF-20: Configurar rúbrica

**Descripción:** El manager debe poder ajustar pesos y criterios de la rúbrica dinámica.

**Criterio de aceptación:**

- `GET /config/rubric`; `PUT /config/rubric` (solo manager)
- Vista con las 7 dimensiones por defecto
- Slider o input numérico para el peso porcentual (suma = 100%)
- Activar/desactivar subcriterios dentro de cada categoría
- Añadir/eliminar tanto categorías como subcategorías
- La IA usa únicamente los subcriterios activos al evaluar

**Prioridad:** Media

---

#### RF-21: Configurar umbrales de QA

**Descripción:** El manager debe poder ajustar los umbrales de calidad.

**Criterio de aceptación:**

- `GET /config/settings`; `PUT /config/settings` (solo manager)
- Umbrales persistidos en `app_settings`: `qa_target_score` (90), `qa_low_agent_threshold` (80), `qa_red_call_threshold` (60), `qa_min_calls_ranking` (5), `qa_trend_drop_alert` (5)
- Los cambios rigen la clasificación y las alertas del panel

**Prioridad:** Media

---

#### RF-22: Configurar idioma de análisis

**Descripción:** El manager debe poder cambiar el idioma global de análisis.

**Criterio de aceptación:**

- Selector con los idiomas soportados (persistido en `app_settings`)
- Por defecto: español
- El cambio aplica a las próximas llamadas; las ya procesadas conservan su idioma

**Prioridad:** Media

---

#### RF-23: Configurar proveedor de IA

**Descripción:** El sistema debe permitir alternar entre Groq (por defecto), Claude, OpenAI y Azure.

**Criterio de aceptación:**

- Configurable vía variable de entorno con un patrón factory; valor por defecto: Groq
- No expuesto en la UI (solo backend/configuración)

**Prioridad:** Media

---

### Módulo: Exportación

#### RF-24: Exportar reporte de llamada

**Descripción:** Generar PDF con el análisis de una llamada.

**Criterio de aceptación:**

- `GET /calls/{id}/report.pdf` (scoped por rol), generado con reportlab
- PDF con: metadata, scores, recomendaciones, transcripción
- Branding Minsait; encabezado "Vista previa para evaluación"

**Prioridad:** Media

---

## 2. Requerimientos No Funcionales (RNF)

Los requerimientos no funcionales describen **cómo debe ser** el sistema.

### Performance

#### RNF-01: Tiempo de respuesta de la API

- Endpoints de consulta (GET): p95 < 500ms
- Endpoints de escritura (POST/PUT): p95 < 1s

#### RNF-02: Tiempo de procesamiento

- Transcripción: ≤ 1 minuto para audio de 10 minutos
- Análisis IA: ≤ 30 segundos por transcripción
- Procesamiento total objetivo: ≤ 3 minutos para audio de 10 min

#### RNF-03: Carga del frontend

- Time to Interactive: < 3 segundos
- Lighthouse Performance Score: > 80

---

### Escalabilidad

#### RNF-04: Volumen de procesamiento

- El sistema debe procesar hasta 500 llamadas/día sin degradación
- En local, la cola Celery + Redis maneja procesamiento en paralelo; en el despliegue se procesa inline vía BackgroundTasks (`PROCESS_INLINE=true`)

#### RNF-05: Almacenamiento

- Soportar hasta 10,000 llamadas históricas en PostgreSQL
- Audios en object storage (S3 opcional vía boto3)

---

### Seguridad

#### RNF-06: Autenticación

- JWT firmado (python-jose) con refresh tokens
- Contraseñas hasheadas con bcrypt (passlib)
- Rate limit en login (5 intentos / 15 min, slowapi)

#### RNF-07: Protección de datos sensibles

- Datos en tránsito: HTTPS/TLS
- Datos sensibles en transcripción enmascarados *best-effort* (regex de números de tarjeta, DNI); no es garantía de cumplimiento
- Variables de entorno para API keys (nunca en código)
- CORS restringido a los orígenes configurados

#### RNF-08: Auditoría

- Logs estructurados de operaciones críticas
- El log JSON marca `environment="evaluation"`

---

### Disponibilidad

#### RNF-09: Uptime y arranque en frío

- Objetivo de disponibilidad: 99% en horario laboral
- El plan gratuito de Render duerme el backend tras ~15 min; el arranque en frío (~50s) se mitiga con una GitHub Action keepalive (ping a `/health` cada 12 min) y resiliencia en el frontend (timeout 90s, reintentos y mensaje "activando el servidor")
- El PostgreSQL gratuito de Render caduca a los 90 días

---

### Usabilidad

#### RNF-10: Diseño responsivo

- Funcional en resoluciones de escritorio (prioridad: desktop)
- Mobile-friendly no obligatorio en esta fase

#### RNF-11: Idioma de la interfaz

- Interfaz en español por defecto
- Estructura preparada para i18n

#### RNF-12: Accesibilidad

- Contraste mínimo WCAG AA
- Navegación por teclado en formularios

#### RNF-13: Identidad visual Minsait

- Paleta oficial Minsait: Pruno (#480E2A) y Gris Cerámica (#E3E2DA) dominantes, Fucsia (#FF0054) solo como acento
- Tipografía ForFuture Sans (woff2 locales)
- Logo oficial Minsait; contenedores achaflanados (clase `.chamfer`); titulares en minúscula con la palabra clave en Fucsia
- CTA en píldora Fucsia; modo claro por defecto (Gris Cerámica) y modo oscuro Pruno; sidebar siempre Pruno con logo blanco
- Fuente de verdad del color: `frontend/app/globals.css` + `tailwind.config.ts`
- (La identidad anterior "Aetheric Intelligence" Índigo/Slate queda obsoleta)

---

### Mantenibilidad

#### RNF-14: Calidad de código

- Backend: tipado con Pydantic v2, SQLAlchemy 2.0
- Frontend: TypeScript, Next.js 14 (App Router), Tailwind
- README/`AGENTS.md` con instrucciones de setup

#### RNF-15: Tests

- **78 tests** de backend (pytest, SQLite en memoria, externos mockeados)
- Cubren: auth, roles y scoping (admin/jefe/asesor), agents, campañas, cálculo de score, enmascarado, matching difuso, idempotencia del reintento, modo inline, umbrales QA, creación de login de asesor, **y la analítica de Fase 2** (métricas de conversación, compliance de nota de producto y endpoints de dashboard con scoping)

#### RNF-16: Logging

- Logs estructurados (JSON) con marca `environment="evaluation"`
- Niveles: DEBUG, INFO, WARNING, ERROR
- Logs centralizados en el despliegue (Render)

---

### Portabilidad

#### RNF-17: Contenedorización

- Stack completo dockerizado (`docker compose up -d --build`: postgres, redis, api, worker, frontend)
- Frontend desplegable en hosting estático/serverless (Vercel)

#### RNF-18: Variables de entorno

- Todas las configuraciones externalizadas (`.env`)
- En Vercel: `NEXT_PUBLIC_API_URL`; en Render: `GROQ_API_KEY`, `CORS_ORIGINS`, `PROCESS_INLINE=true`, `JWT_SECRET`
- Proveedor de IA conmutable por configuración (patrón factory)

---

### Costos (criterio MVP)

#### RNF-19: Costo objetivo

- Costo de infraestructura mensual: $0 con el stack actual (Vercel + Render en plan gratuito)
- Costo por análisis con el proveedor por defecto (Groq, gratis): $0 por llamada
- Si se cambia a un proveedor de pago (Claude/OpenAI): objetivo ≤ $0.05 USD por llamada de 10 min

---

## 3. Matriz de Trazabilidad (Casos de Uso → Requerimientos)

| Caso de Uso | Requerimientos Funcionales |
|---|---|
| CU-01: Subir llamada | RF-10, RF-11, RF-12, RF-13, RF-14, RF-15 |
| CU-02: Consultar análisis | RF-16, RF-17, RF-24 |
| CU-03: Rendimiento del ejecutivo | RF-19, RF-24 |
| CU-04: Gestionar equipo y logins | RF-03, RF-04, RF-05, RF-06 |
| CU-05: Gestionar campañas | RF-07, RF-08, RF-09 |
| CU-06: Configurar rúbrica | RF-20 |
| CU-07: Configurar umbrales QA | RF-21 |
| CU-08: Dashboard | RF-18 |
| Transversal (auth/roles/config) | RF-01, RF-02, RF-22, RF-23 |

---

## 4. Priorización (MoSCoW)

### Must Have (imprescindible)

RF-01, RF-02, RF-03, RF-04, RF-05, RF-07, RF-09, RF-10, RF-12, RF-13, RF-14, RF-16, RF-17, RF-18, RF-19
RNF-01, RNF-02, RNF-06, RNF-07, RNF-13, RNF-15, RNF-17, RNF-18

### Should Have (importante pero no bloqueante)

RF-06, RF-08, RF-11, RF-15, RF-20, RF-21, RF-22, RF-24
RNF-03, RNF-09, RNF-10, RNF-16

### Could Have (si hay tiempo)

RF-23, RNF-11, RNF-12

### Won't Have (fuera de alcance de esta fase — roadmap)

- Integraciones telefónicas en tiempo real
- App móvil
- Multi-tenant
- Métricas de conversación (talk/listen ratio, % silencio, monólogos, velocidad de habla)
- Reproductor de audio sincronizado con la transcripción
- Exportación CSV del equipo
- Analítica de jefe de alto impacto (alertas agregadas, top problemas recurrentes)
- Vista de asesor enriquecida (percentil anónimo dentro de la campaña, evidencia detallada)
