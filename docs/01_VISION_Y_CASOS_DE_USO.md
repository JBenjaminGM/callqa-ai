# 📄 Documento de Visión y Casos de Uso

**Proyecto:** Plataforma de QA Automatizado para Call Center Bancario
**Nombre tentativo:** CallQA AI
**Versión:** 1.0 — MVP
**Fecha:** Mayo 2026

---

## 1. Visión del Producto

### 1.1 Problema a resolver

Los call centers bancarios necesitan evaluar la calidad de las llamadas entre ejecutivos y clientes para garantizar:

- Cumplimiento de protocolos y normativa financiera
- Calidad del servicio al cliente (asertividad, tono, empatía)
- Mención correcta de promociones y productos
- Resolución efectiva de las consultas

Actualmente, esta evaluación se hace de forma manual por supervisores de QA, quienes escuchan llamadas al azar. El proceso es:

- **Lento:** Un supervisor solo puede revisar ~10-15 llamadas/día
- **Subjetivo:** La evaluación depende del criterio personal
- **No escalable:** Solo se audita el 1-2% de las llamadas
- **Inconsistente:** Diferentes supervisores evalúan distinto

### 1.2 Solución propuesta

Una plataforma web donde el supervisor de QA sube grabaciones de llamadas y, mediante IA (transcripción + análisis con modelos de lenguaje), obtiene en minutos:

- Transcripción completa con timestamps
- Evaluación objetiva contra una rúbrica predefinida (7 dimensiones)
- Score numérico por dimensión + score global tipo NPS
- Recomendaciones accionables específicas para el ejecutivo
- Comparativa contra el promedio del equipo

### 1.3 Propuesta de valor

| Métrica | Antes (manual) | Con CallQA AI |
|---|---|---|
| Llamadas evaluadas/día | 10-15 | Ilimitadas |
| Tiempo por llamada | 20-30 min | 2-3 min |
| Cobertura del equipo | 1-2% | 100% |
| Consistencia | Variable | Alta |
| Costo por evaluación | Alto (hora-supervisor) | Bajo (API) |

### 1.4 Alcance del MVP (este proyecto)

**Sí incluye:**

- Subida manual de archivos de audio (MP3, WAV, M4A)
- Transcripción automática en español (configurable a otros idiomas)
- Análisis IA sobre 7 dimensiones de evaluación
- Dashboard de supervisor con métricas y reportes
- Gestión de ejecutivos (alta, baja, edición)
- Comparativas individuales vs promedio del equipo
- Exportación de reportes (PDF/CSV)

**NO incluye (para futuras versiones):**

- Integración con sistemas telefónicos (Genesys, Avaya, etc.)
- Análisis en tiempo real durante la llamada
- Aplicación móvil
- Vista para el ejecutivo (solo supervisor en MVP)
- Multi-tenant (varios call centers en una sola instancia)

---

## 2. Usuarios y Roles

### 2.1 Rol único: Supervisor de QA

En esta versión MVP existe un único rol con todos los permisos:

| Capacidad | Descripción |
|---|---|
| Subir llamadas | Carga archivos de audio individualmente o en lote |
| Asignar ejecutivo | Indica a qué ejecutivo pertenece cada llamada |
| Ver análisis | Consulta transcripción, scores y recomendaciones |
| Gestionar ejecutivos | Crea/edita/elimina ejecutivos del equipo |
| Configurar rúbrica | Ajusta pesos de cada dimensión de evaluación |
| Ver dashboard | Consulta métricas agregadas del equipo |
| Exportar reportes | Descarga reportes en PDF/CSV |
| Configurar idioma | Cambia el idioma de análisis |

### 2.2 Actores externos (no-usuarios del sistema)

- **Ejecutivo de call center:** Sujeto evaluado. No accede al sistema en MVP, pero recibe el feedback a través del supervisor.
- **Cliente del banco:** Persona en la llamada. Su voz se procesa pero no se identifica nominalmente.

---

## 3. Casos de Uso Principales

### CU-01: Subir una llamada para análisis

**Actor:** Supervisor de QA
**Precondición:** Usuario autenticado, ejecutivo registrado en el sistema
**Flujo principal:**

1. El supervisor accede a la sección "Nueva llamada"
2. Selecciona el ejecutivo al que pertenece la llamada
3. Adjunta el archivo de audio (MP3/WAV/M4A, máx. 100MB)
4. Opcionalmente añade metadatos: fecha de la llamada, tipo de campaña, motivo
5. Confirma la subida
6. El sistema valida el archivo y lo encola para procesamiento
7. El sistema muestra el estado: "En cola → Transcribiendo → Analizando → Listo"
8. Al finalizar, el supervisor puede acceder al análisis completo

**Postcondición:** La llamada queda registrada con su transcripción y análisis.

**Flujo alternativo:**

- **3a.** Si el archivo excede el tamaño o formato no soportado → mostrar error y permitir reintento.
- **6a.** Si la transcripción falla → marcar llamada como "Error" y permitir reintento manual.

---

### CU-02: Consultar el análisis de una llamada

**Actor:** Supervisor de QA
**Precondición:** Llamada procesada con estado "Listo"
**Flujo principal:**

1. El supervisor accede al listado de llamadas
2. Filtra por ejecutivo, fecha o score
3. Selecciona una llamada
4. El sistema muestra:
   - Datos generales (ejecutivo, fecha, duración)
   - Score global (0-100, tipo NPS)
   - Score por cada una de las 7 dimensiones
   - Recomendaciones accionables priorizadas
   - Comparativa contra promedio del equipo
   - Transcripción completa con timestamps (opcional, expandible)
5. El supervisor puede descargar el reporte en PDF

**Postcondición:** El supervisor obtiene insights para retroalimentar al ejecutivo.

---

### CU-03: Comparar performance del ejecutivo vs equipo

**Actor:** Supervisor de QA
**Precondición:** Al menos 5 llamadas analizadas del ejecutivo y 20 del equipo
**Flujo principal:**

1. El supervisor accede al perfil del ejecutivo
2. El sistema muestra:
   - Score promedio del ejecutivo por dimensión (últimos 30 días)
   - Score promedio del equipo por dimensión (mismo periodo)
   - Tendencia temporal (gráfico de líneas)
   - Top 3 fortalezas y top 3 áreas de mejora
3. El supervisor exporta el reporte para reunión 1-a-1

**Postcondición:** El supervisor cuenta con un reporte ejecutivo para coaching.

---

### CU-04: Gestionar el equipo de ejecutivos

**Actor:** Supervisor de QA
**Precondición:** Usuario autenticado
**Flujo principal:**

1. El supervisor accede a "Equipo"
2. Visualiza la lista de ejecutivos activos
3. Puede:
   - Crear nuevo ejecutivo (nombre, email, fecha ingreso, campaña asignada)
   - Editar datos de un ejecutivo existente
   - Desactivar un ejecutivo (no se elimina, se marca inactivo)
4. Los cambios se reflejan inmediatamente en los formularios de subida

**Postcondición:** El equipo está actualizado.

---

### CU-05: Configurar la rúbrica de evaluación

**Actor:** Supervisor de QA
**Precondición:** Usuario autenticado
**Flujo principal:**

1. El supervisor accede a "Configuración → Rúbrica"
2. El sistema muestra las 7 dimensiones por defecto con sus pesos
3. El supervisor puede ajustar el peso porcentual de cada dimensión (suma = 100%)
4. Opcionalmente, ajusta los criterios específicos de cada dimensión (texto libre)
5. Guarda los cambios — aplicarán a las próximas llamadas analizadas

**Postcondición:** La rúbrica queda configurada según las prioridades del negocio.

---

### CU-06: Ver dashboard agregado del equipo

**Actor:** Supervisor de QA
**Precondición:** Usuario autenticado, al menos una llamada procesada
**Flujo principal:**

1. El supervisor accede al dashboard principal
2. El sistema muestra:
   - KPIs principales: total de llamadas analizadas, score promedio del equipo, tendencia semanal
   - Top 5 ejecutivos con mejor performance
   - Top 5 ejecutivos con mayor oportunidad de mejora
   - Distribución de scores por dimensión (gráfico)
   - Listado de últimas llamadas procesadas
3. Puede aplicar filtros temporales (últimos 7/30/90 días)

**Postcondición:** El supervisor tiene visibilidad completa del estado del equipo.

---

## 4. Reglas de Negocio

### RN-01: Dimensiones de evaluación

La rúbrica parte de 7 dimensiones por defecto, cada una evaluada de 0 a 100. La rúbrica es editable: se pueden activar/desactivar subcategorías y añadir/eliminar tanto categorías como subcategorías; la IA evalúa según los subcriterios activos.

1. **Saludo y protocolo de apertura/cierre**
2. **Asertividad y tono** (empatía, claridad, paciencia)
3. **Mención correcta de promociones/productos**
4. **Cumplimiento normativo** (disclaimers, grabación, datos sensibles)
5. **Resolución efectiva del motivo de la llamada**
6. **Manejo de objeciones del cliente**
7. **Detección de sentimiento del cliente** (satisfacción percibida)

### RN-02: Cálculo del score global

El score global (tipo NPS, escala 0-100) se calcula como:

```
Score Global = Σ (Score_dimensión_i × Peso_dimensión_i) / 100
```

Donde los pesos por defecto son iguales (14.28% cada una), pero el supervisor puede ajustarlos.

### RN-03: Clasificación del score

| Score | Clasificación | Color |
|---|---|---|
| 80-100 | Excelente | 🟢 Verde |
| 60-79 | Aceptable | 🟡 Amarillo |
| 0-59 | Requiere atención | 🔴 Rojo |

### RN-04: Retención de datos

- Audios originales: se conservan por 90 días, luego se eliminan automáticamente
- Transcripciones y análisis: se conservan indefinidamente
- Los ejecutivos desactivados conservan su historial

### RN-05: Formatos de audio soportados

- MP3, WAV, M4A, OGG, FLAC
- Tamaño máximo: 100 MB
- Duración máxima recomendada: 60 minutos por llamada

### RN-06: Idioma configurable

- Idioma por defecto: español
- Configurable a nivel global (no por llamada en MVP)
- Whisper soporta 90+ idiomas; el prompt de análisis se adapta al idioma seleccionado

---

## 5. Métricas de Éxito del MVP

| Métrica | Objetivo |
|---|---|
| Tiempo de procesamiento por llamada | < 3 minutos para audio de 10 min |
| Precisión de transcripción | > 92% (WER < 8%) |
| Disponibilidad del servicio | > 99% en horario laboral |
| Llamadas procesables por día | > 500 (sin degradación) |
| Tiempo de carga del dashboard | < 2 segundos |
| Satisfacción del supervisor (encuesta) | NPS > 50 |

---

## 6. Restricciones y Supuestos

### Restricciones

- Las llamadas deben estar en formato de audio (no video)
- El audio debe tener calidad mínima audible (no se pueden procesar audios muy ruidosos)
- Datos sensibles del cliente (números de tarjeta, DNI completo) no deben mostrarse en transcripción visible — se enmascaran automáticamente

### Supuestos

- El supervisor cuenta con conexión estable a internet
- Las llamadas a procesar son grabaciones legales con consentimiento del cliente
- El call center cumple con la normativa local de protección de datos (GDPR, Ley de Protección de Datos Personales del país)

---

## 7. Compliance y Gobernanza de Datos (Contexto Minsait/Indra)

> **Importante:** Este MVP es un **prototipo/piloto interno** para validar el concepto. Antes de su paso a producción con datos reales, los siguientes puntos deben ser validados con las áreas correspondientes.

### 7.1 Fases del proyecto y manejo de datos

| Fase | Datos utilizados | Aprobaciones requeridas |
|---|---|---|
| **Prototipo (actual)** | Audios sintéticos / grabaciones propias simuladas | Ninguna formal — uso interno de demo |
| **Piloto controlado** | Audios reales anonimizados con consentimiento explícito | Aprobación de supervisor directo + DPO |
| **Producción** | Audios reales del call center en operación | Compliance + Legal + Seguridad de la Información + DPO |

### 7.2 Áreas a involucrar antes de producción

Cuando se decida escalar más allá del prototipo, se requiere coordinar con:

- **Compliance / Cumplimiento normativo:** Validación del uso de IA generativa con datos de clientes bancarios
- **DPO (Data Protection Officer):** Evaluación de impacto en protección de datos (EIPD/DPIA) bajo GDPR y leyes locales
- **Seguridad de la Información (CISO):** Aprobación de proveedores externos (Anthropic, OpenAI, Groq), análisis de riesgos
- **Arquitectura Corporativa:** Migración a infraestructura corporativa (Azure, posiblemente)
- **Legal:** Revisión de contratos con proveedores de IA, cláusulas de tratamiento de datos
- **Compras/Procurement:** Si se requiere contrato corporativo con Anthropic/OpenAI vs cuenta personal

### 7.3 Roadmap de cumplimiento sugerido

```
PROTOTIPO (HOY)               PILOTO (Q3 2026)              PRODUCCIÓN (Q4 2026+)
─────────────────             ──────────────────            ────────────────────────
Railway + Vercel              Azure App Service             Azure App Service
APIs públicas (Claude/Groq)   Azure OpenAI Service          Azure OpenAI + Whisper on-prem
Datos simulados               Datos anonimizados            Datos reales con consentimiento
Sin EIPD formal               EIPD inicial                  EIPD completa + auditoría
1 supervisor demo             5-10 ejecutivos piloto        Todo el call center
```

### 7.4 Consideraciones específicas de Minsait/Indra

- **Cloud preferente para producción:** Azure (estándar del grupo Indra para muchas áreas)
- **Servicios IA equivalentes en Azure:** Azure OpenAI Service (GPT-4), Azure AI Speech (transcripción)
- **El código generado debe ser portable:** Por eso usamos variables de entorno y patrones factory, para que la migración Cloud no requiera reescribir el sistema
- **Branding:** Aplicación interna con paleta de colores corporativa Minsait, con disclaimer "Prototipo - Demo" visible en todas las pantallas durante esta fase

### 7.5 Disclaimer del prototipo

Todas las pantallas del prototipo deben incluir un banner persistente:

> ⚠️ **PROTOTIPO — DEMO INTERNA**
> Esta es una prueba de concepto. No utilizar con datos reales de clientes sin aprobación previa de Compliance.

---

## 8. Glosario

| Término | Definición |
|---|---|
| **QA** | Quality Assurance — Aseguramiento de calidad |
| **NPS** | Net Promoter Score — Escala de 0-100 para medir satisfacción |
| **Rúbrica** | Conjunto de criterios para evaluar de forma estandarizada |
| **STT** | Speech-to-Text — Transcripción de voz a texto |
| **LLM** | Large Language Model — Modelo de lenguaje grande (Claude, GPT) |
| **Whisper** | Modelo open-source de OpenAI para transcripción de audio |
| **Groq** | Plataforma de inferencia ultra rápida con Whisper vía API |
| **MVP** | Minimum Viable Product — Producto mínimo viable |
| **DPO** | Data Protection Officer — Delegado de Protección de Datos |
| **EIPD/DPIA** | Evaluación de Impacto en Protección de Datos |
| **CISO** | Chief Information Security Officer — Director de Seguridad |
| **GDPR** | General Data Protection Regulation (UE) |
| **PoC** | Proof of Concept — Prueba de concepto |
