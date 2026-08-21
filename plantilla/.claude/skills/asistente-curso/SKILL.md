---
name: asistente-curso
description: |
  Asistente conversacional acotado a UN curso y a SU plataforma, al estilo de Gabos: sabe
  del contenido de las unidades, de las actividades evaluables y de como moverse por el
  sitio, y de nada mas. Incluye cadena de modelos con relevo automatico ante cuota agotada
  o proveedor caido, herramienta de navegacion que el modelo decide y el cliente ejecuta,
  contexto de ubicacion inyectado en cada turno, y widget flotante.

  Usar cuando: "agrega un asistente al curso", "quiero un chatbot como Gabos", "un
  asistente que conozca la plataforma", "que responda dudas del curso", "un Gabos para
  esta materia", "asistente conversacional del aula virtual", "chatbot que navegue la
  plataforma".

  Pre-requisito: Next.js + Vercel AI SDK v5 + una llave de proveedor de IA, y sesion de
  usuario ya resuelta (skill PLATAFORMA-CURSO-COBACH o ADD-LOGIN).
  NO USAR para: un chat de proposito general (usar la skill AI, template `chat`), ni para
  un agente con intencion comercial o de ventas, ni para RAG sobre documentos (usar AI,
  template `rag`).
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(npm *), Bash(npx tsc *)
metadata:
  author: cobach
  version: "1.0"
---

# Asistente del curso

> Extraído de **Gabos**, el asistente del curso «E-commerce incluyente» del Colegio de
> Bachilleres, el 20 de agosto de 2026. En producción con profesorado real.

---

## Qué lo distingue de un chat genérico

Si lo que hace falta es un chat cualquiera, la skill **`ai`** con el template `chat` lo
resuelve en menos pasos. Esta skill existe por cuatro cosas que ese template no trae:

| Pieza | Por qué |
|---|---|
| **Alcance cerrado** | Sabe del curso y de la plataforma. Nada más. No es una regla de estilo: es la regla dura del prompt |
| **Relevo de modelos** | Prueba cuatro en orden y salta al siguiente **antes del primer token** si hay cuota agotada o caída. La persona no ve el error |
| **Herramienta cliente-servidor** | El modelo decide *qué* navegar; el navegador lo mueve. «Llévame a la actividad 3» te lleva |
| **Contexto de ubicación** | Cada turno le dice dónde está la persona, para que pueda responder «ya estás ahí» |

---

## Alcance: sabe del curso y de nada más

Es la decisión de diseño central. Un asistente de curso que además responde de política,
recetas o tareas de otra materia deja de ser una herramienta del curso y se vuelve un
chatbot más, con el costo de cuota que eso implica.

En el prompt del sistema va como regla dura, no como sugerencia:

- Solo el contenido del curso, sus actividades y esta plataforma.
- Ante algo ajeno: lo dice en una frase y reconduce. **No responde aunque sepa la
  respuesta.**
- Ante algo del curso que no está en su conocimiento: lo admite y sugiere con quién
  confirmarlo. No lo inventa.
- No inventa unidades, actividades ni pestañas que no existan.

**Y aclara que es una IA.** Si el asistente lleva el nombre o el tono de la persona
titular —como Gabos—, tiene que decir con naturalidad que es su asistente y no ella.

---

## Los tres archivos

| Archivo | Va en | Qué es |
|---|---|---|
| `assets/proveedores.ts` | `src/lib/ai/proveedores.ts` | La cadena de modelos y la traducción de errores |
| `assets/route.ts` | `src/app/api/chat/asistente/route.ts` | La ruta. Trae **tres huecos marcados** con «← AJUSTA» |
| `assets/AsistenteWidget.tsx` | `src/features/asistente/` | El widget flotante. Se monta una vez en el layout |

### Los tres huecos que hay que llenar

1. **`CONOCIMIENTO_CURSO`** — unidad por unidad: qué se ve, qué actividades hay, cómo se
   llama exactamente cada pestaña. Es lo que más determina si el asistente sirve.
2. **`SYSTEM_PROMPT`** — nombre, curso, institución y quién es la persona titular.
3. **`navegarEnPlataforma`** — los destinos reales de tu plataforma y los rangos de
   unidades y actividades.

> **Sé literal con los nombres de pestaña.** «Sesión 3 trata de marketing» no permite
> responder «¿dónde está el copy AIDA?». «Está en la Sesión 3, pestaña "2. Copywriting
> persuasivo con IA"» sí. La diferencia entre un asistente útil y uno decorativo está casi
> toda en esta parte.

---

## Relevo de modelos: la pieza que lo mantiene en pie

Con la capa gratuita de Gemini —20 peticiones diarias por modelo— un grupo de treinta
personas agota el primero a media sesión. Sin relevo, a partir de ahí el asistente devuelve
error a todo el mundo.

La clave está en **esperar a `warnings`** antes de dar por bueno el modelo:

```typescript
const resultado = streamText({ ...opciones, model: modelo(), maxRetries: 0 })
try {
  await resultado.warnings   // se resuelve cuando el proveedor ya respondió
  return resultado
} catch (e) {
  // 429 o 503: rechaza ANTES del primer token, se pasa al siguiente sin que se note
}
```

Consumir el texto en lugar de `warnings` anularía el streaming. Y `maxRetries: 0` es
deliberado: reintentar contra un modelo sin cuota solo suma espera.

### Orden medido, no supuesto

El orden no es «el más nuevo primero». En el proyecto de origen, con dos corridas por
modelo contra la tarea real:

| Modelo | Resultado |
|---|---|
| `gemini-3.5-flash` | 2/2 correctas, 7.5–9.6 s. Se queda de principal |
| `gemini-3.6-flash` | 2/2 correctas, 7.6–8.0 s |
| `gemini-3.7-flash` | 1/2: devuelve 503 «high demand» de forma intermitente |
| `gemini-3.1-flash-lite` | Veredictos más laxos; sirve de relevo, no de principal |

Tres hallazgos para no repetir el camino: los `gemini-2.5-*` devuelven 404 porque están
retirados para cuentas nuevas; los alias móviles tipo `gemini-flash-latest` se colgaron con
timeout a 70 s, así que conviene fijar versiones concretas; y los modelos gratuitos de
OpenRouter no soportan tool calling de forma confiable —ante «llévame al Hack 3» devolvían
un valor fuera del enum—, aunque cierran la cadena igual, porque una respuesta imperfecta
es mejor que un asistente caído.

**Mide tú antes de fijar tu orden.** Los nombres y los tiempos cambian.

---

## La herramienta que el cliente ejecuta

La herramienta se declara en el servidor **sin `execute`**. Eso hace que la llamada llegue
al navegador, y es ahí donde ocurre la navegación de verdad.

Por qué así: el servidor no tiene por qué conocer el enrutamiento del cliente ni saber qué
unidades están habilitadas para esa persona. El reparto queda limpio — **el modelo decide
qué, el cliente decide si se puede y lo hace.**

Dos detalles que se pasan por alto:

- Cuando la unidad está bloqueada, el cliente **responde a la herramienta con el motivo,
  no con un error**. Así el asistente lo explica con naturalidad en vez de romperse.
- `sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithToolCalls` reanuda la
  conversación al devolver el resultado, para que confirme en una frase lo que pasó. Sin
  eso, la navegación ocurre en silencio.

---

## Seguridad y costo

**La ruta exige sesión.** No es opcional. En el proyecto de origen quedó abierta un tiempo
y cualquiera que conociera la dirección podía conversar con ella y agotar la cuota diaria,
dejando sin asistente a quienes sí tomaban el curso.

**Los errores se traducen.** Sin `onError` y sin `describirErrorIA`, el SDK enmascara todo
como «An error occurred», que no dice si hay que esperar unos minutos, recargar crédito o
cambiar la llave.

**Calcula la cuota antes de abrirlo.** Personas × preguntas por sesión contra el límite
diario por modelo. Si no cuadra, o se activa facturación o se acota el asistente a la
franja de la sesión.

---

## Nada de markdown

El prompt lo prohíbe de forma explícita y el widget pinta texto plano. Si el modelo
devuelve `**negritas**`, se ven los asteriscos crudos. Si prefieres renderizar markdown,
quita la regla del prompt **y** agrega el renderizador; cambiar solo una de las dos cosas
deja la interfaz peor de como estaba.

---

## Checklist

- [ ] `CONOCIMIENTO_CURSO` nombra las pestañas con su texto exacto.
- [ ] El prompt dice que es una IA, no la persona titular.
- [ ] La regla de alcance está y se probó: preguntarle algo ajeno y ver que reconduce.
- [ ] La ruta devuelve 401 sin sesión iniciada.
- [ ] El relevo se probó de verdad: poner una llave inválida en el primer modelo y
      comprobar que el segundo responde sin que se vea el error.
- [ ] «Llévame a la actividad N» navega, y con una unidad bloqueada lo explica en vez de
      fallar.
- [ ] El widget se monta una sola vez, en el layout.
- [ ] La cuota diaria alcanza para el tamaño del grupo.
