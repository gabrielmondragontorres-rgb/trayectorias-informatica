---
name: docx-cobach
description: |
  Motor de documentos Word (.docx) con la identidad visual del Colegio de Bachilleres.
  Entrega bloques listos —portada, jerarquia de titulos, fichas, tablas con cebreado,
  avisos, citas, bloques de codigo y de prompt, cuadros de meta, imagenes con pie— para
  que ninguna skill vuelva a escribir XML de Word a mano. Incluye validador que detecta
  los archivos que Word marcaria como danados y autochequeo de contraste de la paleta.

  Usar cuando: se va a producir cualquier .docx institucional (guias, programas,
  materiales, reportes, evidencias), o cuando otra skill necesita generar Word y no
  quiere reinventar el formato. Tambien para validar un .docx antes de entregarlo.

  Pre-requisito: python-docx y lxml instalados.
  NO USAR para: decidir QUE secciones lleva un documento. Eso lo mandan `estructura-guia`
  y `formato-word-guia`. Esta skill solo dibuja.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(python *), Bash(pip *)
metadata:
  author: cobach
  version: "1.0"
---

# docx-cobach — motor de documentos Word

> Nacio el 19 de agosto de 2026 al producir los seis documentos de `Hacks resueltos/`.
> Ocho skills de esta fabrica terminan en un `.docx` y ninguna compartia motor.

---

## Propósito

Separar **cómo se ve** un documento de **qué dice**. Esta skill resuelve lo primero y no
opina sobre lo segundo.

| Sí hace | No hace |
|---|---|
| Dibujar portada, títulos, tablas, fichas, avisos, imágenes | Decidir qué secciones lleva una guía |
| Aplicar la paleta y la tipografía institucionales | Redactar contenido |
| Verificar que la paleta cumpla contraste | Verificar la corrección curricular |
| Detectar `.docx` que Word abriría como dañados | Corregir la ortografía |

La estructura de contenido la mandan **`estructura-guia`** y **`formato-word-guia`**.
La redacción, **`perfil-escritura-gabo`** y **`lenguaje-incluyente`**.

---

## Uso mínimo

```python
import sys
sys.path.insert(0, ".claude/skills/docx-cobach/scripts")
from docx_cobach import Doc

d = Doc(perfil="guia", pie="Guía de estudio · Colegio de Bachilleres")

d.portada(
    "Guía de estudio",
    "Aplicación del comercio electrónico",
    sobretitulo="Quinto semestre",
    metadatos=[("Plantel", "16 Tláhuac"), ("Ciclo escolar", "2026-A")],
)
d.h1("Presentación", salto_antes=False)
d.p("Texto justificado, que admite **negritas en línea**.")
d.tabla(["Corte", "Meta de aprendizaje"], [["Corte 1", "Desarrollar una landing page…"]])
d.guardar("salida.docx")
```

Después, **siempre**:

```bash
python .claude/skills/docx-cobach/scripts/validar_docx.py salida.docx
```

---

## Perfiles visuales

Se elige con `Doc(perfil=...)`. Los dos comparten el verde institucional; cambian los
tamaños, los márgenes y el ritmo vertical.

| | `documento-tecnico` | `guia` |
|---|---|---|
| Para qué | Reportes, materiales, evidencias, documentación | Guías y programas de estudio |
| Título 1 | 16 pt, banda verde `#006837` con texto blanco | 14 pt, verde `#006837` sobre blanco |
| Título 2 | 13.5 pt verde, con regla inferior | 12 pt verde, sin regla |
| Título 3 | 11.5 pt `#007A42` | 11 pt `#007A42` |
| Cebreado de tabla | `#F4F9F6` | `#D1EBE5` verde menta |
| Tipografía en tablas | 9.5 pt | 10 pt |
| Espaciado posterior | 6 pt | 2 pt |
| Márgenes | 2.2 / 2.2 / 2.4 / 2.4 cm | 3.75 / 2.54 / 1.91 / 1.91 cm |

Comunes a los dos: Noto Sans, interlineado 1.15, encabezado de tabla `#006837` con texto
blanco, enlaces en azul `#0563C1`.

**Los enlaces se quedan en azul.** Decisión del 19 de agosto de 2026: el texto azul
subrayado es la convención que la gente reconoce como enlace. No volver a proponer el
cambio.

**El perfil `guia` está construido pero no adoptado.** Antes de usarlo en producción hay
que reproducir una guía ya aprobada y comparar. Mientras tanto, las guías se siguen
haciendo con el flujo actual.

---

## Referencia de bloques

| Llamada | Qué dibuja |
|---|---|
| `portada(titulo, subtitulo, sobretitulo, metadatos)` | Carátula con tabla de metadatos y salto de página |
| `h1(texto, salto_antes=True)` | Título de primer nivel. `salto_antes=False` para el primero |
| `h2(texto)` / `h3(texto)` | Segundo y tercer nivel |
| `p(texto)` | Párrafo justificado. Interpreta `**negritas**` |
| `vineta(texto, nivel=0)` / `numerada(texto)` | Listas |
| `tabla(encabezados, filas, anchos, cebra=True)` | Tabla con encabezado de color y cebreado |
| `ficha(campos)` | Tabla de dos columnas etiqueta / valor |
| `cuadro_meta(texto, prefijo)` | Tabla 1×1 de meta específica: contorno negro, sin relleno |
| `etiqueta(texto)` | Franja de color que rotula el bloque siguiente |
| `cita(texto)` | Bloque con barra lateral de acento |
| `aviso(titulo, texto)` | Recuadro de color para advertencias |
| `bloque_prompt(texto)` | Texto literal sobre fondo oscuro, monoespaciado |
| `bloque_codigo(texto)` | Fragmento de código sobre fondo claro |
| `imagen(ruta, ancho_cm, pie)` | Imagen centrada con pie numerado automáticamente |
| `espacio(pt)` / `salto()` | Separación y salto de página |
| `guardar(ruta)` | Escribe el archivo, creando la carpeta si hace falta |

---

## Auto-blindaje: el orden de los elementos en OOXML

**El error.** Insertar `<w:shd>` o `<w:pBdr>` al final de `<w:pPr>` produce un archivo que
Word abre con el aviso «documento dañado» y ofrece reparar. El esquema exige que ambos
vayan **antes** de `w:spacing`, `w:ind` y `w:jc`. En `<w:tcPr>`, `w:shd` va después de
`w:tcBorders`.

**Cómo apareció.** El 19 de agosto de 2026, con seis documentos ya producidos. Se detectó
al revisar el XML, no al abrirlos.

**La regla.** Nunca `pPr.append(shd)`. Usar siempre los ayudantes del módulo:
`sombrear_parrafo()`, `sombrear_celda()`, `borde_parrafo()`, que llaman internamente a
`_colocar()` con la secuencia correcta del esquema.

**El seguro.** `validar_docx.py` recorre todo el XML del paquete y reporta cuántos `w:pPr`
y `w:tcPr` tienen hijos fuera de orden. Correrlo antes de entregar cualquier documento.

Segundo aprendizaje, heredado de `formato-word-guia`: la fuente hay que forzarla también en
`w:eastAsia` del `rFonts`, o Word Online la sustituye por Calibri. El motor ya lo hace en
cada `run`.

---

## Verificación de contraste

La paleta se comprueba sola, porque una fábrica que enseña accesibilidad no puede publicar
documentos que no la cumplan:

```python
from docx_cobach import verificar_perfil
for etq, fg, bg, ratio, ok in verificar_perfil("guia"):
    print(f"{ratio:.2f}:1", "OK" if ok else "NO CUMPLE", etq)
```

Este autochequeo ya encontró un fallo real: `#00A859` sobre blanco da **3.11:1**, por debajo
del mínimo de 4.5:1. Era el color del tercer nivel y se bajó a `#007A42` (5.44:1).
**`#00A859` solo sirve como fondo con texto blanco encima, nunca como color de texto.**

---

## Scripts

| Archivo | Para qué |
|---|---|
| `scripts/docx_cobach.py` | El motor. Se importa |
| `scripts/validar_docx.py` | Valida uno o varios `.docx`, o una carpeta entera |
| `scripts/demo.py` | Genera una muestra por perfil e imprime el contraste de cada paleta |

```bash
python scripts/demo.py ./muestras
python scripts/validar_docx.py "Hacks resueltos/"
```

---

## Documentos ya producidos con este motor

Los seis de `Hacks resueltos/` (19 de agosto de 2026, perfil `documento-tecnico`):
el catálogo maestro y las cinco sesiones, unas 49 500 palabras y 222 tablas en total.
Validados: 0 problemas.

---

## Pendiente

- Prueba de fidelidad del perfil `guia` contra una guía ya aprobada, antes de adoptarlo.
- Definir el perfil `programa`.
- Encabezado con logotipo institucional: hoy solo hay pie de página.
