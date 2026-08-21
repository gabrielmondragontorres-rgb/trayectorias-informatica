// Fragmento del store que conecta el botón con el panel.
//
// Son dos piezas que viven en sitios distintos del árbol —el botón en la barra de
// navegación, el panel en el layout raíz— y necesitan compartir un solo booleano.
// Por eso el estado está fuera de los dos y no dentro del panel.
//
// Extraído de src/shared/store/useAppStore.ts el 20 de agosto de 2026.
// Adapta los nombres a tu store; lo único que importa es que existan el valor y su setter.

// --- 1. En la interfaz del estado -------------------------------------------
export interface EstadoAccesibilidad {
  isAccessibilityPanelOpen: boolean
}

// --- 2. En el valor inicial --------------------------------------------------
export const estadoInicialAccesibilidad: EstadoAccesibilidad = {
  isAccessibilityPanelOpen: false,
}

// --- 3. En las acciones del store -------------------------------------------
//
// Con Zustand normal:
//
//   export const useAppStore = create<Estado>((set) => ({
//     isAccessibilityPanelOpen: false,
//     setAccessibilityPanelOpen: (open: boolean) =>
//       set({ isAccessibilityPanelOpen: open }),
//   }))
//
// En el proyecto de origen el store es una implementación propia con suscriptores,
// así que la acción se ve así:
//
//   setAccessibilityPanelOpen(open: boolean) {
//     currentStoreState = { ...currentStoreState, isAccessibilityPanelOpen: open }
//     notificarSuscriptores()
//   }

// --- 4. En el componente -----------------------------------------------------
//
//   const isOpen  = useAppStore((s) => s.isAccessibilityPanelOpen)
//   const setOpen = useAppStore((s) => s.setAccessibilityPanelOpen)
//
// NO metas aquí las preferencias de accesibilidad (tamaño de letra, contraste…).
// Esas viven en el propio AccessibilityToolbar y se guardan en localStorage con la
// clave `cobach_accessibility_settings`. Lo único compartido es si el panel está
// abierto o cerrado.
