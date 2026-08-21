/**
 * Widget flotante del asistente del curso.  →  src/features/asistente/AsistenteWidget.tsx
 *
 * Esqueleto con las cuatro piezas que no son obvias. La presentación —colores, tamaños,
 * animaciones— se adapta a cada proyecto; lo que NO conviene cambiar es la mecánica de la
 * herramienta y el envío del contexto.
 *
 * Se monta una sola vez, en el layout, junto al menú de accesibilidad.
 */
'use client'

import { useState, useRef, useEffect } from 'react'
import { useChat } from '@ai-sdk/react'
import {
  DefaultChatTransport,
  lastAssistantMessageIsCompleteWithToolCalls,
} from 'ai'
import { useAppStore } from '@/shared/store/useAppStore'

// Sugerencias de arranque. Sirven para dos cosas: enseñar de qué SÍ sabe el asistente,
// y evitar la pantalla en blanco, que es donde la gente lo cierra sin usarlo.
const SUGERENCIAS = [
  '¿Qué se ve en la unidad 2?',
  '¿Dónde subo la evidencia de la actividad 3?',
  'Llévame a los foros',
]

export function AsistenteWidget() {
  const [abierto, setAbierto] = useState(false)
  const [texto, setTexto] = useState('')
  const finRef = useRef<HTMLDivElement>(null)

  // ---------------------------------------------------------------- contexto
  // Dónde está la persona ahora mismo. Se manda en cada turno para que el asistente
  // pueda decir "ya estás ahí" en vez de navegar a donde ya está.
  const unidadActiva = useAppStore((s) => s.unidadActiva)
  const setUnidadActiva = useAppStore((s) => s.setUnidadActiva)
  const setVista = useAppStore((s) => s.setVista)
  const unidadesHabilitadas = useAppStore((s) => s.unidadesHabilitadas)

  const contexto = `La persona está en la unidad ${unidadActiva}.`

  // ------------------------------------------------------------ herramienta
  // El servidor declara navegarEnPlataforma SIN "execute", así que la llamada llega
  // aquí. Este cliente es quien de verdad mueve la aplicación, y quien sabe si la
  // unidad pedida está bloqueada — cosa que el servidor no tiene por qué saber.
  //
  // `sendAutomaticallyWhen` reanuda la conversación en cuanto se devuelve el resultado
  // de la herramienta, para que el asistente confirme en una frase lo que pasó.
  const { messages, sendMessage, status, error, addToolOutput } = useChat({
    transport: new DefaultChatTransport({ api: '/api/chat/asistente' }),
    sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithToolCalls,
    onToolCall: async ({ toolCall }) => {
      if (toolCall.toolName !== 'navegarEnPlataforma') return

      const input = toolCall.input as {
        destino: 'inicio' | 'unidades' | 'foro'
        unidadId?: number
        actividadNumero?: number
      }

      let mensaje = ''

      if (input.destino === 'foro') {
        setVista('foro')
        mensaje = 'Listo, abrí los foros.'
      } else if (input.destino === 'unidades') {
        setVista('unidades')
        mensaje = 'Listo, abrí la vista de unidades.'
      } else {
        // Resolver la unidad: si pidieron una actividad, se traduce a su unidad.
        const destinoUnidad =
          input.unidadId ?? unidadDeActividad(input.actividadNumero) ?? unidadActiva

        if (!unidadesHabilitadas.includes(destinoUnidad)) {
          // Se responde a la herramienta con el motivo, NO con un error: así el
          // asistente lo explica con naturalidad en vez de romperse.
          mensaje = `La unidad ${destinoUnidad} todavía está bloqueada; quien coordina aún no la habilita.`
        } else {
          setUnidadActiva(destinoUnidad)
          setVista('inicio')
          mensaje = input.actividadNumero
            ? `Listo, te llevé a la actividad ${input.actividadNumero}, en la unidad ${destinoUnidad}.`
            : `Listo, abrí la unidad ${destinoUnidad}.`
        }
      }

      addToolOutput({
        tool: 'navegarEnPlataforma',
        toolCallId: toolCall.toolCallId,
        output: { mensaje },
      })
    },
  })

  useEffect(() => {
    finRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const enviar = (valor: string) => {
    if (!valor.trim()) return
    sendMessage({ text: valor }, { body: { contexto } })
    setTexto('')
  }

  // ------------------------------------------------------------------- vista
  if (!abierto) {
    return (
      <button
        onClick={() => setAbierto(true)}
        aria-label="Abrir el asistente del curso"
        className="fixed bottom-5 right-5 z-40 w-14 h-14 rounded-full bg-[#0E6B37] text-white shadow-lg"
      >
        {/* Icono. aria-hidden porque el nombre accesible ya está en aria-label. */}
        <span aria-hidden="true">💬</span>
      </button>
    )
  }

  return (
    <section
      aria-label="Asistente del curso"
      className="fixed bottom-5 right-5 z-40 flex w-[min(24rem,calc(100vw-2.5rem))] flex-col
                 rounded-2xl border border-slate-200 bg-white shadow-2xl"
    >
      <header className="flex items-center justify-between border-b px-4 py-3">
        <p className="font-bold text-[#0A5129]">Asistente del curso</p>
        <button onClick={() => setAbierto(false)} aria-label="Cerrar el asistente"
                className="min-h-11 min-w-11">✕</button>
      </header>

      <div className="max-h-96 overflow-y-auto px-4 py-3 space-y-3">
        {messages.length === 0 && (
          <div className="space-y-2">
            <p className="text-sm text-slate-600">
              Te ayudo con el contenido del curso y a moverte por la plataforma.
            </p>
            {SUGERENCIAS.map((s) => (
              <button key={s} onClick={() => enviar(s)}
                      className="block w-full rounded-lg border px-3 py-2 text-left text-sm min-h-11">
                {s}
              </button>
            ))}
          </div>
        )}

        {messages.map((m) => (
          <p key={m.id} className={m.role === 'user' ? 'text-right' : ''}>
            {/* El prompt del sistema prohíbe markdown, así que se pinta texto plano. */}
            {m.parts.filter((p) => p.type === 'text').map((p, i) => (
              <span key={i} className="inline-block rounded-xl px-3 py-2 text-sm
                                       whitespace-pre-wrap bg-slate-100">{p.text}</span>
            ))}
          </p>
        ))}

        {/* El motivo real del fallo, no un "ocurrió un error". */}
        {error && <p role="alert" className="text-sm text-red-700">{error.message}</p>}
        <div ref={finRef} />
      </div>

      <form onSubmit={(e) => { e.preventDefault(); enviar(texto) }}
            className="flex gap-2 border-t p-3">
        <label htmlFor="asistente-entrada" className="sr-only">Escribe tu pregunta</label>
        <input id="asistente-entrada" value={texto} onChange={(e) => setTexto(e.target.value)}
               placeholder="Escribe tu pregunta"
               className="min-h-11 flex-1 rounded-lg border-2 border-slate-500 px-3" />
        <button type="submit" disabled={status !== 'ready'}
                className="min-h-11 rounded-lg bg-[#0E6B37] px-4 font-bold text-white">
          Enviar
        </button>
      </form>
    </section>
  )
}

/** Traduce el número de actividad a la unidad que la contiene. Ajusta el reparto. */
function unidadDeActividad(n?: number): number | null {
  if (!n) return null
  const reparto: Record<number, number[]> = {
    1: [1, 2],
    2: [3, 4],
    3: [5, 6],
  }
  for (const [unidad, actividades] of Object.entries(reparto)) {
    if (actividades.includes(n)) return Number(unidad)
  }
  return null
}
