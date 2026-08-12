# Trayectorias Informática — cómo seguir

Esta carpeta ya tiene todo lo necesario para tu proyecto. Aquí están las
instrucciones mínimas, por si no tienes el manual a la mano.

Manual completo:
<https://github.com/gabrielmondragontorres-rgb/trayectorias-informatica>

---

## Para empezar

```powershell
npm install
copy .env.local.example .env.local
claude
```

Cuando se abra tu asistente, escribe `/primer` para que conozca tu proyecto.
Después háblale en español: le dices qué quieres y él lo construye.

---

## Si algo falla

**Escribes `trayectorias` y responde que no reconoce el comando.** Casi siempre
es una de dos cosas:

- Instalaste en una terminal y estás trabajando en otra. Windows PowerShell —la
  que trae Windows— y PowerShell 7 son programas distintos y no se comparten el
  comando.
- Windows todavía no tiene permiso para cargarlo.

Las dos se resuelven igual: vuelve a ejecutar la línea de instalación **desde la
terminal que vayas a usar**, y responde `s` si pregunta por el permiso.

```powershell
irm https://raw.githubusercontent.com/gabrielmondragontorres-rgb/trayectorias-informatica/main/instalar.ps1 | iex
```

Si en vez de eso te dice que la política la fija tu institución, no es algo que
puedas cambiar tú: pide a soporte técnico del plantel que habilite
`RemoteSigned` para tu usuario.

**Cualquier otro problema:** descríbeselo a tu asistente en español. Para eso
está.

---

## Tus claves son tuyas

Tus contraseñas de Supabase y Vercel van en el archivo `.env.local`. Ese archivo
**nunca** se sube a internet y **nunca** se comparte por mensaje.

---

*Trayectorias Informática · Colegio de Bachilleres*
