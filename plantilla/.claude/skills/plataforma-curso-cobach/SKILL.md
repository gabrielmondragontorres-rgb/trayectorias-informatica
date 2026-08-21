---
name: plataforma-curso-cobach
description: |
  Plantilla reutilizable de "aula virtual" para un curso del Colegio de Bachilleres: registro
  y autorizacion manual de docentes, sesiones/modulos que el profesor titular habilita
  progresivamente y se reflejan en tiempo real, foros de discusion con reacciones (un voto
  real por persona), panel de administracion, PWA instalable, bienvenida automatica en el
  primer login, y contacto sin depender de correo saliente automatico.

  Usar cuando: "quiero un aula virtual para otra materia", "replica esta plataforma para
  otro curso COBACH", "necesito algo como el curso de e-commerce pero para [materia]",
  "arma la plataforma del curso de [materia]", "quiero hacer una plataforma LMS",
  "plataforma academica", "algo estilo Moodle", "un Moodle propio", "campus virtual",
  "plataforma educativa", "sistema de gestion del aprendizaje", "una plataforma como la
  del Mtro. Gabriel Mondragon", "plataforma para mis alumnos", "plataforma de curso".

  PREGUNTA OBLIGATORIA ANTES DE EMPEZAR: si es para el Colegio de Bachilleres o para otra
  institucion. La respuesta cambia identidad visual, nomenclatura y catalogo de sedes.
  Segunda pregunta obligatoria: como se divide el curso y como se llama cada division
  (5 sesiones, 3 cortes, N unidades...). Nunca dar por hecho que son cinco sesiones.

  Pre-requisito: proyecto Next.js + Supabase ya inicializado (skill NEW-APP).
  NO USAR para: apps que no sean "curso con personas autorizadas por quien coordina"
  (para SaaS genérico sin autorización manual, usar ADD-LOGIN en su lugar).
  Esta plantilla SI usa Supabase Auth: la autenticación propia con contraseña en texto
  plano que tuvo el proyecto de origen se eliminó el 14 de agosto de 2026 por ser
  explotable. No volver a ese modelo.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(npm *), Bash(npx tsc *)
metadata:
  author: saas-factory
  version: "2.0"
---

# Plataforma de Curso COBACH — Plantilla de Aula Virtual

---

## 0. Punto de Partida (Pregunta Obligatoria)

Antes de escribir una sola línea, preguntar:

> **¿La plataforma es para (a) el Colegio de Bachilleres, o (b) otra institución?**

No continuar sin esa respuesta. Determina la identidad visual, la nomenclatura y qué partes
del modelo institucional se conservan.

| | (a) Colegio de Bachilleres | (b) Otra institución |
|---|---|---|
| Color | Verde institucional `#006837`, acento `#00A859` | El de la institución; si no lo tiene, preguntar antes de elegir |
| Tipografía | Noto Sans | La de la institución, o Noto Sans por omisión |
| Mascota | El lobo, con la regla de vestimenta del `USER_DNA.md` | Ninguna, salvo que la institución tenga la suya |
| Catálogo de planteles | Tabla `planteles_cobach` con los planteles reales | Lista de sedes o campus que dé la institución, o campo libre |
| Nomenclatura | UAC, TOB, corte, meta de aprendizaje, evidencia | Términos genéricos: asignatura, unidad, objetivo, entregable |
| Rol que autoriza | Profesor titular | Coordinación o quien la institución designe |

**Segunda pregunta obligatoria, en los dos casos:**

> **¿Cómo se divide el curso, y cómo se llama cada división?**

El profesorado decide la estructura. La plantilla no impone cinco sesiones.

---

## 0.1 La unidad estructural es configurable

El curso de origen tenía **5 sesiones**, pero eso es un dato de ese curso, no de la
plantilla. Alguien que imparte una UAC dividida en **3 cortes** debe poder montar tres
bloques y nada más.

El modelo de datos **ya es genérico** y no hay que tocarlo:

```sql
sesiones_config (id INT primary key, titulo TEXT not null, habilitada BOOLEAN default false)
```

Nada ahí dice «sesión». Se llenan tantas filas como bloques tenga el curso, con el título
que corresponda:

```sql
-- Curso de formación en 5 sesiones
insert into public.sesiones_config (id, titulo, habilitada) values
  (1, 'Sesión 1. Ecosistema y estrategia de conversión', true),
  (2, 'Sesión 2. Construcción de la landing page', false);

-- UAC semestral en 3 cortes
insert into public.sesiones_config (id, titulo, habilitada) values
  (1, 'Corte 1. Desarrolla una landing page accesible', true),
  (2, 'Corte 2. Implementa un sistema de tráfico digital', false),
  (3, 'Corte 3. Optimiza la conversión mediante mensajería', false);
```

**Lo que sí está amarrado es el código, y hay que resolverlo al replicar.** El proyecto de
origen tiene carpetas `src/features/sesion1` … `sesion5` escritas a mano, y
`hacks_config.sesion_id` apunta a ellas. Al replicar:

1. Preguntar cuántos bloques hay y cómo se llaman.
2. Crear **solo esos** módulos, con el nombre que el profesorado eligió.
3. Renombrar en la interfaz la palabra «sesión» por la que corresponda —corte, unidad,
   módulo, bloque—. En la base de datos la tabla puede seguir llamándose
   `sesiones_config`; lo que ve la persona usuaria es el `titulo`.

> **Regla:** nunca dar por hecho que son cinco sesiones. Es la configuración de un curso
> concreto, no la forma de la plantilla.

> Esta skill no es teoria: documenta la arquitectura real y ya probada en producción de un
> aula virtual COBACH completa (curso "E-commerce incluyente: Hacks de IA y accesibilidad"),
> incluyendo los bugs reales que salieron y como quedaron corregidos, para que la siguiente
> materia que se arme con este patrón no los repita.

---

## Qué produce esta plantilla

Un aula virtual donde:

1. **Quien coordina** —el profesor titular— es la única persona que habilita unidades,
   autoriza el acceso y califica.
2. **El profesorado** se registra, queda `pendiente_aprobacion` y solo entra cuando lo
   autorizan. Sin depender de ningún correo de confirmación automático.
3. El contenido se divide en **unidades habilitables progresivamente**, y el cambio se ve
   **en tiempo real** en el dispositivo de quien ya tenga la aplicación abierta.
4. Hay **foros de discusión** con reacciones que cuentan un voto real por persona.
5. Cada unidad puede tener **actividades evaluables con lista de cotejo**, con calificación
   asistida por IA, umbral de acreditación, reentrega y generación automática del documento
   de evidencia.
6. Quien olvida su contraseña la **recupera con autorización de quien coordina**, sin correo
   saliente.
7. La aplicación es instalable como **PWA** y puede mandar **notificaciones push**.
8. Trae **menú de accesibilidad** flotante (ver skill `widget-accesibilidad`).
9. Nadie necesita revisar su correo para enterarse de nada: la autorización se confirma con
   un **mensaje de bienvenida dentro de la aplicación** en el primer ingreso real.

---

## Arquitectura de datos

> **El esquema completo está en `assets/schema.sql`.** Es un solo archivo, se corre entero
> en el editor SQL de Supabase sobre un proyecto nuevo, y **nace con los permisos cerrados**.
> No lo transcribas ni lo parafrasees: cópialo.

Once tablas. Lo que hay que saber de cada una:

| Tabla | Para qué | Detalle que importa |
|---|---|---|
| `planteles_cobach` | Catálogo de sedes | Única tabla de lectura pública: el registro la necesita antes de iniciar sesión. Cámbiala o bórrala si no es COBACH |
| `profiles` | Quién es cada persona y en qué estado está | **No tiene columna de contraseña.** Su `id` apunta a `auth.users`; las credenciales las cifra Supabase Auth |
| `bitacora_accesos` | Registro de entradas | Solo se escribe desde `registrar_acceso()` |
| `sesiones_config` | Las unidades del curso | `(id, titulo, habilitada)`. Nada dice «sesión»: aquí caben 5 sesiones o 3 cortes |
| `entregables` | Las entregas del profesorado | El `id` es TEXT, no UUID: lo genera el cliente como `ENT-<marca>` |
| `hacks_config` | Actividades evaluables y sus listas de cotejo | `criterios_cotejo` es jsonb; las ponderaciones deben sumar 100 |
| `foro_posts` | Temas del foro | El `id` es TEXT (`post-<marca>`); las respuestas viven en una columna jsonb |
| `foro_reacciones` | Un voto por persona | **Clave primaria compuesta** de cuatro columnas. Es lo que impide votar dos veces |
| `solicitudes_password` | Recuperación autorizada | El código se guarda con hash, caduca y cuenta intentos |
| `push_subscriptions`, `notifications` | Notificaciones push | Opcionales: omítelas si la réplica no las va a usar |

### Ocho funciones en la base, y por qué están ahí

La lógica sensible no vive en el navegador. Cada función existe por una razón concreta:

- **`es_admin()` y `es_usuario_activo()`** — resuelven el rol en la base. Son
  `security definer` a propósito: si consultaran `profiles` con los permisos de quien llama,
  las políticas de `profiles` se llamarían a sí mismas y Postgres abortaría por recursión.
- **`handle_new_user()`** — dispara con el alta en `auth.users` y crea el perfil siempre como
  `pendiente_aprobacion`. Registrarse nunca da acceso por sí solo.
- **`correo_de_usuario()`** — permite entrar con nombre de usuario y no solo con correo.
  Supabase Auth solo conoce correos, así que hay que traducir antes de iniciar sesión.
- **`registrar_acceso()`** — actualiza la bitácora sin dar permiso de UPDATE sobre `profiles`.
  Si lo diera, cualquiera podría escribirse `rol = 'admin'` en su propia fila.
- **`responder_foro()`** — deja responder sin poder reescribir el tema. Como las respuestas
  viven dentro del jsonb, un UPDATE normal permitiría cambiar también título y contenido.
- **`toggle_reaccion_foro()`** — pone y quita reacciones contando en la base.
- **Las de recuperación de contraseña** — ver el flujo 6.

---
## Flujo 1: Registro → Autorización (sin correo automático)

1. `RegistroForm` inserta en `profiles` con `estado: 'pendiente_aprobacion'`.
2. El admin ve la solicitud en su panel (`obtenerSolicitudesSupabase`, filtra
   `estado = 'pendiente_aprobacion'`) y hace clic en "Autorizar".
3. `autorizarUsuarioSupabase(id)` actualiza `estado: 'activo'`.
4. **Nada se envía por correo.** El docente ve el resultado la primera vez que hace login
   real (ver Flujo 3).

**Bug real ya corregido — no lo repitas:** si el proyecto también mantiene un respaldo local
(Zustand/localStorage) de las solicitudes "por si Supabase falla", el botón de autorizar
puede terminar operando sobre un id que solo existe en ese respaldo local (no en Supabase),
autorizando algo que no existe realmente mientras el registro real sigue pendiente. Si vas a
tener un respaldo local, el flujo de autorización debe **resolver primero el id real por
correo contra Supabase** antes de actuar, o mejor aún: no tener respaldo local en absoluto
para este flujo (Supabase es la única fuente de verdad — ver `CLAUDE.md`).

---

## Flujo 2: Sesiones habilitables en tiempo real

- El admin llama `actualizarSesionConfigSupabase(id, habilitada)`.
- **Cualquier componente que muestre las sesiones al docente debe, al montar, pedir el
  estado real con `obtenerSesionesConfigSupabase()`** — nunca asumir que el valor local
  (localStorage/estado inicial) ya está actualizado, porque para un docente que nunca visitó
  el panel de admin, ese valor local nunca se sincronizó.
- Además, suscribirse a `postgres_changes` sobre `sesiones_config` (patrón completo en
  `supabase/SKILL.md`) para que el cambio se vea sin recargar si el docente ya tiene la app
  abierta cuando el admin la habilita.

---

## Flujo 3: Bienvenida automática en el primer login (reemplaza el correo)

En vez de un correo de confirmación (poco confiable sin dominio propio — ver
`add-emails/SKILL.md`), la propia función de login detecta si es la primera conexión real:

```typescript
// profile.total_conexiones arranca en 0 al registrarse, y la autorizacion del admin
// NO lo modifica — solo un login real lo incrementa. Por eso "== 1 despues de incrementar"
// significa, de forma confiable, "esta es la primera vez que esta persona entra de verdad".
const nuevosIngresos = (profile.total_conexiones || 0) + 1
// ...actualizar total_conexiones = nuevosIngresos...
return { success: true, primeraVez: nuevosIngresos === 1, user: {...} }
```

El componente de login, si `primeraVez` es verdadero y el rol no es admin, dispara un modal
de bienvenida (firmado por el profesor titular) dentro de la propia sesión — cero dependencia
de correo, WhatsApp, o cualquier canal externo.

---

## Flujo 4: Foro con reacciones — un voto real por persona

**El conteo NO se hace en el navegador.** Se llama a la función `toggle_reaccion_foro()` de
la base y ella decide:

```typescript
const { data: nuevoTotal } = await supabase.rpc('toggle_reaccion_foro', {
  p_post_id: postId,
  p_tipo: tipo,                    // 'destacados' | 'ideas' | 'meGusta'
  p_target: respuestaId ?? '__post__',
})
```

**Por qué así, y no en el cliente.** La primera versión leía el contador, le sumaba uno y lo
volvía a escribir. Con dos personas reaccionando a la vez, una sobrescribía a la otra y el
número quedaba mal. Peor: si la consulta de «¿ya reaccionó?» fallaba, el código asumía que no,
y el contador solo subía, sin poder bajar nunca.

Con la función en la base los dos problemas desaparecen: la clave primaria compuesta de
`foro_reacciones` impide el voto doble, y el incremento ocurre en una sola sentencia.

**Las reacciones deben estar en el tema y en cada respuesta.** Si solo el tema las tiene, y
solo quien coordina crea temas, en la práctica únicamente se puede reaccionar al contenido de
quien coordina y nunca a las aportaciones del profesorado. De ahí el parámetro `p_target`.

---

## Flujo 5: Contacto sin correo saliente

Ver `add-emails/SKILL.md`, sección "Sin dominio propio verificado". El componente de
referencia es un botón flotante fijo que abre `mail.google.com` con destinatario y asunto
precargados — cero backend, cero dependencia de un dominio verificado.

---

## Flujo 6: Recuperación de contraseña autorizada

Sin correo saliente, igual que el registro. Tres pasos:

1. La persona pide restablecer desde el formulario. Se crea una fila en
   `solicitudes_password` con estado `pendiente`.
2. Quien coordina la ve en su panel y la autoriza. Ahí se genera un código de un solo uso:
   **se guarda con hash, nunca en claro**, con fecha de caducidad. El código se entrega por
   el canal que el grupo ya usa.
3. La persona escribe el código y su contraseña nueva. La ruta valida hash, caducidad e
   intentos, y actualiza la credencial en `auth.users` con la llave de servicio.

Rutas: `/api/auth/recuperacion` (solicitar), `/api/auth/recuperacion/autorizar`,
`/api/auth/recuperacion/completar`.

**Tres cosas que no se pueden omitir:** el código va con hash y con caducidad; la columna
`intentos` existe para frenar la prueba por fuerza bruta; y la política de RLS deja ver la
tabla **solo** a quien coordina, porque contiene los correos de todo el mundo.

---

## Flujo 7: Actividades evaluables con lista de cotejo

Es el subsistema más grande y el que más valor añade. `hacks_config` guarda, por actividad,
su peso en la calificación, el umbral de acreditación y el arreglo de criterios.

El ciclo completo:

1. La persona llena la ficha de la actividad y adjunta evidencia. Si no adjunta archivo, la
   plataforma **genera el documento de evidencia** con lo capturado.
2. El archivo va al bucket de Storage; la fila va a `entregables` con su `intento`.
3. `/api/ai/calificar-entrega` manda a la IA la entrega y los criterios, y pide una
   respuesta estructurada: criterio por criterio, cumplido o no, con justificación.
4. El resultado se guarda en `calificacion_ia_json` con estado `pendiente`. **La IA no
   califica sola:** quien coordina aprueba, edita o descarta.
5. Si el porcentaje queda por debajo del umbral, la entrega se marca para reentrega y el
   siguiente intento incrementa `intento`.

**Reglas al configurar las rúbricas.** Las ponderaciones de todas las actividades deben sumar
100, y dentro de cada actividad la suma de sus criterios debe coincidir con su peso. La
consulta de comprobación está al final de `assets/schema.sql`.

**Cuidado con la ruta de calificación.** Debe exigir sesión y rol de quien coordina. En el
proyecto de origen quedó abierta un tiempo y cualquiera que conociera la dirección podía
consumir la cuota diaria de la API de IA.

---

## Flujo 8: Notificaciones y materiales protegidos  (opcional)

**Notificaciones push:** `push_subscriptions` guarda el endpoint de cada dispositivo y
`notifications` el historial. Ver la skill `add-mobile` para las llaves VAPID y las
particularidades de iOS.

**Materiales protegidos:** los archivos del curso no se sirven desde `public/`, porque ahí
cualquiera con la dirección los descarga. Pasan por una ruta que verifica la sesión antes de
entregar el archivo (`/api/materiales/[...ruta]` en el proyecto de origen).

**Menú de accesibilidad:** ver la skill `widget-accesibilidad`. Se monta **una sola vez en el
layout raíz**, nunca por página.

---

## Seguridad: lo que se rompió de verdad y no debe repetirse

Todo esto ocurrió en el proyecto de origen y ya está corregido en `assets/schema.sql`. Se
documenta porque son errores fáciles de repetir y difíciles de notar.

| Qué pasó | Por qué es grave | Cómo queda resuelto |
|---|---|---|
| Las contraseñas se guardaban en texto plano en `profiles.password` | Con la llave pública, que viaja dentro del JavaScript de la página, cualquiera leía la tabla completa | La columna no existe. Las credenciales viven cifradas en `auth.users` |
| Las 12 tablas tenían políticas `using (true)` | La base estaba abierta a internet. Se comprobó creando y borrando un tema del foro sin sesión | El esquema nace con políticas reales por tabla y por operación |
| La sesión vivía en `localStorage` sin firma | Escribir `{"rol":"admin"}` en el navegador daba acceso de administrador | El rol lo resuelve la base con `auth.uid()` y lo verifica RLS en cada operación |
| El bucket de evidencias quedó público | Con la llave pública y sin sesión se podían **listar y descargar** las entregas del profesorado | El bucket nace privado y con políticas. El código debe usar `createSignedUrl()`, no `getPublicUrl()` |
| Las rutas de IA no pedían sesión | Cualquiera podía agotar la cuota diaria de la API | Exigen sesión, y la de calificar además exige rol de quien coordina |

**El detalle que hace que esto se escape:** un barrido de políticas con
`where schemaname = 'public'` **no toca las de Storage**, que viven en el esquema `storage`.
Por eso el bucket siguió abierto después de cerrar todo lo demás. En `assets/schema.sql` se
barren los dos esquemas.

---

## PWA

- `public/manifest.json` con íconos 72/96/128/144/192/512.
- `public/sw.js` **sin fetch handler** (comentario obligatorio en el archivo explicando por
  qué: un fetch handler mal hecho rompe Safari/iOS de formas difíciles de diagnosticar). Solo
  maneja `push`, `notificationclick`, y limpieza de cachés viejas en `activate`.
- El ícono de la PWA se cachea en el dispositivo **al momento de instalar** — si se cambia
  después, quien ya instaló no lo ve actualizado solo, tiene que desinstalar y reinstalar.

---

## Panel de administración — pestañas típicas

1. Autorización de registro (solicitudes pendientes).
2. Usuarios autorizados y bitácora.
3. Habilitación de sesiones.
4. Entregables/evidencias (si el curso las requiere).
5. Moderación de foros.

---

## Checklist antes de dar por terminada una réplica de esta plantilla

- [ ] `obtenerSesionesConfigSupabase()` se llama al montar la vista del docente, no solo en
      el panel de admin.
- [ ] Las tablas con necesidad de tiempo real están en la publicación `supabase_realtime`
      (verificado con una prueba real de insert/listen, no asumido).
- [ ] El flujo de autorización resuelve el id real por correo si existe cualquier respaldo
      local con ids no-UUID.
- [ ] Las reacciones del foro existen también en las respuestas, no solo en el tema.
- [ ] No hay ningún envío de correo automático sin que el usuario haya confirmado que tiene
      dominio propio verificado.
### Antes de empezar
- [ ] Se preguntó si es para el Colegio de Bachilleres o para otra institución.
- [ ] Se preguntó en cuántas unidades se divide el curso y cómo se llama cada una.
- [ ] Se crearon **solo** esos módulos, con el nombre elegido, y la interfaz no dice
      «sesión» si el curso habla de cortes.

### Base de datos
- [ ] Se corrió `assets/schema.sql` **completo**, no por partes.
- [ ] Las tres comprobaciones del final del archivo salen bien: ninguna tabla sin RLS,
      ninguna política abierta a anónimos salvo el catálogo de sedes, y las ponderaciones
      suman 100.
- [ ] La cuenta que coordina se creó desde el panel de Authentication y se promovió con el
      `update`. Hay una y solo una con rol admin.
- [ ] **Ninguna contraseña aparece en ningún archivo del repositorio.**

### Seguridad, comprobada y no supuesta
- [ ] Con la llave pública y sin sesión, `profiles` y `foro_posts` devuelven vacío.
- [ ] Con la llave pública y sin sesión, **listar el bucket de evidencias falla**.
- [ ] Escribir un rol falso en el almacenamiento del navegador y recargar **no** da acceso.
- [ ] Las rutas de IA rechazan las peticiones sin sesión.

### Funcionamiento
- [ ] `obtenerSesionesConfigSupabase()` se llama al montar la vista del profesorado, no solo
      en el panel de quien coordina.
- [ ] Las tablas con tiempo real están en la publicación `supabase_realtime`, verificado con
      una prueba real de insert y escucha, no asumido.
- [ ] El flujo de autorización resuelve el id real por correo si existe cualquier respaldo
      local con ids que no sean UUID.
- [ ] Las reacciones del foro existen también en las respuestas, no solo en el tema.
- [ ] El menú de accesibilidad está montado **una sola vez en el layout raíz**.
- [ ] No hay ningún envío de correo automático sin que la institución tenga dominio propio
      verificado.
- [ ] `npx tsc --noEmit` y `npm run build` limpios antes de considerar el flujo terminado.

---

## Lo que esta skill NO trae

Para que nadie lo dé por hecho:

- **El contenido pedagógico.** Los módulos de cada unidad se construyen aparte; la plantilla
  da la estructura, no las actividades.
- **El tablero NOVA** del curso de origen, por ser específico de esa materia.
- **Las llaves.** Supabase, la API de IA y las VAPID de notificaciones las pone quien
  despliega.
- **La identidad visual completa.** El apartado 0 dice qué cambia; los archivos de diseño
  los aporta la institución.
