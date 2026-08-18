# Los casos que ya han mordido

```bash
python3 casos/correr.py
```

Sale 0 si pasan todos, 1 si falla alguno. Sin dependencias, como el medidor.

**Esto no viaja con el artefacto.** Vive fuera de `prompts-que-no-colapsan/`, que es lo que se
descarga el lector y que tiene que seguir siendo autocontenido.

## Por qué existe

El medidor lleva seis tandas de arreglos, y cinco fallaron de la misma manera: cada una montó
sus CSV a mano, comprobó el caso que la motivaba, y los tiró. La siguiente empezaba de cero, así
que volvía a caer en la clase de al lado sin enterarse. El resumen honesto de esas cinco:

| Tanda | Arreglaba | Y dejaba viva |
|---|---|---|
| B2 | `--empresa company` en la documentación | la misma clase en `--columna` |
| A6 | `--empresa` inexistente ya para | `--columna` seguía siendo permisiva |
| Veredicto parcial | el verde sin prueba de pares | hizo el verde **más** afirmativo, agravando lo anterior |
| N1 y N2 | `--columna` estricta, cabecera que dice qué mide | los nombres repetidos |
| N9 | el nombre repetido | se negaba a medir exports sanos con duplicados ajenos |

Ninguna se detectó sola. Las cinco las encontró una lectura de fuera, después de que la tanda se
hubiera dado por buena.

## Cómo se añade un caso

Un caso es una entrada en la lista `CASOS` de `correr.py`, con su lote en `lotes/`:

```python
{
    "nombre": "qué comprueba, en una línea",
    "porque": "de dónde salió. Esto es obligatorio",
    "lote": "mi-lote.csv",
    "flags": ["--columna", "texto"],
    "exit": 1,
    "contiene": ["un trozo de la salida"],
    "no_contiene": ["algo que no debería aparecer"],
}
```

Tres reglas, las tres aprendidas a base de fallar:

1. 🔴 **Comprueba que la cadena que busca una aserción existe de verdad en alguna salida del
medidor.** Una que no aparezca nunca no falla jamás: se queda en verde para siempre sin proteger
nada, y no da ni un aviso. Ha pasado dos veces, las dos al reescribir el texto que la aserción
vigilaba, y las dos veces en el mismo commit que lo reescribía. El barrido es mecánico: por cada
cadena de `contiene` y `no_contiene`, búscala en los literales de `medir-colapso.py`. Si solo
vive en un comentario, está muerta.

**Añade el caso ANTES de dar el arreglo por bueno.** Si no, el arreglo se queda y la prueba
   no, que es exactamente cómo llegamos hasta aquí.
2. **Añade también el caso contrario**, el que comprueba que no te has pasado de freno. La mitad
   de estos casos son de eso. Un arreglo que se niega a medir lotes sanos no es un arreglo.
3. **Afirma sobre el comportamiento, no sobre la redacción.** Un `contiene` con la frase entera
   del mensaje falla cuando alguien mejora el texto, y entonces la suite culpa al commit
   equivocado. Pasó al montar esto.

## Que la suite tenga dientes

Una suite que pasa a la primera no ha demostrado nada. La pregunta no es si pasa: es **si se
enteraría de que el medidor se ha roto**.

Eso es lo que hace `mutantes.py`, y viaja con el repo:

```bash
python3 casos/mutantes.py
```

Rompe el medidor de 10 formas distintas, una por una, y exige que la suite **falle** con
cada una. Las 10:

| Qué se rompe |
|---|
| apertura sin descontar el saludo |
| pares sin descontar el saludo |
| el umbral de apertura nunca bloquea |
| el umbral de apertura bloquea siempre |
| la apertura mira 1 palabra en vez de 8 |
| el n-grama interno pasa a 1 |
| los pares de compañeros no se calculan |
| no avisa con menos de 8 mensajes |
| la nota de avisos vuelve a imprimirse siempre |
| la nota vuelve a explicar las dos metricas siempre |

Tiene que decir **10/10 muertos**. Si alguno sobrevive, hay un fallo que tus tests no
verían, y lo que importa es cuál: el propio script te lo nombra.
