# Línea del tiempo

> Qué ha pasado en este proyecto, en orden, en lenguaje normal.
>
> Es un resumen para entender la historia de un vistazo. El detalle técnico de cada
> cambio está en [`CHANGELOG.md`](CHANGELOG.md); el detalle exacto, en el historial de git.

---

## Junio 2026 · Construcción

| Cuándo | Qué pasó |
|---|---|
| **1 jun** | **Nace el proyecto.** En un solo día se levanta todo: backend, frontend, base de datos y las primeras pruebas. Ese mismo día se decide que la IA sea Groq (gratis) y se despliega por primera vez en internet. |
| **3 jun** | Se ordena la documentación en la carpeta `docs/`. |
| **13 jun** | **Campañas.** Cada campaña pasa a tener una "nota de producto" (qué se vende, a qué precio, qué frases son obligatorias) y la IA evalúa si el ejecutivo la respetó. |
| **16 jun** | ⚠️ **Se sube por error una clave de Groq real al repositorio.** Se detecta y se revoca una semana después. |
| **22 jun** | **Roles.** Aparecen tres perfiles: administrador, jefe y asesor. Cada uno ve solo lo que le corresponde. |
| **23 jun** | **Fase 2: analítica.** Alertas, KPIs por campaña, percentil del asesor, métricas de cómo se habla en la llamada. Y un rediseño completo de los indicadores. |

## Julio 2026 · Orden

| Cuándo | Qué pasó |
|---|---|
| **10-11 jul** | Se monta el sistema de dos repositorios: uno privado con todo, otro público solo con el código limpio. |
| **11 jul** | Auditoría de coherencia: se borra código muerto y se corrige documentación desactualizada. **Último cambio antes de dos meses de silencio.** |

## Agosto 2026 · La caída silenciosa

| Cuándo | Qué pasó |
|---|---|
| *(sin fecha exacta)* | ⚠️ **La base de datos de producción caduca y Render la elimina.** El plan gratuito las borra a los 30 días. El backend queda muerto: arranca, no encuentra la base y se apaga. **Nadie se entera durante dos meses**, porque el vigilante que hacía ping estaba mal configurado y se tragaba el error. Los datos de producción se pierden. No había copia de seguridad. |

## Septiembre 2026 · Rebrand y reconstrucción

| Cuándo | Qué pasó |
|---|---|
| **7 sep** | **El proyecto pasa de "CallQA AI" a "CallAIbrate".** Identidad nueva completa: paleta, tipografías, wordmark. Se retira la marca Minsait. |
| **7 sep** | **Reproductor de audio sincronizado**: se escucha la llamada mientras se resalta la frase que suena; al hacer clic en un segmento, el audio salta ahí. |
| **7 sep** | **Exportación a CSV** del reporte del equipo. |
| **7 sep** | **Seguridad:** las contraseñas de demostración dejan de estar escritas en el código; ahora se generan al azar. Se añade un seguro que impide arrancar en producción con la clave de firma de ejemplo. |
| **8 sep** | **Se descubre la caída.** Se reconstruye la infraestructura desde cero, aprovechando para renombrarla toda a `callaibrate`. Se pierde lo que había; no había nada que recuperar. |
| **8 sep** | **Se arregla un bug que expulsaba al usuario:** recargar cualquier página te devolvía al login. |
| **8 sep** | **Vigilancia real y copias de seguridad:** el ping ahora falla y avisa; se añade un volcado diario de la base de datos. |
| **8 sep** | ⚠️ **Groq retira el acceso al modelo de análisis.** Se cambia a `openai/gpt-oss-120b` y se verifica de punta a punta con una llamada real. |
| **9 sep** | Documentación de arquitectura, esta línea del tiempo y el registro de acuerdos. |

---

## Las tres lecciones que costaron caro

1. **Un servicio "gratis" puede borrarte los datos.** El plan gratuito de Render caduca las
   bases PostgreSQL a los 30 días. Volverá a pasar si nada cambia.
2. **Un vigilante que nunca falla no vigila nada.** El ping terminaba en `|| true`: siempre
   daba verde. Por eso dos meses de caída pasaron desapercibidos.
3. **Un proveedor de IA puede quitarte un modelo sin avisar**, aunque su documentación siga
   listándolo. Conviene poder cambiar de proveedor con una variable — y eso ya está resuelto.

---

## Cómo leer esto en el futuro

- **Esta línea del tiempo** cuenta *qué pasó*, para humanos.
- **[`CHANGELOG.md`](CHANGELOG.md)** cuenta *qué se cambió*, con detalle técnico.
- **[`ACUERDOS.md`](ACUERDOS.md)** cuenta *qué decidimos y por qué*, y qué se puede revisar.
- **[`ESTADO_DEL_PROYECTO.md`](ESTADO_DEL_PROYECTO.md)** cuenta *dónde estamos ahora*.
