#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Detecta si un programa de estudio COBACH esta escrito en la estructura por UAC
(Modelo 2023) o por Asignatura (Modelo Educativo 2025).

No decide solo: entrega un veredicto con la evidencia que lo sostiene, para que
la persona docente lo confirme antes de generar nada.

Uso:
    python detectar_modelo.py "ruta/al/programa.docx"
    python detectar_modelo.py "ruta/al/programa.docx" --json
"""

import sys
import json
import zipfile
import re
import unicodedata

try:
    from lxml import etree
except ImportError:
    sys.stderr.write(
        "Falta lxml. Instalar con: pip install lxml python-docx\n")
    sys.exit(2)

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


# --------------------------------------------------------------------------
# Marcadores. El peso refleja cuanto discrimina cada expresion, no cuanto
# aparece. "Asignatura" a secas pesa poco: los programas por UAC la nombran
# constantemente en la transversalidad con el componente fundamental.
# --------------------------------------------------------------------------

MARCADORES_UAC = [
    (r'unidad(es)? de aprendizaje curricular', 10, 'Unidad de Aprendizaje Curricular'),
    (r'\bproposito de la uac\b', 10, 'Proposito de la UAC'),
    (r'\bmetas? especificas?\b', 8, 'Metas especificas'),
    (r'\bmetas? de aprendizaje\b', 6, 'Meta de aprendizaje'),
    (r'instrumentacion didactica', 8, 'Instrumentacion didactica'),
    (r'conceptos centrales de la educacion para el desarrollo sostenible', 9,
     'Conceptos Centrales (CoCEDS)'),
    (r'\bcoceds\b', 9, 'CoCEDS'),
    (r'progresion(es)? de aprendizaje', 7, 'Progresiones de aprendizaje'),
    (r'\buac\b', 4, 'Sigla UAC'),
    (r'para saber mas', 4, 'Apartado "Para saber mas..."'),
]

MARCADORES_ASIGNATURA = [
    (r'actividad clave de la competencia laboral basica', 12,
     'Actividad clave de la competencia laboral basica'),
    (r'desarrollo de la competencia laboral basica', 12,
     'Desarrollo de la competencia laboral basica'),
    (r'referentes ocupacionales', 9, 'Referentes ocupacionales'),
    (r'\bsinco\b', 7, 'SINCO-2019'),
    (r'\bscian\b', 7, 'SCIAN-2023'),
    (r'habilidades para el desarrollo sostenible', 9,
     'Habilidades para el Desarrollo Sostenible (HDS)'),
    (r'\bhds\b', 6, 'Sigla HDS'),
    (r'propositos? formativos?', 8, 'Propositos formativos'),
    (r'resultado de aprendizaje', 7, 'Resultado de aprendizaje'),
    (r'estrategia didactica', 6, 'Estrategia didactica'),
    (r'modelo educativo 2025', 8, 'Modelo Educativo 2025'),
    (r'fase de (apertura|desarrollo|cierre)', 5, 'Fases de apertura/desarrollo/cierre'),
    (r'estandar(es)? de referencia', 5, 'Estandares de referencia (CONOCER)'),
]

# Carga horaria: senal secundaria, util para desempatar.
CARGA_UAC = [r'\b80\s*h(oras)?\b', r'\b32\s*h(oras)?\b']
CARGA_ASIGNATURA = [r'\b64\s*h(oras)?\b', r'\b4\s*h(oras)?\s*semanal']

# La nota de portada que cita el programa por UAC del que deriva el nuevo es una
# referencia historica legitima del Modelo 2025, no un residuo. Si no se descuenta,
# un programa por asignatura impecable se marca como hibrido.
CITA_HISTORICA = re.compile(
    r'(con base en|a partir de|derivad[oa] d[el]{1,2})\s+(el\s+)?programa\s+'
    r'(de\s+(la\s+)?)?(estudi[o]?s?\s+)?(de\s+)?(la\s+)?unidad(es)? de aprendizaje curricular')


def sin_acentos(t):
    return ''.join(c for c in unicodedata.normalize('NFD', t)
                   if unicodedata.category(c) != 'Mn')


def texto_documento(ruta):
    """Extrae todo el texto, incluido el insertado con control de cambios."""
    z = zipfile.ZipFile(ruta)
    partes = []
    for nombre in z.namelist():
        if not re.match(r'word/(document|header\d*|footer\d*)\.xml$', nombre):
            continue
        raiz = etree.fromstring(z.read(nombre))
        for nodo in raiz.iter(W + 't'):
            # w:delText es texto borrado: no cuenta como contenido vigente
            if any(etree.QName(a).localname == 'delText'
                   for a in nodo.iterancestors()):
                continue
            if nodo.text:
                partes.append(nodo.text)
    z.close()
    return ' '.join(partes)


def puntuar(texto_norm, marcadores):
    total = 0
    hallados = []
    for patron, peso, etiqueta in marcadores:
        n = len(re.findall(patron, texto_norm))
        if n:
            total += peso
            hallados.append({'marcador': etiqueta, 'apariciones': n, 'peso': peso})
    return total, hallados


def analizar(ruta):
    crudo = texto_documento(ruta)
    norm = sin_acentos(crudo).lower()

    citas_historicas = len(CITA_HISTORICA.findall(norm))
    # Se neutraliza para el conteo: la portada no debe pesar como residuo.
    norm_uac = CITA_HISTORICA.sub(' [cita historica] ', norm)

    p_uac, h_uac = puntuar(norm_uac, MARCADORES_UAC)
    p_asig, h_asig = puntuar(norm, MARCADORES_ASIGNATURA)

    carga = None
    if any(re.search(p, norm) for p in CARGA_ASIGNATURA):
        carga = '64 h / 4 h semanales (propio del Modelo 2025)'
        p_asig += 4
    elif any(re.search(p, norm) for p in CARGA_UAC):
        carga = '80 h o 32 h (propio de la estructura por UAC)'
        p_uac += 4

    total = p_uac + p_asig
    if total == 0:
        veredicto, confianza = 'indeterminado', 0.0
    else:
        confianza = round(max(p_uac, p_asig) / float(total), 3)
        if p_asig > p_uac:
            veredicto = 'asignatura'
        elif p_uac > p_asig:
            veredicto = 'uac'
        else:
            veredicto = 'indeterminado'

    # Un documento hibrido es la senal mas importante de todas: significa que
    # alguien migro a medias y la planeacion heredaria la mezcla.
    #
    # Exige evidencia ESTRUCTURAL sostenida de las dos partes. No basta el
    # puntaje: expresiones como "estrategia didactica" o "resultado de
    # aprendizaje" aparecen sueltas en programas por UAC sin que eso signifique
    # migracion. Solo cuentan los marcadores de peso alto (>= 8), que son los
    # que nombran piezas propias de una estructura y no de la otra, y ademas
    # tienen que repetirse: un termino citado una vez es una mencion, no un
    # apartado.
    def estructurales(hallados):
        return [h for h in hallados if h['peso'] >= 8 and h['apariciones'] >= 2]

    e_uac, e_asig = estructurales(h_uac), estructurales(h_asig)
    minoritario = min(p_uac, p_asig)
    hibrido = (len(e_uac) >= 2 and len(e_asig) >= 2
               and total > 0 and (minoritario / float(total)) >= 0.25)

    return {
        'archivo': ruta,
        'veredicto': veredicto,
        'confianza': confianza,
        'hibrido': hibrido,
        'citas_historicas_descontadas': citas_historicas,
        'puntaje_uac': p_uac,
        'puntaje_asignatura': p_asig,
        'carga_horaria_detectada': carga,
        'evidencia_uac': sorted(h_uac, key=lambda x: -x['peso']),
        'evidencia_asignatura': sorted(h_asig, key=lambda x: -x['peso']),
        'caracteres_leidos': len(crudo),
    }


ETIQUETA = {
    'uac': 'Programa por UAC (Modelo 2023)',
    'asignatura': 'Programa por Asignatura (Modelo Educativo 2025)',
    'indeterminado': 'No se pudo determinar',
}


def informe(r):
    lineas = []
    lineas.append('=' * 68)
    lineas.append('DETECCION DE ESTRUCTURA DEL PROGRAMA DE ESTUDIO')
    lineas.append('=' * 68)
    lineas.append('Archivo: %s' % r['archivo'])
    lineas.append('Caracteres leidos: %s' % r['caracteres_leidos'])
    lineas.append('')
    lineas.append('VEREDICTO: %s' % ETIQUETA[r['veredicto']])
    lineas.append('Confianza: %.0f %%   (UAC %s pts / Asignatura %s pts)'
                  % (r['confianza'] * 100, r['puntaje_uac'], r['puntaje_asignatura']))
    if r['carga_horaria_detectada']:
        lineas.append('Carga horaria: %s' % r['carga_horaria_detectada'])
    lineas.append('')

    if r.get('citas_historicas_descontadas'):
        lineas.append('Nota: se descontaron %s cita(s) de portada del tipo "elaborado con'
                      % r['citas_historicas_descontadas'])
        lineas.append('base en el Programa de la Unidad de Aprendizaje Curricular". Es una')
        lineas.append('referencia historica legitima del Modelo 2025, no un residuo.')
        lineas.append('')

    if r['hibrido']:
        lineas.append('!! DOCUMENTO HIBRIDO')
        lineas.append('   Conviven marcadores de las dos estructuras con fuerza.')
        lineas.append('   Suele significar una migracion a medias. Preguntar a la')
        lineas.append('   persona docente cual es la version vigente ANTES de planear,')
        lineas.append('   o la planeacion heredara la mezcla.')
        lineas.append('')
    else:
        # Residuo aislado: no cambia el veredicto, pero conviene decirlo, porque
        # la planeacion no debe copiar vocabulario derogado.
        perdedor = ('evidencia_uac' if r['veredicto'] == 'asignatura'
                    else 'evidencia_asignatura')
        if r['veredicto'] != 'indeterminado' and r[perdedor]:
            otro = 'Plan 2023' if perdedor == 'evidencia_uac' else 'Modelo 2025'
            lineas.append('Residuos de vocabulario del %s (no cambian el veredicto,' % otro)
            lineas.append('pero no deben copiarse a la planeacion):')
            for e in r[perdedor]:
                lineas.append('   - %s (x%s)' % (e['marcador'], e['apariciones']))
            lineas.append('')

    if r['confianza'] < 0.70 and r['veredicto'] != 'indeterminado':
        lineas.append('!! CONFIANZA BAJA: confirmar con la persona docente.')
        lineas.append('')

    for titulo, clave in (('Evidencia de estructura por UAC', 'evidencia_uac'),
                          ('Evidencia de estructura por Asignatura',
                           'evidencia_asignatura')):
        lineas.append(titulo)
        if not r[clave]:
            lineas.append('   (ninguna)')
        for e in r[clave]:
            lineas.append('   %-52s x%-3s (peso %s)'
                          % (e['marcador'], e['apariciones'], e['peso']))
        lineas.append('')

    lineas.append('-' * 68)
    lineas.append('El veredicto NO sustituye la confirmacion de quien imparte la')
    lineas.append('asignatura. Preguntar siempre antes de generar la planeacion.')
    return '\n'.join(lineas)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.stderr.write(__doc__)
        sys.exit(2)
    r = analizar(args[0])
    if '--json' in sys.argv:
        sys.stdout.write(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(informe(r))
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
