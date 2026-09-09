# Acuerdos

> Las decisiones que hemos tomado, por qué, y **qué costaría cambiarlas**.
>
> Ninguna es inamovible. Este documento existe para que puedas revisar cualquiera sabiendo
> el precio real de darle la vuelta. Si cambias una, edita aquí el motivo: es la memoria del
> proyecto.

**Cómo leer el coste de cambio**

| | Significa |
|---|---|
| 🟢 **Barato** | Horas. Sin riesgo para lo que ya funciona. |
| 🟡 **Medio** | Días. Hay que volver a probar cosas. |
| 🔴 **Caro** | Semanas, o implica downtime o pérdida de datos. |

---

## Producto y marca

### A-01 · El producto se llama CallAIbrate
**Qué acordamos.** El nombre se escribe siempre `CallAIbrate`, con "AI" en mayúsculas y
resaltado en color `rust` en la interfaz. La fuente de verdad de la marca es
[`BRAND.md`](BRAND.md); [`DESIGN.md`](DESIGN.md) explica cómo se aplica.

**Por qué.** Juego de palabras entre *Call*, *AI* y *Calibrate*: calibrar es ajustar un
instrumento de medición con precisión, que es literalmente lo que hace el producto.

**Coste de cambio.** 🟡 Otro rebrand completo son unos días: tokens de color, tipografías,
wordmark, copy y documentación. La infraestructura ya no habría que tocarla.

---

### A-02 · La identidad Minsait está retirada
**Qué acordamos.** Paleta Pruno/Cerámica/Fucsia, tipografía ForFuture Sans y contenedores
achaflanados quedan **obsoletos**. Se mantienen las referencias de negocio al sector banca.

**Por qué.** El producto dejó de presentarse bajo la marca del cliente. Además, las
tipografías ForFuture Sans tenían licencia de Minsait: eliminarlas era también lo correcto
legalmente.

**Coste de cambio.** 🟡 Igual que A-01.

---

### A-03 · La plataforma se presenta como terminada, no como prototipo
**Qué acordamos.** El banner de "vista previa" se retiró de la interfaz. Se conservan dos
salvaguardas internas que el usuario no ve: la cabecera HTTP `X-Prototype-Notice` y el campo
`environment="evaluation"` en los registros.

**Por qué.** Decisión tuya: querías presentarlo como producto acabado. Las salvaguardas
internas se quedan como aviso técnico de que aún no está aprobado para datos reales.

**Coste de cambio.** 🟢 Retirar las salvaguardas es un commit — pero solo debe hacerse
cuando existan las tres firmas de [`COMPLIANCE_CHECKLIST.md`](COMPLIANCE_CHECKLIST.md).

---

## Tecnología

### A-04 · El frontend sigue en Next.js, no migra a Astro
**Qué acordamos.** Next.js 14 con React y TypeScript. **Revisado el 9 sep 2026 a petición
tuya y confirmado.**

**Por qué.** Astro es excelente para páginas que son casi todo texto, porque envía muy poco
código al navegador. CallAIbrate es lo contrario: un panel detrás de un login donde **las
trece pantallas son interactivas** —filtros, gráficas, reproductor de audio sincronizado—.
Ninguna se puede servir como texto estático, así que la ventaja de Astro aquí es cero:
acabarías usándolo como envoltorio de los mismos componentes React que ya existen.

**Dónde sí encajaría Astro.** Una web pública de CallAIbrate (qué es, precios, contacto).
Eso sería un sitio aparte conviviendo con la app, no un reemplazo.

**Coste de cambio.** 🔴 Rehacer enrutado, layouts, protección de sesión y carga de
tipografías, más volver a probar 13 pantallas. Días de trabajo, riesgo de regresiones, y el
usuario no notaría nada.

---

### A-05 · El proveedor de IA lo fija una variable de entorno, nunca la base de datos
**Qué acordamos.** `AI_PROVIDER` y `WHISPER_PROVIDER` deciden qué IA se usa. Por defecto
`groq`. El código está preparado para Claude, OpenAI y Azure sin tocar lógica.

**Por qué.** Groq es gratis y rápido. Pero un proveedor gratuito no da garantías —ya nos
quitó un modelo sin avisar—, así que poder cambiar con una variable es un seguro barato.

**Coste de cambio.** 🟢 Cambiar de proveedor es editar una variable y poner la clave nueva.
Los de pago cuestan dinero por llamada; Groq cuesta $0.

---

### A-06 · El modelo de análisis es `openai/gpt-oss-120b`
**Qué acordamos.** Ese modelo, servido por Groq, para puntuar las llamadas. Whisper large v3
para transcribir.

**Por qué.** El anterior (`llama-3.3-70b-versatile`) dejó de estar disponible para esta
cuenta el 8 sep 2026, aunque la documentación de Groq seguía listándolo.

**Coste de cambio.** 🟢 Cambiar `AI_MODEL_GROQ` en `render.yaml` **y** en el panel de Render.
Si vuelve a fallar con `404 model_not_found`, elegir otro de
<https://console.groq.com/docs/models>.

---

### A-07 · En producción las llamadas se procesan sin worker
**Qué acordamos.** `PROCESS_INLINE=true` en Render: la propia API procesa la llamada en
segundo plano. En local sí se usa Celery + Redis vía Docker.

**Por qué.** El plan gratuito de Render no ofrece workers. Funciona bien con el volumen
actual.

**Coste de cambio.** 🟡 Si el volumen crece, habrá que pagar un worker: la API se bloqueará
procesando y las respuestas se harán lentas.

---

## Infraestructura y coste

### A-08 · Todo vive en planes gratuitos
**Qué acordamos.** Vercel (frontend), Render (API + PostgreSQL), Groq (IA), GitHub (código).
Coste total: **$0 al mes**.

**Por qué.** El proyecto empezó como demostración y no había presupuesto.

**Lo que cuesta de verdad.** Tres consecuencias, ya sufridas:
- La **base de datos caduca a los 30 días** y Render la borra con todo dentro. Ya pasó una vez.
- El **servidor se duerme** tras 15 minutos sin uso: la primera visita tarda ~50 segundos.
- Los **audios subidos se borran** en cada despliegue.

**Coste de cambio.** 🟢 Pasar Render a plan de pago se hace con un clic y resuelve los tres
problemas de golpe. **Es la decisión más importante que tienes pendiente.**

---

### A-09 · Frontend en Vercel, backend en Render
**Qué acordamos.** Separados, no en el mismo sitio.

**Por qué.** Vercel lo hacen los creadores de Next.js: se despliega sin configurar nada. Pero
no sirve para el backend, que necesita un proceso Python encendido de forma continua y una
base de datos gestionada. Render sí hace eso.

**Coste de cambio.** 🔴 Mover cualquiera de los dos implica migrar datos y reconfigurar DNS.

---

### A-10 · La infraestructura se renombró a `callaibrate`
**Qué acordamos.** Servicios `callaibrate-api` y `callaibrate-db`, dominios
`callaibrate.vercel.app` y `callaibrate-api.onrender.com`, repositorio `callaibrate`. El
dominio anterior redirige al nuevo.

**Por qué.** Se pudo hacer sin coste porque la base ya se había perdido: no había datos que
migrar. En otro momento habría implicado downtime.

**Dos excepciones a propósito:**
- El usuario/base `callqa` del `docker-compose.yml` **local** — renombrarlo borra tus datos
  de desarrollo.
- La clave `callqa-auth` del navegador — cambiarla cerraría la sesión de todos los usuarios.

**Coste de cambio.** 🔴 Otro renombrado ahora sí costaría downtime: hay datos.

---

### A-11 · Dos repositorios: uno privado y uno público
**Qué acordamos.** `callaibrate` (privado, todo) y `callqa` (público, solo código limpio,
con historial propio). El público se genera con `ops/publish-clean.ps1`.

**Por qué.** Poder enseñar el código sin exponer documentación interna ni el historial.

**Coste de cambio.** 🟢 Dejar de publicar el limpio es no ejecutar el script.

---

## Seguridad y datos

### A-12 · Ninguna contraseña ni clave vive en el código
**Qué acordamos.** El seed genera contraseñas al azar y las muestra una sola vez. Las claves
de API viven solo en el panel de Render (`sync: false`). El repositorio nunca las contiene.

**Por qué.** Antes estaban escritas en el código y publicadas en el README.

**Coste de cambio.** 🟢 Puedes fijar contraseñas concretas con `SEED_ADMIN_PASSWORD`,
`SEED_JEFE_PASSWORD` y `SEED_ASESOR_PASSWORD` si prefieres controlarlas tú.

---

### A-13 · No se reescribe el historial de git por la clave filtrada
**Qué acordamos.** La clave de Groq que se subió por error en junio sigue en el historial.
**Está revocada** (verificado: responde 401).

**Por qué.** Reescribir el historial cambiaría todos los identificadores de commit y rompería
cualquier copia del repositorio, a cambio de borrar una clave que ya no sirve para nada.

**Coste de cambio.** 🔴 Y sin beneficio. **Lo que nunca hay que hacer es reutilizar esa clave.**

---

### A-14 · Los audios se guardan en disco local, no en S3
**Qué acordamos.** `STORAGE_PROVIDER=local`. El código soporta S3 con solo cambiar la variable.

**Por qué.** Simplicidad y coste cero.

**Lo que cuesta.** Los audios **se pierden en cada despliegue**. Comprobado en vivo. Para uso
real con clientes esto no es aceptable.

**Coste de cambio.** 🟡 Activar S3 es cambiar la variable y dar las credenciales de AWS. Cuesta
unos céntimos al mes. **Recomendado antes de cualquier uso serio.**

---

### A-15 · Sin aprobación de Compliance no entran datos reales
**Qué acordamos.** Nada de grabaciones reales de clientes hasta cerrar
[`COMPLIANCE_CHECKLIST.md`](COMPLIANCE_CHECKLIST.md) con tres firmas: Compliance, DPO y
Seguridad.

**Por qué.** El audio original sale entero hacia Groq (Estados Unidos) y el enmascarado de
datos personales es *best-effort*, no una garantía.

**Coste de cambio.** 🔴 No es una decisión técnica. Es un requisito legal.

---

## Cómo trabajamos

### A-16 · El agente trabaja de forma autónoma
**Qué acordamos.** Ejecuta lo necesario sin pedir confirmación paso a paso: git, docker,
dependencias, migraciones, pruebas, despliegues. Se detiene solo ante algo que únicamente tú
puedes dar.

**Coste de cambio.** 🟢 Basta con que lo digas.

---

### A-17 · El agente no introduce claves ni contraseñas en formularios
**Qué acordamos.** Configurar servicios, diagnosticar, desplegar y verificar: sí. Escribir una
API key o una contraseña en un campo: no. Eso lo haces tú.

**Por qué.** Un secreto que pasa por el agente queda registrado en la conversación. Que lo
pegues tú directamente es sencillamente más seguro.

**Coste de cambio.** 🔴 Este no se negocia.

---

### A-18 · Nada se da por bueno sin verificarlo de verdad
**Qué acordamos.** Nada se reporta como funcionando sin probarlo contra el sistema real:
pruebas automáticas, la pantalla abierta, la llamada procesada de punta a punta.

**Por qué.** Fue así como aparecieron los tres fallos que nadie habría visto: la base de datos
borrada, la sesión que se cerraba al recargar y el modelo de Groq retirado.

**Coste de cambio.** 🟢 Puedes pedir que vaya más rápido y verifique menos. No te lo recomiendo.

---

## Decisiones abiertas

Cosas que aún no hemos decidido y que tarde o temprano habrá que decidir:

| | Decisión pendiente | Por qué importa |
|---|---|---|
| **D-1** | ¿Pasamos Render a plan de pago? | Resuelve de un golpe la caducidad de la base, el arranque lento y —con S3— los audios. |
| **D-2** | ¿Activamos S3 para los audios? | Hoy se borran en cada despliegue. |
| **D-3** | ¿Web pública de CallAIbrate? | Si la hay, ahí sí tiene sentido Astro (ver A-04). |
| **D-4** | ¿Quién usa esto de verdad, y cuándo? | Define si hay que cerrar el checklist de Compliance o sigue siendo una demo. |
