/**
 * Ruta del asistente del curso.  →  src/app/api/chat/asistente/route.ts
 *
 * Tres cosas la distinguen de un chat genérico, y las tres importan:
 *   1. Exige sesión. No es un chat para internet.
 *   2. Relevo de modelos ANTES del primer token, para que una cuota agotada no se vea.
 *   3. Una herramienta que el modelo decide y el CLIENTE ejecuta (navegación).
 *
 * Rellena los tres huecos marcados con  ← AJUSTA.
 */
import { NextResponse } from 'next/server'
import { convertToModelMessages, streamText, tool, type UIMessage } from 'ai'
import { z } from 'zod'
import { CADENA_MODELOS_CHAT, describirErrorIA } from '@/lib/ai/proveedores'
import { perfilActivo } from '@/lib/supabase/sesion-servidor'

export const maxDuration = 60

// ============================================================ ← AJUSTA (1 de 3)
// El conocimiento del curso. Es lo único que el asistente sabe.
//
// Escribe aquí, unidad por unidad: qué se ve, qué actividades hay, en qué pestaña
// está cada tema y cómo se llama exactamente. Cuanto más literales sean los nombres
// de pestañas y secciones, mejor ubica a la gente.
//
// No lo dejes en generalidades: "Sesión 3 trata de marketing" no sirve para
// responder "¿dónde está el copy AIDA?".
const CONOCIMIENTO_CURSO = `
UNIDAD 1 — [título exacto como aparece en la plataforma]:
[Qué se trabaja. Qué pestañas tiene. Qué actividades evaluables incluye y con qué número.]

UNIDAD 2 — [...]:
[...]

Cada actividad tiene: prompts de IA sugeridos para copiar, campos para llenar la
evidencia, una lista de cotejo, y un botón para guardar la evidencia.
`

// ============================================================ ← AJUSTA (2 de 3)
const SYSTEM_PROMPT = `Eres [NOMBRE], el asistente de inteligencia artificial del curso "[TÍTULO DEL CURSO]" de [INSTITUCIÓN].

Eres un asistente de IA, no una persona real: si alguien pregunta si eres [la persona titular], aclara con naturalidad que eres su asistente, entrenado con el contenido del curso.

Tu función es ayudar a quienes toman el curso a:
1. Resolver dudas sobre el contenido de las unidades.
2. Indicar exactamente en qué unidad y en qué pestaña se encuentra un tema o una actividad.
3. Explicar los conceptos del curso con ejemplos claros.
4. Orientar sobre cómo navegar la plataforma: dónde están las unidades, los foros, el panel de accesibilidad, cómo subir evidencia.
5. Navegar la plataforma por la persona cuando lo pida explícitamente, con la herramienta navegarEnPlataforma en vez de solo explicar dónde está.

ALCANCE — esto es una regla dura:
- Solo sabes del contenido de este curso, de sus actividades y de esta plataforma. Nada más.
- Si te preguntan algo ajeno al curso —noticias, tareas de otras materias, temas generales, escribir código que no es del curso—, dilo con amabilidad y en una frase, y reconduce: "Eso queda fuera de lo que manejo; yo te puedo ayudar con el contenido del curso y con moverte por la plataforma". No respondas la pregunta ajena aunque sepas la respuesta.
- Si te preguntan algo del curso que no está en tu conocimiento, dilo con honestidad y sugiere confirmarlo con [la persona titular]. No lo inventes.
- No inventes unidades, actividades ni pestañas que no existan.

Reglas sobre la herramienta navegarEnPlataforma:
- Úsala SOLO cuando pidan explícitamente ir, abrir, mostrar o que los lleves. Si solo preguntan dónde está algo, respóndelo en texto.
- Si piden una actividad concreta, usa actividadNumero: la plataforma resuelve sola la unidad y la pestaña.
- Si piden una unidad sin actividad, usa destino "inicio" con unidadId.
- Después de que la herramienta responda, confirma en una frase lo que pasó. Si dice que la unidad está bloqueada, explícalo con naturalidad y sugiere seguir con la actual mientras quien coordina la habilita.

Reglas de estilo:
- Español de México, en sentence case, con lenguaje claro e incluyente y no sexista: colectivos neutros como "el equipo", "el estudiantado", "la persona docente".
- Breve y directo: 2 a 4 oraciones, salvo que pidan explicar un tema a fondo.
- Al indicar dónde está algo, nombra la unidad y la pestaña exactas.
- Escribe SIEMPRE en texto plano. Nunca uses markdown: ni negritas, ni guiones de lista, ni numeración, ni encabezados. Si necesitas enumerar, hazlo dentro de la misma oración con comas o con "luego". El widget no renderiza markdown y se vería el asterisco crudo.

Conocimiento del curso:
${CONOCIMIENTO_CURSO}`

// ============================================================ ← AJUSTA (3 de 3)
// Herramienta SIN "execute" a propósito.
//
// El modelo decide QUÉ navegar; el widget del cliente es quien mueve la aplicación
// y quien valida si la unidad pedida está bloqueada. Si le pusieras "execute" aquí,
// el servidor tendría que conocer el enrutamiento del cliente, que no le corresponde.
const navegarEnPlataforma = tool({
  description:
    'Navega a una sección, unidad o actividad de la plataforma cuando la persona lo pide explícitamente (ej. "ve a la actividad 3", "ábreme la unidad 2", "llévame a foros").',
  inputSchema: z.object({
    destino: z
      .enum(['inicio', 'unidades', 'foro'])
      .describe('"inicio" para entrar al contenido de una unidad o actividad; "unidades" para la vista de todas; "foro" para los foros.'),
    unidadId: z.number().int().min(1).max(20).optional()
      .describe('Número de unidad, si se pidió una unidad concreta sin actividad.'),
    actividadNumero: z.number().int().min(1).max(50).optional()
      .describe('Número de actividad, si se pidió una actividad concreta.'),
  }),
})

/**
 * Arranca el streaming con el primer modelo de la cadena que acepte la petición.
 *
 * La clave está en esperar a `warnings`: esa promesa se resuelve cuando el proveedor ya
 * respondió al primer intercambio. Si el modelo está sin cuota (429) o caído (503),
 * rechaza ANTES de que se emita un solo token, y se puede pasar al siguiente sin que la
 * persona vea nada raro. Consumir el texto en su lugar anularía el streaming.
 */
interface OpcionesChat {
  system: string
  messages: Awaited<ReturnType<typeof convertToModelMessages>>
  temperature: number
  tools: Record<string, unknown>
}

async function iniciarStreamConRespaldo(opciones: OpcionesChat) {
  let ultimoError: unknown
  for (const { nombre, modelo } of CADENA_MODELOS_CHAT) {
    const resultado = streamText({ ...opciones, model: modelo(), maxRetries: 0 } as never)
    try {
      await resultado.warnings
      return resultado
    } catch (e) {
      ultimoError = e
      console.error(`Asistente: el modelo ${nombre} no aceptó la petición:`, e)
    }
  }
  throw ultimoError ?? new Error('Ningún modelo aceptó la conversación.')
}

export async function POST(req: Request) {
  // El asistente es para quien está inscrito, no para internet. Dejar esta ruta abierta
  // permite que cualquiera que conozca la dirección converse con ella y agote la cuota
  // diaria, dejando sin asistente a quienes sí toman el curso. Pasó en el proyecto de
  // origen.
  const perfil = await perfilActivo()
  if (!perfil) {
    return NextResponse.json(
      { error: 'Inicia sesión con tu cuenta del curso para conversar con el asistente.' },
      { status: 401 }
    )
  }

  const { messages, contexto }: { messages: UIMessage[]; contexto?: string } = await req.json()
  const modelMessages = await convertToModelMessages(messages)

  let result: Awaited<ReturnType<typeof iniciarStreamConRespaldo>>
  try {
    result = await iniciarStreamConRespaldo({
      // El contexto dice en qué parte de la plataforma está la persona ahora mismo.
      // Sin él, el asistente responde en abstracto y no puede decir "ya estás ahí".
      system: contexto ? `${SYSTEM_PROMPT}\n\nContexto actual: ${contexto}` : SYSTEM_PROMPT,
      messages: modelMessages,
      temperature: 0.4,
      tools: { navegarEnPlataforma },
    })
  } catch (e) {
    // Ningún proveedor aceptó. Se responde con un stream que lleva el motivo real, para
    // que la persona lea algo accionable en vez de un mensaje genérico.
    return new Response(
      `data: ${JSON.stringify({ type: 'start' })}\n\n` +
        `data: ${JSON.stringify({ type: 'error', errorText: describirErrorIA(e) })}\n\n` +
        'data: [DONE]\n\n',
      { status: 200, headers: { 'Content-Type': 'text/event-stream' } }
    )
  }

  // Sin onError, el SDK enmascara cualquier fallo del stream como "An error occurred",
  // que no le dice nada a la persona ni deja rastro en los registros del servidor.
  return result.toUIMessageStreamResponse({
    onError: (error) => {
      console.error('Error en el chat del asistente:', error)
      return describirErrorIA(error)
    },
  })
}
