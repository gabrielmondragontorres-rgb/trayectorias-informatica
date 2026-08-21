---
name: planeacion-didactica
description: |
  Elabora la planeación didáctica de una persona docente a partir de SU programa
  de estudio, en el formato oficial del Colegio de Bachilleres. Reconoce si el
  programa está escrito en la estructura por UAC (Modelo 2023) o por Asignatura
  (Modelo Educativo 2025) y adapta nomenclatura, etiquetas y transversalidad al
  modelo que corresponda.

  Usar cuando: "hazme la planeación didáctica", "planeación de mi asignatura",
  "necesito la planeación del corte 1", "sube el programa y desarróllame la
  planeación", "planeación didáctica del semestre", "secuencia didáctica",
  "instrumentación didáctica de mi UAC", "estrategia didáctica de mi
  asignatura", "planeación por cortes", "el profesor subió su programa".

  REQUISITO ABSOLUTO: no se genera ninguna planeación sin el programa de estudio.
  No es una formalidad. La planeación se deriva del programa; sin él, lo que se
  produce es una plantilla rellenada con invenciones. La persona docente puede
  subirlo, indicar dónde está en línea, o dar el nombre de la asignatura y el
  semestre para buscarlo y confirmárselo.

  Pregunta también el CONTEXTO antes de redactar: condiciones y recursos del
  plantel, caracterización del grupo, y la problemática situada que tenga en
  mente. Sin eso salen actividades correctas en el papel que el plantel no puede
  ejecutar.

  Pre-requisito: python-docx y lxml. Usa el motor `docx-cobach` para el Word.
  NO USAR para: elaborar o migrar el programa de estudio en sí (eso es
  `elaboracion-programas` para UAC y `elaboracion-programas-asignatura` para el
  Modelo 2025), ni para guías de estudio (`elaboracion-guias`).
argument-hint: "[ruta del programa de estudio .docx] (opcional: número de corte)"
user-invocable: true
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Planeación didáctica COBACH — de un programa de estudio a la planeación

Esta skill convierte el programa de estudio de una persona docente en su
planeación didáctica, con el formato oficial y en el idioma curricular correcto.

Su razón de ser es un hecho concreto: desde agosto de 2026 el Componente de
Formación Laboral tiene **dos estructuras vivas al mismo tiempo**. Los programas
de sexto semestre siguen escritos por Unidad de Aprendizaje Curricular y los de
tercero ya están por Asignatura. Una planeación que use el vocabulario del
modelo equivocado se lee de inmediato como una plantilla ajena rellenada de
prisa, y quien la revisa lo nota en la primera tabla.

---

## 0. Lo primero, y no es negociable: pedir el programa

**Sin programa de estudio no hay planeación.** Ante cualquier petición, la
primera acción es conseguirlo.

La razón no es burocrática. La planeación didáctica no inventa contenido: lo
**deriva**. La competencia laboral, el propósito, la meta del corte, los
desarrollos, las evidencias y la transversalidad ya están escritos en el
programa y tienen redacción oficial. Producir una planeación sin él significa
fabricar metas que no existen, y ese documento no sobrevive a la primera
revisión.

Hay tres maneras de conseguirlo, y conviene ofrecerlas en este orden:

1. **Que la persona docente lo suba.** Es la vía más segura: se trabaja sobre la
   versión que ella tiene, que es la que va a aplicar.
2. **Que indique dónde está en línea.** Se descarga y se le confirma cuál se tomó.
3. **Que diga el nombre de la asignatura o UAC y el semestre**, y se busca. En
   ese caso hay que **mostrarle qué documento se encontró y pedir que confirme
   que es el suyo** antes de usarlo, porque circulan versiones y actualizaciones
   distintas del mismo programa.

Lo que no se hace nunca es empezar sin él, ni reconstruirlo de memoria.

Cuando el programa llega, el orden es este:

```
1. Detectar la estructura      →  scripts/detectar_modelo.py
2. CONFIRMAR con la persona    →  nunca dar por buena la detección a solas
3. Extraer los elementos       →  leer el programa, no la memoria
4. Preguntar el alcance        →  ¿un corte o el semestre completo?
5. Preguntar el CONTEXTO       →  plantel, grupo y problemática situada
6. Redactar la planeación      →  JSON con la estructura del formato
7. Validar                     →  scripts/validar_planeacion.py
8. Generar el .docx            →  scripts/generar_planeacion.py
9. Validar el archivo          →  docx-cobach/scripts/validar_docx.py
```

### La pregunta obligatoria

Después de correr el detector, **preguntar siempre**, incluso cuando la
confianza salga al 100 %:

> Tu programa está escrito en la estructura **[por UAC / por asignatura]**.
> ¿Es correcto? Lo pregunto porque de esto depende toda la nomenclatura del
> documento.

El detector lee marcadores de vocabulario, y el vocabulario puede mentir. Un
programa migrado a medias conserva las dos mitades; uno recién convertido puede
traer la nota de portada que cita el programa por UAC del que deriva, que es
correcta y no significa que el documento sea del modelo anterior. Quien imparte
la asignatura sabe cuál es la versión vigente. El detector solo opina.

Si el detector marca **DOCUMENTO HIBRIDO**, no seguir: preguntar cuál es la
versión vigente. Una planeación construida sobre un programa a medio migrar
hereda la mezcla y la propaga.

### La segunda pregunta

**¿Un corte o el semestre completo?** Y con ella, cuántos cortes tiene el
programa. Nunca suponer tres. El formato oficial de referencia trae un solo
corte por archivo, y así se usa con frecuencia.

### La tercera pregunta: los datos de identificación

Se piden juntos, antes de generar: **nombre de la persona docente, plantel y
ciclo escolar**. La **fecha se toma del sistema**, no se pregunta.

El nombre **no se toma de ningún padrón ni de la plataforma de un curso**. Se
pregunta. La planeación puede elaborarse fuera de ese contexto y el dato saldría
equivocado.

Ese nombre va en dos lugares: la celda de identificación y las **propiedades del
archivo de Word**, como autor. El documento lo firma quien imparte la asignatura,
no la herramienta que lo genera.

Si la planeación es genérica para varios planteles, el campo de plantel se deja
vacío para que cada quien lo llene. Un campo vacío es un formulario; una frase
del tipo "escriba aquí su plantel" es relleno, y no va.

### La cuarta pregunta: el contexto en que se va a impartir

Es la que convierte una plantilla en una planeación aplicable. Sin ella salen
actividades correctas en el papel que el plantel no puede ejecutar. Se pregunta
en tres frentes.

**1. Condiciones del plantel.** Con qué se cuenta realmente para trabajar: si hay
sala de cómputo o se trabaja con los teléfonos del grupo, cuántos equipos hay y
en qué estado, si la conexión a internet es estable, si hay proyector, y qué
material específico existe para esa asignatura (componentes electrónicos,
cámaras, licencias de software). Conviene preguntar también qué **no** hay, que
suele ser más informativo.

Esta respuesta cambia la forma de las actividades, no su exigencia. Un corte que
pide producir una landing page accesible sigue pidiéndolo aunque el grupo trabaje
desde el teléfono; lo que cambia es la herramienta, la organización por equipos y
la manera de comprobar el resultado.

**2. Caracterización del grupo.** Cómo es el estudiantado que le tocó: cuántas
personas hay, qué experiencia previa traen con las herramientas de la asignatura,
qué tan dispares están entre sí, si hay estudiantes con alguna condición que
requiera apoyos concretos, y qué le funciona o le cuesta a ese grupo en
particular.

De aquí sale sobre todo el **andamiaje**: qué apoyo se ofrece a quien se atore,
sin resolverle la tarea. Un grupo numeroso y disparejo necesita otro reparto de
tiempos y otra forma de acompañamiento que uno pequeño y homogéneo.

**3. La problemática situada que tenga en mente.** Es el elemento detonador que
los programas piden plantear al inicio del corte, y el que da sentido a todo lo
que sigue: el caso, el negocio, la necesidad real del plantel o de la comunidad
sobre la que se va a trabajar durante el semestre.

Preguntar si ya trae una idea. Si la tiene, la planeación se construye sobre ella
y gana coherencia de inmediato. Si no la tiene, se le proponen dos o tres
opciones ancladas en su contexto para que elija, en vez de imponer una.

> **Por qué esta pregunta importa más de lo que parece.** Sin contexto, dos
> docentes con el mismo programa reciben planeaciones que se diferencian solo por
> el azar de la redacción. Con contexto, se diferencian por una razón: cada quien
> recibe algo que puede ejecutar con lo que tiene y con el grupo que tiene. Y dos
> docentes en condiciones parecidas reciben propuestas parecidas, que también es
> lo correcto.

---

## 1. Las dos estructuras, lado a lado

Esta es la tabla que gobierna todo el documento. Consultable en cualquier
momento con `python scripts/terminologia.py --equivalencias`.

| Elemento de la planeación | Programa por UAC (2023) | Programa por Asignatura (2025) |
|---|---|---|
| Unidad que se planea | **UAC** | **Asignatura** |
| Enunciado de propósito | **Propósito de UAC** | **Resultado de aprendizaje** |
| Meta del corte | **Meta de aprendizaje** | **Actividad clave de la competencia laboral básica** |
| Columna izquierda de la tabla de evidencias | **Metas específicas** | **Desarrollo de la competencia laboral básica** |
| Vínculo con el componente fundamental | **Progresión(es)** | **Propósito(s) formativo(s)** |
| Cuarta columna de transversalidad | **Conceptos Centrales (CoCEDS)** | **Habilidades para el Desarrollo Sostenible (HDS)** |
| Apartado de estrategia | **Instrumentación didáctica** | **Estrategia didáctica** |
| Momentos | Apertura / Desarrollo / Cierre | **Fase de** apertura / desarrollo / cierre |
| Carga típica | 80 h (3.º-5.º) o 32 h (6.º) | **64 h**, 4 h semanales, en todos los semestres |

### Lo que NO cambia, y traducirlo es el error inverso

No todo lo que suena a Plan 2023 está derogado. Estas piezas se conservan
idénticas en los dos modelos:

- **La competencia laboral básica**, en su redacción literal. Es la pieza
  intocable: todos los ajustes se hacen sobre los demás elementos.
- **El producto o proyecto integrador.** Es elemento vigente del Modelo 2025,
  con sus criterios de evaluación. Darlo por derogado fue un error documentado
  que contaminó tres skills y dos informes antes de corregirse.
- **La Trayectoria Ocupacional Básica (TOB).**
- **Las Habilidades para la Vida y el Trabajo (HVyT)**, con el mismo catálogo
  de doce.
- **Las evidencias de conocimiento, desempeño y producto.** Lo que el Modelo
  2025 añade es la exigencia de declarar el instrumento de cada una.
- **La nota de portada** "elaborado con base en el Programa de la Unidad de
  Aprendizaje Curricular", cuando aparece en un programa por asignatura. Es una
  referencia histórica correcta.

### Progresiones y propósitos formativos no son sinónimos

El paso de uno a otro **no es un cambio de etiqueta**. Son elementos que viven
en documentos curriculares distintos, así que la vinculación hay que **rehacerla,
no traducirla**. En una conversión real cambiaron incluso las asignaturas
vinculadas: donde el programa por UAC citaba *Cultura Digital III*, el de
asignatura tuvo que recurrir a *Pensamiento Matemático III* y a *Pensamiento
Filosófico y Humanidades III*.

> **Cultura Digital no se cursa en tercer semestre.** Solo llega a segundo
> (claves 941 y 942), y Cultura Digital III corresponde a sexto. Toda referencia
> heredada debe sustituirse. Verificar el semestre en el listado de asignaturas
> con claves, nunca en la prosa de los programas, que trae menciones
> incidentales de otros semestres.

Componente fundamental de tercer semestre: 913 Lengua y Comunicación III,
923 Inglés III, 933 Pensamiento Matemático III, 963 Ciencias Sociales III,
973 Pensamiento Filosófico y Humanidades III, 983 Ciencias Naturales,
Experimentales y Tecnología III.

---

## 2. Estructura del documento

Cinco bloques por cada corte, en este orden. El formato de referencia está en
`assets/formato-oficial-corte.docx` y un corte completo, ya aprobado, en
`assets/ejemplo-aprobado-uac.docx`.

**1. Datos generales de identificación.** Institución, docente, plantel,
currículum, TOB, unidad (UAC o asignatura), semestre, ciclo escolar, horas del
semestre y fecha.

**2. Elementos curriculares.** Competencia laboral, propósito, número y nombre
del corte con sus horas, y la meta del corte. **Todo se copia del programa con
su redacción oficial.** Aquí no se redacta nada nuevo.

**3. Desarrollos y evidencias, más transversalidad.** Un bloque por desarrollo.
Debajo, la transversalidad con el componente fundamental, las HVyT y la cuarta
columna.

> **Las columnas de evidencias son variables, y se deciden POR DESARROLLO.**
> No todos declaran las tres. Si un desarrollo trae conocimientos y productos, su
> bloque lleva dos columnas; si trae desempeño y producto, esas dos; si trae las
> tres, las tres. **Nunca una columna vacía**: se lee como descuido y es el
> defecto que más salta a la vista.
>
> La decisión es por desarrollo y no por corte porque dentro de un mismo corte
> las evidencias varían. Es además la forma en que el propio programa maqueta sus
> tablas, con un encabezado de Evidencias por cada desarrollo. Al aplicarlo, las
> celdas vacías por documento bajaron de dieciséis a dos.

**4, 5 y 6. Una tabla por fase**, apertura, desarrollo y cierre, cada una con
actividades y tiempo, recursos didácticos y tecnológicos, y su evaluación
(diagnóstica, formativa y sumativa respectivamente) con evidencia, criterios,
instrumentos y ponderación. El cierre añade la retroalimentación.

---

## 2.1 La carga horaria manda: los tiempos no se escriben a mano

**Es el error más caro que cometió la primera versión de esta skill.** Los tiempos
se redactaban junto a cada actividad, a ojo, y el conjunto de seis planeaciones
acabó asignando **526 horas donde los programas autorizaban 432**: un 22 % de más.
Nadie lo nota leyendo el documento, porque un bloque de dos o tres horas parece
razonable. Solo aparece al sumar.

**Regla:** el tiempo de cada actividad se **deriva** de la carga que el programa
declara para ese corte. La suma de apertura, desarrollo, cierre y
retroalimentación da **exactamente** esa cifra. Lo calcula
`scripts/repartir_horas.py` y lo verifica con `--verificar`.

> **La trampa del doble conteo.** Si el tiempo de la evaluación repite el de su
> actividad, el total se infla al doble. En apertura y desarrollo la evaluación
> ocurre **dentro** de la actividad y no consume tiempo propio; solo la evidencia
> sumativa del cierre se aplica aparte. Este descuido hizo creer, en una
> medición, que faltaban cien horas cuando en realidad sobraban.

## 2.2 La profundidad la fija la taxonomía de Bloom

Antes de redactar, clasificar el **verbo rector** de la meta del corte y de cada
desarrollo. El nivel determina qué tiene que hacer la actividad, no solo de qué
tiene que hablar.

| Nivel | Verbos típicos | Qué exige la actividad |
|---|---|---|
| Recordar / Comprender | identificar, reconocer, explicar, describir | Recuperar y reformular con sus propias palabras |
| Aplicar | aplicar, configurar, habilitar, gestionar, realizar | Ejecutar un procedimiento en condiciones reales |
| Analizar | analizar, comparar, examinar, planear, estructurar | Descomponer y contrastar con criterio explícito |
| Evaluar | evaluar, valorar, validar, verificar | Emitir un juicio sostenido en evidencia medida |
| Crear | diseñar, desarrollar, producir, integrar, implementar | Producir un artefacto completo y verificable |

Una actividad de nivel Crear que solo pide leer y comentar está por debajo de lo
que el programa exige, aunque el texto suene bien. Y al revés: exigir un producto
terminado donde el programa pide reconocer infla el trabajo sin fundamento.

## 2.3 Cada corte cierra con una práctica integradora

Los programas la exigen y la primera versión no la traía: el desarrollo pasaba
directo al cierre. Va como **una actividad más del desarrollo**, con su tiempo
propio, al final. **La práctica consolida, no sustituye** a las demás
actividades; un corte cuyo único respaldo es la práctica está incompleto.

Su exigencia sigue el nivel de Bloom del corte: producir el artefacto completo en
los de Crear, ejecutar el procedimiento en condiciones reales en los de Aplicar,
sostener un juicio con evidencia en los de Analizar y Evaluar.

Lo que distingue una buena práctica integradora es que **somete el trabajo a
alguien o a algo externo**: otro equipo que lo ejecuta tal como está escrito, una
persona usuaria real que lo prueba, un dispositivo distinto, el presupuesto
verdadero de la plataforma. Ahí aparece lo que el equipo daba por supuesto.

---

## 3. Cómo se redactan las actividades

Lo que distingue una planeación útil de una plantilla llena es esta parte. Aquí
sí se redacta, y el programa solo da el marco.

**Los tres momentos con su duración.** La referencia trabajada es apertura de
10 minutos, desarrollo de 60 y cierre de 20 para una sesión de 90. Para un corte
completo, los tiempos se reparten según las horas del corte.

**Para cada momento, cuatro datos:**

1. Qué hace el estudiantado, redactado como **acción observable**.
2. Qué hace la persona docente mientras tanto.
3. Recursos concretos, **incluidos los que hay que preparar antes de la clase**.
4. El andamiaje para quien se atore: qué apoyo se da **sin resolverle la tarea**.

**La problemática situada atraviesa el corte.** Se plantea en la apertura y
vuelve en el desarrollo y en el cierre. Un caso que se enuncia el primer día y no
se vuelve a mencionar es decorado. Cuidado además con el integrador **huérfano**:
anunciado solo en el cierre, sin que la apertura ni el desarrollo lo sostengan.

**Las actividades se escriben con los recursos que el plantel declaró.** Si el
grupo trabaja desde el teléfono, la actividad lo dice y organiza el trabajo en
consecuencia. Nombrar equipo que no existe vuelve la planeación inaplicable, y
quien la revisa lo detecta de inmediato.

**Decir lo que no cabe.** Si la meta no alcanza a cubrirse en el tiempo
disponible, hay que declararlo y proponer qué parte pasa a la siguiente sesión.
Ocurrió en un caso real: la meta incluía publicar la página y validar el flujo en
dos dispositivos, y no cabía en 90 minutos; se recortó el alcance y la
publicación pasó a la semana siguiente. Una planeación que no declara lo que no
cabe es una planeación que se incumple en la semana tres.

**Todas las viñetas en infinitivo.** Mezclar infinitivo con imperativo dentro de
la misma oración es un defecto frecuente.

**Las actividades permanentes** —recapitular al inicio de cada sesión, por
ejemplo— pertenecen al desarrollo, no a la apertura del curso.

**El cierre no pide tres veces lo mismo.** Tres viñetas solicitando presentar la
misma solución contravienen el criterio de eliminar actividades repetitivas.

---

## 4. Evaluación

**Los tres momentos, con cinco datos cada uno:** evidencia que se evalúa;
criterios de logro redactados de forma que dos personas distintas calificarían
igual; instrumento con el motivo de haberlo elegido; ponderación; y agentes que
participan (autoevaluación, coevaluación, heteroevaluación) con el porqué.

**Un solo instrumento por columna.** La convención es guía de observación para
el desempeño y lista de cotejo para el producto. Los criterios van debajo de la
descripción de la evidencia, **nunca dentro de la celda de instrumentos**.

**Congruencia con el programa.** Si los cortes solo declaran guía de observación
y lista de cotejo, la planeación no puede recomendar pruebas objetivas, rúbricas
y bitácoras. Es un caso real de documento que se contradice a sí mismo.

### La ponderación

- **Diagnóstica y formativa: sin peso.** Acompañan el proceso, no califican. En
  la columna se escribe **"Sin ponderación"**, no "0 %": un cero invita a leer
  que la evidencia no vale, cuando lo que ocurre es que no se califica.
- **Sumativa: sí tiene peso.** Y la suma de las evidencias sumativas de **todos
  los cortes cierra exactamente el 100 %** del semestre. Se reparte en
  proporción a la carga horaria de cada corte.

Verificar la suma antes de entregar. Un semestre que cierra en 95 % o en 105 %
es un documento que no se puede aplicar.

### El nivel más bajo de una rúbrica se redacta en positivo

Nunca "no logra", "carece de" o "no aplica". La fórmula es **"falta lograr
que…"**, que dice exactamente lo mismo y nombra el siguiente paso en vez de la
carencia. Importa porque la rúbrica se le entrega al estudiantado, no solo se
archiva.

> Falta lograr una verificación propia: la accesibilidad se afirma sin medición
> ni recorrido de teclado que la respalde.

---

## 5. Los catálogos son listas cerradas

El error más frecuente y el más difícil de ver, porque los términos inventados
suenan verosímiles. Consultables con `python scripts/terminologia.py --catalogos`.

**Hábitos (CONOCER):** organización, puntualidad, perseverancia, autoevaluación.
**Valores:** responsabilidad, respeto, honestidad, compromiso, solidaridad.
**Actitudes:** iniciativa, flexibilidad, empatía, colaboración, actitud positiva.

**Habilidades para la Vida y el Trabajo (12):** regulación de emociones,
autoconocimiento, comunicación, logro de metas, autonomía, toma de decisiones,
resolución de problemas, mentalidad de crecimiento, creatividad, empatía,
conciencia social, trabajo en equipo y colaboración.

**Habilidades para el Desarrollo Sostenible (4):** Nexo Agua-Energía-Alimento,
Servicios Ecosistémicos, Sistemas Socio-ecológicos, Economía Ecológica.

**No pertenecen a ningún catálogo, aunque lo parezcan:** ética profesional,
responsabilidad ambiental y social, trabajo colaborativo, comunicación efectiva,
innovación y mejora de procesos, uso responsable de la tecnología.

> **Matiz que evita corregir de más.** "Pensamiento crítico" es legítimo cuando
> describe el enfoque pedagógico de la Nueva Escuela Mexicana. Solo es error
> presentarlo como una de las doce HVyT. Leer el contexto antes de tacharlo.

**Regla operativa:** al nombrar HVyT o HDS en la prosa, tomar las que están
marcadas con equis en la matriz de transversalidad de ese corte. Se leen de la
tabla; no se eligen por intuición.

---

## 6. Los scripts

```bash
# 1. ¿Qué estructura tiene este programa?
python scripts/detectar_modelo.py "programa.docx"

# 2. Consultar vocabulario y catálogos
python scripts/terminologia.py --equivalencias
python scripts/terminologia.py --catalogos

# 3. Sacar las evidencias del programa (conocimientos, desempeños, productos)
python scripts/extraer_evidencias.py "programa.pdf" --asignatura --todos --json ev.json
python scripts/extraer_evidencias.py "programa.pdf" --uac --corte 1

# 4. Repartir las horas del corte y verificar que cuadren
python scripts/repartir_horas.py 30 --actividades 4 --primer-corte
python scripts/repartir_horas.py --verificar planeacion.json

# 5. Plantilla del JSON de trabajo
python scripts/generar_planeacion.py --esquema > planeacion.json

# 6. Revisar ANTES de generar (sale 1 si hay algo grave)
python scripts/validar_planeacion.py planeacion.json

# 7. Generar el Word y comprobar que Word no lo marque como dañado
python scripts/generar_planeacion.py planeacion.json "Planeacion.docx"
python ../docx-cobach/scripts/validar_docx.py "Planeacion.docx"
```

`validar_planeacion.py` revisa ocho cosas: vocabulario del modelo contrario,
catálogos cerrados, ponderaciones, cobertura de las tres fases, un instrumento
por columna, lenguaje incluyente, rúbricas redactadas en negativo y referencias
a Cultura Digital en tercer semestre. **Los GRAVE impiden entregar.**

---

## 6.1 Extraer las evidencias del PDF: lo que ya se intentó

**Esta es la parte más difícil de la skill. Costó siete intentos.** Antes de
reescribir `extraer_evidencias.py` desde cero, leer esto.

**Por qué es difícil.** Los programas oficiales no comparten maquetación. En unos
el desempeño ocupa una fila propia bajo su encabezado; en otros vive en la misma
fila del desarrollo, en columnas contiguas; en otros el encabezado se parte entre
dos páginas. Cualquier analizador afinado contra un archivo pierde datos en el
vecino, **y los pierde en silencio**. Eso es lo grave: una evidencia atribuida a
la meta equivocada no la detecta nadie al revisar el documento final.

**Lo que NO funciona, comprobado:**

- **Leer el texto plano del PDF.** Al aplanarlo las columnas se pegan y los
  conocimientos de un desarrollo terminan en el vecino, o en el corte siguiente.
- **Emparejar por índice de columna.** `pdfplumber` reconstruye un número
  distinto de columnas en cada tabla, así que el índice del encabezado no
  coincide con el del contenido. Ese error llegó a poner en la columna de
  Producto el texto de la Actividad clave y una progresión del currículum
  fundamental.

**Lo que sí funciona:** tres analizadores con supuestos distintos, y la unión de
sus resultados campo por campo. Ninguno cubre los seis programas por sí solo.

**Después de extraer, control de calidad siempre.** Un conocimiento es nominal;
un desempeño abre con verbo en tercera persona. Lo que no cumpla eso está en la
columna equivocada. El script lo reporta y **no corrige solo**: en un documento
oficial, reportar es más seguro que adivinar.

**Restos que hay que limpiar**, todos observados en programas reales:

- El **encabezado de página en versalita** se pega al final del párrafo anterior.
- La **cola de la matriz de transversalidad** se cuela al final de las celdas
  ("Componentes: fundamental y ampliado", los nombres de los ámbitos).
- La celda de **Instrumentos** captura "*Propósitos formativos" de la tabla
  vecina. Solo deben entrar los del catálogo: guía de observación, lista de
  cotejo, rúbrica, escala estimativa, cuestionario.
- Los **asteriscos** de esas capturas hacen fallar `validar_docx.py`.
- Algunas celdas arrastran **un fragmento pegado al inicio**, cola de la celda
  anterior.

**Y un aviso práctico:** Word bloquea el archivo que tiene abierto. Si la
generación falla con `PermissionError`, pedir que lo cierren; no es un error del
código.

---

## 7. Lenguaje incluyente

Se aplica en todo el documento. Formas usadas en las correcciones reales: *una
persona que lidera el proyecto*, *diseñadoras o diseñadores*, *las personas
usuarias*, *quien programa*, *el estudiantado*.

El defecto típico aparece en los roles de equipo y en las preguntas de debate,
y suele convivir con su propia contradicción: el mismo documento que dice "las
personas usuarias" en las evidencias escribe "los usuarios" en las actividades.

Cuidado con corregir de más: **"las y los estudiantes" ya es incluyente**. El
validador lo contempla, porque marcarlo enseña a ignorar sus avisos.

---

## 8. Residuos de la asignatura de origen

Cuando una planeación se construye copiando otra, sobrevive vocabulario de la
asignatura equivocada sin que se note. La fórmula "cuatro diseñadores de
soluciones informáticas" apareció intacta en programas de diseño gráfico y de
accesibilidad. La mención de "laboratorio" como espacio de trabajo es residuo de
la Trayectoria de Laboratorio de control de calidad; en informática corresponde
"sala de cómputo".

Revisar siempre que la evaluación diagnóstica y el nombre de la Trayectoria
correspondan **a esta asignatura**. Se encontró una diagnóstica sobre estructura
empresarial y organigrama dentro de un programa de programación.

---

## 9. Registro de escritura

Persona culta que domina el tema, no un manual ni un modelo de lenguaje. Sin
guion largo como inciso; usar comas, paréntesis o dos puntos. Sin comillas
angulares en la prosa que se redacta.

Evitar los tics que delatan escritura automática: simetría forzada, señalización
redundante ("es importante señalar que", "cabe destacar"), negritas dispersas en
prosa corrida, hedging defensivo, cierres que resumen lo ya leído y tabla donde
correspondía prosa.

---

## 10. Antes de entregar

- [ ] Se consiguió el programa de estudio, y si se buscó en línea, la persona
      docente confirmó que es el suyo.
- [ ] Se preguntó el contexto: condiciones del plantel, caracterización del grupo
      y problemática situada.
- [ ] Las actividades usan los recursos que el plantel declaró tener, y el
      andamiaje responde al grupo descrito.
- [ ] La problemática situada aparece en la apertura, el desarrollo y el cierre,
      no solo enunciada al principio.
- [ ] Se detectó la estructura **y se confirmó con la persona docente**.
- [ ] Competencia, propósito, meta y desarrollos están copiados con la redacción
      oficial del programa, no reescritos.
- [ ] Las etiquetas del documento corresponden al modelo confirmado.
- [ ] No queda vocabulario del modelo contrario **dentro de la prosa**, no solo
      en las etiquetas.
- [ ] Las tres fases tienen actividades propias y el corte cierra con su
      práctica integradora.
- [ ] **Las horas suman exactamente la carga que declara el programa**
      (`repartir_horas.py --verificar`), y el tiempo de la evaluación no repite
      el de su actividad.
- [ ] Cada bloque de evidencias lleva solo las columnas que ese desarrollo
      declara. Ninguna columna vacía.
- [ ] La profundidad de las actividades corresponde al nivel de Bloom del verbo
      rector del corte.
- [ ] Un solo instrumento por columna, y son los que el programa declara.
- [ ] Diagnóstica y formativa dicen "Sin ponderación"; las sumativas de todos los
      cortes cierran exactamente el 100 %.
- [ ] Se preguntaron nombre, plantel y ciclo; la fecha es la del sistema y el
      nombre docente figura como autor del archivo.
- [ ] El nivel más bajo de cada rúbrica está redactado en positivo.
- [ ] Las habilidades nombradas existen en el catálogo y están marcadas en la
      matriz de transversalidad del corte.
- [ ] No hay residuos de la asignatura de origen ni de otra Trayectoria.
- [ ] Lenguaje incluyente aplicado, sin corregir lo que ya era incluyente.
- [ ] `validar_planeacion.py` sale sin GRAVE.
- [ ] `validar_docx.py` sale sin problemas.

---

## Lo que esta skill NO hace

- **No elabora ni migra el programa de estudio.** Para eso están
  `elaboracion-programas` (UAC) y `elaboracion-programas-asignatura` (Modelo
  2025). Esta skill consume el programa; no lo produce.
- **No inventa metas, competencias ni evidencias.** Si el programa no las trae,
  la respuesta es señalar el hueco, no rellenarlo.
- **No decide el modelo por su cuenta.** Detecta y pregunta.
- **No genera el instrumento de evaluación completo** con todos sus
  descriptores como documento aparte. La planeación declara el instrumento y sus
  criterios; desarrollarlo a fondo es trabajo de
  `evaluacion-competencia-tob`.

---

## Procedencia

El formato y el ejemplo aprobado los proporcionó el Mtro. Luis Gabriel Mondragón
Torres. Los criterios de migración provienen del *Informe de ajustes. Migración
de UAC a asignatura* (agosto de 2026), levantado al convertir tres programas de
tercer semestre, incluido en `assets/`. Los criterios de secuencia didáctica y
de redacción de rúbricas provienen del Hack #11 de la sesión 5 del curso de
e-commerce, que vale 30 % de la calificación y reúne la planeación de los tres
cortes con su instrumento de evaluación.
