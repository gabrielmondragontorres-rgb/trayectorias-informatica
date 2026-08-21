#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fuente unica de verdad del vocabulario de los dos modelos.

Un programa por UAC (Modelo 2023) y uno por Asignatura (Modelo Educativo 2025)
nombran las mismas piezas con palabras distintas. La planeacion didactica tiene
que hablar el idioma del programa que la origina, o el documento delata que se
copio una plantilla ajena.

Uso como consulta:
    python terminologia.py uac
    python terminologia.py asignatura
    python terminologia.py --equivalencias
    python terminologia.py --traducir "metas especificas"
"""

import sys
import unicodedata


# Etiquetas de los campos de la planeacion, por modelo.
UAC = {
    'modelo': 'uac',
    'etiqueta_modelo': 'Programa por UAC (Modelo 2023)',
    'unidad': 'UAC',
    'unidad_larga': 'Unidad de Aprendizaje Curricular',
    'proposito': 'Propósito de UAC',
    'meta_corte': 'Meta de aprendizaje',
    'desarrollos': 'Metas específicas',
    'transversal_fundamental': 'UAC',
    'transversal_vinculo': 'Progresión(es)',
    'sostenible': 'Conceptos Centrales de la Educación para el Desarrollo Sostenible',
    'sostenible_corto': 'CoCEDS',
    'estrategia': 'Instrumentación didáctica',
    'fase_apertura': 'Apertura',
    'fase_desarrollo': 'Desarrollo',
    'fase_cierre': 'Cierre',
    'fuentes': 'Para saber más…',
    'carga_tipica': '80 horas (3.º a 5.º) o 32 horas (6.º)',
}

ASIGNATURA = {
    'modelo': 'asignatura',
    'etiqueta_modelo': 'Programa por Asignatura (Modelo Educativo 2025)',
    'unidad': 'Asignatura',
    'unidad_larga': 'Asignatura',
    'proposito': 'Resultado de aprendizaje',
    'meta_corte': 'Actividad clave de la competencia laboral básica',
    'desarrollos': 'Desarrollo de la competencia laboral básica',
    'transversal_fundamental': 'Asignatura',
    'transversal_vinculo': 'Propósito(s) formativo(s)',
    'sostenible': 'Habilidades para el Desarrollo Sostenible',
    'sostenible_corto': 'HDS',
    'estrategia': 'Estrategia didáctica',
    'fase_apertura': 'Fase de apertura',
    'fase_desarrollo': 'Fase de desarrollo',
    'fase_cierre': 'Fase de cierre',
    'fuentes': 'Fuentes de información',
    'carga_tipica': '64 horas en todos los semestres (4 h semanales, 8 créditos)',
}

MODELOS = {'uac': UAC, 'asignatura': ASIGNATURA}


# Traduccion literal Plan 2023 -> Modelo 2025. Se usa para detectar residuos:
# si una planeacion por asignatura contiene la clave izquierda, esta copiando
# vocabulario derogado.
EQUIVALENCIAS = [
    ('Unidad de Aprendizaje Curricular', 'Asignatura'),
    ('UAC', 'Asignatura'),
    ('Propósito de la UAC', 'Resultado de aprendizaje'),
    ('Meta de aprendizaje', 'Actividad clave de la competencia laboral básica'),
    ('Metas específicas', 'Desarrollo de la competencia laboral básica'),
    ('Progresiones de aprendizaje', 'Propósitos formativos'),
    ('Instrumentación didáctica', 'Estrategia didáctica'),
    ('Conceptos Centrales de la Educación para el Desarrollo Sostenible',
     'Habilidades para el Desarrollo Sostenible'),
    ('CoCEDS', 'HDS'),
    ('Para saber más', 'Fuentes de información'),
    ('Apertura / Desarrollo / Cierre',
     'Fase de apertura / Fase de desarrollo / Fase de cierre'),
    ('80 h (3.º-5.º) / 32 h (6.º)', '64 h en todos los semestres'),
]


# Lo que NO cambia entre modelos. Traducir estos terminos es el error inverso,
# y ocurre: no todo lo que suena a Plan 2023 esta derogado.
NO_SE_TRADUCEN = [
    ('Competencia laboral básica',
     'Se conserva en su redacción literal. Es la pieza intocable: todos los '
     'ajustes se hacen sobre los demás elementos.'),
    ('Producto o proyecto integrador',
     'Vigente en el Modelo 2025 como elemento de la estrategia didáctica, con '
     'sus criterios de evaluación. No es vocabulario derogado.'),
    ('Trayectoria Ocupacional Básica (TOB)',
     'Se conserva en los dos modelos.'),
    ('Habilidades para la Vida y el Trabajo (HVyT)',
     'Se conserva en los dos modelos, con el mismo catálogo de 12.'),
    ('Evidencias de conocimiento, desempeño y producto',
     'Se conservan. El Modelo 2025 añade la exigencia de declarar el '
     'instrumento con que se evalúa cada una.'),
    ('Nota de portada "elaborado con base en el Programa de la Unidad de '
     'Aprendizaje Curricular"',
     'Referencia histórica legítima en un programa por asignatura. Conservar.'),
]


# Catalogos cerrados. Nombrar algo que no este aqui es el error mas frecuente
# y el mas dificil de ver, porque los terminos inventados suenan verosimiles.
HABITOS = ['organización', 'puntualidad', 'perseverancia', 'autoevaluación']
VALORES = ['responsabilidad', 'respeto', 'honestidad', 'compromiso', 'solidaridad']
ACTITUDES = ['iniciativa', 'flexibilidad', 'empatía', 'colaboración',
             'actitud positiva']

HVYT = [
    'regulación de emociones', 'autoconocimiento', 'comunicación',
    'logro de metas', 'autonomía', 'toma de decisiones',
    'resolución de problemas', 'mentalidad de crecimiento', 'creatividad',
    'empatía', 'conciencia social', 'trabajo en equipo y colaboración',
]

HDS = ['Nexo Agua-Energía-Alimento', 'Servicios Ecosistémicos',
       'Sistemas Socio-ecológicos', 'Economía Ecológica']

# Suenan al marco y no pertenecen a ningun catalogo.
FALSOS_AMIGOS = [
    'ética profesional', 'responsabilidad ambiental y social',
    'trabajo colaborativo', 'comunicación efectiva',
    'innovación y mejora de procesos', 'uso responsable de la tecnología',
]

# "Pensamiento critico" es legitimo como descripcion del enfoque de la Nueva
# Escuela Mexicana. Solo es error presentarlo como una de las doce HVyT.
MATIZ_PENSAMIENTO_CRITICO = (
    'Pensamiento crítico: válido como descripción pedagógica general del '
    'enfoque NEM. Solo constituye error cuando se presenta como una de las '
    'doce habilidades del catálogo HVyT. Leer el contexto antes de corregir.'
)

# Componente fundamental de tercer semestre, con claves.
FUNDAMENTAL_3 = [
    ('913', 'Lengua y Comunicación III'),
    ('923', 'Inglés III'),
    ('933', 'Pensamiento Matemático III'),
    ('963', 'Ciencias Sociales III'),
    ('973', 'Pensamiento Filosófico y Humanidades III'),
    ('983', 'Ciencias Naturales, Experimentales y Tecnología III'),
]

AVISO_CULTURA_DIGITAL = (
    'Cultura Digital NO se cursa en tercer semestre: solo llega a 2.º (claves '
    '941 y 942), y Cultura Digital III corresponde a 6.º. Toda referencia '
    'heredada a Cultura Digital III en un programa de 3.º debe sustituirse.'
)


def obtener(modelo):
    clave = (modelo or '').strip().lower()
    if clave not in MODELOS:
        raise ValueError(
            'Modelo desconocido: %r. Valores validos: uac, asignatura.' % modelo)
    return MODELOS[clave]


def _norm(t):
    t = ''.join(c for c in unicodedata.normalize('NFD', t)
                if unicodedata.category(c) != 'Mn')
    return t.lower().strip()


def traducir(termino):
    """Devuelve el equivalente en Modelo 2025, o None si no aplica."""
    n = _norm(termino)
    for viejo, nuevo in EQUIVALENCIAS:
        if _norm(viejo) == n:
            return nuevo
    for fijo, motivo in NO_SE_TRADUCEN:
        if _norm(fijo).startswith(n) or n in _norm(fijo):
            return 'NO SE TRADUCE. %s' % motivo
    return None


def _mostrar(d):
    ancho = max(len(k) for k in d)
    for k in sorted(d):
        print('  %-*s  %s' % (ancho, k, d[k]))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    arg = sys.argv[1]
    if arg == '--equivalencias':
        print('Plan 2023 (UAC)  ->  Modelo 2025 (Asignatura)')
        print('-' * 72)
        for v, n in EQUIVALENCIAS:
            print('  %-52s -> %s' % (v, n))
        print('')
        print('NO se traducen:')
        for f, m in NO_SE_TRADUCEN:
            print('  %s' % f)
            print('      %s' % m)
    elif arg == '--traducir':
        if len(sys.argv) < 3:
            print('Falta el termino.')
            return
        r = traducir(sys.argv[2])
        print(r if r else 'Sin equivalencia registrada: %r' % sys.argv[2])
    elif arg == '--catalogos':
        print('Habitos (CONOCER):   %s' % ', '.join(HABITOS))
        print('Valores (CONOCER):   %s' % ', '.join(VALORES))
        print('Actitudes (CONOCER): %s' % ', '.join(ACTITUDES))
        print('HVyT (12):           %s' % ', '.join(HVYT))
        print('HDS (4):             %s' % ', '.join(HDS))
        print('')
        print('NO pertenecen a ningun catalogo, aunque lo parezcan:')
        for f in FALSOS_AMIGOS:
            print('   - %s' % f)
        print('')
        print(MATIZ_PENSAMIENTO_CRITICO)
    else:
        _mostrar(obtener(arg))


if __name__ == '__main__':
    main()
