import type { Metadata } from 'next'
import { SITIO } from '../config/sitio'
import './globals.css'

export const metadata: Metadata = {
  title: SITIO.nombre,
  description: SITIO.descripcion,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  )
}
