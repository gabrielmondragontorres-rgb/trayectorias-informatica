#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Revisa una planeacion didactica ANTES de generar el .docx.

Nace de un defecto real: al cambiar el modelo de un mismo archivo, las etiquetas
se adaptaron pero la prosa siguio diciendo "Unidad de Aprendizaje Curricular"
dentro de una planeacion por asignatura. Renombrar la etiqueta no migra el
contenido. Esto lo detecta.

Uso:
    python validar_planeacion.py planeacion.json
    python validar_planeacion.py planeacion.json --json
"""

import sys
import json
import re
import unicodedata

import terminologia as T

GRAVE, MEDIO, LEVE = 'GRAVE', 'MEDIO', 'LEVE'


def _norm(t):
    t = ''.join(c for c in unicodedata.normalize('NFD', t or '')
                if unicodedata.category(c) != 'Mn')
    return t.lower()


def _texto_de(spec):
    """Aplana toda la prosa de la planeacion, con la ruta de cada fragmento."""
    piezas = []

    def anda(nodo, ruta):
        if isinstance(nodo, dict):
            for k, v in nodo.items():
                anda(v, '%s.%s' % (ruta, k) if ruta else k)
        elif isinstance(nodo, list):
            for i, v in enumerate(nodo):
                anda(v, '%s[%d]' % (ruta, i))
        elif isinstance(nodo, str) and nodo.strip():
            piezas.append((ruta, nodo))

    anda(spec, '')
    return piezas


# --------------------------------------------------------------------------
# Reglas
# --------------------------------------------------------------------------

# Vocabulario del Plan 2023 que no debe aparecer en una planeacion por
# asignatura. Se excluye la cita historica de portada, que es legitima.
RESIDUOS_2023 = [
    (r'unidad(es)? de aprendizaje curricular', 'Unidad de Aprendizaje Curricular'),
    (r'\bmetas? especificas?\b', 'Metas específicas'),
    (r'\bcoceds\b', 'CoCEDS'),
    (r'conceptos centrales de la educacion para el desarrollo sostenible',
     'Conceptos Centrales (CoCEDS)'),
    (r'progresion(es)? de aprendizaje', 'Progresiones de aprendizaje'),
    (r'instrumentacion didactica', 'Instrumentación didáctica'),
]

# Y al reves: una planeacion por UAC no deberia hablar en Modelo 2025.
RESIDUOS_2025 = [
    (r'actividad clave de la competencia laboral basica',
     'Actividad clave de la competencia laboral básica'),
    (r'desarrollo de la competencia laboral basica',
     'Desarrollo de la competencia laboral básica'),
    (r'habilidades para el desarrollo sostenible',
     'Habilidades para el Desarrollo Sostenible'),
    (r'propositos? formativos?', 'Propósitos formativos'),
]

CITA_HISTORICA = re.compile(
    r'(con base en|a partir de|derivad[oa] d[el]{1,2})\s+(el\s+)?programa\s+'
    r'(de\s+(la\s+)?)?(estudi[o]?s?\s+)?(de\s+)?(la\s+)?unidad(es)? de aprendizaje curricular')

# Masculino generico frecuente en estos documentos.
#
# El lookbehind evita marcar las formas que YA son incluyentes: dentro de "las y
# los estudiantes" aparece el fragmento "los estudiantes", pero ese texto esta
# bien escrito. Sin la guarda, el validador corrige lo que ya estaba correcto, y
# eso ensena a ignorar sus avisos. Se detecto sobre una progresion oficial.
_INC = r'(?<!las y )(?<!los y las )(?<!las y los )'

MASCULINO = [
    (_INC + r'\blos alumnos\b', 'el estudiantado / las y los estudiantes'),
    (_INC + r'\blos estudiantes\b', 'el estudiantado / las y los estudiantes'),
    (_INC + r'\blos usuarios\b', 'las personas usuarias'),
    (_INC + r'\blos docentes\b', 'el personal docente'),
    (_INC + r'\blos profesores\b', 'el personal docente'),
    (r'\bel alumno\b', 'cada estudiante'),
    (_INC + r'\blos participantes\b', 'las personas participantes'),
    (_INC + r'\blos responsables\b', 'las personas responsables'),
    (r'\bun lider\b', 'una persona que lidera'),
    (r'\blos disenadores\b', 'las personas que disenan'),
    (r'\blos programadores\b', 'quienes programan'),
]

# Redaccion en negativo del nivel mas bajo de una rubrica.
#
# Solo entran formulas que describen inequivocamente la carencia de una PERSONA.
# Se excluyen "no cumple" y "no aplica" porque son polisemicas y disparaban sobre
# prosa legitima: "un juego de datos que no cumple las condiciones esperadas"
# describe un caso de prueba, no a quien estudia. Un validador que marca lo
# correcto ensena a ignorarlo.
NEGATIVO = [r'\bno logra\b', r'\bcarece de\b', r'\bno identifica\b',
            r'\bno presenta\b', r'\bincapaz\b', r'\bno realiza\b',
            r'\bno alcanza\b', r'\bno demuestra\b', r'\bno consigue\b']


def revisar(spec):
    hallazgos = []

    def add(nivel, regla, detalle, donde='', arreglo=''):
        hallazgos.append({'nivel': nivel, 'regla': regla, 'detalle': detalle,
                          'donde': donde, 'arreglo': arreglo})

    modelo = (spec.get('modelo') or '').lower()
    if modelo not in ('uac', 'asignatura'):
        add(GRAVE, 'modelo', 'El campo "modelo" debe ser "uac" o "asignatura".',
            'raiz', 'Preguntar a la persona docente y fijarlo antes de generar.')
        return hallazgos

    piezas = _texto_de(spec)

    # 1. Residuos de vocabulario del modelo contrario
    tabla = RESIDUOS_2023 if modelo == 'asignatura' else RESIDUOS_2025
    otro = 'Plan 2023' if modelo == 'asignatura' else 'Modelo 2025'
    for ruta, txt in piezas:
        n = _norm(txt)
        limpio = CITA_HISTORICA.sub(' ', n)
        for patron, etiqueta in tabla:
            if re.search(patron, limpio):
                equiv = T.traducir(etiqueta) or '(ver tabla de equivalencias)'
                add(GRAVE, 'vocabulario',
                    'Aparece "%s", que pertenece al %s.' % (etiqueta, otro),
                    ruta, 'Sustituir por: %s' % equiv)

    # 2. Catalogos cerrados: HVyT y HDS
    ponderacion_por_corte = []
    for corte in spec.get('cortes', []):
        n_corte = corte.get('numero', '?')
        tr = corte.get('transversalidad') or {}

        hvyt = _norm(tr.get('hvyt', ''))
        if hvyt:
            for falso in T.FALSOS_AMIGOS:
                if _norm(falso) in hvyt:
                    add(GRAVE, 'catalogo',
                        '"%s" no pertenece a ningun catalogo, aunque lo parezca.'
                        % falso, 'corte %s / hvyt' % n_corte,
                        'Usar una de las 12 HVyT: %s' % ', '.join(T.HVYT[:4]) + '...')
            if not any(_norm(h) in hvyt for h in T.HVYT):
                add(MEDIO, 'catalogo',
                    'Ninguna de las 12 HVyT del catalogo aparece nombrada.',
                    'corte %s / hvyt' % n_corte,
                    'Tomar las marcadas en la matriz de transversalidad del corte.')

        sost = _norm(tr.get('sostenible', ''))
        if sost and not any(_norm(h) in sost for h in T.HDS):
            add(MEDIO, 'catalogo',
                'El valor no corresponde a ninguna de las 4 HDS del catalogo.',
                'corte %s / sostenible' % n_corte,
                'Validos: %s' % ' · '.join(T.HDS))

        # 3. Ponderaciones del corte.
        #
        # En el formato oficial las ponderaciones se reparten sobre el SEMESTRE,
        # no dentro de cada corte: el ejemplo aprobado de referencia lleva 0 %,
        # 0 % y 25 % en su Corte 1, y es correcto. Exigir aqui el 100 % marcaria
        # como defecto un documento validado. Por eso este punto solo caza el
        # exceso, y la suma global se revisa despues sobre el conjunto.
        total, leidas = 0.0, 0
        for fase in ('apertura', 'desarrollo', 'cierre'):
            ev = (corte.get(fase) or {}).get('evaluacion') or {}
            for f in ev.get('filas') or []:
                if len(f) >= 4:
                    m = re.search(r'(\d+(?:[.,]\d+)?)\s*%', str(f[3]))
                    if m:
                        total += float(m.group(1).replace(',', '.'))
                        leidas += 1
        if leidas:
            ponderacion_por_corte.append((n_corte, total))
            if total > 100.5:
                add(GRAVE, 'ponderacion',
                    'Las ponderaciones del corte suman %.1f %%, mas del 100 %%.'
                    % total, 'corte %s' % n_corte, '')

        # 4. Cobertura: los tres cortes necesitan actividades propias
        for fase in ('apertura', 'desarrollo', 'cierre'):
            f = corte.get(fase)
            if not f:
                add(GRAVE, 'cobertura',
                    'Falta la fase de %s.' % fase, 'corte %s' % n_corte,
                    'Un corte sin actividades propias se apoya solo en la '
                    'practica, y la practica consolida pero no sustituye.')
                continue
            actividades = [a for a in (f.get('actividades') or [])
                           if (a.get('texto') or '').strip()]
            if not actividades:
                add(GRAVE, 'cobertura',
                    'La fase de %s no tiene ninguna actividad descrita.' % fase,
                    'corte %s / %s' % (n_corte, fase), '')
            if not (f.get('recursos') or '').strip():
                add(LEVE, 'recursos',
                    'La fase de %s no declara recursos.' % fase,
                    'corte %s / %s' % (n_corte, fase), '')

        # 5. Instrumento: uno por columna
        for fase in ('apertura', 'desarrollo', 'cierre'):
            ev = (corte.get(fase) or {}).get('evaluacion') or {}
            for i, f in enumerate(ev.get('filas') or []):
                if len(f) >= 3 and f[2]:
                    partes = re.split(r'\s+y\s+|,|;|/', str(f[2]))
                    partes = [p for p in (p.strip() for p in partes) if p]
                    if len(partes) > 1:
                        add(MEDIO, 'instrumento',
                            'La celda declara mas de un instrumento: "%s".' % f[2],
                            'corte %s / %s / fila %d' % (n_corte, fase, i + 1),
                            'La convencion es uno por columna: guia de '
                            'observacion para el desempeno, lista de cotejo '
                            'para el producto.')

    # 6. Lenguaje incluyente
    vistos = set()
    for ruta, txt in piezas:
        n = _norm(txt)
        for patron, sug in MASCULINO:
            if re.search(patron, n):
                clave = (patron, ruta)
                if clave in vistos:
                    continue
                vistos.add(clave)
                add(MEDIO, 'lenguaje',
                    'Masculino generico: %s' % patron.strip('\\b'), ruta,
                    'Sustituir por: %s' % sug)

    # 7. Rubrica en negativo
    for ruta, txt in piezas:
        n = _norm(txt)
        for patron in NEGATIVO:
            if re.search(patron, n):
                add(MEDIO, 'redaccion',
                    'El nivel se redacta en negativo (%s).' % patron.strip('\\b'),
                    ruta,
                    'Usar la formula "falta lograr que...", que dice lo mismo y '
                    'nombra el siguiente paso. La rubrica se entrega al '
                    'estudiantado, no solo se archiva.')

    # 7b. Suma global de ponderaciones.
    # Solo tiene sentido exigir el 100 % cuando la planeacion cubre el semestre
    # completo. Con un corte suelto se informa el avance y nada mas: reclamar el
    # faltante seria reclamar lo que aun no se ha escrito.
    if ponderacion_por_corte:
        suma = sum(t for _, t in ponderacion_por_corte)
        n_cortes = len(ponderacion_por_corte)
        detalle = ' + '.join('corte %s: %.0f %%' % (c, t)
                             for c, t in ponderacion_por_corte)
        if n_cortes >= 3:
            if abs(suma - 100.0) > 0.5:
                add(GRAVE, 'ponderacion',
                    'La planeacion cubre %d cortes y sus ponderaciones suman '
                    '%.1f %%, no 100 %%.' % (n_cortes, suma),
                    detalle,
                    'La diagnostica va en 0 %. Formativa y sumativa reparten '
                    'el 100 % del semestre entre todos los cortes.')
        elif suma > 100.5:
            add(GRAVE, 'ponderacion',
                'Con %d corte(s) las ponderaciones ya suman %.1f %%.'
                % (n_cortes, suma), detalle, '')
        else:
            add(LEVE, 'ponderacion',
                'Planeacion parcial: %d corte(s) que suman %.1f %% del semestre.'
                % (n_cortes, suma), detalle,
                'Verificar que al completar los cortes restantes se llegue a 100 %.')

    # 8. Cultura Digital en tercer semestre
    sem = _norm(str((spec.get('identificacion') or {}).get('semestre', '')))
    if 'tercer' in sem or sem.strip() in ('3', '3o', '3.o'):
        for ruta, txt in piezas:
            if 'cultura digital' in _norm(txt):
                add(GRAVE, 'transversalidad',
                    'Se cita Cultura Digital en un programa de tercer semestre.',
                    ruta, T.AVISO_CULTURA_DIGITAL)

    return hallazgos


ORDEN = {GRAVE: 0, MEDIO: 1, LEVE: 2}


def informe(hallazgos, archivo):
    L = []
    L.append('=' * 70)
    L.append('VALIDACION DE LA PLANEACION DIDACTICA')
    L.append('=' * 70)
    L.append('Archivo: %s' % archivo)
    L.append('')
    if not hallazgos:
        L.append('Sin hallazgos. La planeacion pasa las 8 reglas.')
        return '\n'.join(L)

    n = {k: 0 for k in ORDEN}
    for h in hallazgos:
        n[h['nivel']] += 1
    L.append('%s grave(s) · %s medio(s) · %s leve(s)'
             % (n[GRAVE], n[MEDIO], n[LEVE]))
    L.append('')
    for h in sorted(hallazgos, key=lambda x: (ORDEN[x['nivel']], x['regla'])):
        L.append('[%-5s] %s' % (h['nivel'], h['detalle']))
        if h['donde']:
            L.append('         donde: %s' % h['donde'])
        if h['arreglo']:
            L.append('         %s' % h['arreglo'])
        L.append('')
    L.append('-' * 70)
    L.append('Los GRAVE impiden entregar. Los MEDIO se corrigen antes de')
    L.append('enviar a validacion. Los LEVE quedan a criterio docente.')
    return '\n'.join(L)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.stderr.write(__doc__)
        sys.exit(2)
    with open(args[0], 'rb') as f:
        spec = json.loads(f.read().decode('utf-8'))
    h = revisar(spec)
    if '--json' in sys.argv:
        sys.stdout.write(json.dumps(h, ensure_ascii=False, indent=2))
    else:
        sys.stdout.write(informe(h, args[0]))
    sys.stdout.write('\n')
    sys.exit(1 if any(x['nivel'] == GRAVE for x in h) else 0)


if __name__ == '__main__':
    main()
