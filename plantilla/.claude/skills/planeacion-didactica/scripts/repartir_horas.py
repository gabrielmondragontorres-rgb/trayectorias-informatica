#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reparte la carga horaria de cada corte entre sus actividades, y verifica que la
suma sea EXACTAMENTE la que declara el programa.

Nace de un error real. En la primera version los tiempos se escribian a mano al
redactar cada actividad, y el conjunto de seis planeaciones acabo asignando 526
horas donde los programas autorizaban 432: un 22 % de mas. Nadie lo noto leyendo
el documento, porque los bloques sueltos de dos o tres horas parecen razonables;
solo aparece al sumar.

Y hay una trampa adicional que costo una hora de diagnostico: si el tiempo de la
evaluacion repite el de su actividad, el conteo se infla al doble. En apertura y
desarrollo la evaluacion ocurre DENTRO de la actividad y no consume tiempo
propio; solo la evidencia sumativa del cierre se aplica aparte.

Uso:
    python repartir_horas.py 30 --actividades 4
    python repartir_horas.py 30 --actividades 4 --primer-corte
    python repartir_horas.py --verificar planeacion.json
"""

import sys
import json
import re


def texto_horas(n):
    return '1 hora' if n == 1 else '%d horas' % n


def leer_horas(t):
    """Sumar las horas declaradas en una cadena como '3 horas' o '90 minutos'."""
    t = (t or '').lower()
    h = sum(float(x) for x in re.findall(r'(\d+(?:[.,]\d+)?)\s*hora', t.replace(',', '.')))
    m = sum(float(x) for x in re.findall(r'(\d+)\s*min', t))
    return h + m / 60.0


def repartir(total, n_actividades, primer_corte=False):
    """Distribuye las horas del corte entre sus cuatro momentos.

    Criterios: la apertura del primer corte lleva una hora mas porque incluye el
    encuadre de la asignatura; el cierre toma alrededor de un sexto de la carga,
    repartido entre la actividad de integracion y la aplicacion de la evidencia
    sumativa; la retroalimentacion cierra con una o dos horas segun el tamano
    del corte; y el resto se reparte entre las actividades del desarrollo, que
    absorben cualquier residuo para que la suma cuadre al entero.
    """
    if n_actividades < 1:
        raise ValueError('El desarrollo necesita al menos una actividad.')
    apertura = 3 if primer_corte else 2
    retro = 2 if total >= 24 else 1
    cierre = max(3, round(total * 0.16))
    disponible = total - apertura - retro - cierre
    if disponible < n_actividades:
        raise ValueError(
            'No caben %d actividades en %d horas de desarrollo. Reduce el numero '
            'de actividades o revisa la carga del corte.' % (n_actividades, disponible))

    base, resto = divmod(disponible, n_actividades)
    desarrollo = [base + (1 if i < resto else 0) for i in range(n_actividades)]

    # el cierre se parte entre la actividad de integracion y la evidencia sumativa
    act_cierre = max(1, cierre - max(1, cierre // 2))
    ev_cierre = cierre - act_cierre

    reparto = {
        'total': total,
        'apertura': apertura,
        'desarrollo': desarrollo,
        'cierre_actividad': act_cierre,
        'cierre_evaluacion': ev_cierre,
        'retroalimentacion': retro,
    }
    suma = apertura + sum(desarrollo) + act_cierre + ev_cierre + retro
    if suma != total:
        raise AssertionError('El reparto suma %d y el corte declara %d.' % (suma, total))
    return reparto


def informe(r):
    L = ['Carga del corte: %d horas' % r['total'], '']
    L.append('  Apertura                 %s' % texto_horas(r['apertura']))
    for i, h in enumerate(r['desarrollo'], 1):
        L.append('  Desarrollo, actividad %-2d %s' % (i, texto_horas(h)))
    L.append('  Cierre, actividad        %s' % texto_horas(r['cierre_actividad']))
    L.append('  Cierre, evidencia        %s' % texto_horas(r['cierre_evaluacion']))
    L.append('  Retroalimentacion        %s' % texto_horas(r['retroalimentacion']))
    L.append('')
    L.append('  SUMA                     %d horas  (coincide con el programa)' % r['total'])
    return '\n'.join(L)


# --------------------------------------------------------------------------
# Verificacion sobre una planeacion ya armada
# --------------------------------------------------------------------------

def verificar(spec):
    """Comprueba corte por corte que lo planeado sea lo que el programa autoriza."""
    fallos = []
    total_prog = total_plan = 0.0
    for c in spec.get('cortes', []):
        declara = leer_horas(c.get('horas_corte'))
        usadas = 0.0
        sin_tiempo = 0
        for f in ('apertura', 'desarrollo', 'cierre'):
            fase = c.get(f) or {}
            for a in (fase.get('actividades') or []):
                usadas += leer_horas(a.get('tiempo'))
                if not (a.get('tiempo') or '').strip():
                    sin_tiempo += 1
            usadas += leer_horas((fase.get('evaluacion') or {}).get('tiempo'))
        rt = (c.get('cierre') or {}).get('retroalimentacion')
        if rt:
            usadas += leer_horas(rt.get('tiempo'))

        total_prog += declara
        total_plan += usadas
        if declara and abs(usadas - declara) > 0.01:
            fallos.append('Corte %s: el programa declara %.0f h y la planeacion asigna %.0f h (%+.0f).'
                          % (c.get('numero', '?'), declara, usadas, usadas - declara))
        if sin_tiempo:
            fallos.append('Corte %s: %d actividad(es) sin tiempo declarado.'
                          % (c.get('numero', '?'), sin_tiempo))
    return fallos, total_prog, total_plan


def main():
    args = sys.argv[1:]
    if '--verificar' in args:
        ruta = args[args.index('--verificar') + 1]
        with open(ruta, 'rb') as f:
            spec = json.loads(f.read().decode('utf-8'))
        fallos, tp, tl = verificar(spec)
        print('Programa: %.0f h   Planeacion: %.0f h' % (tp, tl))
        if fallos:
            print('')
            for x in fallos:
                print('  [FALLA] %s' % x)
            print('')
            print('Los tiempos se derivan de la carga del programa, no se escriben a mano.')
            sys.exit(1)
        print('Sin descuadres. La planeacion cabe exactamente en la carga autorizada.')
        return

    if not args:
        print(__doc__)
        return
    total = int(args[0])
    n = 3
    if '--actividades' in args:
        n = int(args[args.index('--actividades') + 1])
    print(informe(repartir(total, n, '--primer-corte' in args)))


if __name__ == '__main__':
    main()
