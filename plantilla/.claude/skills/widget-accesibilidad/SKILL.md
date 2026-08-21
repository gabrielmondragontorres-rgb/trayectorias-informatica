---
name: widget-accesibilidad
description: |
  Menu flotante de accesibilidad para cualquier sitio Next.js + React: lector de voz con
  resaltado palabra por palabra, alto contraste, escala de grises, cursor grande, mascara y
  guia de lectura, fuente para dislexia, y ajuste de tamano de letra, interlineado y
  espaciado entre letras. Incluye el boton flotante que lo abre y el restablecer.

  Usar cuando: "agrega el menu de accesibilidad", "widget de accesibilidad", "boton de
  accesibilidad", "quiero el lector de voz", "que se pueda agrandar la letra", "opciones de
  accesibilidad", "panel de accesibilidad", "replica el menu de accesibilidad de la
  plataforma del curso".

  Pre-requisito: proyecto Next.js con React 19 y Tailwind. El estado del panel vive en un
  store de Zustand.
  NO USAR para: auditar la accesibilidad de una pagina (eso lo hace `accesibilidad-medible`),
  ni para el boton flotante de WhatsApp, que es otra cosa.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(npm *), Bash(npx tsc *)
metadata:
  author: cobach
  version: "1.0"
  estado: "COMPLETA v1.0 — panel, boton y store como assets; montaje global, persistencia y foco verificados"
---

# Widget de accesibilidad — menú flotante

> Extraído de la plataforma del curso «E-commerce incluyente» el 19 de agosto de 2026,
> a petición del Mtro. Luis Gabriel: *«ha sido un éxito»*.
>
> El componente real está en `assets/AccessibilityToolbar.tsx` (527 líneas). Esta skill lo
> documenta y explica cómo trasplantarlo; **no lo reescribe**.

---

## Qué hace

Doce funciones, todas del lado del navegador y sin dependencias externas:

| Función | Qué hace | A quién atiende |
|---|---|---|
| Lector de voz | Lee el contenido en voz alta **resaltando palabra por palabra** mientras avanza. Con pausa y reanudación | Baja visión, dislexia, lectura lenta |
| Tamaño de letra | 5 pasos, de −2 a +2, sobre una base de 16 px (2 px por paso) | Presbicia, baja visión |
| Interlineado | 3 niveles: normal, 1.8 y 2.2 | Dislexia, seguimiento de línea |
| Espaciado de letras | 3 niveles: normal, 0.08em y 0.16em | Dislexia |
| Fuente para dislexia | Cambia la tipografía de toda la página | Dislexia |
| Alto contraste | Refuerza la relación figura-fondo | Baja visión |
| Escala de grises | Elimina el color | Sensibilidad al color, migraña |
| Cursor grande | Puntero ampliado | Motricidad fina, baja visión |
| Máscara de lectura | Oscurece todo salvo la banda que se lee | Déficit de atención |
| Guía de lectura | Línea que sigue el cursor | Seguimiento de línea |
| Resaltar enlaces | Hace evidente qué es enlace | Daltonismo, baja visión |
| Restablecer | Devuelve todo al estado inicial de una sola vez | Todos |

**Por qué importa el restablecer:** sin él, alguien que activa la escala de grises por
error no sabe cómo volver, y abandona el sitio.

---

## Cómo está construido

Tres piezas, no una:

1. **`assets/AccessibilityToolbar.tsx`** — el panel. Se monta **una sola vez, en el layout
   raíz**. Panel lateral fijo a la derecha, de 288 px en móvil y 320 px en pantalla grande.
2. **`assets/BotonAccesibilidad.tsx`** — el botón que lo abre. Vive en la barra de
   navegación, no dentro del panel. Mide 44×44 px y su `aria-label` cambia según el estado:
   «Abrir panel de accesibilidad» / «Cerrar panel de accesibilidad».
3. **`assets/store-accesibilidad.ts`** — el booleano compartido. Están separados a propósito:
   así el botón puede vivir en la barra de navegación y el panel en el layout raíz.

Los tres archivos se copian tal cual. Solo hay que adaptar los nombres del store.

### Qué escribe exactamente sobre `documentElement`

Al trasplantarlo hay que llevarse también estas reglas de CSS, o los interruptores no harán
nada visible:

| Ajuste | Cómo se aplica | Valores |
|---|---|---|
| Escala de grises | clase `.grayscale-filter` | — |
| Cursor grande | clase `.large-cursor` | — |
| Alto contraste | clase `.high-contrast` | es la más grande: **56 reglas** en el proyecto de origen |
| Fuente para dislexia | clase `.dyslexia-font` | 10 reglas |
| Resaltar enlaces | clase `.highlight-links` | 2 reglas |
| Tamaño de letra | estilo en línea `font-size` | `16 + paso * 2` px, con paso de −2 a 2 |
| Interlineado | estilo en línea `line-height` | `normal`, `1.8`, `2.2` |
| Espaciado de letras | estilo en línea `letter-spacing` | `normal`, `0.08em`, `0.16em` |

La máscara y la guía de lectura no tocan `documentElement`: son dos capas fijas que el propio
componente dibuja siguiendo la posición del ratón.

---

## Cómo trasplantarlo a otro proyecto

1. Copiar `assets/AccessibilityToolbar.tsx` a `src/shared/components/`.
2. Agregar al store `isAccessibilityPanelOpen: boolean` y `setAccessibilityPanelOpen(open)`.
3. Colocar el botón en la barra de navegación, con `aria-label` que diga qué hace —
   «Abrir opciones de accesibilidad», no «Accesibilidad» a secas.
4. Montar `<AccessibilityToolbar />` en el layout, **no en una página suelta**.
5. Comprobar con la tecla Tab que el botón recibe foco y que al cerrar el panel el foco
   regresa al botón.

---

## El error a evitar: montarlo por página en vez de en el layout

En la plataforma de origen, `<AccessibilityToolbar />` estaba montado **cinco veces**: en las
cuatro ramas de retorno de `src/app/page.tsx` —sesión cargando, sin sesión, administrador y
docente— y otra vez en `src/app/saber-mas/page.tsx`. Aun así, `/login`, `/signup`,
`/dashboard` y `/profesor/dashboard` **se quedaban sin menú de accesibilidad**, aunque el
botón que lo abre sí aparecía, porque vive en la barra de navegación, que es global.

Es el peor de los dos mundos: repetido donde no hacía falta y ausente donde sí.

**Corregido el 19 de agosto de 2026.** Se movió a `src/app/layout.tsx`, después de
`{children}` y antes de `<PWARegister />`, y se quitaron los cinco montajes con sus imports.
Comprobado sirviendo la aplicación y consultando el HTML de cinco rutas: el panel aparece en
las cinco, incluidas las que antes no lo tenían.

> **Al replicar esta skill, montarlo siempre en el layout raíz.** Va después de `{children}`
> a propósito: el panel es de posición fija y no debe interponerse en el recorrido con la
> tecla Tab antes del contenido.

---

## Advertencia sobre el proyecto de origen

Al ir a hacer este cambio, `layout.tsx`, `page.tsx` y `globals.css` estaban **sobrescritos
por los archivos vacíos de la plantilla SaaS Factory** (8 líneas contra 192, 6 contra 211).
Es la misma incidencia registrada el 14 de agosto de 2026 en la memoria del proyecto. Se
restauraron desde el último commit —los vacíos quedaron en un `git stash`— y solo entonces se
hizo el cambio.

La misma incidencia se había llevado `allowImportingTsExtensions` del `tsconfig.json` y los
tipos de `src/lib/supabase/server.ts`. Ambos restaurados. **Antes de tocar el layout de un
proyecto de esta fábrica, comparar con `git status`.**

---

## Persistencia entre visitas

Quien necesita alto contraste o letra grande lo necesita **siempre**, no una vez. Sin
persistencia, el panel obliga a reconfigurarlo en cada carga y deja de servir.

Resuelto el 19 de agosto de 2026. Son **dos piezas**, y hacen falta las dos:

**1. Guardar y restaurar** — en `AccessibilityToolbar.tsx`, con la clave
`cobach_accessibility_settings`:

- Un efecto de montaje lee lo guardado; un efecto de cambio lo escribe.
- Existe una bandera `ajustesCargados`: **sin ella, el estado inicial pisaría la preferencia
  guardada** en el primer render, antes de haberla leído. Es el error clásico de este patrón.
- No se lee durante el render: el servidor no tiene `localStorage` y React marcaría desajuste
  de hidratación.
- `leerAjustes()` **sanea** lo que venga: nunca se confía en `localStorage`, que puede traer
  datos de una versión anterior o haber sido editado desde la consola. Un nivel fuera de rango
  dejaría `lineHeights[undefined]` y rompería el estilo.
- Si todo está en su valor por omisión se **borra** la clave en vez de guardarla: no se ocupa
  almacenamiento de quien nunca abrió el panel.
- El lector de voz **no** se guarda. Es una acción, no una preferencia, y una página que
  empieza a hablar sola al cargar asusta en vez de ayudar.

**2. Aplicar antes del primer pintado** — un script en línea y síncrono en el `<head>` del
layout. Sin él la página se dibuja con los valores por omisión y el panel corrige después: en
cada carga hay un parpadeo, y quien usa alto contraste ve un destello del tema normal. Es la
única forma de correr antes del pintado.

> El script refleja la misma lógica que el componente. **Si se cambian ahí las clases o los
> niveles, hay que cambiarlos también en el script del layout.** Es la deuda que deja esta
> solución, y está anotada en ambos archivos.

### Comprobado

Sirviendo la aplicación compilada y con navegador real: persiste tras recargar, se aplica
antes del pintado, se comparte entre rutas, sobrevive a un JSON corrupto sin romper la
página, acota los niveles fuera de rango, y en una primera visita no deja nada guardado.

---

## Foco y teclado

Comprobado el 20 de agosto de 2026 con navegador real, y **se corrigieron dos defectos** que
tenía el proyecto de origen:

| Comportamiento | Estado |
|---|---|
| El botón mide 44×44 px | Ya cumplía |
| El botón recibe foco y su `aria-label` cambia al abrir | Ya cumplía |
| **Escape cierra el panel** | **Corregido.** Antes no hacía nada |
| **Al cerrar, el foco vuelve al botón que abrió** | **Corregido.** Antes se iba al `<body>`, así que quien navega con teclado tenía que recorrer la página entera para volver a donde estaba |

Las dos correcciones están en un solo efecto del componente: al abrirse guarda
`document.activeElement` en una referencia y registra el escuchador de Escape; al cerrarse
devuelve el foco, si el elemento sigue en la página.

> **Cuidado al verificarlo.** El contenedor con `aria-label="Barra de herramientas de
> accesibilidad"` **existe siempre**, esté el panel abierto o cerrado. Comprobar contra él da
> un falso «abierto» permanente: me pasó, y me hizo creer que Escape no funcionaba cuando sí.
> Para saber si el panel está abierto hay que buscar el panel lateral o su botón de cerrar.

---

## Preferencias del sistema: recomendado, no implementado

El navegador ya sabe algunas cosas antes de que la persona toque nada:

- `prefers-contrast: more` — pide más contraste.
- `prefers-reduced-motion: reduce` — pide menos movimiento.
- `prefers-color-scheme` — tema claro u oscuro.

**No se implementó a propósito**, y conviene explicar el motivo antes de que alguien lo
agregue sin pensarlo: activar el alto contraste automáticamente cambia la página entera sin
que nadie lo haya pedido, y quien ya guardó su preferencia vería cómo se la sobrescribe el
sistema.

Si se implementa, la regla correcta es: **la preferencia guardada manda siempre**, y la del
sistema solo sirve como valor inicial cuando `localStorage` está vacío. Nunca al revés.

---

## Lo que falta para dar esta skill por terminada

Nada bloqueante. Versión **1.0** del 20 de agosto de 2026: panel, botón y store como assets,
montaje global, persistencia entre visitas sin parpadeo, y foco y teclado verificados.

Ideas para más adelante, ninguna urgente:

- Respetar `prefers-contrast` como valor inicial, con la regla del apartado anterior.
- Atrapar el foco dentro del panel mientras está abierto, para que Tab no se salga a la
  página de atrás.
- Traducir los rótulos, hoy fijos en español.
