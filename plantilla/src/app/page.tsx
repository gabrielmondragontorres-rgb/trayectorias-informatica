import { SITIO } from '../config/sitio'

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold">{SITIO.nombre}</h1>
      <p className="mt-2 text-gray-600">Tu sitio está listo. Empieza a construir.</p>
    </main>
  )
}
