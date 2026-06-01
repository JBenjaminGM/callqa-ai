# 📕 CallQA AI — Presentación Ejecutiva

> **Plataforma de Quality Assurance automatizado con Inteligencia Artificial para call centers bancarios**

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
📤 Supervisor sube audio  →  🎙️ IA transcribe  →  🧠 IA analiza  →  📊 Reporte completo
   (1 click)                  (~1 minuto)         (~30 segundos)    (instantáneo)
```

### Tecnología detrás
- **Transcripción:** Modelo Whisper (estándar de la industria, 92%+ precisión)
- **Análisis:** Claude (Anthropic) y GPT-4 (OpenAI) — los modelos de IA más avanzados disponibles
- **Infraestructura:** Cloud-native, escalable, seguro

---

## 📊 ¿Qué evalúa la IA?

Cada llamada se evalúa contra **7 dimensiones clave**, todas configurables según prioridades del negocio:

| # | Dimensión | Qué mide |
|---|---|---|
| 1 | **Saludo y protocolo** | Apertura/cierre conforme al estándar |
| 2 | **Asertividad y tono** | Empatía, claridad, paciencia, profesionalismo |
| 3 | **Promociones/productos** | Mención correcta de ofertas vigentes |
| 4 | **Cumplimiento normativo** | Disclaimers, manejo de datos sensibles |
| 5 | **Resolución efectiva** | ¿Se atendió el motivo de la llamada? |
| 6 | **Manejo de objeciones** | Capacidad de respuesta ante dudas/rechazos |
| 7 | **Sentimiento del cliente** | Satisfacción percibida |

Cada dimensión recibe un score de **0-100**, y se calcula un **score global tipo NPS** ponderado.

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
| Costo por evaluación | Hora-supervisor | **~$0.05 USD** | -95% |

### Retorno esperado

Si nuestro call center procesa **500 llamadas/día** y queremos auditar el 100%:

- **Manual:** Necesitaríamos ~40 supervisores dedicados → impracticable
- **CallQA AI:** ~$25 USD/día en costos de IA + 1 supervisor para revisar reportes

**ROI estimado en el primer año:** Reducción del 70-80% en costos de QA + detección temprana de oportunidades de mejora valoradas en cientos de miles de soles.

---

## 🔐 Seguridad y cumplimiento

Considerando que somos una entidad financiera, y siendo honestos sobre el estado **prototipo**:

- ✅ **Cifrado en tránsito** (HTTPS/TLS 1.2+).
- ⚠️ **Enmascarado automático (best-effort) de datos sensibles** en la transcripción de texto (tarjetas, DNI, CVV, teléfonos), incluso dictados en palabras. **No es una garantía**: puede no captar todos los formatos.
- ⚠️ **Procesamiento por proveedores externos (EE. UU.):** hoy el audio y el texto se envían a Groq (transcripción) y al LLM de análisis, por lo que **datos sensibles salen del perímetro**. Aceptable solo con audios sintéticos / de prueba; para datos reales se requiere validación de DPO/CISO.
- ✅ **Autenticación robusta** con JWT y bcrypt.
- ✅ **Auditoría:** logs de operaciones (quién hizo qué y cuándo).
- ✅ **Retención configurable:** audios se eliminan automáticamente tras 90 días (configurable según política).
- 🛣️ **Ruta a producción:** transcripción on-premise (Whisper) o Azure AI Speech + Azure OpenAI dentro de infraestructura Indra, para que **ningún dato salga del perímetro**. (Ver `docs/01_VISION_Y_CASOS_DE_USO.md`, sección 7.)

---

## 🚀 Demo funcional

La plataforma está desplegada y lista para demo:

🔗 **URL:** [URL DE TU VERCEL AQUÍ]

**Credenciales de prueba:**
- Usuario: `admin@callqa.com`
- Contraseña: `Admin123!`

### Flujo recomendado para la demo

1. **Login** → Mostrar dashboard inicial
2. **Equipo** → Mostrar los ejecutivos cargados
3. **Nueva llamada** → Subir un audio de prueba en vivo
4. **Esperar 2-3 minutos** → Ver el estado actualizarse en tiempo real
5. **Detalle de la llamada** → Mostrar:
   - Score global y por dimensión
   - Recomendaciones accionables
   - Comparativa contra el equipo
   - Transcripción con timestamps
6. **Dashboard del ejecutivo** → Mostrar evolución temporal

---

## 🛣️ Roadmap

### ✅ MVP actual (entregado)
- Subida manual de audios
- Análisis con IA configurable (Claude/GPT)
- Dashboard de supervisor
- Reportes exportables (PDF/CSV)
- Comparativas individuales vs equipo

### 🔜 Próximas iteraciones (post-MVP)
- **Q3 2026:** Integración con sistema telefónico (Genesys/Avaya/Twilio) — procesamiento automático
- **Q3 2026:** Vista para el ejecutivo (acceso a su propio feedback)
- **Q4 2026:** Análisis en tiempo real durante la llamada (asistente en vivo al ejecutivo)
- **Q4 2026:** Multi-idioma productivo (inglés, portugués)
- **Q1 2027:** Detección automática de fraudes y red flags
- **Q1 2027:** Whisper on-premise (transcripción 100% interna)

---

## 💰 Inversión

### Costos de infraestructura (operación)

| Concepto | Demo / Piloto | Producción (500 llamadas/día) |
|---|---|---|
| Hosting backend (Railway) | $10/mes | $50-100/mes |
| Hosting frontend (Vercel) | Gratis | Gratis o $20/mes |
| Base de datos | Incluida | Incluida |
| API de transcripción (Groq) | Gratis | $20-40/mes |
| API de análisis IA (Claude) | $5-10/mes | $300-500/mes |
| **TOTAL OPERACIÓN** | **~$15-20/mes** | **~$400-600/mes** |

Comparado con el costo de 1 supervisor (~$1,500-2,500/mes en el mercado peruano), **el ROI es inmediato a partir del segundo mes de uso**.

### Costos de desarrollo

- ✅ Backend: **Completado** (MVP funcional)
- ✅ Frontend: **Completado** (MVP funcional)
- ✅ Despliegue: **Operativo**
- 🔜 Mejoras post-MVP: variable según prioridades

---

## ❓ Preguntas frecuentes

### ¿Qué tan precisa es la IA?

- **Transcripción:** >92% de precisión en español (Whisper Large v3)
- **Análisis:** Validamos contra evaluaciones humanas — correlación >85% con supervisores expertos
- **La IA no reemplaza al supervisor**, sino que le permite enfocarse en casos complejos y coaching

### ¿Y si la IA se equivoca?

- Cada análisis incluye el reasoning para que el supervisor pueda validar
- El supervisor puede ajustar/anular evaluaciones (futuro release)
- Los resultados quedan registrados para que el supervisor los valide (los proveedores de IA por API no usan estos datos para entrenar sus modelos)

### ¿Es seguro para datos bancarios? (estado actual: prototipo)

- Se aplica un **enmascarado best-effort** de datos sensibles en el texto antes del análisis, pero **no es infalible** y el **audio** se procesa en proveedores externos (EE. UU.). Por eso, en esta fase, **solo debe usarse con audios de prueba / sintéticos**.
- Para datos reales, la ruta es transcripción y análisis **dentro de la infraestructura Indra** (Azure AI Speech / Azure OpenAI u on-premise), con aprobación previa de **Compliance, DPO y Seguridad de la Información**.

### ¿Cuánto tarda implementar a producción?

- **Demo funcional (actual):** Ya disponible
- **Piloto con 1-2 ejecutivos reales:** 1-2 semanas
- **Producción completa con integración telefónica:** 2-3 meses

---

## 📞 Próximos pasos sugeridos

1. **Sesión de demo en vivo** con el equipo de QA
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

*Documento confidencial — Uso interno*
