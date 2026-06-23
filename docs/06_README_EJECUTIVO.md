# 📕 CallQA AI — Presentación Ejecutiva

> **Plataforma de Quality Assurance automatizado con Inteligencia Artificial para call centers bancarios**

---

> 🔎 **Vista previa para evaluación.** Esta es una **vista previa para evaluación**
> que se presenta oficialmente al cliente. Sigue siendo un prototipo: **no debe
> usarse con datos reales de clientes sin la aprobación previa de Compliance.**

---

## 🎯 El problema que resolvemos

En nuestro call center, los supervisores de QA evalúan manualmente las llamadas entre ejecutivos y clientes. Este proceso actual presenta limitaciones significativas:

| Limitación | Impacto |
|---|---|
| 🕐 Solo se auditan 10-15 llamadas/día por supervisor | **Cobertura del 1-2% del total** |
| 👤 Evaluación subjetiva según el criterio del supervisor | **Inconsistencia entre evaluadores** |
| ⏱️ 20-30 minutos por llamada evaluada | **Costo operativo alto** |
| 📊 Insights tardíos, una vez al mes | **Reacción lenta a problemas** |

**Como resultado, no podemos garantizar la calidad uniforme del servicio ni detectar oportunidades de mejora a tiempo.**

---

## 💡 Nuestra solución

**CallQA AI** es una plataforma web que utiliza inteligencia artificial para analizar automáticamente cada llamada del call center y entregar evaluaciones objetivas, consistentes y accionables en minutos.

### ¿Cómo funciona?

```
📤 Sube audio  →  🎙️ IA transcribe  →  🔒 Enmascara PII  →  🧠 IA analiza  →  📊 Reporte + PDF
   (1 click)       (Groq Whisper)      (best-effort)        (Llama 3.3 70B)   (scores + recomendaciones)
```

Cada llamada se analiza contra una **rúbrica dinámica** y produce **scores por dimensión**, un **score global ponderado**, **recomendaciones accionables** y un **reporte PDF** descargable.

### Tecnología detrás
- **Transcripción:** Groq Whisper large v3 (estándar de la industria, alta precisión en español)
- **Análisis:** por defecto **Groq con Llama 3.3 70B** (capa gratuita); el patrón factory es portable a Claude (Anthropic), OpenAI o Azure solo cambiando configuración
- **Infraestructura:** Cloud-native, desplegada en vivo, coste $0

---

## 🪪 Tres vistas según el rol

CallQA AI adapta la experiencia al rol de cada usuario. Hay **tres roles**:

| Rol | Qué ve y qué puede hacer |
|---|---|
| 👑 **Admin** | Gestión completa + analítica global del equipo |
| 🧑‍💼 **Jefe** | Mismos permisos que admin (gestión + analítica global): sube/asigna/reintenta/elimina llamadas, gestiona ejecutivos y campañas, configura rúbrica y umbrales |
| 🎧 **Asesor** | **Solo su propio rendimiento**: su ficha de ejecutivo, sus llamadas y su panel **"Mi rendimiento"** |

El asesor inicia sesión vinculado a su ficha de ejecutivo; no accede al dashboard global ni a las acciones de gestión. La navegación y la redirección se ajustan al rol automáticamente (asesor → "Mi panel"; admin/jefe → Dashboard).

---

## 📦 Campañas con nota de producto

CallQA AI evalúa cada llamada **en el contexto de la campaña** a la que pertenece. Cada **campaña** lleva una **nota de producto** de 9 campos:

- Producto/servicio · Descripción de la oferta · Beneficios clave
- Precio/condiciones · Requisitos del cliente · Frases obligatorias
- Claims prohibidos · Público objetivo · Notas

La nota de producto se crea **por formulario (con asistente de IA)** o **subiendo un PDF**: la IA lo parsea y autocompleta los campos, y lo que no encuentre se pide en el formulario. Esa nota se **inyecta en el análisis** para verificar si el ejecutivo ofreció la oferta correcta y respetó las frases obligatorias y los claims prohibidos.

---

## 📊 ¿Qué evalúa la IA?

Cada llamada se evalúa contra una **rúbrica dinámica** de dimensiones clave (con subcriterios), todas configurables y ponderables según las prioridades del negocio:

| # | Dimensión | Qué mide |
|---|---|---|
| 1 | **Saludo y protocolo** | Apertura/cierre conforme al estándar |
| 2 | **Asertividad y tono** | Empatía, claridad, paciencia, profesionalismo |
| 3 | **Promociones/productos** | Mención correcta de la oferta de la campaña |
| 4 | **Cumplimiento normativo** | Disclaimers, frases obligatorias, manejo de datos sensibles |
| 5 | **Resolución efectiva** | ¿Se atendió el motivo de la llamada? |
| 6 | **Manejo de objeciones** | Capacidad de respuesta ante dudas/rechazos |
| 7 | **Sentimiento del cliente** | Satisfacción percibida |

Cada dimensión recibe un score de **0-100**, y se calcula un **score global ponderado**.

### Umbrales de QA configurables

El jefe puede ajustar los umbrales que gobiernan la analítica y las alertas: meta de score (90), umbral de asesor bajo (80), umbral de llamada en rojo (60), mínimo de llamadas para entrar al ranking (5) y caída de tendencia que dispara alerta (5). Quedan persistidos y solo un manager puede editarlos.

---

## 📈 Beneficios cuantitativos

### Comparativa: situación actual vs CallQA AI

| Métrica | Antes | Con CallQA AI | Mejora |
|---|---|---|---|
| Llamadas evaluadas por día | 10-15 | **Ilimitadas** | ∞ |
| Tiempo de evaluación | 20-30 min | **2-3 min** | -90% |
| Cobertura del equipo | 1-2% | **100%** | +9,900% |
| Consistencia evaluación | Variable | **Alta** | ✅ |
| Detección de incidentes | Días/semanas | **Minutos** | ⚡ |
| Costo por evaluación | Hora-supervisor | **~$0 (Groq, capa gratuita)** | -99% |

### Retorno esperado

Si nuestro call center procesa **500 llamadas/día** y queremos auditar el 100%:

- **Manual:** Necesitaríamos ~40 supervisores dedicados → impracticable
- **CallQA AI:** análisis con Groq en su capa gratuita ($0 en IA) + infraestructura gratuita (Vercel/Render) + 1 supervisor para revisar reportes

**ROI estimado en el primer año:** Reducción del 70-80% en costos de QA + detección temprana de oportunidades de mejora valoradas en cientos de miles de soles.

---

## 🔐 Seguridad y cumplimiento

Considerando que somos una entidad financiera, y siendo honestos sobre el estado **vista previa para evaluación**:

- ✅ **Cifrado en tránsito** (HTTPS/TLS 1.2+).
- ⚠️ **Enmascarado automático (best-effort) de datos sensibles** en la transcripción de texto (tarjetas, DNI, CVV, teléfonos), incluso dictados en palabras. **No es una garantía**: puede no captar todos los formatos.
- ⚠️ **Procesamiento por proveedores externos (EE. UU.):** hoy el audio y el texto se envían a Groq (transcripción) y al LLM de análisis, por lo que **datos sensibles salen del perímetro**. Aceptable solo con audios sintéticos / de prueba; para datos reales se requiere validación de DPO/CISO.
- ✅ **Autenticación robusta** con JWT y bcrypt, con **control de acceso por rol** (admin/jefe/asesor) y *scoping* de datos (el asesor solo ve lo suyo).
- ✅ **Auditoría:** logs de operaciones (quién hizo qué y cuándo).
- ✅ **Retención configurable:** audios se eliminan automáticamente tras 90 días (configurable según política).
- 🛣️ **Ruta a producción:** transcripción on-premise (Whisper) o Azure AI Speech + Azure OpenAI dentro de infraestructura Indra, para que **ningún dato salga del perímetro**. (Ver `docs/01_VISION_Y_CASOS_DE_USO.md`, sección 7.)

El banner persistente de la aplicación lo recuerda: *"Vista previa — entorno de evaluación. No utilizar con datos reales de clientes sin la aprobación previa de Compliance."*

---

## 🎨 Identidad visual Minsait

La interfaz está rebrandeada a la **identidad oficial Minsait**:

- **Paleta:** **Pruno** (`#480E2A`) y **Gris Cerámica** (`#E3E2DA`) dominan; **Fucsia** (`#FF0054`) solo como acento.
- **Tipografía:** **ForFuture Sans**.
- **Logo oficial Minsait** y contenedores **achaflanados** (chaflán).
- **Titulares en minúscula** con la palabra clave en Fucsia (dispositivo "calidad con impacto"); CTA = píldora Fucsia.
- **Modo claro por defecto** (Gris Cerámica) y modo oscuro Pruno; sidebar siempre Pruno con el logo blanco.

---

## 🚀 Vista previa en vivo

La plataforma está **desplegada en vivo** y lista para evaluación (coste $0):

🔗 **Frontend:** https://callqa-ai.vercel.app
🔗 **API (backend):** https://callqa-api.onrender.com (`/docs`, `/health`)

> ⏱️ **Nota de arranque en frío:** el plan gratuito de Render **duerme el backend tras ~15 min** de inactividad. La primera petición puede tardar ~50 s en despertarlo (podría verse como un "error de API"). El frontend muestra el mensaje *"activando el servidor"* y reintenta automáticamente; además un *keepalive* programado lo mantiene despierto la mayor parte del tiempo.

**Cuentas sembradas para la evaluación:**
- 👑 Admin — `admin@callqa.com` / `Admin123!`
- 🧑‍💼 Jefe — `jefe@callqa.com` / `Jefe123!`
- 🎧 Asesor — el email del ejecutivo demo (p. ej. `maria@banco.com`) / `Asesor123!`

> Por seguridad, el login **ya no muestra credenciales en pantalla** y el seed **ya no imprime contraseñas**.

### Recorrido recomendado

1. **Login como jefe** → Dashboard global del equipo.
2. **Campañas** → Crear una campaña subiendo un PDF (la IA autocompleta la nota de producto) o por formulario con el asistente de IA.
3. **Equipo** → Ver los ejecutivos cargados.
4. **Nueva llamada** → Subir un audio de prueba, asociado a su campaña.
5. **Esperar 2-3 minutos** → Ver el estado actualizarse en tiempo real.
6. **Detalle de la llamada** → Score global y por dimensión, recomendaciones accionables, transcripción con timestamps y **reporte PDF**.
7. **Login como asesor** → Comprobar que solo ve **"Mi rendimiento"**, sus llamadas y su ficha (sin acceso al dashboard global).

---

## 🛣️ Roadmap

### ✅ Entregado en esta vista previa
- Subida manual de audios + procesamiento (transcripción, enmascarado, análisis)
- Análisis con IA configurable (Groq por defecto; Claude/OpenAI/Azure opcionales)
- **Tres vistas por rol** (admin/jefe/asesor) con scoping de datos
- **Campañas con nota de producto** (formulario + asistente IA + parseo de PDF)
- Rúbrica dinámica con subcriterios y **umbrales de QA configurables**
- Reportes en **PDF**
- **Identidad visual Minsait**

### 🔜 Próximas iteraciones (no implementadas todavía)
- Analítica de jefe de alto impacto: fila de alertas accionables, KPIs por campaña, top asesores por campaña, top problemas recurrentes
- Métricas de conversación (talk/listen ratio, % de silencio, monólogos, velocidad de habla) derivadas de la transcripción
- Vista de asesor enriquecida (percentil anónimo dentro de la campaña, "qué cambiar" con evidencia, cumplimiento por campaña)
- Reproductor de audio sincronizado y exportación CSV del equipo
- Validaciones de Compliance/DPO/Seguridad previas a producción real

---

## 💰 Inversión

### Costos de infraestructura (operación)

| Concepto | Vista previa en vivo (actual) | Producción estimada (500 llamadas/día) |
|---|---|---|
| Hosting backend (Render) | Gratis | $25-100/mes (plan con worker) |
| Hosting frontend (Vercel) | Gratis | Gratis o $20/mes |
| Base de datos (Render PostgreSQL) | Gratis | Incluida / plan de pago |
| API de transcripción (Groq) | Gratis | $20-40/mes |
| API de análisis IA (Groq, capa gratuita) | Gratis | Gratis ($0) |
| **TOTAL OPERACIÓN** | **$0** | **~$45-160/mes** |

La **vista previa actual cuesta literalmente $0** (Groq gratis + tiers gratuitos de
Vercel y Render). Incluso en una proyección de producción y comparado con el costo
de 1 supervisor (~$1,500-2,500/mes en el mercado peruano), **el ROI es inmediato**.

> ⚠️ El PostgreSQL gratuito de Render **caduca a los 90 días**; para una operación continuada se migra a un plan de pago.

### Costos de desarrollo

- ✅ Backend: **Completado** (funcional)
- ✅ Frontend: **Completado** (funcional)
- ✅ Despliegue: **Operativo en vivo**
- 🔜 Mejoras del roadmap: variable según prioridades

---

## ❓ Preguntas frecuentes

### ¿Qué tan precisa es la IA?

- **Transcripción:** alta precisión en español (Groq Whisper large v3)
- **Análisis:** Llama 3.3 70B contra una rúbrica dinámica con subcriterios; cada análisis incluye recomendaciones y resumen para que el supervisor valide
- **La IA no reemplaza al supervisor**, sino que le permite enfocarse en casos complejos y coaching

### ¿Y si la IA se equivoca?

- Cada análisis incluye recomendaciones y un resumen para que el supervisor pueda validar
- Los resultados quedan registrados para auditoría
- Los proveedores de IA por API no usan estos datos para entrenar sus modelos

### ¿Es seguro para datos bancarios? (estado actual: vista previa para evaluación)

- Se aplica un **enmascarado best-effort** de datos sensibles en el texto antes del análisis, pero **no es infalible** y el **audio** se procesa en proveedores externos (EE. UU.). Por eso, en esta fase, **solo debe usarse con audios de prueba / sintéticos y nunca con datos reales de clientes sin aprobación previa de Compliance**.
- Para datos reales, la ruta es transcripción y análisis **dentro de la infraestructura Indra** (Azure AI Speech / Azure OpenAI u on-premise), con aprobación previa de **Compliance, DPO y Seguridad de la Información**.

### ¿Cuánto tarda implementar a producción?

- **Vista previa funcional (actual):** Ya disponible
- **Piloto con 1-2 ejecutivos reales:** 1-2 semanas
- **Producción completa con integración telefónica:** 2-3 meses

---

## 📞 Próximos pasos sugeridos

1. **Sesión de evaluación en vivo** con el equipo de QA
2. **Piloto controlado** con 5-10 ejecutivos y llamadas reales (1 mes)
3. **Validación de resultados** contra evaluaciones manuales
4. **Decisión de scaling:** integración con sistema telefónico para automatización completa
5. **Roadmap definitivo** según prioridades del negocio

---

## 👥 Contacto

**Líder del proyecto:** [TU NOMBRE]
**Cargo:** [TU CARGO]
**Email:** [TU EMAIL]
**Slack/Teams:** [TU USUARIO]

---

*Documento confidencial — Vista previa para evaluación · Minsait (Grupo Indra)*
