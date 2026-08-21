#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extrae del programa las evidencias de cada desarrollo: conocimientos, desempenos,
productos e instrumentos.

ES LA PARTE MAS DIFICIL DE ESTA SKILL. Costo siete intentos y conviene no
reescribirla desde cero sin leer esto antes.

Por que es dificil: los programas oficiales no comparten maquetacion. En unos, el
desempeno ocupa una fila propia bajo su encabezado; en otros vive en la MISMA
fila del desarrollo, en columnas contiguas; y en otros el encabezado se parte
entre dos paginas. Cualquier analizador afinado contra un archivo pierde datos en
el vecino, y los pierde EN SILENCIO, que es lo grave: una evidencia atribuida a
la meta equivocada no la detecta nadie al revisar el documento final.

Que NO funciona, comprobado:
  - Leer el texto plano del PDF. Al aplanarlo, las columnas se pegan y los
    conocimientos de un desarrollo terminan en el vecino, o en el corte siguiente.
  - Emparejar por indice de columna. pdfplumber reconstruye un numero distinto de
    columnas en cada tabla, asi que el indice del encabezado no coincide con el
    del contenido. Ese error llego a poner en la columna de Producto el texto de
    la Actividad clave y una progresion del curriculum fundamental.

Que si funciona: correr TRES analizadores con supuestos distintos y unir sus
resultados campo por campo, quedandose con el primer valor no vacio. Ninguno
cubre los seis programas por si solo; juntos si.

  A) por fila:    el encabezado Desempenos/Productos abre la fila siguiente.
  B) por columna: la fila del desarrollo ya trae las evidencias al lado.
  C) por lectura: las celdas alternan desempeno y producto tras el encabezado,
                  y el bloque pertenece al ultimo desarrollo numerado visto.

Despues de extraer, SIEMPRE pasar el control de calidad: un conocimiento es
nominal y un desempeno abre con verbo en tercera persona. Lo que no cumpla eso
esta en la columna equivocada.

Uso:
    python extraer_evidencias.py "programa.pdf" --corte 1
    python extraer_evidencias.py "programa.pdf" --todos --json salida.json
"""

import os, re, io, json, sys
import pdfplumber

SP = os.path.dirname(os.path.abspath(__file__))

NUM = re.compile(r'^\s*(\d)\.\s+[A-ZÁÉÍÓÚ]')
RUIDO = re.compile(r'^(Desarrollo de la|competencia laboral|Evidencias|Meta espec|Conocimientos?|'
                   r'Desempe[ñn]os?|Productos?|Instrumentos?|Corte \d|Carga horaria|'
                   r'Actividad clave|Meta de aprendizaje|b[áa]sica|\d{1,3})\s*$', re.I)
ES_DES = re.compile(r'^Desempe[ñn]os?$', re.I)
ES_PRO = re.compile(r'^Productos?$', re.I)
ES_CON = re.compile(r'^Conocimientos?$', re.I)
ES_INS = re.compile(r'^Instrumentos?$', re.I)

CAMPOS = ('conocimiento', 'desempeno', 'producto', 'instrumentos')


def lim(c):
    return re.sub(r'\s+', ' ', (c or '')).strip()


def vinetas(t):
    t = lim(t)
    if not t:
        return ''
    t = re.sub(r'\s*•\s*', '\n• ', t)
    return re.sub(r'\n{2,}', '\n', t).strip()


def nueva():
    return {k: '' for k in CAMPOS}


def paginas(pdf, n, modelo):
    ini = fin = None
    pat_ini = re.compile(r'Corte\s+%d\.[\s\S]{0,170}?Carga\s+horaria' % n, re.I)
    pat_fin = (re.compile(r'Transversalidad\s+corte\s+%d' % n, re.I) if modelo == 'asignatura'
               else re.compile(r'Transversalidad\s+corte\s+de\s+aprendizaje\s+%d' % n, re.I))
    for i, pg in enumerate(pdf.pages):
        t = pg.extract_text() or ''
        if ini is None and pat_ini.search(t):
            ini = i
        if ini is not None and fin is None and pat_fin.search(t):
            fin = i
            break
    if ini is None:
        return []
    return list(range(ini, (fin if fin is not None else ini + 4) + 1))


def filas(pdf, n, modelo):
    for pi in paginas(pdf, n, modelo):
        for tb in (pdf.pages[pi].extract_tables() or []):
            if len(tb) < 2:
                continue
            for f in tb:
                celdas = [lim(c) for c in f]
                llenas = [(j, c) for j, c in enumerate(celdas) if c]
                if llenas:
                    yield llenas


def _pon(f, campo, txt):
    v = vinetas(txt)
    if v and not f[campo]:
        f[campo] = v


# --------------------------------------------------------------------- A
def parser_a(pdf, n, modelo):
    """El encabezado Desempenos/Productos anuncia la fila siguiente."""
    res, actual, esperando = {}, None, None
    for llenas in filas(pdf, n, modelo):
        texto_fila = ' '.join(c for _, c in llenas)
        cols = {}
        for j, c in llenas:
            if ES_DES.match(c):
                cols['desempeno'] = j
            elif ES_PRO.match(c):
                cols['producto'] = j
        solo_enc = all(ES_DES.match(c) or ES_PRO.match(c) or RUIDO.match(c)
                       for _, c in llenas)
        if cols and solo_enc:
            if esperando and esperando[0] == 'dp':
                cols = dict(esperando[1], **cols)   # encabezado partido entre paginas
            esperando = ('dp', cols)
            continue
        if all(ES_INS.match(c) for _, c in llenas):
            esperando = ('ins', None)
            continue

        mnum = next(((j, c) for j, c in llenas if NUM.match(c)), None)
        if mnum:
            j0, txt = mnum
            actual = int(txt.strip()[0])
            res.setdefault(actual, nueva())
            otras = [(j, c) for j, c in llenas
                     if j != j0 and not RUIDO.match(c) and len(c) > 20]
            if esperando and esperando[0] == 'dp':
                _reparte(res[actual], otras, esperando[1])
            elif otras:
                _pon(res[actual], 'conocimiento', max(otras, key=lambda x: len(x[1]))[1])
            esperando = None
            continue

        if not actual or actual not in res:
            continue
        f = res[actual]
        if esperando and esperando[0] == 'dp':
            _reparte(f, llenas, esperando[1])
            esperando = None
        elif esperando and esperando[0] == 'ins':
            vals = [c for _, c in llenas if 4 < len(c) < 70 and not RUIDO.match(c)]
            if vals and not f['instrumentos']:
                f['instrumentos'] = ' / '.join(dict.fromkeys(vals))
            esperando = None
        else:
            for _, c in llenas:
                if not RUIDO.match(c) and len(c) > 20 and c.startswith('•'):
                    f['conocimiento'] = (f['conocimiento'] + '\n' + vinetas(c)).strip()
                    break
    return res


def _reparte(f, llenas, cols):
    cd, cp = cols.get('desempeno'), cols.get('producto')
    for j, c in llenas:
        if RUIDO.match(c) or NUM.match(c) or len(c) < 12:
            continue
        if cd is not None and cp is not None:
            campo = 'desempeno' if abs(j - cd) <= abs(j - cp) else 'producto'
        elif cd is not None:
            campo = 'desempeno'
        elif cp is not None:
            campo = 'producto'
        else:
            continue
        _pon(f, campo, c)


# --------------------------------------------------------------------- B
def parser_b(pdf, n, modelo):
    """La fila del desarrollo ya trae conocimiento, desempeno y producto."""
    res, actual, cols, tras_ins = {}, None, {}, False
    for llenas in filas(pdf, n, modelo):
        nuevas = {}
        for j, c in llenas:
            if ES_CON.match(c):
                nuevas['conocimiento'] = j
            elif ES_DES.match(c):
                nuevas['desempeno'] = j
            elif ES_PRO.match(c):
                nuevas['producto'] = j
        if nuevas and all(RUIDO.match(c) for _, c in llenas):
            cols.update(nuevas)      # el mapa se acumula entre filas y paginas
            tras_ins = False
            continue
        if all(ES_INS.match(c) for _, c in llenas):
            tras_ins = True
            continue

        mnum = next(((j, c) for j, c in llenas if NUM.match(c)), None)
        if mnum:
            actual = int(mnum[1].strip()[0])
            res.setdefault(actual, nueva())
        if not actual or actual not in res:
            continue
        f = res[actual]

        if tras_ins:
            vals = [c for _, c in llenas if 4 < len(c) < 70 and not RUIDO.match(c)]
            if vals and not f['instrumentos']:
                f['instrumentos'] = ' / '.join(dict.fromkeys(vals))
            tras_ins = False
            continue

        if not cols:
            continue
        for j, c in llenas:
            if RUIDO.match(c) or NUM.match(c) or len(c) < 12:
                continue
            campo = min(cols, key=lambda k: abs(j - cols[k]))
            _pon(f, campo, c)
    return res



# --------------------------------------------------------------------- C
def parser_c(pdf, n, modelo):
    """Por orden de lectura: el bloque pertenece al ultimo desarrollo visto y
    dentro de el las celdas alternan desempeno y producto."""
    res, ancla, cola, idx = {}, None, [], 0

    def f(k):
        return res.setdefault(k, nueva())

    def add(k, campo, txt):
        v = vinetas(txt)
        if not v:
            return
        d = f(k)
        if not d[campo]:
            d[campo] = v
        elif v not in d[campo]:
            d[campo] = (d[campo] + '\n' + v).strip()

    for llenas in filas(pdf, n, modelo):
        for _, c in llenas:
            if NUM.match(c):
                # El encabezado de Conocimientos aparece ANTES del numero, asi que
                # el ancla no borra el modo vigente: solo reinicia la alternancia.
                ancla = int(c.strip()[0]); f(ancla); idx = 0; continue
            if ES_CON.match(c):
                cola, idx = ['conocimiento'], 0; continue
            if ES_DES.match(c):
                cola = ['desempeno', 'producto'] if 'producto' not in cola else cola
                idx = 0; continue
            if ES_PRO.match(c):
                if cola != ['desempeno', 'producto']:
                    cola = ['producto']
                idx = 0; continue
            if ES_INS.match(c):
                cola, idx = ['instrumentos'], 0; continue
            if ancla is None or not cola or RUIDO.match(c):
                continue
            if cola == ['instrumentos']:
                if 4 < len(c) < 70:
                    add(ancla, 'instrumentos', c)
                continue
            if len(c) <= 20:
                continue
            add(ancla, cola[idx % len(cola)], c); idx += 1
    return res


# ------------------------------------------------------------------ union
INSTRUMENTO = re.compile(
    r'^(gu[íi]a de observaci[óo]n|lista de cotejo|r[úu]brica[^\n]{0,20}|'
    r'escala estimativa|cuestionario)$', re.I)

# Restos de la tabla vecina que se cuelan al final de una celda.
COLA_AJENA = re.compile(
    r'\n\s*(Componentes: fundamental|Habilidades para (la Vida|el)|Asignatura\b|'
    r'Empoderamiento|Empleabilidad|Ciudadan[íi]a|Aprendizaje\b|Desarrollo Sostenible|'
    r'competencia laboral b[áa]sica|Para saber m[áa]s)[\s\S]*$', re.I)

ARRANQUE = re.compile(r'^•?\s*[A-ZÁÉÍÓÚ]')


def depurar(v):
    """Limpia una ficha de evidencias de los restos que arrastra el PDF."""
    for campo in ('conocimiento', 'desempeno', 'producto'):
        t = v.get(campo) or ''
        if not t:
            continue
        t = COLA_AJENA.sub('', t)
        t = re.sub(r'\*+', '', t).strip()
        # la primera linea puede ser la cola de la celda anterior
        lineas = t.split('\n')
        if len(lineas) > 1 and not ARRANQUE.match(lineas[0]) and ARRANQUE.match(lineas[1]):
            t = '\n'.join(lineas[1:]).strip()
        v[campo] = t
    ins = v.get('instrumentos') or ''
    if ins:
        buenos = [x.strip() for x in re.split(r'[\n/]', ins) if INSTRUMENTO.match(x.strip())]
        v['instrumentos'] = ' / '.join(dict.fromkeys(buenos))
    return v


def evidencias_corte(pdf, n, modelo):
    """Union de los tres analizadores, campo por campo, ya depurada."""
    partes = [parser_a(pdf, n, modelo), parser_b(pdf, n, modelo), parser_c(pdf, n, modelo)]
    claves = sorted(set().union(*[set(p) for p in partes]))
    union = {}
    for k in claves:
        ficha = nueva()
        for campo in CAMPOS:
            for p in partes:
                val = (p.get(k) or {}).get(campo) or ''
                if val:
                    ficha[campo] = val
                    break
        union[k] = depurar(ficha)
    return union


VERBO_3A = re.compile(r'^•?\s*[A-ZÁÉÍÓÚ][a-záéíóúñ]+[ae]\b')


def control_de_calidad(union):
    """Un conocimiento es nominal; un desempeno abre con verbo en 3.a persona.

    Devuelve la lista de celdas que estan en la columna equivocada. No corrige
    sola: reportar es mas seguro que adivinar en un documento oficial.
    """
    avisos = []
    for k, v in sorted(union.items()):
        if v['desempeno'] and not VERBO_3A.match(v['desempeno']):
            avisos.append('Desarrollo %s: el desempeno no abre con verbo en 3.a persona.' % k)
        if v['conocimiento'] and VERBO_3A.match(v['conocimiento']):
            avisos.append('Desarrollo %s: el conocimiento abre con verbo; parece un desempeno.' % k)
    return avisos


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        sys.stderr.write(__doc__)
        sys.exit(2)
    ruta = args[0]
    modelo = 'asignatura' if '--asignatura' in sys.argv else (
        'uac' if '--uac' in sys.argv else None)
    if modelo is None:
        sys.stderr.write('Indica el modelo con --uac o --asignatura '
                         '(lo determina antes scripts/detectar_modelo.py).\n')
        sys.exit(2)
    cortes = [1, 2, 3] if '--todos' in sys.argv else [
        int(sys.argv[sys.argv.index('--corte') + 1]) if '--corte' in sys.argv else 1]

    salida = {}
    with pdfplumber.open(ruta) as pdf:
        for n in cortes:
            u = evidencias_corte(pdf, n, modelo)
            salida[str(n)] = {str(k): v for k, v in u.items()}
            marcas = []
            for k, v in sorted(u.items()):
                m = ''.join(x for x, c in (('C', 'conocimiento'), ('D', 'desempeno'),
                                           ('P', 'producto'), ('I', 'instrumentos'))
                            if v[c])
                marcas.append('%s:%s' % (k, m or '-'))
            print('Corte %d -> %s' % (n, ' '.join(marcas) or '(sin evidencias)'))
            for aviso in control_de_calidad(u):
                print('   [revisar] %s' % aviso)

    if '--json' in sys.argv:
        destino = sys.argv[sys.argv.index('--json') + 1]
        io.open(destino, 'w', encoding='utf-8').write(
            json.dumps(salida, ensure_ascii=False, indent=1))
        print('\nGuardado en %s' % destino)


if __name__ == '__main__':
    main()
