# 📄 Documento de Visión y Casos de Uso

**Proyecto:** Plataforma de QA Automatizado para Call Center Bancario
**Nombre tentativo:** CallQA AI
**Versión:** 1.0 — Vista previa para evaluación
**Fecha:** Junio 2026

---

## 1. Visión del Producto

### 1.1 Problema a resolver

Los call centers bancarios necesitan evaluar la calidad de las llamadas entre ejecutivos y clientes para garantizar:

- Cumplimiento de protocolos y normativa financiera
- Calidad del servicio al cliente (asertividad, tono, empatía)
- Mención correcta de promociones y productos (incluida la oferta de la campaña vigente)
- Resolución efectiva de las consultas

Actualmente, esta evaluación se hace de forma manual por jefes y supervisores de QA, quienes escuchan llamadas al azar. El proceso es:

- **Lento:** Un evaluador solo puede revisar ~10-15 llamadas/día
- **Subjetivo:** La evaluación depende del criterio personal
- **No escalable:** Solo se audita el 1-2% de las llamadas
- **Inconsistente:** Diferentes evaluadores puntúan distinto

### 1.2 Solución propuesta

Una plataforma web donde el equipo de QA sube grabaciones de llamadas y, mediante IA (transcripción + análisis con modelos de lenguaje), obtiene en minutos:

- Transcripción completa con timestamps (Groq Whisper large v3)
- Enmascarado *best-effort* de datos sensibles (PII) en la transcripción
- Evaluación objetiva contra una rúbrica dinámica (7 dimensiones por defecto) con Groq Llama 3.3 70B
- Score numérico por dimensión + score global ponderado (escala 0-100)
- Recomendaciones accionables específicas para el ejecutivo
- Reporte PDF descargable

Cliente: **Minsait (Grupo Indra)**, sector banca.

### 1.3 Propuesta de valor

| Métrica | Antes (manual) | Con CallQA AI |
|---|---|---|
| Llamadas evaluadas/día | 10-15 | Ilimitadas |
| Tiempo por llamada | 20-30 min | 2-3 min |
| Cobertura del equipo | 1-2% | 100% |
| Consistencia | Variable | Alta |
| Costo por evaluación | Alto (hora-evaluador) | $0 en esta fase (API Groq gratuita) |

### 1.4 Alcance actual (esta vista previa)

**Sí incluye:**

- Subida manual de archivos de audio (MP3, WAV, M4A, OGG, FLAC), individual o en lote
- Transcripción automática en español (configurable a otros idiomas)
- Enmascarado *best-effort* de PII antes del análisis
- Análisis IA sobre una rúbrica dinámica editable (7 dimensiones por defecto, con subcriterios activables)
- Gestión de **campañas** con nota de producto: la IA evalúa si el ejecutivo ofreció la oferta correcta
- **Roles diferenciados** (admin, jefe, asesor) con navegación y permisos por rol
- Dashboard de gestión con métricas y filtros (campaña, ejecutivo, fechas, periodo)
- Panel "Mi rendimiento" para el asesor
- Gestión de ejecutivos (alta, edición, baja)
- Umbrales de QA configurables (objetivo, alertas, ranking)
- Reporte PDF por llamada

**NO incluye (roadmap, aún no implementado):**

- Integración con sistemas telefónicos (Genesys, Avaya, etc.)
- Análisis en tiempo real durante la llamada
- Aplicación móvil
- Multi-tenant (varios call centers en una sola instancia)
- Métricas de conversación (talk/listen ratio, % silencio, monólogos, velocidad de habla)
- Reproductor de audio sincronizado con la transcripción
- Exportación CSV del equipo
- Analítica de jefe de alto impacto (alertas accionables agregadas, KPIs por campaña, top problemas recurrentes)
- Vista de asesor enriquecida (percentil anónimo dentro de la campaña, evidencia detallada)

---

## 2. Usuarios y Roles

La plataforma define **tres roles**. Por ahora **admin** y **jefe** comparten los mismos permisos (gestión + analítica global); el **asesor** solo ve su propio rendimiento.

### 2.1 Admin / Jefe (gestión y analítica)

Mismos permisos por el momento (helper interno `is_manager`). Capacidades:

| Capacidad | Descripción |
|---|---|
| Subir llamadas | Carga archivos de audio individualmente o en lote |
| Asignar ejecutivo | Indica a qué ejecutivo pertenece cada llamada |
| Reintentar / eliminar | Reprocesa o borra llamadas |
| Gestionar ejecutivos | Crea/edita/desactiva ejecutivos y crea su login de asesor |
| Gestionar campañas | Crea/edita campañas con su nota de producto (formulario, IA o PDF) |
| Configurar rúbrica | Ajusta pesos, dimensiones y subcriterios activos |
| Configurar umbrales QA | Define objetivo y umbrales de alerta/ranking |
| Ver dashboard global | Consulta métricas agregadas del equipo con filtros |
| Descargar reportes | Genera el PDF de cada llamada |
| Configurar idioma | Cambia el idioma de análisis |

### 2.2 Asesor (su propio rendimiento)

El asesor está vinculado a su ficha de ejecutivo (`User.agent_id`). Solo ve lo suyo:

| Capacidad | Descripción |
|---|---|
| Ver "Mi rendimiento" | Panel con su score, tendencia y detalle |
| Ver su ficha | Sus datos de ejecutivo |
| Ver sus llamadas | Únicamente las llamadas asociadas a su ficha |
| Descargar su reporte | El PDF de sus propias llamadas |

El asesor recibe **403** al intentar acceder al dashboard global, subir/asignar/reintentar/eliminar llamadas, la configuración o la gestión de ejecutivos. El frontend redirige por rol: asesor → `/mi-panel`; admin/jefe → `/dashboard`.

### 2.3 Actores externos (no-usuarios del sistema)

- **Cliente del banco:** Persona en la llamada. Su voz se procesa pero no se identifica nominalmente.

---

## 3. Casos de Uso Principales

### CU-01: Subir una llamada para análisis

**Actor:** Admin / Jefe
**Precondición:** Usuario manager autenticado, ejecutivo registrado en el sistema
**Flujo principal:**

1. El manager accede a la sección "Nueva llamada"
2. Selecciona el ejecutivo y la campaña a la que pertenece la llamada
3. Adjunta el archivo de audio (MP3/WAV/M4A/OGG/FLAC, máx. 100MB)
4. Opcionalmente añade metadatos: fecha de la llamada, motivo
5. Confirma la subida
6. El sistema valida el archivo y lo encola para procesamiento (Celery en local, inline vía BackgroundTasks en el despliegue)
7. El sistema muestra el estado: "En cola → Transcribiendo → Analizando → Listo"
8. Al finalizar, el manager puede acceder al análisis completo

**Postcondición:** La llamada queda registrada con su transcripción y análisis.

**Flujo alternativo:**

- **3a.** Si el archivo excede el tamaño o el formato no soportado → mostrar error y permitir reintento.
- **6a.** Si la transcripción o el análisis fallan → marcar llamada como "Error" y permitir reintento manual (idempotente).

---

### CU-02: Consultar el análisis de una llamada

**Actor:** Admin / Jefe (cualquier llamada); Asesor (solo las suyas)
**Precondición:** Llamada procesada con estado "Listo"
**Flujo principal:**

1. El usuario accede al listado de llamadas (el asesor solo ve las propias)
2. Filtra por ejecutivo, fecha o score
3. Selecciona una llamada
4. El sistema muestra:
   - Datos generales (ejecutivo, campaña, fecha, duración)
   - Score global (0-100)
   - Score por cada dimensión activa de la rúbrica
   - Recomendaciones accionables priorizadas
   - Transcripción completa con timestamps (opcional, expandible)
5. El usuario puede descargar el reporte en PDF

**Postcondición:** Se obtienen insights para retroalimentar al ejecutivo.

---

### CU-03: Revisar el rendimiento de un ejecutivo

**Actor:** Admin / Jefe (cualquier ejecutivo); Asesor (solo el propio, vía "Mi rendimiento")
**Precondición:** Al menos algunas llamadas analizadas del ejecutivo
**Flujo principal:**

1. El usuario accede al perfil del ejecutivo (admin/jefe) o a "Mi rendimiento" (asesor)
2. El sistema muestra:
   - Score promedio del ejecutivo por dimensión
   - Tendencia temporal
   - Fortalezas y áreas de mejora
3. El manager puede exportar el reporte de una llamada para reunión 1-a-1

**Postcondición:** Se cuenta con información para coaching.

---

### CU-04: Gestionar el equipo de ejecutivos y sus logins

**Actor:** Admin / Jefe
**Precondición:** Usuario manager autenticado
**Flujo principal:**

1. El manager accede a "Equipo"
2. Visualiza la lista de ejecutivos activos
3. Puede:
   - Crear nuevo ejecutivo (nombre, email, campaña asignada)
   - Editar datos de un ejecutivo existente
   - Desactivar un ejecutivo (no se elimina, se marca inactivo)
   - Crear el **login de asesor** de un ejecutivo (`POST /agents/{id}/login`), que vincula el `User` con su `Agent`
4. Los cambios se reflejan inmediatamente en los formularios de subida

**Postcondición:** El equipo está actualizado y los asesores pueden acceder a su panel.

---

### CU-05: Gestionar campañas con nota de producto

**Actor:** Admin / Jefe
**Precondición:** Usuario manager autenticado
**Flujo principal:**

1. El manager accede a "Campañas"
2. Crea una campaña de tres formas:
   - **Formulario** (con asistente IA, `POST /campaigns/assist`)
   - **Subiendo un PDF** que la IA parsea (`POST /campaigns/extract`, vía pypdf + LLM) y autocompleta; lo que no encuentre se completa a mano
3. Completa la **nota de producto** (9 campos): producto/servicio, descripción de la oferta, beneficios clave, precio/condiciones, requisitos del cliente, frases obligatorias, claims prohibidos, público objetivo y notas
4. Guarda la campaña; queda disponible para asignar a llamadas

**Postcondición:** La nota de producto se inyecta en el prompt de análisis para evaluar si el ejecutivo ofreció la oferta correcta (integrado en los criterios de promociones/cumplimiento).

---

### CU-06: Configurar la rúbrica de evaluación

**Actor:** Admin / Jefe
**Precondición:** Usuario manager autenticado
**Flujo principal:**

1. El manager accede a "Configuración → Rúbrica"
2. El sistema muestra las 7 dimensiones por defecto con sus pesos y subcriterios
3. El manager ajusta el peso porcentual de cada dimensión (suma = 100%)
4. Opcionalmente, añade/elimina dimensiones y activa/desactiva subcriterios (la IA evalúa solo los subcriterios activos)
5. Guarda los cambios — aplicarán a las próximas llamadas analizadas

**Postcondición:** La rúbrica queda configurada según las prioridades del negocio.

---

### CU-07: Configurar los umbrales de QA

**Actor:** Admin / Jefe
**Precondición:** Usuario manager autenticado
**Flujo principal:**

1. El manager accede a "Configuración → Ajustes"
2. Define los umbrales de QA persistidos en `app_settings`:
   - `qa_target_score` (objetivo de score, por defecto 90)
   - `qa_low_agent_threshold` (asesor de bajo rendimiento, 80)
   - `qa_red_call_threshold` (llamada en rojo, 60)
   - `qa_min_calls_ranking` (mínimo de llamadas para entrar al ranking, 5)
   - `qa_trend_drop_alert` (caída de tendencia que dispara alerta, 5)
3. Guarda los cambios

**Postcondición:** Los umbrales rigen la clasificación y las alertas del panel.

---

### CU-08: Ver dashboard agregado del equipo

**Actor:** Admin / Jefe
**Precondición:** Usuario manager autenticado, al menos una llamada procesada
**Flujo principal:**

1. El manager accede al dashboard principal (`/dashboard`)
2. El sistema muestra:
   - KPIs principales: total de llamadas analizadas, score promedio del equipo, tendencia
   - Ejecutivos con mejor performance y con mayor oportunidad de mejora
   - Distribución de scores por dimensión
   - Listado de últimas llamadas procesadas
3. Puede aplicar filtros por campaña, ejecutivo, rango de fechas y periodo

**Postcondición:** El manager tiene visibilidad completa del estado del equipo.

---

## 4. Reglas de Negocio

### RN-01: Dimensiones de evaluación

La rúbrica parte de 7 dimensiones por defecto, cada una evaluada de 0 a 100. Es **dinámica**: se pueden activar/desactivar subcriterios y añadir/eliminar tanto categorías como subcategorías; la IA evalúa según los subcriterios activos.

1. **Saludo y protocolo de apertura/cierre**
2. **Asertividad y tono** (empatía, claridad, paciencia)
3. **Mención correcta de promociones/productos** (incluida la oferta de la campaña, según su nota de producto)
4. **Cumplimiento normativo** (disclaimers, grabación, datos sensibles, claims prohibidos de la campaña)
5. **Resolución efectiva del motivo de la llamada**
6. **Manejo de objeciones del cliente**
7. **Detección de sentimiento del cliente** (satisfacción percibida)

### RN-02: Cálculo del score global

El score global (escala 0-100) se calcula como:

```
Score Global = Σ (Score_dimensión_i × Peso_dimensión_i) / 100
```

Donde los pesos por defecto son prácticamente iguales (~14.28% cada una; ajustados para sumar 100%), pero el manager puede modificarlos.

### RN-03: Umbrales y clasificación del score

La clasificación usa los umbrales de QA configurables (ver CU-07). Con los valores por defecto:

| Score | Clasificación | Color |
|---|---|---|
| ≥ qa_red_call_threshold (60) y por encima | Aceptable / Excelente | 🟡 / 🟢 |
| < qa_red_call_threshold (60) | Llamada en rojo (requiere atención) | 🔴 Rojo |

Un asesor con promedio por debajo de `qa_low_agent_threshold` (80) se marca como bajo rendimiento; el objetivo del equipo es `qa_target_score` (90).

### RN-04: Campaña y nota de producto

- Cada llamada se asocia a una campaña (`Call.campaign_id`); se conserva `campaign_type` (texto) por compatibilidad y para los filtros del dashboard.
- La nota de producto de la campaña se inyecta en el prompt de análisis para verificar que el ejecutivo ofreció la oferta correcta y respetó frases obligatorias y claims prohibidos.

### RN-05: Retención de datos

- Audios originales: se conservan por 90 días, luego se eliminan automáticamente
- Transcripciones y análisis: se conservan indefinidamente
- Los ejecutivos desactivados conservan su historial

### RN-06: Formatos de audio soportados

- MP3, WAV, M4A, OGG, FLAC
- Tamaño máximo: 100 MB
- Duración máxima recomendada: 60 minutos por llamada

### RN-07: Idioma configurable

- Idioma por defecto: español
- Configurable a nivel global (no por llamada)
- Whisper soporta 90+ idiomas; el prompt de análisis se adapta al idioma seleccionado

---

## 5. Métricas de Éxito

| Métrica | Objetivo |
|---|---|
| Tiempo de procesamiento por llamada | < 3 minutos para audio de 10 min |
| Precisión de transcripción | > 92% (WER < 8%) |
| Disponibilidad del servicio | > 99% en horario laboral |
| Llamadas procesables por día | > 500 (sin degradación) |
| Tiempo de carga del dashboard | < 2 segundos |
| Satisfacción del evaluador (encuesta) | NPS > 50 |

---

## 6. Restricciones y Supuestos

### Restricciones

- Las llamadas deben estar en formato de audio (no video)
- El audio debe tener calidad mínima audible (no se pueden procesar audios muy ruidosos)
- Datos sensibles del cliente (números de tarjeta, DNI completo) se enmascaran en la transcripción mediante reglas regex *best-effort* (no es garantía de cumplimiento; el audio original se envía íntegro al proveedor de transcripción)
- El plan gratuito de Render duerme el backend tras ~15 min de inactividad; el primer acceso tras el reposo sufre un arranque en frío (~50s) que puede percibirse como un error de API. Se mitiga con un ping periódico (GitHub Action keepalive) y reintentos/resiliencia en el frontend.

### Supuestos

- El usuario cuenta con conexión estable a internet
- Las llamadas a procesar son grabaciones legales con consentimiento del cliente
- El call center cumple con la normativa local de protección de datos (GDPR, Ley de Protección de Datos Personales del país)

---

## 7. Compliance y Gobernanza de Datos (Contexto Minsait/Indra)

> **Importante:** Esta es una **vista previa para evaluación** que se presenta oficialmente al cliente. Sigue siendo un prototipo: antes de pasar a producción con datos reales, los siguientes puntos deben ser validados con las áreas correspondientes.

### 7.1 Fases del proyecto y manejo de datos

| Fase | Datos utilizados | Aprobaciones requeridas |
|---|---|---|
| **Vista previa para evaluación (actual)** | Audios sintéticos / grabaciones propias simuladas | Ninguna formal — entorno de evaluación |
| **Piloto controlado** | Audios reales anonimizados con consentimiento explícito | Aprobación de jefe directo + DPO |
| **Producción** | Audios reales del call center en operación | Compliance + Legal + Seguridad de la Información + DPO |

### 7.2 Áreas a involucrar antes de producción

Cuando se decida escalar más allá de la evaluación, se requiere coordinar con:

- **Compliance / Cumplimiento normativo:** Validación del uso de IA generativa con datos de clientes bancarios
- **DPO (Data Protection Officer):** Evaluación de impacto en protección de datos (EIPD/DPIA) bajo GDPR y leyes locales
- **Seguridad de la Información (CISO):** Aprobación de proveedores externos (Groq, y los configurables: Anthropic, OpenAI, Azure), análisis de riesgos
- **Arquitectura Corporativa:** Migración a infraestructura corporativa (Azure, posiblemente)
- **Legal:** Revisión de contratos con proveedores de IA, cláusulas de tratamiento de datos
- **Compras/Procurement:** Si se requiere contrato corporativo con el proveedor de IA vs cuenta personal

### 7.3 Roadmap de cumplimiento sugerido

```
EVALUACIÓN (HOY)             PILOTO (Q3 2026)              PRODUCCIÓN (Q4 2026+)
─────────────────             ──────────────────            ────────────────────────
Vercel + Render               Azure App Service             Azure App Service
API pública Groq (gratis)     Azure OpenAI Service          Azure OpenAI + Whisper on-prem
Datos simulados               Datos anonimizados            Datos reales con consentimiento
Sin EIPD formal               EIPD inicial                  EIPD completa + auditoría
Cuentas demo (admin/jefe/     5-10 ejecutivos piloto        Todo el call center
asesor)
```

### 7.4 Consideraciones específicas de Minsait/Indra

- **Cloud preferente para producción:** Azure (estándar del grupo Indra para muchas áreas)
- **Servicios IA equivalentes en Azure:** Azure OpenAI Service, Azure AI Speech (transcripción)
- **El código generado debe ser portable:** Por eso usamos variables de entorno y un patrón factory para el proveedor de IA, de modo que la migración Cloud no requiera reescribir el sistema
- **Branding:** Aplicación con la **identidad oficial Minsait** (paleta Pruno / Gris Cerámica con acento Fucsia, tipografía ForFuture Sans, logo Minsait, contenedores achaflanados), con un banner de "Vista previa — entorno de evaluación" visible durante esta fase

### 7.5 Aviso de la vista previa

Todas las pantallas incluyen un banner persistente:

> ⚠️ **Vista previa — entorno de evaluación.**
> No utilizar con datos reales de clientes sin la aprobación previa de Compliance.

A nivel técnico, el header HTTP conserva el nombre `X-Prototype-Notice` con el valor `Evaluation environment - Do not use with real customer data`, y el log JSON usa `environment="evaluation"`. El reporte PDF dice "Vista previa para evaluación". El login ya no muestra credenciales demo y el seed ya no imprime contraseñas.

---

## 8. Glosario

| Término | Definición |
|---|---|
| **QA** | Quality Assurance — Aseguramiento de calidad |
| **Rúbrica** | Conjunto de criterios para evaluar de forma estandarizada |
| **Campaña** | Iniciativa comercial con una nota de producto que la IA usa para evaluar la oferta |
| **Nota de producto** | Ficha de 9 campos que describe la oferta de una campaña |
| **STT** | Speech-to-Text — Transcripción de voz a texto |
| **LLM** | Large Language Model — Modelo de lenguaje grande (Llama, Claude, GPT) |
| **Whisper** | Modelo de transcripción de audio (se usa Whisper large v3 vía Groq) |
| **Groq** | Plataforma de inferencia ultra rápida (Whisper + Llama) vía API; proveedor de IA por defecto |
| **PII** | Personally Identifiable Information — datos personales sensibles |
| **DPO** | Data Protection Officer — Delegado de Protección de Datos |
| **EIPD/DPIA** | Evaluación de Impacto en Protección de Datos |
| **CISO** | Chief Information Security Officer — Director de Seguridad |
| **GDPR** | General Data Protection Regulation (UE) |
| **PoC** | Proof of Concept — Prueba de concepto |
