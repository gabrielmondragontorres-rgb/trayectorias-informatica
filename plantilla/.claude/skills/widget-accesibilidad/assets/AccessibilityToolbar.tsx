'use client'

import { useState, useEffect, useRef } from 'react'
import { useAppStore } from '@/shared/store/useAppStore'

/**
 * Preferencias de accesibilidad que sobreviven a la recarga.
 *
 * Quien necesita el alto contraste o la letra grande lo necesita SIEMPRE, no una vez.
 * Obligarle a reconfigurar el panel en cada visita anula buena parte de su utilidad.
 *
 * El lector de voz queda fuera a propósito: es una acción, no una preferencia, y una
 * página que empieza a hablar sola al cargar asusta en vez de ayudar.
 */
export const CLAVE_AJUSTES = 'cobach_accessibility_settings'

export interface AjustesAccesibilidad {
  isGrayscale: boolean
  isLargeCursor: boolean
  isHighContrast: boolean
  isReadingMask: boolean
  isReadingGuide: boolean
  isDyslexiaFont: boolean
  isHighlightLinks: boolean
  lineSpacingLevel: number
  letterSpacingLevel: number
  fontSizeStep: number
}

const AJUSTES_INICIALES: AjustesAccesibilidad = {
  isGrayscale: false,
  isLargeCursor: false,
  isHighContrast: false,
  isReadingMask: false,
  isReadingGuide: false,
  isDyslexiaFont: false,
  isHighlightLinks: false,
  lineSpacingLevel: 0,
  letterSpacingLevel: 0,
  fontSizeStep: 0,
}

/**
 * Sanea lo que venga de localStorage. Nunca se confía en su contenido: puede traer
 * datos de una versión anterior del panel, o haber sido editado a mano desde la consola.
 * Un nivel fuera de rango dejaría `lineHeights[undefined]` y rompería el estilo.
 */
function leerAjustes(): AjustesAccesibilidad {
  if (typeof window === 'undefined') return AJUSTES_INICIALES
  try {
    const crudo = window.localStorage.getItem(CLAVE_AJUSTES)
    if (!crudo) return AJUSTES_INICIALES
    const datos = JSON.parse(crudo) as Partial<AjustesAccesibilidad>
    const acotar = (valor: unknown, min: number, max: number) =>
      typeof valor === 'number' && Number.isFinite(valor)
        ? Math.min(max, Math.max(min, Math.round(valor)))
        : 0
    const booleano = (valor: unknown, previo: boolean) =>
      typeof valor === 'boolean' ? valor : previo

    return {
      isGrayscale: booleano(datos.isGrayscale, false),
      isLargeCursor: booleano(datos.isLargeCursor, false),
      isHighContrast: booleano(datos.isHighContrast, false),
      isReadingMask: booleano(datos.isReadingMask, false),
      isReadingGuide: booleano(datos.isReadingGuide, false),
      isDyslexiaFont: booleano(datos.isDyslexiaFont, false),
      isHighlightLinks: booleano(datos.isHighlightLinks, false),
      lineSpacingLevel: acotar(datos.lineSpacingLevel, 0, 2),
      letterSpacingLevel: acotar(datos.letterSpacingLevel, 0, 2),
      fontSizeStep: acotar(datos.fontSizeStep, -2, 2),
    }
  } catch {
    // JSON corrupto: se ignora y se arranca con los valores por omisión.
    return AJUSTES_INICIALES
  }
}

export function AccessibilityToolbar() {
  const isOpen = useAppStore((state) => state.isAccessibilityPanelOpen)
  const setIsOpen = useAppStore((state) => state.setAccessibilityPanelOpen)

  // Estados de accesibilidad institucional COBACH
  const [isGrayscale, setIsGrayscale] = useState(false)
  const [isReading, setIsReading] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [isLargeCursor, setIsLargeCursor] = useState(false)
  const [isHighContrast, setIsHighContrast] = useState(false)
  const [isReadingMask, setIsReadingMask] = useState(false)
  const [isReadingGuide, setIsReadingGuide] = useState(false)
  const [isDyslexiaFont, setIsDyslexiaFont] = useState(false)
  const [lineSpacingLevel, setLineSpacingLevel] = useState(0) // 0, 1, 2
  const [letterSpacingLevel, setLetterSpacingLevel] = useState(0) // 0, 1, 2
  const [fontSizeStep, setFontSizeStep] = useState(0) // -2, -1, 0, 1, 2
  const [isHighlightLinks, setIsHighlightLinks] = useState(false)

  // Los ajustes guardados no se pueden leer durante el primer render: el servidor no tiene
  // localStorage y React marcaría desajuste de hidratación. Se leen al montar, y hasta que
  // eso ocurre no se guarda nada, o el estado inicial pisaría la preferencia guardada.
  const [ajustesCargados, setAjustesCargados] = useState(false)

  // Referencias para resaltado directo palabra por palabra sobre el DOM de la página
  const activeElementRef = useRef<{
    el: HTMLElement
    originalHTML: string
  } | null>(null)

  const wordTimerRef = useRef<NodeJS.Timeout | null>(null)
  const isReadingRef = useRef(false)

  // Posición del mouse para Máscara y Guía de Lectura
  const [mouseY, setMouseY] = useState(0)

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMouseY(e.clientY)
    }
    if (isReadingMask || isReadingGuide) {
      window.addEventListener('mousemove', handleMouseMove)
    } else {
      window.removeEventListener('mousemove', handleMouseMove)
    }
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [isReadingMask, isReadingGuide])

  // Limpiar e imborrar el HTML original del elemento leído
  const clearHighlight = () => {
    if (wordTimerRef.current) {
      clearInterval(wordTimerRef.current)
      wordTimerRef.current = null
    }
    if (activeElementRef.current) {
      const { el, originalHTML } = activeElementRef.current
      el.innerHTML = originalHTML
      activeElementRef.current = null
    }
  }

  // Cargar/Aplicar cambios en DOM y LocalStorage
  const handleReset = () => {
    setIsGrayscale(false)
    stopVoiceReader()
    setIsLargeCursor(false)
    setIsHighContrast(false)
    setIsReadingMask(false)
    setIsReadingGuide(false)
    setIsDyslexiaFont(false)
    setLineSpacingLevel(0)
    setLetterSpacingLevel(0)
    setFontSizeStep(0)
    setIsHighlightLinks(false)

    if (typeof window !== 'undefined') {
      window.speechSynthesis?.cancel()
      const root = document.documentElement
      root.classList.remove('grayscale-filter', 'large-cursor', 'high-contrast', 'dyslexia-font', 'highlight-links')
      root.style.fontSize = '16px'
      root.style.lineHeight = 'normal'
      root.style.letterSpacing = 'normal'

      localStorage.removeItem('cobach_accessibility_settings')
    }
  }

  // Cerrar con Escape y devolver el foco a donde estaba.
  //
  // Se comprobó el 20 de agosto de 2026 que faltaban las dos cosas: Escape no hacía
  // nada, y al cerrar el panel el foco se iba al <body>, así que quien navega con
  // teclado tenía que recorrer la página entera otra vez para volver a donde estaba.
  const disparadorRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (isOpen) {
      // Se recuerda quién abrió el panel para devolverle el foco al cerrar.
      disparadorRef.current = document.activeElement as HTMLElement | null
      const alPresionar = (e: KeyboardEvent) => {
        if (e.key === 'Escape') setIsOpen(false)
      }
      window.addEventListener('keydown', alPresionar)
      return () => window.removeEventListener('keydown', alPresionar)
    }
    // Al cerrarse, el foco vuelve al botón que lo abrió, si sigue en la página.
    const previo = disparadorRef.current
    if (previo && document.contains(previo)) {
      previo.focus()
      disparadorRef.current = null
    }
  }, [isOpen, setIsOpen])

  // Restaurar la preferencia guardada, una sola vez al montar.
  useEffect(() => {
    const guardado = leerAjustes()
    setIsGrayscale(guardado.isGrayscale)
    setIsLargeCursor(guardado.isLargeCursor)
    setIsHighContrast(guardado.isHighContrast)
    setIsReadingMask(guardado.isReadingMask)
    setIsReadingGuide(guardado.isReadingGuide)
    setIsDyslexiaFont(guardado.isDyslexiaFont)
    setIsHighlightLinks(guardado.isHighlightLinks)
    setLineSpacingLevel(guardado.lineSpacingLevel)
    setLetterSpacingLevel(guardado.letterSpacingLevel)
    setFontSizeStep(guardado.fontSizeStep)
    setAjustesCargados(true)
  }, [])

  // Guardar cada cambio. No se escribe antes de haber leído, para no pisar lo guardado
  // con los valores por omisión del primer render.
  useEffect(() => {
    if (!ajustesCargados || typeof window === 'undefined') return
    const ajustes: AjustesAccesibilidad = {
      isGrayscale,
      isLargeCursor,
      isHighContrast,
      isReadingMask,
      isReadingGuide,
      isDyslexiaFont,
      isHighlightLinks,
      lineSpacingLevel,
      letterSpacingLevel,
      fontSizeStep,
    }
    try {
      // Si todo está en su valor por omisión, se borra la clave en vez de guardarla:
      // no se ocupa almacenamiento de quien nunca abrió el panel, y así «Restablecer»
      // deja el navegador como estaba antes de la primera visita.
      const sinCambios = (Object.keys(AJUSTES_INICIALES) as (keyof AjustesAccesibilidad)[])
        .every((k) => ajustes[k] === AJUSTES_INICIALES[k])
      if (sinCambios) {
        window.localStorage.removeItem(CLAVE_AJUSTES)
        return
      }
      window.localStorage.setItem(CLAVE_AJUSTES, JSON.stringify(ajustes))
    } catch {
      // Modo privado o almacenamiento lleno: el panel sigue funcionando en esta visita,
      // simplemente no recuerda. Preferible a romper la página.
    }
  }, [
    ajustesCargados,
    isGrayscale,
    isLargeCursor,
    isHighContrast,
    isReadingMask,
    isReadingGuide,
    isDyslexiaFont,
    isHighlightLinks,
    lineSpacingLevel,
    letterSpacingLevel,
    fontSizeStep,
  ])

  // Efectos en el DOM
  useEffect(() => {
    if (typeof window === 'undefined') return
    const root = document.documentElement

    root.classList.toggle('grayscale-filter', isGrayscale)
    root.classList.toggle('large-cursor', isLargeCursor)
    root.classList.toggle('high-contrast', isHighContrast)
    root.classList.toggle('dyslexia-font', isDyslexiaFont)
    root.classList.toggle('highlight-links', isHighlightLinks)

    const baseSize = 16 + fontSizeStep * 2
    root.style.fontSize = `${baseSize}px`

    const lineHeights = ['normal', '1.8', '2.2']
    root.style.lineHeight = lineHeights[lineSpacingLevel]

    const letterSpacings = ['normal', '0.08em', '0.16em']
    root.style.letterSpacing = letterSpacings[letterSpacingLevel]
  }, [isGrayscale, isLargeCursor, isHighContrast, isDyslexiaFont, isHighlightLinks, fontSizeStep, lineSpacingLevel, letterSpacingLevel])

  // Lector de voz directamente sobre el texto de la página PALABRA POR PALABRA en Amarillo (#FACC15)
  const startVoiceReader = () => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return

    window.speechSynthesis.cancel()
    clearHighlight()

    const mainContainer = document.getElementById('main-content') || document.body
    // Seleccionar títulos, párrafos y listas dentro del contenido de la página
    const nodes = Array.from(mainContainer.querySelectorAll<HTMLElement>('h1, h2, h3, h4, p, li, blockquote'))
      .filter(el => {
        const text = el.innerText?.trim()
        return text && text.length > 5 && el.offsetParent !== null && !el.closest('aside') && !el.closest('nav')
      })

    if (nodes.length === 0) return

    isReadingRef.current = true
    setIsReading(true)
    setIsPaused(false)

    let nodeIndex = 0

    const readNextNode = () => {
      if (!isReadingRef.current || nodeIndex >= nodes.length) {
        stopVoiceReader()
        return
      }

      clearHighlight()
      const currentEl = nodes[nodeIndex]
      const rawText = currentEl.innerText.trim()

      if (!rawText) {
        nodeIndex++
        readNextNode()
        return
      }

      // Guardar el HTML original exacto del elemento para restauración limpia
      activeElementRef.current = {
        el: currentEl,
        originalHTML: currentEl.innerHTML
      }

      // Descomponer el texto en palabras individuales envueltas en spans identificados
      const tokens = rawText.split(/(\s+)/)
      let wordCounter = 0
      const wrappedHTML = tokens.map(token => {
        if (token.trim().length === 0) return token // Preservar espacios en blanco
        const spanId = `w_span_${wordCounter++}`
        return `<span id="${spanId}" style="transition: background-color 0.15s ease, color 0.15s ease; border-radius: 4px; padding: 1px 3px;">${token}</span>`
      }).join('')

      currentEl.innerHTML = wrappedHTML
      const totalWords = wordCounter

      // Scroll suave al centro de la pantalla
      currentEl.scrollIntoView({ behavior: 'smooth', block: 'center' })

      const utterance = new SpeechSynthesisUtterance(rawText)
      utterance.lang = 'es-MX'
      utterance.rate = 0.75 // Velocidad pausada, clara y accesible

      let currentActiveSpanIndex = -1

      const highlightWordIndex = (idx: number) => {
        if (idx < 0 || idx >= totalWords) return

        // Desactivar amarillo de la palabra anterior
        if (currentActiveSpanIndex !== -1 && currentActiveSpanIndex !== idx) {
          const prevSpan = currentEl.querySelector<HTMLElement>(`#w_span_${currentActiveSpanIndex}`)
          if (prevSpan) {
            prevSpan.style.backgroundColor = 'transparent'
            prevSpan.style.color = 'inherit'
            prevSpan.style.fontWeight = 'inherit'
            prevSpan.style.boxShadow = 'none'
          }
        }

        // Resaltar en Amarillo Canario (#FACC15) la palabra actual directamente en el texto de la página
        const currentSpan = currentEl.querySelector<HTMLElement>(`#w_span_${idx}`)
        if (currentSpan) {
          currentSpan.style.backgroundColor = '#FACC15' // Amarillo Canario
          currentSpan.style.color = '#0F172A' // Texto oscuro de alto contraste
          currentSpan.style.fontWeight = '900'
          currentSpan.style.boxShadow = '0 0 8px rgba(234, 179, 8, 0.7)'
          currentSpan.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
        }

        currentActiveSpanIndex = idx
      }

      // 1. Escuchar eventos boundary palabra por palabra de la API de voz
      let wordCountOffset = 0
      utterance.onboundary = (e) => {
        if (e.name === 'word') {
          highlightWordIndex(wordCountOffset)
          wordCountOffset++
        }
      }

      // 2. Temporizador síncrono de respaldo (~440ms por palabra a 0.75x)
      const msPerWord = Math.round(444 / utterance.rate)
      let fallbackIndex = 0
      wordTimerRef.current = setInterval(() => {
        if (wordCountOffset === 0 && fallbackIndex < totalWords) {
          highlightWordIndex(fallbackIndex)
          fallbackIndex++
        }
      }, msPerWord)

      utterance.onend = () => {
        if (wordTimerRef.current) clearInterval(wordTimerRef.current)
        clearHighlight()
        nodeIndex++
        if (isReadingRef.current) {
          readNextNode()
        }
      }

      utterance.onerror = () => {
        if (wordTimerRef.current) clearInterval(wordTimerRef.current)
        clearHighlight()
        nodeIndex++
        if (isReadingRef.current) {
          readNextNode()
        }
      }

      window.speechSynthesis.speak(utterance)
    }

    readNextNode()
  }

  const pauseVoiceReader = () => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return
    if (isPaused) {
      window.speechSynthesis.resume()
      setIsPaused(false)
    } else {
      window.speechSynthesis.pause()
      setIsPaused(true)
    }
  }

  const stopVoiceReader = () => {
    isReadingRef.current = false
    if (wordTimerRef.current) {
      clearInterval(wordTimerRef.current)
      wordTimerRef.current = null
    }
    if (typeof window !== 'undefined') {
      window.speechSynthesis?.cancel()
    }
    clearHighlight()
    setIsReading(false)
    setIsPaused(false)
  }

  return (
    <>
      {/* 1. BARRA SUPERIOR INFORMATIVA (el botón redondo verde del Navbar abre/cierra el panel) */}
      <aside
        aria-label="Barra de herramientas de accesibilidad"
        className="bg-[#064E3B] text-white py-2 px-4 border-b border-[#00A859] text-sm font-medium"
      >
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-[#00A859] animate-pulse" />
            <span className="font-bold text-slate-100">Accesibilidad WCAG 2.2 • Nivel AA (Colegio de Bachilleres)</span>
          </div>

          {isReading && (
            <button
              onClick={stopVoiceReader}
              className="px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded-xl font-extrabold text-sm shadow transition-all flex items-center gap-1"
            >
              <span>⏹️ Detener lectura en voz alta</span>
            </button>
          )}
        </div>
      </aside>

      {/* 2. PANEL LATERAL DESPLEGABLE INSTITUCIONAL (w-72 sm:w-80) */}
      {isOpen && (
        <div className="fixed top-0 right-0 h-full w-72 sm:w-80 bg-[#F8FAF8] shadow-2xl z-50 border-l-2 border-[#BBF7D0] flex flex-col animate-in slide-in-from-right duration-300 text-slate-800 font-sans text-sm">
          
          {/* Header del Panel con Botón Restablecer */}
          <div className="p-3.5 bg-[#F0FDF4] border-b border-[#BBF7D0] flex items-center justify-between shrink-0">
            <button
              onClick={handleReset}
              className="px-3.5 py-1.5 bg-[#006837] hover:bg-[#00A859] text-white rounded-xl font-extrabold text-sm flex items-center gap-1.5 shadow transition-colors"
            >
              <svg className="w-3.5 h-3.5 fill-current rotate-180" viewBox="0 0 24 24">
                <path d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z" />
              </svg>
              <span>Restablecer</span>
            </button>

            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-emerald-100 font-black text-sm"
              aria-label="Cerrar panel"
            >
              ✕
            </button>
          </div>

          {/* Lista de Herramientas de Accesibilidad COBACH */}
          <div className="flex-1 overflow-y-auto p-3 space-y-2.5">

            {/* 1. Escala de grises */}
            <button
              onClick={() => setIsGrayscale(!isGrayscale)}
              className={`w-full p-2.5 rounded-2xl border text-left flex items-center gap-2.5 transition-all ${
                isGrayscale ? 'bg-[#006837] text-white border-[#00A859] shadow' : 'bg-white text-slate-800 border-[#BBF7D0] hover:bg-[#F0FDF4]'
              }`}
            >
              <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 font-black text-sm shadow-sm">
                ◐
              </div>
              <span className="font-bold text-sm leading-tight">Cambiar escala de grises</span>
            </button>

            {/* 2. Lector de pantalla con resaltado amarillo palabra por palabra */}
            <button
              onClick={() => (isReading ? stopVoiceReader() : startVoiceReader())}
              className={`w-full p-2.5 rounded-2xl border text-left flex items-center gap-2.5 transition-all ${
                isReading ? 'bg-[#006837] text-white border-[#00A859] shadow animate-pulse' : 'bg-white text-slate-800 border-[#BBF7D0] hover:bg-[#F0FDF4]'
              }`}
            >
              <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 text-sm shadow-sm">
                🔊
              </div>
              <span className="font-bold text-sm leading-tight">
                {isReading ? 'Detener lectura en voz alta' : 'Usar lector palabra por palabra'}
              </span>
            </button>

            {/* 3. Tamaño de cursor */}
            <button
              onClick={() => setIsLargeCursor(!isLargeCursor)}
              className={`w-full p-2.5 rounded-2xl border text-left flex items-center gap-2.5 transition-all ${
                isLargeCursor ? 'bg-[#006837] text-white border-[#00A859] shadow' : 'bg-white text-slate-800 border-[#BBF7D0] hover:bg-[#F0FDF4]'
              }`}
            >
              <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 text-sm shadow-sm">
                ⇖
              </div>
              <span className="font-bold text-sm leading-tight">Cambiar tamaño de cursor</span>
            </button>

            {/* 4. Contraste de color */}
            <button
              onClick={() => setIsHighContrast(!isHighContrast)}
              className={`w-full p-2.5 rounded-2xl border text-left flex items-center gap-2.5 transition-all ${
                isHighContrast ? 'bg-[#006837] text-white border-[#00A859] shadow' : 'bg-white text-slate-800 border-[#BBF7D0] hover:bg-[#F0FDF4]'
              }`}
            >
              <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 text-sm shadow-sm">
                🎨
              </div>
              <span className="font-bold text-sm leading-tight">Cambiar contraste de color</span>
            </button>

            {/* 5. Máscara de lectura */}
            <button
              onClick={() => { setIsReadingMask(!isReadingMask); if (isReadingGuide) setIsReadingGuide(false); }}
              className={`w-full p-2.5 rounded-2xl border text-left flex items-center gap-2.5 transition-all ${
                isReadingMask ? 'bg-[#006837] text-white border-[#00A859] shadow' : 'bg-white text-slate-800 border-[#BBF7D0] hover:bg-[#F0FDF4]'
              }`}
            >
              <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 text-sm shadow-sm">
                ═
              </div>
              <span className="font-bold text-sm leading-tight">Máscara de lectura</span>
            </button>

            {/* 6. Guía de lectura */}
            <button
              onClick={() => { setIsReadingGuide(!isReadingGuide); if (isReadingMask) setIsReadingMask(false); }}
              className={`w-full p-2.5 rounded-2xl border text-left flex items-center gap-2.5 transition-all ${
                isReadingGuide ? 'bg-[#006837] text-white border-[#00A859] shadow' : 'bg-white text-slate-800 border-[#BBF7D0] hover:bg-[#F0FDF4]'
              }`}
            >
              <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 text-sm shadow-sm">
                <u>U</u>
              </div>
              <span className="font-bold text-sm leading-tight">Guía de lectura</span>
            </button>

            {/* 7. Tipografía dislexia */}
            <button
              onClick={() => setIsDyslexiaFont(!isDyslexiaFont)}
              className={`w-full p-2.5 rounded-2xl border text-left flex items-center gap-2.5 transition-all ${
                isDyslexiaFont ? 'bg-[#006837] text-white border-[#00A859] shadow' : 'bg-white text-slate-800 border-[#BBF7D0] hover:bg-[#F0FDF4]'
              }`}
            >
              <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 font-serif italic text-base shadow-sm">
                I
              </div>
              <span className="font-bold text-sm leading-tight">Tipografía para dislexia</span>
            </button>

            {/* 8. Espaciado vertical */}
            <div className="p-2.5 bg-white rounded-2xl border border-[#BBF7D0] flex items-center justify-between gap-2">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 text-sm shadow-sm">
                  ↕
                </div>
                <span className="font-bold text-sm leading-tight">Espaciado vertical</span>
              </div>
              <div className="flex gap-1">
                {[0, 1, 2].map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setLineSpacingLevel(lvl)}
                    className={`w-6 h-6 rounded-lg text-xs font-black border ${
                      lineSpacingLevel === lvl ? 'bg-[#006837] text-white border-[#00A859]' : 'bg-slate-100 text-slate-600 border-slate-300'
                    }`}
                  >
                    {lvl === 0 ? '1x' : lvl === 1 ? '1.8x' : '2x'}
                  </button>
                ))}
              </div>
            </div>

            {/* 9. Espaciado Horizontal */}
            <div className="p-2.5 bg-white rounded-2xl border border-[#BBF7D0] flex items-center justify-between gap-2">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 text-sm shadow-sm">
                  ↔
                </div>
                <span className="font-bold text-sm leading-tight">Espaciado horizontal</span>
              </div>
              <div className="flex gap-1">
                {[0, 1, 2].map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setLetterSpacingLevel(lvl)}
                    className={`w-6 h-6 rounded-lg text-xs font-black border ${
                      letterSpacingLevel === lvl ? 'bg-[#006837] text-white border-[#00A859]' : 'bg-slate-100 text-slate-600 border-slate-300'
                    }`}
                  >
                    {lvl === 0 ? '1x' : lvl === 1 ? '2x' : '3x'}
                  </button>
                ))}
              </div>
            </div>

            {/* 10. Cambiar tamaño */}
            <div className="p-2.5 bg-white rounded-2xl border border-[#BBF7D0] flex items-center justify-between gap-2">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 text-sm font-black shadow-sm">
                  A
                </div>
                <span className="font-bold text-sm leading-tight">Tamaño de letra</span>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setFontSizeStep(Math.max(-2, fontSizeStep - 1))}
                  className="w-7 h-7 bg-[#006837] hover:bg-[#00A859] text-white rounded-lg font-black text-sm shadow flex items-center justify-center"
                  title="Disminuir tamaño de letra"
                >
                  -
                </button>
                <button
                  onClick={() => setFontSizeStep(Math.min(3, fontSizeStep + 1))}
                  className="w-7 h-7 bg-[#006837] hover:bg-[#00A859] text-white rounded-lg font-black text-sm shadow flex items-center justify-center"
                  title="Aumentar tamaño de letra"
                >
                  +
                </button>
              </div>
            </div>

            {/* 11. Resaltar Enlaces */}
            <button
              onClick={() => setIsHighlightLinks(!isHighlightLinks)}
              className={`w-full p-2.5 rounded-2xl border text-left flex items-center gap-2.5 transition-all ${
                isHighlightLinks ? 'bg-[#006837] text-white border-[#00A859] shadow' : 'bg-white text-slate-800 border-[#BBF7D0] hover:bg-[#F0FDF4]'
              }`}
            >
              <div className="w-8 h-8 rounded-xl bg-[#006837] text-white flex items-center justify-center shrink-0 text-sm shadow-sm">
                ✎
              </div>
              <span className="font-bold text-sm leading-tight">Resaltar enlaces</span>
            </button>

          </div>

          <div className="p-3 bg-[#F0FDF4] text-center text-xs text-[#006837] font-extrabold border-t border-[#BBF7D0]">
            Colegio de Bachilleres • Herramientas de Accesibilidad
          </div>
        </div>
      )}

      {/* 3. OVERLAYS DE MÁSCARA Y GUÍA DE LECTURA */}
      {isReadingMask && (
        <div className="fixed inset-0 pointer-events-none z-40 flex flex-col justify-between">
          <div 
            className="bg-black/75 w-full transition-all duration-75"
            style={{ height: Math.max(0, mouseY - 40) + 'px' }}
          />
          <div className="h-20 border-y-2 border-[#00A859] w-full" />
          <div className="bg-black/75 w-full flex-1" />
        </div>
      )}

      {isReadingGuide && (
        <div 
          className="fixed left-0 right-0 h-1 bg-[#00A859] shadow-[0_0_8px_#00A859] pointer-events-none z-40 transition-all duration-75"
          style={{ top: mouseY + 'px' }}
        />
      )}
    </>
  )
}
