/**
 * Cadena de modelos con relevo automático.
 *
 * Es la pieza que mantiene el asistente en pie. Con la capa gratuita de Gemini —20
 * peticiones diarias por modelo— un grupo de treinta personas agota el primer modelo en
 * media sesión. Sin relevo, a partir de ahí el asistente devuelve error a todo el mundo.
 *
 * El orden NO es "el modelo más nuevo primero", sino el que resultó más fiable al medirlo
 * contra la tarea real. En el proyecto de origen, con dos corridas por modelo:
 *
 *   gemini-3.5-flash       2/2 correctas, 7.5-9.6 s   <- estable, se queda de principal
 *   gemini-3.6-flash       2/2 correctas, 7.6-8.0 s
 *   gemini-3.7-flash       1/2: devuelve 503 "high demand" de forma intermitente
 *   gemini-3.1-flash-lite  veredictos más laxos, sirve de relevo pero no de principal
 *
 * Hallazgos para no repetir el camino:
 *  - Los `gemini-2.5-*` devuelven 404: están retirados para cuentas nuevas.
 *  - Los alias móviles tipo `gemini-flash-latest` se colgaron (timeout a 70 s). Fija
 *    versiones concretas.
 *  - Los modelos gratuitos de OpenRouter no soportan tool calling de forma confiable:
 *    ante "llévame al Hack 3" devolvían un valor fuera del enum. Van al final igual,
 *    porque una respuesta imperfecta es mejor que un asistente caído.
 *
 * MIDE ESTO TÚ antes de fijar tu orden. Los nombres de modelo y sus tiempos cambian.
 */
import { createGoogleGenerativeAI } from '@ai-sdk/google'
import type { LanguageModel } from 'ai'

const google = createGoogleGenerativeAI({
  apiKey: process.env.GOOGLE_GENERATIVE_AI_API_KEY ?? '',
})

export const CADENA_MODELOS_CHAT: { nombre: string; modelo: () => LanguageModel }[] = [
  { nombre: 'gemini-3.5-flash', modelo: () => google('gemini-3.5-flash') },
  { nombre: 'gemini-3.6-flash', modelo: () => google('gemini-3.6-flash') },
  { nombre: 'gemini-3.1-flash-lite', modelo: () => google('gemini-3.1-flash-lite') },
  // Agrega aquí tu proveedor de respaldo, p. ej. OpenRouter.
]

/**
 * Traduce el error del proveedor a algo que la persona pueda accionar.
 *
 * Sin esto, el SDK enmascara todo como "An error occurred", que no dice si hay que
 * esperar, recargar crédito o cambiar la llave.
 */
export function describirErrorIA(error: unknown): string {
  const texto =
    error instanceof Error
      ? `${error.message} ${String((error as { cause?: unknown }).cause ?? '')}`
      : String(error)

  if (/API key not valid|API_KEY_INVALID|UNAUTHENTICATED|401|Unauthorized|No auth credentials/i.test(texto)) {
    return 'La llave de la IA no es válida o fue revocada. Hay que generar una nueva y actualizar la variable de entorno.'
  }
  if (/PERMISSION_DENIED|403/i.test(texto)) {
    return 'La llave no tiene permiso para usar ese modelo. Revisa la configuración del proyecto en el proveedor.'
  }
  if (/402|Insufficient credits/i.test(texto)) {
    return 'La cuenta del proveedor se quedó sin crédito.'
  }
  if (/RESOURCE_EXHAUSTED|429|rate limit|Too Many Requests|quota/i.test(texto)) {
    return 'Se alcanzó el límite de peticiones por ahora. Vuelve a intentarlo en unos minutos.'
  }
  if (/timeout|aborted|ETIMEDOUT|ENOTFOUND|fetch failed|network|503|UNAVAILABLE/i.test(texto)) {
    return 'El servicio de IA no respondió a tiempo. Vuelve a intentarlo en un momento.'
  }
  return 'No se pudo completar la respuesta del asistente. Intenta de nuevo.'
}
