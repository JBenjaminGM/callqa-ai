# 📋 Requerimientos Funcionales y No Funcionales

**Proyecto:** CallQA AI — Plataforma de QA para Call Center
**Versión:** 1.0 — MVP

---

## 1. Requerimientos Funcionales (RF)

Los requerimientos funcionales describen **qué debe hacer** el sistema. Cada uno incluye su criterio de aceptación.

### Módulo: Autenticación y Usuarios

#### RF-01: Login del supervisor

**Descripción:** El sistema debe permitir el inicio de sesión mediante email y contraseña.

**Criterio de aceptación:**

- Dado un email y contraseña válidos, el usuario accede al dashboard
- Tras 5 intentos fallidos, la cuenta se bloquea por 15 minutos
- La sesión expira tras 8 horas de inactividad
- El sistema genera un JWT firmado para gestionar la sesión

**Prioridad:** Alta

---

#### RF-02: Recuperación de contraseña

**Descripción:** El sistema debe permitir recuperar la contraseña vía email.

**Criterio de aceptación:**

- El usuario solicita recuperación ingresando su email
- El sistema envía un enlace con token de un solo uso (validez: 1 hora)
- El usuario establece nueva contraseña (mínimo 8 caracteres, 1 mayúscula, 1 número)

**Prioridad:** Media

---

### Módulo: Gestión de Ejecutivos

#### RF-03: Crear ejecutivo

**Descripción:** El supervisor debe poder registrar ejecutivos en el sistema.

**Criterio de aceptación:**

- Campos requeridos: nombre completo, email, fecha de ingreso
- Campos opcionales: campaña asignada, supervisor directo, foto
- El email debe ser único en el sistema
- Al crear, se asigna un código interno auto-incrementable

**Prioridad:** Alta

---

#### RF-04: Editar ejecutivo

**Descripción:** El supervisor debe poder modificar datos de ejecutivos existentes.

**Criterio de aceptación:**

- Todos los campos son editables excepto el código interno
- Los cambios se reflejan inmediatamente
- Se registra un historial de cambios (auditoría)

**Prioridad:** Alta

---

#### RF-05: Desactivar ejecutivo

**Descripción:** El supervisor debe poder desactivar (no eliminar) ejecutivos.

**Criterio de aceptación:**

- Un ejecutivo desactivado no aparece en los formularios de subida
- Su historial de llamadas permanece accesible
- Puede ser reactivado en cualquier momento

**Prioridad:** Media

---

### Módulo: Subida y Procesamiento de Llamadas

#### RF-06: Subir archivo de audio individual

**Descripción:** El supervisor debe poder subir un archivo de audio.

**Criterio de aceptación:**

- Formatos aceptados: MP3, WAV, M4A, OGG, FLAC
- Tamaño máximo: 100 MB
- Validación del formato antes de la subida
- Indicador de progreso durante la carga
- Asignación obligatoria a un ejecutivo
- Campos opcionales: fecha de la llamada, tipo de campaña, motivo

**Prioridad:** Alta

---

#### RF-07: Subida en lote (batch upload)

**Descripción:** El supervisor debe poder subir múltiples archivos de una vez.

**Criterio de aceptación:**

- Hasta 20 archivos por lote
- Asignar todos al mismo ejecutivo o distintos ejecutivos
- Procesamiento asíncrono (se encolan)
- Indicador de progreso por archivo

**Prioridad:** Media

---

#### RF-08: Transcripción automática

**Descripción:** El sistema debe transcribir el audio automáticamente.

**Criterio de aceptación:**

- Usa Groq Whisper API (configurable a Whisper local en el futuro)
- Genera transcripción con timestamps por segmento
- Detecta automáticamente quién habla (diarización: ejecutivo vs cliente)
- Idioma según configuración global (español por defecto)
- Tiempo objetivo: ≤ 1 minuto por audio de 10 minutos

**Prioridad:** Alta

---

#### RF-09: Análisis automático con IA

**Descripción:** El sistema debe analizar la transcripción y generar scores.

**Criterio de aceptación:**

- Usa Claude API o OpenAI GPT (configurable vía variable de entorno)
- Evalúa las 7 dimensiones definidas en la rúbrica
- Genera score 0-100 por dimensión
- Calcula score global ponderado
- Genera 3-5 recomendaciones accionables priorizadas
- Detecta y enmascara datos sensibles (números de tarjeta, DNI)
- Tiempo objetivo: ≤ 30 segundos tras transcripción

**Prioridad:** Alta

---

#### RF-10: Estados del procesamiento

**Descripción:** El sistema debe mostrar el estado en tiempo real.

**Criterio de aceptación:**

- Estados: `En cola → Transcribiendo → Analizando → Listo` / `Error`
- Actualización vía polling o WebSockets (recomendado polling para MVP)
- Notificación visual al supervisor cuando una llamada esté lista

**Prioridad:** Alta

---

#### RF-11: Reintento en caso de error

**Descripción:** El sistema debe permitir reintentar llamadas con error.

**Criterio de aceptación:**

- Botón de "Reintentar" en llamadas con estado `Error`
- Detalle del error visible para troubleshooting
- Se reintenta desde el paso donde falló (transcripción o análisis)

**Prioridad:** Media

---

### Módulo: Consulta de Resultados

#### RF-12: Listado de llamadas

**Descripción:** El supervisor debe ver todas las llamadas procesadas.

**Criterio de aceptación:**

- Tabla paginada (50 por página)
- Columnas: fecha, ejecutivo, duración, score global, estado
- Filtros: ejecutivo, fecha (rango), score (rango), estado
- Ordenamiento por cualquier columna
- Búsqueda por nombre de ejecutivo

**Prioridad:** Alta

---

#### RF-13: Detalle de llamada

**Descripción:** El supervisor debe ver el análisis completo de una llamada.

**Criterio de aceptación:**

- Metadata: ejecutivo, fecha, duración, archivo de audio (reproducible)
- Score global con clasificación visual (Excelente/Aceptable/Requiere atención)
- Score por cada dimensión con barra de progreso
- Sección de recomendaciones accionables (3-5 items)
- Comparativa con promedio del equipo (mismo periodo)
- Transcripción expandible con timestamps clickeables
- Botón para descargar reporte PDF
- Reproductor de audio sincronizado con transcripción

**Prioridad:** Alta

---

#### RF-14: Dashboard del equipo

**Descripción:** El supervisor debe ver KPIs agregados del equipo.

**Criterio de aceptación:**

- KPIs principales: total llamadas, score promedio, tendencia
- Filtro temporal: 7 / 30 / 90 días
- Gráfico de distribución de scores
- Top 5 mejor performance / Top 5 oportunidad de mejora
- Listado de últimas 10 llamadas procesadas
- Tiempo de carga ≤ 2 segundos

**Prioridad:** Alta

---

#### RF-15: Perfil del ejecutivo

**Descripción:** El supervisor debe ver el detalle de cada ejecutivo.

**Criterio de aceptación:**

- Datos personales del ejecutivo
- Score promedio histórico y de los últimos 30 días
- Tendencia temporal (gráfico de líneas)
- Comparativa por dimensión vs promedio del equipo (gráfico radar)
- Top 3 fortalezas y top 3 áreas de mejora
- Listado de llamadas del ejecutivo (filtrable)

**Prioridad:** Alta

---

### Módulo: Configuración

#### RF-16: Configurar rúbrica

**Descripción:** El supervisor debe poder ajustar pesos y criterios de la rúbrica.

**Criterio de aceptación:**

- Vista con las 7 dimensiones
- Slider o input numérico para el peso porcentual (suma = 100%)
- Validación: la suma debe ser exactamente 100%
- Edición opcional de los criterios descriptivos de cada dimensión
- Guardar cambios — aplica a futuras llamadas

**Prioridad:** Media

---

#### RF-17: Configurar idioma de análisis

**Descripción:** El supervisor debe poder cambiar el idioma global de análisis.

**Criterio de aceptación:**

- Selector con los idiomas soportados (español, inglés, portugués, francés, etc.)
- Por defecto: español
- El cambio aplica inmediatamente a las próximas llamadas
- Las llamadas ya procesadas conservan su idioma original

**Prioridad:** Media

---

#### RF-18: Configurar proveedor de IA

**Descripción:** El sistema debe permitir alternar entre Claude y GPT.

**Criterio de aceptación:**

- Configurable vía variable de entorno (`AI_PROVIDER=claude|openai`)
- No expuesto en la UI en MVP (solo backend)
- Cambio en caliente no requerido

**Prioridad:** Media

---

### Módulo: Exportación

#### RF-19: Exportar reporte de llamada

**Descripción:** Generar PDF con el análisis de una llamada.

**Criterio de aceptación:**

- PDF con: metadata, scores, gráfico de radar, recomendaciones, transcripción
- Branding básico (logo configurable)
- Tiempo de generación ≤ 5 segundos

**Prioridad:** Media

---

#### RF-20: Exportar reporte del ejecutivo

**Descripción:** Generar PDF/CSV con el performance del ejecutivo.

**Criterio de aceptación:**

- PDF para presentación ejecutiva
- CSV con datos crudos para análisis externo
- Rango temporal seleccionable

**Prioridad:** Media

---

## 2. Requerimientos No Funcionales (RNF)

Los requerimientos no funcionales describen **cómo debe ser** el sistema.

### Performance

#### RNF-01: Tiempo de respuesta de la API

- Endpoints de consulta (GET): p95 < 500ms
- Endpoints de escritura (POST/PUT): p95 < 1s
- Subida de archivo (excluyendo upload): respuesta < 2s

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
- La cola de procesamiento debe manejar hasta 50 llamadas en paralelo

#### RNF-05: Almacenamiento

- Soportar hasta 10,000 llamadas históricas en la BD
- Audios en object storage (sin límite en MVP, configurable)

---

### Seguridad

#### RNF-06: Autenticación

- JWT con expiración de 8 horas
- Refresh tokens para renovación sin re-login
- Contraseñas hasheadas con bcrypt (cost factor ≥ 12)

#### RNF-07: Protección de datos sensibles

- Datos en tránsito: HTTPS/TLS 1.2+
- Datos en reposo: cifrado de BD habilitado
- Datos sensibles en transcripción enmascarados automáticamente (regex de números de tarjeta, DNI peruano)
- Variables de entorno para API keys (nunca en código)

#### RNF-08: Auditoría

- Logs de acceso y operaciones críticas (creación, edición, eliminación)
- Retención de logs: 90 días

---

### Disponibilidad

#### RNF-09: Uptime

- Objetivo de disponibilidad: 99% en horario laboral (8am-8pm GMT-5)
- Plan de recuperación: backup diario de BD

---

### Usabilidad

#### RNF-10: Diseño responsivo

- Funcional en resoluciones desde 1280px hasta 1920px
- Mobile-friendly no obligatorio en MVP (prioridad: desktop)

#### RNF-11: Idioma de la interfaz

- Interfaz en español por defecto
- Estructura preparada para i18n (futuras versiones)

#### RNF-12: Accesibilidad

- Contraste mínimo WCAG AA
- Navegación por teclado en formularios

---

### Mantenibilidad

#### RNF-13: Calidad de código

- Backend: typing con Pydantic, formato con `black`, lint con `ruff`
- Frontend: TypeScript estricto, formato con Prettier, lint con ESLint
- Documentación inline en funciones complejas
- README en cada repo con instrucciones de setup

#### RNF-14: Tests

- Cobertura mínima del backend: 60% (rutas críticas)
- Tests de integración para los flujos principales: subida, análisis, consulta

#### RNF-15: Logging

- Logs estructurados (JSON)
- Niveles: DEBUG, INFO, WARNING, ERROR
- Logs centralizados en producción (Railway logs o servicio externo)

---

### Portabilidad

#### RNF-16: Contenedorización

- Backend dockerizado (Dockerfile y docker-compose.yml para desarrollo local)
- Frontend desplegable en cualquier hosting estático/serverless

#### RNF-17: Variables de entorno

- Todas las configuraciones externalizadas en `.env`
- Archivo `.env.example` versionado con valores dummy

---

### Costos (criterio de no-dev / MVP)

#### RNF-18: Costo objetivo

- Costo de infraestructura mensual: ≤ $30 USD para volumen demo
- Costo por análisis (Groq + Claude/GPT): ≤ $0.05 USD por llamada de 10 min

---

## 3. Matriz de Trazabilidad (Casos de Uso → Requerimientos)

| Caso de Uso | Requerimientos Funcionales |
|---|---|
| CU-01: Subir llamada | RF-06, RF-07, RF-08, RF-09, RF-10, RF-11 |
| CU-02: Consultar análisis | RF-12, RF-13, RF-19 |
| CU-03: Comparar performance | RF-15, RF-20 |
| CU-04: Gestionar equipo | RF-03, RF-04, RF-05 |
| CU-05: Configurar rúbrica | RF-16 |
| CU-06: Dashboard | RF-14 |
| Transversal | RF-01, RF-02, RF-17, RF-18 |

---

## 4. Priorización (MoSCoW)

### Must Have (MVP imprescindible)

RF-01, RF-03, RF-04, RF-06, RF-08, RF-09, RF-10, RF-12, RF-13, RF-14, RF-15
RNF-01, RNF-02, RNF-06, RNF-07, RNF-13, RNF-16, RNF-17

### Should Have (Importante pero no bloqueante)

RF-02, RF-05, RF-07, RF-11, RF-16, RF-17, RF-19, RF-20
RNF-03, RNF-09, RNF-10, RNF-14

### Could Have (Si hay tiempo)

RF-18, RNF-11, RNF-12, RNF-15

### Won't Have (Fuera de alcance MVP)

- Integraciones telefónicas en tiempo real
- App móvil
- Multi-tenant
- Análisis en idiomas distintos a español/inglés en MVP
