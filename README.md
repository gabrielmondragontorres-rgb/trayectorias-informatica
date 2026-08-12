# Trayectorias Informática

**Curso de Marketing Digital · Colegio de Bachilleres**

Herramientas para construir una página de aterrizaje profesional, conectarla a una
base de datos y publicarla en internet. Sin saber programar.

---

## Qué vas a construir

Una página web real para un negocio, con:

- Identidad visual propia: logotipo, imágenes y colores
- Textos pensados para convertir visitas en clientela
- Un formulario de contacto que guarda los datos de forma segura
- El sitio publicado en internet, con su propia dirección

---

## Instalación

Copia esta línea, pégala en **PowerShell** y presiona Enter:

```powershell
irm https://raw.githubusercontent.com/gabrielmondragontorres-rgb/trayectorias-informatica/main/instalar.ps1 | iex
```

> **¿Cómo abro PowerShell?** Presiona la tecla de Windows, escribe `PowerShell` y
> ábrelo. No necesitas permisos de administrador.

El instalador revisa lo que necesitas y deja listo el comando `trayectorias`.

**Cierra esa ventana y abre una nueva** para que el comando quede disponible.

---

## Cómo crear un proyecto

Cada vez que empieces un proyecto nuevo:

```powershell
mkdir mi-negocio
cd mi-negocio
trayectorias
```

Eso descarga todo lo necesario en esa carpeta. Después:

```powershell
npm install
claude
```

Y cuando se abra tu asistente, escribe `/primer` para que conozca tu proyecto.

> El comando también responde a `trayectorias-informatica` y a `ti`.

---

## Qué necesitas antes de empezar

| Requisito | Dónde se consigue | Costo |
|---|---|---|
| **Node.js 20+** | [nodejs.org](https://nodejs.org) | Gratis |
| **Claude Code** | `npm install -g @anthropic-ai/claude-code` | Requiere cuenta |
| **Cuenta de GitHub** | [github.com](https://github.com) | Gratis |
| **Cuenta de Supabase** | [supabase.com](https://supabase.com) | Gratis, sin tarjeta |
| **Cuenta de Vercel** | [vercel.com](https://vercel.com) | Gratis, se vincula con GitHub |

El instalador te avisa si falta alguno.

---

## Cómo se trabaja

**Hablas en español, tu asistente construye.** No escribes código. Le dices qué
quieres y él lo hace:

> «Quiero una página para mi taller de repostería»
>
> «Hazme un logotipo con colores cálidos»
>
> «Que la gente pueda dejar su correo para recibir promociones»
>
> «Publica el sitio»

---

## Las 13 herramientas incluidas

| Herramienta | Para qué sirve |
|---|---|
| `primer` | Recuerda de qué trata tu proyecto al abrir una sesión |
| `new-app` | Te entrevista para definir tu negocio |
| `image-generation` | Crea logotipos, banners e imágenes |
| `website-3d` | Construye la página con textos persuasivos |
| `supabase` | Crea la base de datos y la protege |
| `prp` | Planea por escrito antes de construir algo grande |
| `playwright-cli` | Prueba que todo funcione |
| `inclusion` | Revisa que los textos usen lenguaje incluyente |
| `lenguaje-incluyente` | Refuerza la revisión con criterios de la RAE |
| `add-login` | Agrega registro e inicio de sesión |
| `add-emails` | Envía correos automáticos |
| `video-visuals` | Genera piezas gráficas para redes sociales |
| `elaboracion-material-didactico-planteles` | Instrumentos de evaluación |

---

## El curso

**5 sesiones de 5 horas.**

| Sesión | Contenido | Con qué terminas |
|---|---|---|
| 1 | Instalación, cuentas y definición del negocio | Tu negocio definido por escrito |
| 2 | Identidad visual y contenidos | Logotipo, banner e imágenes |
| 3 | Construcción de la página | Sitio funcionando en tu computadora |
| 4 | Base de datos y formulario de contacto | Datos que se guardan y se consultan |
| 5 | Pruebas, revisión y publicación | Tu sitio en internet |

---

## Dos advertencias importantes

**Tus claves son tuyas.** Cada persona configura sus propias contraseñas de
Supabase y Vercel en el archivo `.env.local`. Ese archivo **nunca** se sube a
internet y **nunca** se comparte por mensaje.

**Protege los datos que recojas.** Si tu formulario captura nombres o correos,
esa información está protegida por la normativa de datos personales. Tu asistente
activará la seguridad correspondiente en la base de datos; no la desactives.

---

## Si algo falla

1. Cierra la terminal y abre una nueva.
2. Vuelve a ejecutar la línea de instalación: reinstala sin duplicar nada.
3. Descríbele el problema a tu asistente en español. Para eso está.

---

## Actualizaciones

El comando descarga siempre la versión más reciente. No necesitas reinstalar nada
cuando se agreguen mejoras: basta con crear un proyecto nuevo.

---

## Licencia

Licencia MIT. En términos llanos: **puedes usar, copiar, modificar y compartir
este material con libertad**, incluso adaptándolo a otra materia o a otro
plantel. La única condición es conservar el aviso de autoría.

Consulta el archivo [LICENSE](LICENSE).

---

*Trayectorias Informática · Colegio de Bachilleres · Agosto de 2026*
*Basado en SaaS Factory.*
