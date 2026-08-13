import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'

// El tipo de las cookies se declara a mano porque la opcion que recibe
// createServerClient es una union de dos formas posibles, y TypeScript no
// deduce los parametros a traves de una union. Sin esto, npm run build falla.
type CookieAGuardar = { name: string; value: string; options: CookieOptions }

export async function createClient() {
  const cookieStore = await cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet: CookieAGuardar[]) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // Ignore en Server Components
          }
        },
      },
    }
  )
}
