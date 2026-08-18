#!/usr/bin/env python3
"""
Rompe el medidor a propósito y comprueba si la suite se entera.

    python3 mutantes.py

El criterio de aceptación de una suite NO puede ser que pase. Tiene que ser
cuántos mutantes mata. Los 14 casos de correr.py pasaban en verde mientras se
podía quitar el descontado del saludo de la métrica de apertura, que es el
hallazgo sobre el que descansa el capítulo entero.

Cada mutante lleva escrito qué rompe. Si uno SOBREVIVE, la suite tiene un
agujero justo ahí, y el arreglo es un caso nuevo en correr.py, no bajar el
listón aquí.

Restaura siempre el medidor, incluso si algo revienta.
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MEDIDOR = AQUI.parent / "prompts-que-no-colapsan" / "medir-colapso.py"
CORRER = AQUI / "correr.py"

# (nombre, patrón, reemplazo). Regex sobre el fuente del medidor.
MUTANTES = [
    ("apertura sin descontar el saludo",
     r"(aperturas = \[normalizar\(t, sin_saludo=)True", r"\1False"),
    ("pares sin descontar el saludo",
     r"(por_empresa\.setdefault\(empresa, \[\]\)\.append\(normalizar\(texto, sin_saludo=)True",
     r"\1False"),
    ("el umbral de apertura nunca bloquea",
     r"UMBRAL_APERTURA_BLOQUEA = 0\.15", "UMBRAL_APERTURA_BLOQUEA = 0.99"),
    ("el umbral de apertura bloquea siempre",
     r"UMBRAL_APERTURA_BLOQUEA = 0\.15", "UMBRAL_APERTURA_BLOQUEA = 0.0"),
    ("la apertura mira 1 palabra en vez de 8",
     r"PALABRAS_APERTURA = 8", "PALABRAS_APERTURA = 1"),
    ("el n-grama interno pasa a 1",
     r"N_GRAMA = 4", "N_GRAMA = 1"),
    ("los pares de compañeros no se calculan",
     r"(def pares_de_companeros\(filas\):)", r"\1\n    return 0, 0"),
    ("no avisa con menos de 8 mensajes",
     r"MINIMO_FIABLE = 8", "MINIMO_FIABLE = 0"),
    # La nota de avisos se imprimia siempre en el camino verde, hablando de
    # avisos que no estaban en pantalla. Este mutante deshace la guarda: si
    # sobrevive, es que la suite ya no protege ese arreglo.
    ("la nota de avisos vuelve a imprimirse siempre",
     r"if motivos:", "if True:"),
]


def main():
    if not MEDIDOR.exists():
        sys.exit(f"No encuentro el medidor en {MEDIDOR}")
    fuente = MEDIDOR.read_text(encoding="utf-8")

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(fuente)
        respaldo = f.name

    print(f"\n  {len(MUTANTES)} mutantes contra {CORRER.name}\n")
    vivos = []
    try:
        for nombre, patron, reemplazo in MUTANTES:
            roto, n = re.subn(patron, reemplazo, fuente, count=1)
            if not n:
                print(f"  ⚠️   {nombre}  ·  el patrón ya no existe, mutante obsoleto")
                vivos.append((nombre, "obsoleto"))
                continue
            MEDIDOR.write_text(roto, encoding="utf-8")
            r = subprocess.run([sys.executable, str(CORRER)], capture_output=True, text=True)
            if r.returncode == 0:
                print(f"  🔴  SOBREVIVE  ·  {nombre}")
                vivos.append((nombre, "sobrevive"))
            else:
                print(f"  ✅  muerto     ·  {nombre}")
    finally:
        shutil.copy(respaldo, MEDIDOR)
        Path(respaldo).unlink(missing_ok=True)

    muertos = len(MUTANTES) - len(vivos)
    print(f"\n  {muertos}/{len(MUTANTES)} muertos.")
    if vivos:
        print("\n  La suite NO protege esto:")
        for nombre, estado in vivos:
            print(f"    · {nombre} ({estado})")
        print("\n  Cada superviviente es un caso que falta en correr.py.")
    print()
    return 1 if vivos else 0


if __name__ == "__main__":
    sys.exit(main())
