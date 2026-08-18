#!/usr/bin/env python3
"""
Mide el colapso de plantilla en un lote de mensajes generados.

El colapso es una propiedad del LOTE, no del mensaje: puedes leer tres mensajes
perfectos y estar mandando el mismo 47 veces. Esto lo cuenta.

No toca ninguna API, no envía nada y no escribe en ningún sitio. Lee un archivo
y escribe un informe por pantalla.

Uso:
    python3 medir-colapso.py mensajes.csv
    python3 medir-colapso.py mensajes.csv --columna texto_final --empresa cuenta
    python3 medir-colapso.py mensajes.txt --formato txt

Formatos:
    csv  Una fila por mensaje. Si no nombras las columnas, busca el texto entre
         "mensaje", "message", "texto" y "body", y la empresa entre "empresa" y
         "company". Si SÍ las nombras y no existen, para: nunca mide una columna
         distinta de la que le has pedido. La cabecera del informe dice siempre
         sobre qué columnas ha medido.
    txt  Mensajes separados por una línea con tres guiones (---). Sin columnas,
         así que la prueba de pares de compañeros no se puede ejecutar.
"""

import argparse
import csv
import re
import sys
from collections import Counter

# Umbrales calibrados sobre 296 mensajes reales, no elegidos a ojo.
# La apertura separa limpio; las otras dos no, porque un cierre es formulario
# por naturaleza y un 4-grama al 25% es lenguaje normal.
UMBRAL_APERTURA_BLOQUEA = 0.15
UMBRAL_AVISO = 0.40
PALABRAS_APERTURA = 8
PALABRAS_CIERRE = 5
N_GRAMA = 4
MINIMO_FIABLE = 8


# El punto ciego de la métrica de apertura: si la parte que varía va PRIMERO,
# diez mensajes con el mismo esqueleto pasan por distintos. En español eso pasa
# siempre, porque delante va el saludo y el nombre de pila. Sin quitarlos, un
# lote con 8 de 10 mensajes calcados mide 10% de repetición y pasa el corte.
SALUDOS = (
    "hola", "buenas", "hey", "oye", "qué tal", "que tal", "buenos días",
    "buenos dias", "buenas tardes", "hi", "hello", "hola de nuevo",
)
_NOMBRE = r"[A-ZÁÉÍÓÚÜÑ][\wáéíóúüñ'’-]*"
_RE_SALUDO = re.compile(
    r"^\s*(?:"
    # saludo (insensible a mayúsculas) y, si lo hay, el nombre que lo sigue
    r"(?i:" + "|".join(SALUDOS) + r")\b[\s,]*(?:" + _NOMBRE + r"\b)?"
    r"|"
    # o un vocativo suelto: "Marta, ..." . Exige la coma para no comerse
    # la primera palabra real de frases como "Vi que abristeis sede".
    + _NOMBRE + r"\s*,"
    r")?[\s,.:;!¡¿?-]*",
    flags=re.UNICODE,
)


def quitar_saludo(texto):
    """Quita un saludo inicial y el nombre de pila que lo sigue, si los hay."""
    recortado = _RE_SALUDO.sub("", texto or "", count=1)
    # Si el recorte se lo come casi todo, algo ha ido mal: devuelve el original.
    return recortado if len(recortado) > 20 else (texto or "")


def normalizar(texto, sin_saludo=False):
    """Minúsculas y solo palabras. Los signos no cuentan para la repetición."""
    if sin_saludo:
        texto = quitar_saludo(texto)
    return re.findall(r"\w+", (texto or "").lower(), flags=re.UNICODE)


def repeticion(secuencias):
    """Devuelve (fraccion, secuencia_mas_comun, veces) de la más repetida."""
    reales = [s for s in secuencias if s]
    if not reales:
        return 0.0, "", 0
    comun, veces = Counter(reales).most_common(1)[0]
    return veces / len(reales), comun, veces


def n_gramas(palabras, n):
    return [" ".join(palabras[i:i + n]) for i in range(len(palabras) - n + 1)]


def leer_csv(ruta, col_mensaje, col_empresa):
    """
    Devuelve (filas, columna_de_texto, columna_de_empresa).

    Una sola regla para las dos columnas, que es la que faltaba: **un nombre
    que tú escribes y que no existe para el script, siempre.** Buscarle un
    sustituto por tu cuenta es medir otra cosa sin decirlo, y eso ya produjo
    dos falsos verdes: una bandera de empresa mal escrita saltándose la prueba
    de pares, y una de texto mal escrita midiendo una columna de borradores
    viejos y dando por bueno un lote colapsado al 100%.

    None significa "no me la has nombrado". Ahí sí se busca sola, porque no hay
    ninguna intención que contradecir, y lo que se elija se imprime en la
    cabecera para que se vea sobre qué se ha medido.
    """
    filas = []
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        if not lector.fieldnames:
            sys.exit("El CSV no tiene cabecera.")
        disponibles = ", ".join(lector.fieldnames)
        cuenta = Counter(lector.fieldnames)

        # Un nombre vacío no nombra nada. La autodetección ya lo filtra con su
        # `if c`; a mano se rechaza aquí, porque colarlo dejaba `campo` en ''
        # y la cabecera llegaba a decir "bloques separados por ---" sobre un CSV.
        for bandera, valor in (("--columna", col_mensaje), ("--empresa", col_empresa)):
            if valor is not None and not valor.strip():
                sys.exit(f"{bandera} no puede ir vacía.")

        def parar_si_ambigua(nombre, papel):
            """
            Con dos columnas del mismo nombre, DictReader se queda con la
            última: el nombre deja de identificar una columna y ni la cabecera
            de este informe lo destaparía, porque imprime un nombre y el nombre
            es correcto.

            Solo importa en las columnas que se van a MEDIR. Un export con dos
            'Email' de los que no mido ninguno es asunto suyo: negarme a medir
            un lote sano por eso sería romper la herramienta para protegerla.
            """
            if nombre and cuenta[nombre] > 1:
                sys.exit(
                    f"La cabecera del CSV repite '{nombre}', que es la columna "
                    f"de {papel} que iba a medir. Con el nombre repetido me "
                    f"quedaría con la última y mediría otra cosa sin que se "
                    f"notara. Renómbrala antes. Los nombres repetidos en "
                    f"columnas que no mido no me estorban."
                )

        if col_mensaje is None:
            campo = next((c for c in lector.fieldnames if c and c.lower()
                          in ("mensaje", "message", "texto", "body")), None)
            if campo is None:
                sys.exit(
                    f"No encuentro ninguna columna de mensaje. "
                    f"Columnas disponibles: {disponibles}. Indícala con --columna."
                )
        elif col_mensaje in lector.fieldnames:
            campo = col_mensaje
        else:
            sys.exit(
                f"No encuentro la columna '{col_mensaje}'. "
                f"Columnas disponibles: {disponibles}. Si la has escrito mal, "
                f"corrígela; si prefieres que la busque yo, quita --columna. "
                f"Lo que no voy a hacer es medir otra por mi cuenta."
            )
        parar_si_ambigua(campo, "texto")

        if col_empresa is None:
            campo_empresa = next((c for c in lector.fieldnames if c and c.lower()
                                  in ("empresa", "company")), None)
        elif col_empresa in lector.fieldnames:
            campo_empresa = col_empresa
        else:
            sys.exit(
                f"No encuentro la columna de empresa '{col_empresa}'. "
                f"Columnas disponibles: {disponibles}. Sin ella no corre la prueba "
                f"de pares de compañeros, que es la que más colapso destapa. "
                f"Corrige el nombre, o quita --empresa para seguir sin ella."
            )
        parar_si_ambigua(campo_empresa, "empresa")

        for fila in lector:
            texto = (fila.get(campo) or "").strip()
            if texto:
                empresa = ((fila.get(campo_empresa) or "").strip().lower()
                           if campo_empresa else "")
                filas.append((texto, empresa))
    return filas, campo, campo_empresa


def leer_txt(ruta):
    with open(ruta, encoding="utf-8") as f:
        bloques = re.split(r"^\s*-{3,}\s*$", f.read(), flags=re.MULTILINE)
    # Sin columnas: los dos None se lo dicen a la cabecera.
    return [(b.strip(), "") for b in bloques if b.strip()], None, None


def pares_de_companeros(filas):
    """
    La prueba más dura: dos personas de la misma empresa son las únicas que
    pueden comparar sus mensajes de verdad. Un 2% agregado puede esconder que
    el 77% de los pares de compañeros comparten las dos primeras palabras.
    """
    por_empresa = {}
    for texto, empresa in filas:
        if empresa:
            por_empresa.setdefault(empresa, []).append(normalizar(texto, sin_saludo=True)[:2])

    total = coincidencias = 0
    for aperturas in por_empresa.values():
        for i in range(len(aperturas)):
            for j in range(i + 1, len(aperturas)):
                total += 1
                if aperturas[i] and aperturas[i] == aperturas[j]:
                    coincidencias += 1
    return coincidencias, total


def main():
    p = argparse.ArgumentParser(description="Mide el colapso de plantilla de un lote.")
    p.add_argument("archivo")
    p.add_argument("--formato", choices=["csv", "txt"], default="csv")
    p.add_argument("--columna", default=None,
                   help="Columna con el texto (CSV). Si no la pasas se busca sola "
                        "('mensaje', 'message', 'texto' o 'body'); si la pasas y "
                        "no existe, para.")
    p.add_argument("--empresa", default=None,
                   help="Columna de empresa (CSV). Si no la pasas se busca sola "
                        "('empresa' o 'company'); si la pasas y no existe, para.")
    args = p.parse_args()

    # Una bandera que se acepta y luego se ignora es de la misma familia que
    # una que mide otra columna: el script hace algo distinto de lo que le has
    # pedido y no te lo dice.
    if args.formato == "txt" and (args.columna or args.empresa):
        sys.exit("El formato txt no tiene columnas, así que --columna y --empresa "
                 "no aplican. Quítalas, o pasa un CSV.")

    try:
        filas, campo, campo_empresa = (
            leer_csv(args.archivo, args.columna, args.empresa)
            if args.formato == "csv" else leer_txt(args.archivo))
    except FileNotFoundError:
        sys.exit(f"No encuentro el archivo: {args.archivo}")

    if not filas:
        sys.exit("No he encontrado ningún mensaje en el archivo.")

    n = len(filas)
    print(f"\n{'=' * 62}")
    print(f"  COLAPSO DE PLANTILLA · {n} mensajes")
    # Decir SOBRE QUÉ se ha medido. Es la línea que habría hecho visibles de un
    # vistazo los tres falsos verdes que ha tenido este script, sin necesidad
    # de haberlos anticipado uno a uno.
    if campo:
        emp = f"'{campo_empresa}'" if campo_empresa else "ninguna"
        print(f"  texto: '{campo}'   ·   empresa: {emp}")
    else:
        print("  texto: bloques separados por ---   ·   empresa: ninguna")
    print(f"{'=' * 62}")

    if n < MINIMO_FIABLE:
        print(f"\n  ⚠️  AVISO: con menos de {MINIMO_FIABLE} mensajes el porcentaje no")
        print("     significa nada. Una muestra de 10 miente: han llegado a decir")
        print("     10-30% cuando la verdad sobre 49 mensajes era del 95%.\n")

    palabras = [normalizar(t) for t, _ in filas]
    # La apertura se mide SIN el saludo ni el nombre: son la parte que varía y
    # esconden el esqueleto compartido. Ver la nota de SALUDOS arriba.
    aperturas = [normalizar(t, sin_saludo=True)[:PALABRAS_APERTURA] for t, _ in filas]
    frac_ap, ap, veces_ap = repeticion([" ".join(w) for w in aperturas])
    frac_ci, ci, veces_ci = repeticion([" ".join(w[-PALABRAS_CIERRE:]) for w in palabras])
    todos = [g for w in palabras for g in n_gramas(w, N_GRAMA)]
    if todos:
        g_comun, g_veces = Counter(todos).most_common(1)[0]
        frac_in = sum(1 for w in palabras if g_comun in n_gramas(w, N_GRAMA)) / n
    else:
        g_comun, g_veces, frac_in = "", 0, 0.0

    bloquea = frac_ap >= UMBRAL_APERTURA_BLOQUEA

    print(f"\n  APERTURA  ({PALABRAS_APERTURA} primeras palabras)   "
          f"{frac_ap:6.1%}   {'🔴 BLOQUEA' if bloquea else '✅ ok'}   (umbral 15%)")
    print(f'    más repetida ({veces_ap}x): "{ap[:60]}"')
    print(f"\n  CIERRE    ({PALABRAS_CIERRE} últimas palabras)    "
          f"{frac_ci:6.1%}   {'⚠️  aviso' if frac_ci >= UMBRAL_AVISO else '✅ ok'}   (solo informa)")
    print(f'    más repetido ({veces_ci}x): "{ci[:60]}"')
    print(f"\n  INTERNO   ({N_GRAMA}-grama más repetido)    "
          f"{frac_in:6.1%}   {'⚠️  aviso' if frac_in >= UMBRAL_AVISO else '✅ ok'}   (solo informa)")
    print(f'    más repetido ({g_veces}x): "{g_comun[:60]}"')

    coincidencias, total_pares = pares_de_companeros(filas)
    # Dos motivos distintos para no tener número, y no se le dicen igual al
    # usuario: uno es un hueco suyo y el otro es que el lote no da para más.
    pares_medido = total_pares > 0
    hay_empresas = any(empresa for _, empresa in filas)
    if pares_medido:
        frac_pares = coincidencias / total_pares
        print(f"\n  PARES DE COMPAÑEROS ({total_pares} pares en la misma empresa)")
        print(f"    comparten las 2 primeras palabras:  {frac_pares:6.1%}   "
              f"{'🔴' if frac_pares >= UMBRAL_APERTURA_BLOQUEA else '✅'}")
        print("    Es la prueba más dura: son los únicos que pueden compararse.")
        if frac_pares >= UMBRAL_APERTURA_BLOQUEA:
            bloquea = True
    elif hay_empresas:
        print("\n  PARES DE COMPAÑEROS: no hay dos contactos de la misma empresa.")
        print("    Nada que comparar en este lote. No es un fallo tuyo, pero")
        print("    tampoco es evidencia: la prueba no ha llegado a medir nada.")
    elif campo_empresa:
        print(f"\n  PARES DE COMPAÑEROS: la columna '{campo_empresa}' no trae ni")
        print("    un valor. Prueba NO ejecutada, y no por no habérmela pasado.")
    else:
        print("\n  PARES DE COMPAÑEROS: sin columna de empresa, prueba NO ejecutada.")
        print("    Es la que más colapso destapa. Pásala con --empresa <columna>.")

    print(f"\n{'-' * 62}")
    if bloquea:
        print("  VEREDICTO: NO LANZAR.")
        print("  El arreglo no es prohibir más fuerte: es quitar del prompt las")
        print("  restricciones POSITIVAS que dictan palabras. Mira")
        print("  references/colapso-de-plantilla.md, sección 1.")
        if not pares_medido:
            print()
            print("  Y consigue los datos de empresa antes de volver a medir: sin")
            print("  la prueba de pares, el próximo verde no va a valer gran cosa.")
    elif pares_medido:
        print("  VEREDICTO: el lote pasa el corte, con la prueba de pares hecha.")
        # La nota nombra SOLO las metricas que han saltado de verdad. Antes se
        # imprimia siempre, y luego explicaba las dos aunque solo saltara una:
        # las dos veces hablaba de avisos que no estaban en la pantalla.
        # 🔴 La frase de aquí NO puede decir que eso sea normal. El aviso salta
        # al 40%, y la tabla de calibración llama sanos a los lotes de 18 a 38%
        # en el 4-grama y de ~34% en el cierre: cuando esta nota se ve, el lote
        # YA está fuera de la banda buena. La versión anterior justificaba la
        # normalidad citando un 25%, un valor en el que ni siquiera se imprime.
        motivos = []
        if frac_ci >= UMBRAL_AVISO:
            motivos.append("el cierre pasa del ~34% de los lotes que se leen bien")
        if frac_in >= UMBRAL_AVISO:
            motivos.append("el 4-grama pasa del 38% y entra en la banda de los que colapsan")
        if motivos:
            cabeza = ("El aviso de arriba no bloquea" if len(motivos) == 1
                      else "Los avisos de arriba no bloquean")
            print(f"  {cabeza}, y es a propósito: bloquear por tres métricas")
            print(f"  convierte la alarma en ruido. Pero míralo, porque")
            print(f"  {' y '.join(motivos)}.")
    else:
        print("  VEREDICTO PARCIAL: pasa el corte de apertura, pero SIN la prueba")
        print("  de pares de compañeros, que es la que más colapso destapa.")
        print("  Una apertura agregada del 2% llegó a esconder un 77% de pares")
        print("  compartiendo las dos primeras palabras. Esto todavía no es un")
        print("  verde: es la mitad de la medición.")
    print(f"{'-' * 62}\n")
    return 1 if bloquea else 0


if __name__ == "__main__":
    sys.exit(main())
