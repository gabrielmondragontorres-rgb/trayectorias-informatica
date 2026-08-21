-- ============================================================================
-- AULA VIRTUAL — ESQUEMA CONSOLIDADO Y SEGURO
--
-- Un solo archivo. Se corre entero, de arriba abajo, en el editor SQL de
-- Supabase, sobre un proyecto nuevo y vacío. Es idempotente: volver a correrlo
-- no rompe nada.
--
-- POR QUÉ ESTÁ CONSOLIDADO
-- El proyecto de origen tenía un schema.sql inicial con políticas
-- `using (true)` y cinco migraciones posteriores que las cerraban. Quien corría
-- solo la primera se quedaba con la base de datos abierta a internet, porque la
-- llave "anon" viaja dentro del JavaScript que descarga cualquier visitante.
-- Aquí no existe esa ventana: nace cerrado.
--
-- QUÉ NO TRAE, A PROPÓSITO
--   · Ninguna contraseña. Las credenciales viven cifradas en auth.users.
--   · Ninguna persona usuaria de ejemplo. El administrador se crea al final,
--     con el procedimiento del apartado 12.
--   · Las tablas foro_discusiones y foro_respuestas, de un diseño anterior que
--     la aplicación ya no usa.
--
-- ANTES DE CORRER: revisa el apartado 1 (catálogo de sedes) y el 5 (unidades
-- del curso). Son las dos cosas que cambian en cada institución.
-- ============================================================================


-- ============================================================================
-- 1. CATÁLOGO DE SEDES
--
-- Lo consulta el formulario de registro ANTES de iniciar sesión, así que es la
-- única tabla de lectura pública. No contiene datos personales.
--
-- COBACH: los 20 planteles, ya listados abajo.
-- Otra institución: sustituye la lista por sus sedes, o borra la tabla entera
-- y deja el campo `plantel` de profiles como texto libre.
-- ============================================================================
create table if not exists public.planteles_cobach (
  id     int primary key,
  nombre text not null unique
);

alter table public.planteles_cobach enable row level security;

insert into public.planteles_cobach (id, nombre) values
  (1,  'Plantel 1 El Rosario'),
  (2,  'Plantel 2 Cien Metros "Elisa Acuña Rossetti"'),
  (3,  'Plantel 3 Iztacalco'),
  (4,  'Plantel 4 Culhuacán "Lázaro Cárdenas"'),
  (5,  'Plantel 5 Satélite'),
  (6,  'Plantel 6 Vicente Guerrero'),
  (7,  'Plantel 7 Iztapalapa'),
  (8,  'Plantel 8 Cuajimalpa'),
  (9,  'Plantel 9 Aragón'),
  (10, 'Plantel 10 Aeropuerto'),
  (11, 'Plantel 11 Nueva Atzacoalco'),
  (12, 'Plantel 12 Nezahualcóyotl'),
  (13, 'Plantel 13 Xochimilco-Tepepan "Quirino Mendoza y Cortés"'),
  (14, 'Plantel 14 Milpa Alta "Fidencio Villanueva Rojas"'),
  (15, 'Plantel 15 Contreras'),
  (16, 'Plantel 16 Tláhuac "Manuel Chavarría Chavarría"'),
  (17, 'Plantel 17 Huayamilpas-Pedregal'),
  (18, 'Plantel 18 Tlilhuaca-Azcapotzalco'),
  (19, 'Plantel 19 Ecatepec'),
  (20, 'Plantel 20 Del Valle "Matías Romero"')
on conflict (id) do update set nombre = excluded.nombre;


-- ============================================================================
-- 2. PERFILES
--
-- NO hay columna `password`. Las credenciales las guarda Supabase Auth,
-- cifradas, en auth.users. El perfil no puede existir sin cuenta detrás.
--
-- El perfil nace SIEMPRE como 'pendiente_aprobacion': registrarse no da acceso,
-- hace falta la autorización manual de quien coordina.
-- ============================================================================
create table if not exists public.profiles (
  id               uuid primary key references auth.users (id) on delete cascade,
  usuario          text unique,
  nombre_completo  text not null,
  email            text not null unique,
  plantel          text not null,
  rol              text not null default 'profesor' check (rol in ('admin', 'profesor')),
  estado           text not null default 'pendiente_aprobacion'
                     check (estado in ('pendiente_aprobacion', 'activo', 'bloqueado')),
  fecha_registro   timestamptz default now(),
  ultimo_acceso    timestamptz default now(),
  total_conexiones int  default 0,
  ultima_actividad text default 'Registro en plataforma',
  created_at       timestamptz default now()
);

alter table public.profiles enable row level security;


-- ============================================================================
-- 3. FUNCIONES DE AUTORIZACIÓN
--
-- Son SECURITY DEFINER a propósito: si consultaran profiles con los permisos de
-- quien llama, las políticas de profiles se llamarían a sí mismas y Postgres
-- abortaría por recursión infinita.
-- ============================================================================
create or replace function public.es_admin()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles where id = auth.uid() and rol = 'admin');
$$;

create or replace function public.es_usuario_activo()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles where id = auth.uid() and estado = 'activo');
$$;

grant execute on function public.es_admin() to authenticated;
grant execute on function public.es_usuario_activo() to authenticated;

-- Alta automática del perfil al registrarse.
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (
    id, usuario, nombre_completo, email, plantel, rol, estado,
    total_conexiones, ultima_actividad
  )
  values (
    new.id,
    split_part(new.email, '@', 1),
    coalesce(new.raw_user_meta_data ->> 'nombre_completo', split_part(new.email, '@', 1)),
    lower(new.email),
    coalesce(new.raw_user_meta_data ->> 'plantel', 'Sin asignar'),
    'profesor',
    'pendiente_aprobacion',
    0,
    'Solicitud de registro enviada'
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- Permite entrar con nombre de usuario y no solo con correo. Supabase Auth
-- únicamente conoce correos, así que hay que traducir uno al otro ANTES de
-- iniciar sesión, cuando todavía no hay permiso para leer profiles.
create or replace function public.correo_de_usuario(p_usuario text)
returns text language sql stable security definer set search_path = public as $$
  select email from public.profiles
   where lower(usuario) = lower(btrim(p_usuario))
      or lower(email)   = lower(btrim(p_usuario))
   limit 1;
$$;

grant execute on function public.correo_de_usuario(text) to anon, authenticated;


-- ============================================================================
-- 4. BITÁCORA DE ACCESOS
-- ============================================================================
create table if not exists public.bitacora_accesos (
  id             uuid primary key default gen_random_uuid(),
  usuario_id     uuid references public.profiles (id) on delete cascade,
  usuario        text not null,
  email          text not null,
  plantel        text not null,
  fecha_conexion timestamptz default now(),
  accion         text not null
);

alter table public.bitacora_accesos enable row level security;

-- Existe para NO dar permiso de UPDATE sobre profiles a cada persona: si lo
-- tuvieran, podrían escribirse rol = 'admin' a sí mismas. Aquí solo se tocan
-- las tres columnas de bitácora. Devuelve el total de conexiones, que sirve
-- para saber si es el primer ingreso y mostrar la bienvenida.
create or replace function public.registrar_acceso()
returns integer language plpgsql security definer set search_path = public as $$
declare v_total integer;
begin
  update public.profiles
     set ultimo_acceso    = now(),
         total_conexiones = coalesce(total_conexiones, 0) + 1,
         ultima_actividad = 'Inicio de sesión en Aula Virtual'
   where id = auth.uid()
  returning total_conexiones into v_total;

  if v_total is null then return 0; end if;

  insert into public.bitacora_accesos (usuario_id, usuario, email, plantel, accion)
  select id, usuario, email, plantel, 'Inicio de sesión exitoso'
    from public.profiles where id = auth.uid();

  return v_total;
end;
$$;

grant execute on function public.registrar_acceso() to authenticated;


-- ============================================================================
-- 5. UNIDADES DEL CURSO  ← AJUSTA ESTO
--
-- Nada aquí dice "sesión". La tabla guarda las divisiones del curso, se llamen
-- como se llamen, y `habilitada` es lo que quien coordina abre progresivamente.
-- Pon tantas filas como bloques tenga el curso.
-- ============================================================================
create table if not exists public.sesiones_config (
  id             int primary key,
  titulo         text not null,
  habilitada     boolean default false,
  fecha_apertura timestamptz
);

alter table public.sesiones_config enable row level security;

-- Ejemplo A — curso de formación en 5 sesiones (solo la primera abierta):
insert into public.sesiones_config (id, titulo, habilitada) values
  (1, 'Sesión 1. Título de la primera sesión', true),
  (2, 'Sesión 2. Título de la segunda sesión', false),
  (3, 'Sesión 3. Título de la tercera sesión', false),
  (4, 'Sesión 4. Título de la cuarta sesión', false),
  (5, 'Sesión 5. Título de la quinta sesión', false)
on conflict (id) do nothing;

-- Ejemplo B — UAC semestral en 3 cortes. Si usas este, borra el bloque de
-- arriba antes de correr el archivo:
--
-- insert into public.sesiones_config (id, titulo, habilitada) values
--   (1, 'Corte 1. Nombre del primer corte',  true),
--   (2, 'Corte 2. Nombre del segundo corte', false),
--   (3, 'Corte 3. Nombre del tercer corte',  false)
-- on conflict (id) do nothing;


-- ============================================================================
-- 6. ENTREGAS Y EVIDENCIAS
--
-- El id es TEXT, no UUID: lo genera el cliente con el formato 'ENT-<marca>'.
-- En el proyecto de origen esta tabla se creó primero con UUID y las entregas
-- fallaban en silencio, quedándose solo en el navegador. Aquí ya nace bien.
-- ============================================================================
create table if not exists public.entregables (
  id                       text primary key,
  sesion_id                int  not null,
  hack_id                  int,
  usuario_nombre           text not null,
  usuario_email            text not null,
  plantel                  text not null,
  actividad_titulo         text not null,
  empresa_nombre           text,
  equipo_nombre            text,
  nombre_evidencia_oficial text,
  archivo_nombre           text not null,
  archivo_tamano           text,
  archivo_tipo             text,
  archivo_base64           text,
  archivo_storage_path     text,
  datos_json               text,
  comentario               text,
  estado                   text default 'Pendiente'
                             check (estado in ('Pendiente', 'Revisado', 'Necesita revisión')),
  calificacion             text,
  retroalimentacion        text,
  intento                  int  default 1,
  calificacion_pct         numeric,
  calificacion_numerica    numeric,
  calificacion_ia_json     jsonb,
  calificacion_ia_estado   text check (calificacion_ia_estado in
                             ('pendiente', 'aprobada', 'editada', 'descartada')),
  necesita_revision        boolean default false,
  fecha_envio              text not null,
  created_at               timestamptz default now()
);

alter table public.entregables enable row level security;

create index if not exists idx_entregables_sesion_hack on public.entregables (sesion_id, hack_id);
create index if not exists idx_entregables_usuario     on public.entregables (usuario_email);


-- ============================================================================
-- 7. ACTIVIDADES EVALUABLES Y SUS LISTAS DE COTEJO
--
-- `criterios_cotejo` es un arreglo de objetos:
--   [{ "id": 1, "descripcion": "...", "ponderacion_pct": 2 }, ...]
--
-- Dos reglas que conviene respetar:
--   · La suma de `ponderacion_pct` de todas las actividades debe dar 100.
--   · Dentro de cada actividad, la suma de sus criterios debe coincidir con la
--     `ponderacion_pct` de esa actividad.
-- La consulta de comprobación está al final del archivo.
-- ============================================================================
create table if not exists public.hacks_config (
  id                    int primary key,
  sesion_id             int     not null,
  titulo                text    not null,
  ponderacion_pct       numeric not null default 0,
  umbral_aprobacion_pct numeric not null default 70,
  criterios_cotejo      jsonb   not null default '[]'::jsonb
);

alter table public.hacks_config enable row level security;

-- Ejemplo de una actividad. Repite el patrón para las que tenga el curso.
insert into public.hacks_config
  (id, sesion_id, titulo, ponderacion_pct, umbral_aprobacion_pct, criterios_cotejo)
values (
  1, 1, 'Actividad 1 — título de la actividad', 10, 70,
  $$[
    {"id":1,"descripcion":"Primer criterio observable.","ponderacion_pct":4},
    {"id":2,"descripcion":"Segundo criterio observable.","ponderacion_pct":3},
    {"id":3,"descripcion":"Documenta el uso de IA: el prompt y qué ajustó el equipo.","ponderacion_pct":3}
  ]$$::jsonb
)
on conflict (id) do nothing;


-- ============================================================================
-- 8. FOROS
--
-- Un voto real por persona. El conteo se hace en la base y no en el navegador:
-- antes el cliente leía el contador, le sumaba uno y lo reescribía, así que con
-- dos personas votando a la vez una sobrescribía a la otra.
-- ============================================================================
create table if not exists public.foro_posts (
  id             text primary key,          -- 'post-<marca>', lo genera el cliente
  foro_id        int  default 1,
  autor          text not null,
  plantel        text not null,
  titulo         text not null,
  contenido      text not null,
  respuestas     jsonb default '[]'::jsonb,
  destacados     int  default 0,
  ideas          int  default 0,
  megusta        int  default 0,
  fijado         boolean default false,
  fecha_creacion timestamptz default now()
);

alter table public.foro_posts enable row level security;

-- Esta tabla es la que impide votar dos veces. En el proyecto de origen nunca
-- llegó a existir en un archivo: se creó a mano en el panel de Supabase, así
-- que quien replicaba desde los archivos se topaba con un error.
create table if not exists public.foro_reacciones (
  post_id       text not null,
  target        text not null default '__post__',  -- '__post__' o el id de una respuesta
  usuario_email text not null,
  tipo          text not null check (tipo in ('destacados', 'ideas', 'meGusta')),
  created_at    timestamptz not null default now(),
  primary key (post_id, target, usuario_email, tipo)
);

alter table public.foro_reacciones enable row level security;

-- Responder sin poder reescribir el tema.
-- Las respuestas viven dentro de la columna jsonb del tema. Permitir "responder"
-- con un UPDATE normal implicaría dejar cambiar también el título y el contenido.
create or replace function public.responder_foro(p_post_id text, p_contenido text)
returns jsonb language plpgsql security definer set search_path = public as $$
declare v_nombre text; v_respuesta jsonb;
begin
  select nombre_completo into v_nombre
    from public.profiles where id = auth.uid() and estado = 'activo';
  if v_nombre is null then
    raise exception 'Tu cuenta no tiene acceso autorizado al curso.';
  end if;
  if p_contenido is null or btrim(p_contenido) = '' then
    raise exception 'La respuesta no puede ir vacía.';
  end if;

  v_respuesta := jsonb_build_object(
    'id',         'resp-' || replace(gen_random_uuid()::text, '-', ''),
    'autor',      v_nombre,
    'contenido',  p_contenido,
    'fecha',      to_char(now() at time zone 'America/Mexico_City', 'DD/MM/YYYY, HH24:MI:SS'),
    'destacados', 0, 'ideas', 0, 'megusta', 0
  );

  update public.foro_posts
     set respuestas = coalesce(respuestas, '[]'::jsonb) || v_respuesta
   where id = p_post_id;
  if not found then raise exception 'El tema al que respondes ya no existe.'; end if;

  return v_respuesta;
end;
$$;

grant execute on function public.responder_foro(text, text) to authenticated;

create or replace function public.toggle_reaccion_foro(
  p_post_id text, p_tipo text, p_target text default '__post__'
) returns integer language plpgsql security definer set search_path = public as $$
declare
  v_email text; v_columna text; v_existe boolean;
  v_delta integer; v_nuevo integer; v_respuestas jsonb;
begin
  select email into v_email
    from public.profiles where id = auth.uid() and estado = 'activo';
  if v_email is null then
    raise exception 'Tu cuenta no tiene acceso autorizado al curso.';
  end if;
  if p_tipo not in ('destacados', 'ideas', 'meGusta') then
    raise exception 'Tipo de reacción no válido: %', p_tipo;
  end if;

  v_columna := case when p_tipo = 'meGusta' then 'megusta' else p_tipo end;

  select exists (
    select 1 from public.foro_reacciones
     where post_id = p_post_id and target = p_target
       and usuario_email = v_email and tipo = p_tipo
  ) into v_existe;

  if v_existe then
    delete from public.foro_reacciones
     where post_id = p_post_id and target = p_target
       and usuario_email = v_email and tipo = p_tipo;
    v_delta := -1;
  else
    insert into public.foro_reacciones (post_id, target, usuario_email, tipo)
    values (p_post_id, p_target, v_email, p_tipo);
    v_delta := 1;
  end if;

  if p_target = '__post__' then
    execute format(
      'update public.foro_posts set %I = greatest(0, coalesce(%I, 0) + $1) where id = $2 returning %I',
      v_columna, v_columna, v_columna
    ) into v_nuevo using v_delta, p_post_id;
  else
    select respuestas into v_respuestas from public.foro_posts where id = p_post_id;
    select jsonb_agg(
             case when r ->> 'id' = p_target
               then jsonb_set(r, array[v_columna],
                      to_jsonb(greatest(0, coalesce((r ->> v_columna)::int, 0) + v_delta)))
               else r end)
      into v_respuestas
      from jsonb_array_elements(coalesce(v_respuestas, '[]'::jsonb)) r;

    update public.foro_posts set respuestas = coalesce(v_respuestas, '[]'::jsonb)
     where id = p_post_id;

    select coalesce((r ->> v_columna)::int, 0) into v_nuevo
      from jsonb_array_elements(coalesce(v_respuestas, '[]'::jsonb)) r
     where r ->> 'id' = p_target;
  end if;

  return coalesce(v_nuevo, 0);
end;
$$;

grant execute on function public.toggle_reaccion_foro(text, text, text) to authenticated;


-- ============================================================================
-- 9. RECUPERACIÓN DE CONTRASEÑA AUTORIZADA POR QUIEN COORDINA
--
-- No depende de correo saliente. La persona pide restablecer, quien coordina lo
-- autoriza desde el panel y entrega el código por el canal que ya usan.
-- El código se guarda con hash, caduca, y cuenta los intentos.
-- ============================================================================
create table if not exists public.solicitudes_password (
  id                 uuid primary key default gen_random_uuid(),
  usuario_id         uuid not null,
  email              text not null,
  nombre_completo    text not null,
  plantel            text,
  estado             text not null default 'pendiente'
                       check (estado in ('pendiente', 'autorizada', 'usada', 'rechazada')),
  codigo_hash        text,
  codigo_expira      timestamptz,
  intentos           int  not null default 0,
  fecha_solicitud    timestamptz not null default now(),
  fecha_autorizacion timestamptz,
  fecha_uso          timestamptz
);

alter table public.solicitudes_password enable row level security;


-- ============================================================================
-- 10. NOTIFICACIONES Y PWA  (opcional)
-- Omite este apartado si la réplica no va a instalar notificaciones push.
-- ============================================================================
create table if not exists public.push_subscriptions (
  id            uuid primary key default gen_random_uuid(),
  usuario_email text,
  endpoint      text not null,
  p256dh        text not null,
  auth          text not null,
  platform      text,
  language      text,
  created_at    timestamptz default now(),
  last_used_at  timestamptz default now()
);

create table if not exists public.notifications (
  id            uuid primary key default gen_random_uuid(),
  usuario_email text not null,
  type          text not null,
  title         text not null,
  body          text,
  data          jsonb,
  read          boolean default false,
  created_at    timestamptz default now()
);

alter table public.push_subscriptions enable row level security;
alter table public.notifications      enable row level security;


-- ============================================================================
-- 11. POLÍTICAS DE ACCESO
--
-- Regla general: sin sesión iniciada no se toca nada, cada persona ve lo suyo,
-- y quien coordina (rol = 'admin') administra.
--
-- Se borran primero todas las políticas existentes. En Postgres las políticas
-- de un mismo comando se combinan con OR, así que dejar una permisiva viva
-- anularía todo lo demás.
-- ============================================================================
do $$
declare r record;
begin
  for r in select policyname, tablename from pg_policies where schemaname = 'public'
  loop
    execute format('drop policy %I on public.%I', r.policyname, r.tablename);
  end loop;
end;
$$;

-- planteles: catálogo público, lo necesita el registro antes de iniciar sesión
create policy "Catálogo de sedes de lectura pública"
  on public.planteles_cobach for select to anon, authenticated using (true);

-- profiles: sin política de INSERT (solo nacen por el trigger) y sin UPDATE
-- para la persona dueña; si lo tuviera, podría ponerse rol = 'admin' sola.
create policy "Cada quien ve su perfil; quien coordina ve todos"
  on public.profiles for select to authenticated
  using (id = auth.uid() or public.es_admin());
create policy "Solo quien coordina modifica perfiles"
  on public.profiles for update to authenticated
  using (public.es_admin()) with check (public.es_admin());
create policy "Solo quien coordina elimina perfiles"
  on public.profiles for delete to authenticated using (public.es_admin());

-- bitácora: se escribe solo desde public.registrar_acceso()
create policy "Solo quien coordina consulta la bitácora"
  on public.bitacora_accesos for select to authenticated using (public.es_admin());

-- unidades del curso
create policy "El profesorado ve qué unidades están abiertas"
  on public.sesiones_config for select to authenticated using (true);
create policy "Solo quien coordina habilita unidades"
  on public.sesiones_config for update to authenticated
  using (public.es_admin()) with check (public.es_admin());

-- actividades y rúbricas
create policy "El profesorado lee la configuración de actividades"
  on public.hacks_config for select to authenticated using (true);
create policy "Solo quien coordina cambia la configuración"
  on public.hacks_config for all to authenticated
  using (public.es_admin()) with check (public.es_admin());

-- entregas
create policy "Cada quien ve sus entregas; quien coordina ve todas"
  on public.entregables for select to authenticated
  using (lower(usuario_email) = lower(auth.email()) or public.es_admin());
create policy "Cada quien entrega a su propio nombre"
  on public.entregables for insert to authenticated
  with check (public.es_usuario_activo() and lower(usuario_email) = lower(auth.email()));
create policy "Solo quien coordina califica"
  on public.entregables for update to authenticated
  using (public.es_admin()) with check (public.es_admin());
create policy "Solo quien coordina elimina entregas"
  on public.entregables for delete to authenticated using (public.es_admin());

-- foros: crear y eliminar temas es exclusivo de quien coordina; el profesorado
-- lee y responde, y responder pasa por responder_foro(), no por un UPDATE
create policy "El profesorado autorizado lee los foros"
  on public.foro_posts for select to authenticated
  using (public.es_usuario_activo() or public.es_admin());
create policy "Solo quien coordina crea temas"
  on public.foro_posts for insert to authenticated with check (public.es_admin());
create policy "Solo quien coordina edita temas"
  on public.foro_posts for update to authenticated
  using (public.es_admin()) with check (public.es_admin());
create policy "Solo quien coordina elimina temas"
  on public.foro_posts for delete to authenticated using (public.es_admin());

create policy "Cada quien ve sus reacciones"
  on public.foro_reacciones for select to authenticated
  using (lower(usuario_email) = lower(auth.email()) or public.es_admin());

-- recuperación de contraseña
create policy "Solo quien coordina ve las solicitudes de contraseña"
  on public.solicitudes_password for all to authenticated
  using (public.es_admin()) with check (public.es_admin());

-- notificaciones
create policy "Cada quien administra sus propias suscripciones"
  on public.push_subscriptions for all to authenticated
  using (lower(usuario_email) = lower(auth.email()) or public.es_admin())
  with check (lower(usuario_email) = lower(auth.email()) or public.es_admin());
create policy "Cada quien ve sus notificaciones"
  on public.notifications for select to authenticated
  using (lower(usuario_email) = lower(auth.email()) or public.es_admin());
create policy "Solo quien coordina emite notificaciones"
  on public.notifications for all to authenticated
  using (public.es_admin()) with check (public.es_admin());


-- ============================================================================
-- 12. ALMACENAMIENTO DE EVIDENCIAS
--
-- El bucket se crea PRIVADO. En el proyecto de origen quedó público y con una
-- política `for all using (bucket_id = ...)`, y se comprobó que cualquiera con
-- la llave pública y sin sesión podía listar y descargar los archivos entregados
-- por el profesorado.
--
-- Ojo: el barrido de políticas del apartado 11 solo alcanza al esquema `public`.
-- Las de storage viven en el esquema `storage` y hay que borrarlas aparte, como
-- se hace aquí. Es justo el detalle por el que aquel agujero sobrevivió.
--
-- CONSECUENCIA EN EL CÓDIGO: con el bucket privado, `getPublicUrl()` deja de
-- servir. Hay que usar `createSignedUrl(ruta, segundos)`, que exige sesión.
-- ============================================================================
insert into storage.buckets (id, name, public)
values ('entregables-evidencias', 'entregables-evidencias', false)
on conflict (id) do update set public = false;

do $$
declare r record;
begin
  for r in select policyname from pg_policies
            where schemaname = 'storage' and tablename = 'objects'
  loop
    execute format('drop policy %I on storage.objects', r.policyname);
  end loop;
end;
$$;

create policy "Quien está activo sube su evidencia"
  on storage.objects for insert to authenticated
  with check (bucket_id = 'entregables-evidencias' and public.es_usuario_activo());

create policy "Quien coordina lee todas las evidencias"
  on storage.objects for select to authenticated
  using (bucket_id = 'entregables-evidencias'
         and (public.es_admin() or owner = auth.uid()));

create policy "Solo quien coordina borra evidencias"
  on storage.objects for delete to authenticated
  using (bucket_id = 'entregables-evidencias' and public.es_admin());


-- ============================================================================
-- 13. CREAR LA CUENTA QUE COORDINA
--
-- No se crea por SQL, y es a propósito: la contraseña debe nacer cifrada en
-- auth.users, no escrita en un archivo que acaba en un repositorio.
--
--   1. Panel de Supabase → Authentication → Users → Add user.
--      Correo institucional y contraseña. Marca "Auto Confirm User".
--   2. El trigger crea el perfil como 'pendiente_aprobacion' y rol 'profesor'.
--   3. Córre esto, con el correo real:
--
--      update public.profiles
--         set rol = 'admin', estado = 'activo', usuario = 'coordinacion'
--       where lower(email) = lower('correo@institucion.edu.mx');
--
--   4. Comprueba que quedó una y solo una cuenta con rol admin.
-- ============================================================================


-- ============================================================================
-- 14. COMPROBACIONES
-- Córrelas al terminar. Las tres deben salir en verde.
-- ============================================================================

-- a) Ninguna tabla sin RLS activo. Debe devolver 0 filas.
select tablename as tabla_sin_rls
  from pg_tables t
 where schemaname = 'public'
   and not exists (
     select 1 from pg_class c
      join pg_namespace n on n.oid = c.relnamespace
     where c.relname = t.tablename and n.nspname = 'public' and c.relrowsecurity
   );

-- b) Ninguna política abierta al rol anónimo salvo el catálogo de sedes.
--    Debe devolver solo la fila de planteles_cobach.
select tablename, policyname
  from pg_policies
 where schemaname = 'public' and 'anon' = any(roles);

-- c) Las ponderaciones suman 100 y ninguna actividad quedó sin criterios.
select sum(ponderacion_pct) as suma_total,
       count(*) filter (where jsonb_array_length(criterios_cotejo) = 0) as sin_rubrica
  from public.hacks_config;
