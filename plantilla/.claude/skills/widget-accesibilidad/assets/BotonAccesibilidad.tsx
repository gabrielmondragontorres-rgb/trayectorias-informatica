// Botón que abre el panel de accesibilidad.
// Vive en la barra de navegación, NO dentro del panel: así el botón es global
// aunque el panel se monte en el layout raíz. Los une el store de Zustand.
//
// Extraído de src/shared/components/Navbar.tsx el 20 de agosto de 2026.

'use client'

import { useState, useEffect, useRef } from 'react'
import { useAppStore } from '@/shared/store/useAppStore'

export function BotonAccesibilidadRedondo() {
  const isPanelOpen = useAppStore((state) => state.isAccessibilityPanelOpen)
  const setAccessibilityPanelOpen = useAppStore((state) => state.setAccessibilityPanelOpen)
  const [imgError, setImgError] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)

  // La imagen se renderiza en el HTML del servidor: si ya falló antes de que
  // React hidrate y adjunte onError, ese evento nativo se pierde. Se revisa
  // el estado real de la imagen justo después del montaje como respaldo.
  useEffect(() => {
    const img = imgRef.current
    if (img && img.complete && img.naturalWidth === 0) {
      setImgError(true)
    }
  }, [])

  return (
    <button
      onClick={() => setAccessibilityPanelOpen(!isPanelOpen)}
      aria-label={isPanelOpen ? 'Cerrar panel de accesibilidad COBACH' : 'Abrir panel de accesibilidad COBACH'}
      title="Accesibilidad COBACH"
      className="shrink-0 w-11 h-11 rounded-full p-[3px] shadow-md transition-transform hover:scale-110"
      style={{ background: 'conic-gradient(from 0deg, #006837, #00A859, #BBF7D0, #00A859, #006837)' }}
    >
      <span className="flex items-center justify-center w-full h-full rounded-full bg-white overflow-hidden">
        {!imgError ? (
          <img
            ref={imgRef}
            src="/images/accesibilidad_imagotipo_1785341088315.png"
            onError={() => setImgError(true)}
            alt=""
            className="w-full h-full object-cover"
          />
        ) : (
          <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="#006837" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="5" r="2.4" fill="#006837" stroke="none" />
            <path d="M12 8v7" />
            <path d="M12 10.5 6.5 8.5" />
            <path d="M12 10.5 17.5 8.5" />
            <path d="M12 15 8 20.5" />
            <path d="M12 15 16 20.5" />
          </svg>
        )}
      </span>
    </button>
  )
}
