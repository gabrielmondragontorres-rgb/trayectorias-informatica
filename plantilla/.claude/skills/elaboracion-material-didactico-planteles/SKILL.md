---
name: elaboracion-material-didactico-planteles
description: Skill para elaborar material de apoyo didáctico (plantillas, checklists, instrumentos de evaluación, presentaciones e infografías) para cursos/talleres de formación o para programas de estudio de planteles de nivel medio superior del Colegio de Bachilleres. Pregunta siempre el plantel, la modalidad y si el contenido pertenece a una TOB antes de generar nada, y usa la taxonomía de Bloom como base de la progresión de contenidos.
user-invocable: true
disable-model-invocation: false
---

# Skill: Elaboración de Material Didáctico para Planteles COBACH

Este skill genera material de apoyo didáctico real y operable —plantillas, checklists, instrumentos de evaluación, presentaciones e infografías— para **cursos o talleres de formación** y para **programas de estudio** de nivel medio superior del Colegio de Bachilleres. Está pensado para compartirse entre distintas personas usuarias y distintos planteles: por eso nunca asume contexto institucional, lo pregunta siempre.

**Principio rector:** todo resultado debe ser operable, real y estar acotado al logro de aprendizaje efectivo del estudiantado. Nunca generar contenido genérico, marcadores de posición ("Lorem ipsum", "[completar]") ni ejemplos desconectados de la meta de aprendizaje o del tema real solicitado.

---

## 1. Punto de Partida (Pregunta Obligatoria)

Antes de generar cualquier material, preguntar:

> ¿El material es para (a) un curso o taller de formación, o (b) un programa de estudios?

La respuesta determina la rama de trabajo (Sección 2 o Sección 3). No continuar sin esta respuesta.

---

## 2. Rama A: Curso o Taller de Formación

Preguntar, en este orden, lo que falte:

1. **Tema o contenido** a desarrollar en el curso/taller.
2. **Número de sesiones** (una o varias) y, si son varias, su distribución u orden lógico si el usuario ya lo tiene definido.
3. Continuar con el contexto institucional obligatorio (Sección 4), la regla de evaluación (Sección 5), Bloom (Sección 6), paleta de color (Sección 7) y otras consideraciones (Sección 8).

Con esa información, elaborar el material siguiendo la estructura de la Sección 9, replicando el patrón validado en el taller *"e-Commerce incluyente: Hacks de IA y accesibilidad para el aula emprendedora"* (PROFADD, 2026): información general del curso (propósito, datos generales, contenidos, agenda, criterios de evaluación) + material de apoyo desarrollado a detalle por cada sesión.

---

## 3. Rama B: Programa de Estudios

Preguntar, en este orden, lo que falte:

1. **Nombre del programa de estudios.**
2. Solicitar que el usuario **suba el documento oficial** para revisarlo. Si no lo tiene disponible, buscarlo en `https://www.gob.mx/bachilleres/articulos/programas-de-estudio-vigentes` (usar `WebFetch`/`WebSearch`) y confirmar con el usuario que es el programa correcto antes de usarlo como fuente.
3. **Alcance de la fuente:** ¿se trabaja todo el programa, un corte específico o una meta específica?
4. **Granularidad del entregable:** ¿el material se quiere por sesión, por meta específica, por corte o para el programa completo?
5. Continuar con el contexto institucional obligatorio (Sección 4), la regla de evaluación (Sección 5), Bloom (Sección 6), paleta de color (Sección 7) y otras consideraciones (Sección 8).

Con el programa ya revisado, usar el protocolo de `curriculum-mapping` para extraer metas, evidencias (conocimiento/desempeño/producto) y verbos de Bloom del alcance solicitado, y `detalles-corte`/`esquema-competencia` si hace falta reconstruir cortes o metas que no estén explícitos. Si ya existe una guía de estudio para ese programa en el proyecto, **no la dupliques ni la contradigas**: consulta `elaboracion-guias`, `instrumentacion-didactica`, `criterios-guia` y `estructura-guia` como referencia y genera material complementario (recursos de apoyo, no otra guía completa) salvo que el usuario pida explícitamente una guía nueva.

---

## 4. Contexto Institucional Obligatorio (Preguntar Siempre)

*   **Plantel:** nombre exacto del plantel COBACH. Es obligatorio y debe incluirse en el encabezado o portada de todo material generado (documentos, presentaciones, infografías con créditos).
*   **Nivel:** siempre nivel medio superior (Colegio de Bachilleres), estudiantado adolescente. No adaptar el tono ni la complejidad a otros niveles educativos.
*   **Modalidad** — preguntar siempre cuál aplica:
    *   **Normal (presencial):** heteroevaluación docente + coevaluación en equipos.
    *   **A distancia:** recursos y evidencias entregables en línea; heteroevaluación asincrónica; priorizar formatos digitales verificables (capturas, enlaces, documentos).
    *   **Autodidacta (autogestiva):** aplicar la terminología autogestiva ya establecida en `criterios-guia` y `elaboracion-guias` — evitar los términos "heteroevaluación"/"coevaluación" en el material dirigido al estudiantado; usar "autoevaluación / reflexión individual".
*   **Resultados operables y reales:** cada plantilla, checklist o instrumento debe poder usarse tal cual en el aula o plantel; debe referirse a la meta de aprendizaje, evidencia o tema real solicitado, nunca a un ejemplo abstracto desconectado del contexto entregado por el usuario.

---

## 5. Regla de Evaluación: TOB vs. No-TOB

Preguntar (o inferir con confirmación del usuario si es evidente por el nombre del programa/tema): **¿el contenido pertenece a una Trayectoria Ocupacional Básica (TOB)?**

*   **Si es TOB:** aplicar íntegramente el skill `evaluacion-competencia-tob` — tríada de competencias (conocimiento/desempeño/producto), momentos (diagnóstica/formativa/sumativa), tipos (autoevaluación/coevaluación/heteroevaluación) y ponderaciones (20-30 % / 30-40 % / 30-40 %). Si el material es sobre una UAC, corte o meta específica en particular, esa skill ya exige preguntar el alcance exacto antes de generar instrumentos: respeta esa regla.
*   **Si NO es TOB:** aplicar evaluación general con **prueba objetiva** como instrumento principal para la evidencia de conocimiento. Complementar con listas de cotejo o rúbricas para desempeño/producto únicamente cuando la actividad lo amerite (no reducir todo a opción múltiple si el contenido exige demostrar un desempeño o entregar un producto).

---

## 6. Bloom como Base de los Contenidos

*   Todo contenido, actividad y evidencia debe progresar según la taxonomía de Bloom: **Recordar → Comprender → Aplicar → Analizar → Evaluar → Crear.**
*   Cuando exista un programa de estudios fuente (Rama B), usar el protocolo de `curriculum-mapping`: identificar el verbo operativo de cada meta específica y asegurar que el desarrollo teórico, la actividad y el instrumento de evaluación respondan a ese nivel cognitivo exacto (no usar instrumentos de nivel superior o inferior al que marca la meta).
*   Cuando no exista un programa fuente (Rama A), diseñar la progresión de sesiones para que las primeras trabajen Recordar/Comprender/Aplicar y las últimas Analizar/Evaluar/Crear, replicando el patrón validado: sesiones técnicas que llegan hasta Aplicar/Analizar, y una sesión de cierre/integración que llega a Evaluar/Crear mediante un producto integrador.

---

## 7. Paleta de Color

*   Preguntar si el proyecto, curso o institución tiene un color institucional o clave Pantone definida.
*   Si el usuario lo proporciona, calcular la rampa de variaciones más claras (100 % / 60 % / 40 % / 20 % / 10 %) con la misma fórmula de tinte usada para Pantone 327 C: `tint = color + (255 − color) × (1 − fracción)`. Verificar el hex real de la clave Pantone con una búsqueda web antes de asumirlo de memoria.
*   Si el usuario no lo tiene, ofrecer como opción por defecto la paleta institucional azul ya usada en materiales previos del Colegio de Bachilleres (`#002B5C` / `#005B9E` / `#D6E4F0`) o remitir a `.claude/design-systems/` si el proyecto tiene sistemas de diseño propios.
*   Aplicar la paleta exclusivamente en las tablas y elementos gráficos del material (encabezados oscuros, bandeado en tonos claros); nunca mezclar colores fuera de la rampa acordada con el usuario.

---

## 8. Otras Consideraciones (Pregunta de Cierre)

Antes de empezar a generar contenido, preguntar siempre:

> ¿Hay alguna otra consideración que deba tomar en cuenta (estudiantado con alguna condición particular, recursos tecnológicos disponibles en el plantel, restricciones de tiempo, requisitos adicionales de lenguaje incluyente o accesibilidad, etc.)?

---

## 9. Estructura del Entregable

Aplicar esta estructura a la unidad solicitada (sesión, meta específica, corte o programa completo):

1.  **Encabezado:** curso/taller o UAC, plantel, sesión/corte/meta, fecha, modalidad, elaboró.
2.  **Propósito**, redactado con un verbo acorde al nivel de Bloom correspondiente.
3.  **Competencias o aprendizajes que se trabajan.**
4.  **Instrucciones generales.**
5.  **Desarrollo:** ejercicios o actividades con nombre significativo, instrucciones paso a paso y, si involucran IA, prompts sugeridos junto con la exigencia explícita de revisión crítica del equipo/estudiante sobre la salida del modelo.
6.  **Evidencias esperadas** de cada actividad.
7.  **Recursos y plantillas de apoyo:** desarrollados a detalle (fichas, protocolos, checklists, formatos, guías) — nunca solo mencionados por nombre sin contenido real.
8.  **Instrumento de evaluación** correspondiente a cada evidencia (lista de cotejo / rúbrica / prueba objetiva), conforme a la Sección 5, con ponderación cuando aplique.
9.  **Presentación (.pptx)** si la sesión o unidad requiere exposición de contenido ante el grupo.
10. **Infografía** si el contenido es denso o articula un framework/proceso visual clave (generar con matplotlib u otra herramienta programática para garantizar texto exacto y consistencia de paleta; usar generación de imágenes con IA solo si el proyecto ya tiene `OPENROUTER_API_KEY` configurada y el usuario lo prefiere).
11. **Producto final o rúbrica integradora**, si la unidad culmina en un producto integrador.

---

## 10. Pipeline de Ejecución

1.  Preguntar la rama (Sección 1: curso/taller vs. programa de estudios).
2.  Ejecutar las preguntas específicas de la rama correspondiente (Sección 2 o 3).
3.  Preguntar el contexto institucional obligatorio (Sección 4: plantel, modalidad).
4.  Determinar TOB o no-TOB y aplicar la regla de evaluación correspondiente (Sección 5).
5.  Mapear los contenidos a Bloom (Sección 6).
6.  Confirmar o calcular la paleta de color (Sección 7).
7.  Preguntar si hay otras consideraciones (Sección 8).
8.  Elaborar el material completo de la unidad solicitada siguiendo la Sección 9.
9.  **Validar antes de entregar:** cada recurso mencionado en el cuerpo del material existe realmente desarrollado (no solo nombrado); cada evidencia declarada tiene su instrumento de evaluación correspondiente; las ponderaciones suman 100 % cuando aplica; no quedan tablas o elementos fuera de la paleta acordada.
10. Entregar en el/los formato(s) pertinentes (Word, PowerPoint, imágenes) y confirmar al usuario la ubicación de los archivos generados.

### Regla de Oro — Autoría del Contenido
El contenido debe leerse como elaborado por personal docente/institucional, no por una IA generativa: no incluir menciones, marcas de agua ni frases que insinúen generación por inteligencia artificial (ver regla equivalente en `instrumentacion-didactica`, sección D).
