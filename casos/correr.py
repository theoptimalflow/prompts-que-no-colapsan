#!/usr/bin/env python3
"""
Los casos que ya han mordido a este medidor.

    python3 correr.py

Sale 0 si pasan todos, 1 si falla alguno. Sin dependencias.

Cada caso lleva escrito DE DÓNDE SALIÓ, y eso no es decoración. Este medidor
lleva seis tandas de arreglos y cinco de ellas fallaron igual: cada una montó
sus CSV a mano, probó el caso que la motivaba, y los tiró. La siguiente no
heredaba nada, así que volvía a caer en la clase de al lado sin enterarse.

Cuando arregles algo aquí dentro, **añade su caso antes de dar el arreglo por
bueno**, y añade también el caso contrario: el que comprueba que no te has
pasado de freno. La mitad de los fallos de este archivo son de eso.
"""

import ast
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MEDIDOR = AQUI.parent / "prompts-que-no-colapsan" / "medir-colapso.py"
LOTES = AQUI / "lotes"

CASOS = [
    {
        "nombre": "el lote colapsado bloquea",
        "porque": "es lo que README §4 promete que verás la primera vez",
        "lote": "colapsado.csv",
        "exit": 1,
        "contiene": ["(8 primeras palabras)    80.0%", "NO LANZAR", "texto: 'mensaje'",
                     "comparten las 2 primeras palabras:   80.0%"],
        # 🔴 La aserción va CALIFICADA POR MÉTRICA a propósito. Antes decía
        # solo "80.0%", y este lote imprime 80.0% en las CUATRO métricas, así
        # que no distinguía cuál lo producía: se podía quitar el descontado
        # del saludo de la apertura (el hallazgo que sostiene el capítulo) y
        # los 14 casos seguían en verde.
    },
    {
        "nombre": "el lote sano pasa, y con los pares hechos",
        "porque": "sin este, cualquier freno de más pasa por arreglo",
        "lote": "sano.csv",
        "exit": 0,
        "contiene": ["con la prueba de pares hecha"],
        # Un lote limpio NO puede hablar de avisos: no hay ninguno en pantalla.
        # 🔴 Estas cadenas son el TEXTO REAL de la nota. Si se reescribe la nota
        # hay que reescribirlas: una asercion que busca una frase que ya no
        # existe pasa siempre y deja de proteger sin avisar. Paso una vez.
        "no_contiene": ["no bloquea", "pasa del"],
    },
    {
        "nombre": "verde con UN aviso: la nota nombra solo el que saltó",
        "porque": ("ningún otro lote llega al verde con un aviso saltado, así que "
                   "la nota no se imprimía en toda la suite y se podía romper sin que nadie se enterara"),
        "lote": "verde-con-aviso.csv",
        "exit": 0,
        "contiene": [
            "con la prueba de pares hecha",
            "El aviso de arriba no bloquea",          # singular: solo saltó uno
            "el 4-grama pasa del 38%",                 # y nombra el que saltó
        ],
        # El cierre está en verde: la nota NO puede mencionarlo. Sin esto, se
        # puede volver a explicar las dos métricas aunque solo salte una.
        "no_contiene": ["el cierre pasa del"],
    },
    {
        "nombre": "los pares bloquean aunque la apertura pase",
        "porque": "B2. Apertura al 10% escondiendo el 100% de pares iguales",
        "lote": "pares-ocultos.csv",
        "exit": 1,
        "contiene": ["100.0%", "NO LANZAR"],
    },
    {
        "nombre": "una --empresa mal escrita para",
        "porque": "B2. El README daba --empresa company sobre una columna "
                  "'empresa', y la prueba de pares se saltaba en silencio",
        "lote": "pares-ocultos.csv",
        "flags": ["--empresa", "company"],
        "exit": 1,
        "contiene": ["No encuentro la columna de empresa"],
    },
    {
        "nombre": "sin columna de empresa, veredicto parcial",
        "porque": "addendum 8. Un verde sin la prueba más dura no es un verde",
        "lote": "sin-empresa.csv",
        "exit": 0,
        "contiene": ["VEREDICTO PARCIAL"],
        "no_contiene": ["pares hecha"],
    },
    {
        "nombre": "columna de empresa presente pero vacía: lo dice",
        "porque": "N2. Antes mandaba pasar una bandera que ya habías pasado",
        "lote": "empresa-vacia.csv",
        "exit": 0,
        "contiene": ["no trae ni"],
    },
    {
        "nombre": "'company' en inglés se encuentra sola",
        "porque": "A6. La columna de texto se autodetectaba y la de empresa no",
        "lote": "company-ingles.csv",
        "exit": 1,
        "contiene": ["empresa: 'company'"],
    },
    {
        "nombre": "una --columna mal escrita para",
        "porque": "N1. Medía otra columna candidata en silencio y daba verde "
                  "sobre un lote colapsado al 100%",
        "lote": "dos-textos.csv",
        "flags": ["--columna", "mensaje_finall"],
        "exit": 1,
        "contiene": ["No encuentro la columna 'mensaje_finall'"],
    },
    {
        "nombre": "la cabecera dice qué columna ha medido",
        "porque": "N1. Es la línea que destapa la clase entera de un vistazo",
        "lote": "dos-textos.csv",
        "flags": ["--columna", "mensaje_final"],
        "exit": 1,
        "contiene": ["texto: 'mensaje_final'"],
    },
    {
        "nombre": "un nombre repetido EN la columna medida para",
        "porque": "N9. DictReader se queda con la última, y la cabecera no lo "
                  "veía porque imprime un nombre y el nombre era correcto",
        "lote": "duplicada-medida.csv",
        "exit": 1,
        # "repite" a secas y no la frase entera: afirmar sobre la redacción hace
        # que el caso falle cuando alguien mejora el mensaje, y entonces la
        # suite señala al commit equivocado. Aquí lo que importa es que pare.
        "contiene": ["repite"],
    },
    {
        "nombre": "un nombre repetido FUERA de las medidas no estorba",
        "porque": "el freno de N9 nació demasiado ancho y se negaba a medir "
                  "exports sanos con dos 'Email'. Este es el caso contrario",
        "lote": "duplicada-ajena.csv",
        "flags": ["--columna", "mensaje", "--empresa", "empresa"],
        "exit": 0,
        "contiene": ["con la prueba de pares hecha"],
        "no_contiene": ["repite"],
    },
    {
        "nombre": "el formato txt funciona",
        "porque": "las seis tandas tocaron el camino CSV y ninguna este",
        "lote": "lote.txt",
        "flags": ["--formato", "txt"],
        "exit": 0,
        "contiene": ["bloques separados por ---"],
    },
    {
        "nombre": "txt con banderas de columna para",
        "porque": "N2. Las aceptaba y las ignoraba enteras",
        "lote": "lote.txt",
        "flags": ["--formato", "txt", "--empresa", "X"],
        "exit": 1,
        "contiene": ["El formato txt no tiene columnas"],
    },
    {
        "nombre": "una bandera vacía se rechaza",
        "porque": "N9. Con --columna '' el campo quedaba en '', que es falsy, y "
                  "la cabecera decía 'bloques separados por ---' sobre un CSV",
        "lote": "sano.csv",
        "flags": ["--columna", ""],
        "exit": 1,
        "contiene": ["no puede ir vacía"],
    },
    {
        "nombre": "el 4-grama interno se mide con 4 palabras",
        "porque": "mutantes.py: se podía bajar N_GRAMA a 1 y los 14 casos seguían verdes",
        "lote": "colapsado.csv",
        "exit": 1,
        "contiene": ["(4-grama más repetido)"],
    },
    {
        "nombre": "un lote corto avisa de que el porcentaje no significa nada",
        "porque": "mutantes.py: se podía anular MINIMO_FIABLE sin que nadie se enterara. "
                  "Y es el aviso que impide leer un 95% de una muestra de 5 como si fuera real",
        "lote": "corto.csv",
        "exit": 1,
        "contiene": ["con menos de 8 mensajes el porcentaje no"],
    },
]


def correr(caso):
    """Devuelve (motivos de fallo, salida). Lista vacía = el caso pasa."""
    orden = [sys.executable, str(MEDIDOR), str(LOTES / caso["lote"])]
    orden += caso.get("flags", [])
    r = subprocess.run(orden, capture_output=True, text=True)
    salida = r.stdout + r.stderr

    fallos = []
    if r.returncode != caso["exit"]:
        fallos.append(f"salió con {r.returncode} y esperaba {caso['exit']}")
    for trozo in caso.get("contiene", []):
        if trozo not in salida:
            fallos.append(f"no dice «{trozo}»")
    for trozo in caso.get("no_contiene", []):
        if trozo in salida:
            fallos.append(f"dice «{trozo}» y no debería")
    return fallos, salida


def aserciones_muertas():
    """🔴 Una aserción que busca una frase que el medidor ya no escribe NO FALLA
    NUNCA: se queda en verde para siempre sin proteger nada. Ha pasado tres
    veces, siempre al reescribir el texto que la aserción vigilaba, y siempre en
    el mismo commit que lo reescribía.

    Se comprueba contra el CÓDIGO FUENTE del medidor, no contra la salida de la
    suite, y la distinción importa: un `no_contiene` no aparece en la salida
    normal, para eso está. Lo que sí tiene que poder hacer el medidor es
    ESCRIBIRLO alguna vez, si no la aserción no vigila nada. Una cadena que solo
    vive en un comentario también está muerta: por eso se leen los literales con
    ast y no el fichero entero.
    """
    literales = " ".join(
        n.value for n in ast.walk(ast.parse(MEDIDOR.read_text(encoding="utf-8")))
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    )
    muertas = []
    for caso in CASOS:
        for trozo in caso.get("no_contiene", []):
            if trozo not in literales:
                muertas.append((caso["nombre"], trozo))
    return muertas


def main():
    if not MEDIDOR.exists():
        sys.exit(f"No encuentro el medidor en {MEDIDOR}")

    print(f"\n  {len(CASOS)} casos contra {MEDIDOR.name}\n")
    rotos = []
    for caso in CASOS:
        fallos, _ = correr(caso)
        print(f"  {'✅' if not fallos else '❌'}  {caso['nombre']}")
        if fallos:
            rotos.append(caso)
            for f in fallos:
                print(f"        {f}")
            print(f"        este caso existe porque: {caso['porque']}")

    print()
    muertas = aserciones_muertas()
    if muertas:
        n = len(muertas)
        print(f"  🔴 {n} asercion{'es' if n > 1 else ''} MUERTA{'S' if n > 1 else ''}: "
              f"busca{'n' if n > 1 else ''} algo que el medidor")
        print("     ya no escribe, así que no fallaría nunca.\n")
        for nombre, trozo in muertas:
            print(f"        «{trozo}»")
            print(f"           en el no_contiene de: {nombre}")
        print()

    if rotos or muertas:
        if rotos:
            print(f"  {len(rotos)} de {len(CASOS)} fallan.\n")
        return 1
    print(f"  Los {len(CASOS)} pasan, y ninguna aserción está muerta.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
