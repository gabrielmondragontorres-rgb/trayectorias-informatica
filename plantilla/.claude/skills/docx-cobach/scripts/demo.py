# -*- coding: utf-8 -*-
"""
Genera un documento de muestra por cada perfil e imprime la verificacion de
contraste de sus paletas.

    python demo.py [carpeta_de_salida]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx_cobach import PERFILES, Doc, verificar_perfil  # noqa: E402


def muestra(perfil, salida):
    d = Doc(perfil=perfil, pie=f"Documento de muestra · perfil {perfil} · Colegio de Bachilleres")
    d.portada(
        "Documento de muestra",
        f"Perfil visual «{perfil}»",
        sobretitulo="Motor docx-cobach",
        metadatos=[
            ("Perfil", perfil),
            ("Tipografia", PERFILES[perfil]["fuente"]),
            ("Uso", "Comprobar como se ve cada bloque antes de producir el documento real"),
        ],
    )

    d.h1("Bloques de texto", salto_antes=False)
    d.p("Parrafo justificado normal, que admite **negritas en linea** sin salir del flujo.")
    d.h2("Titulo de segundo nivel")
    d.p("El motor solo dibuja. Que secciones lleva el documento lo mandan las skills "
        "**estructura-guia** y **formato-word-guia**.")
    d.h3("Titulo de tercer nivel")
    d.vineta("Vineta de primer nivel.")
    d.vineta("Vineta anidada.", nivel=1)
    d.numerada("Elemento numerado.")
    d.cita("Cita con barra lateral de acento, para destacar una definicion o una regla.")
    d.aviso("Aviso", "Bloque de color para advertencias y notas que no deben pasarse por alto.")

    d.h1("Tablas y fichas")
    d.h2("Tabla con encabezado y cebreado")
    d.tabla(
        ["Corte", "Meta de aprendizaje", "Horas"],
        [
            ["Corte 1", "Desarrollar una landing page accesible e incluyente.", "30"],
            ["Corte 2", "Implementar un sistema de trafico digital accesible.", "20"],
            ["Corte 3", "Optimizar la conversion mediante mensajeria instantanea.", "30"],
        ],
        anchos=[2.4, 10.6, 2.0],
    )
    d.h2("Ficha de etiqueta y valor")
    d.ficha([
        ("Unidad de Aprendizaje Curricular", "Aplicacion del comercio electronico"),
        ("Semestre", "Quinto · 80 horas, 5 horas semanales"),
    ])
    d.h2("Cuadro de meta especifica")
    d.cuadro_meta(
        "Aplicar los fundamentos del comercio electronico y del embudo de marketing digital, "
        "considerando la estructuracion de una estrategia inicial de conversion accesible.",
        prefijo="Meta especifica 1",
    )

    d.h1("Bloques literales")
    d.etiqueta("Prompt que se copia sin editar")
    d.bloque_prompt("«Actua como consultor de comercio electronico incluyente.\n"
                    "Entrega una tabla con siete filas, una idea por celda.»")
    d.h2("Fragmento de codigo")
    d.bloque_codigo('<a class="cta" href="https://wa.me/525512345678">\n'
                    '  Pedir mi diagnostico por WhatsApp\n'
                    '</a>')

    ruta = os.path.join(salida, f"muestra-{perfil}.docx")
    d.guardar(ruta)
    return ruta


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else "."
    for perfil in PERFILES:
        print(f"\n=== Perfil «{perfil}» — contraste de la paleta ===")
        todo_ok = True
        for etq, fg, bg, ratio, ok in verificar_perfil(perfil):
            if not ok:
                todo_ok = False
            print(f"  {ratio:5.2f}:1  {'CUMPLE AA' if ok else 'NO CUMPLE'}  "
                  f"{etq}  (#{fg} sobre #{bg})")
        print(f"  -> {'toda la paleta cumple 4.5:1' if todo_ok else 'HAY COMBINACIONES POR DEBAJO DE 4.5:1'}")
        print("  documento:", muestra(perfil, salida))


if __name__ == "__main__":
    main()
