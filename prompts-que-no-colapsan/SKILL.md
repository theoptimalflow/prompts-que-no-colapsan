---
name: prompts-que-no-colapsan
description: >-
  Escribe prompts para secuencias de outbound (LinkedIn y email: invitaciones, InMails, correos
  en frío, seguimientos) que producen mensajes que suenan a persona y que NO colapsan en
  plantilla a lo largo del lote, y audita lotes ya generados para detectar el colapso contando
  en vez de leyendo. Úsala cuando alguien quiera escribir, mejorar o depurar un mensaje o una
  variable de IA de outbound, cuando pida que algo "no suene a bot", o cuando quiera comprobar
  antes de lanzar si sus mensajes generados son en realidad el mismo mensaje repetido. NO la
  uses para entregabilidad de correo, para enriquecer o exportar contactos, para variables de
  scoring o cualificación, para posts de tu propio perfil, ni para correos internos.
---

# Prompts de outbound que no colapsan

**El colapso es una propiedad del lote, no del mensaje.** Puedes leer tres mensajes perfectos y
estar mandando el mismo 47 veces. Toda esta skill existe para eso.

## Lee esto antes de escribir nada

1. `references/colapso-de-plantilla.md`: los seis disfraces del fallo, medidos sobre campañas reales,
   y la distinción entre restricciones positivas y negativas. **Vinculante.**
2. `references/reglas-de-escritura.md`: las reglas que sobreviven a escala.
3. `references/tu-contexto.md`: rellénalo con tu empresa y tu voz antes de la primera vez.

## Cómo se escribe un prompt aquí

**La regla maestra:** ¿mandaría un comercial de verdad este mensaje exacto desde su cuenta
personal, con su nombre puesto, sin editarlo antes? Si no, se reescribe.

**La estructura:** un prompt largo en CONTEXTO y corto en INSTRUCCIONES. Al revés es como se
colapsa, porque cada instrucción de más es vocabulario que el modelo va a reutilizar.

1. **CONTEXTO.** Quién manda el mensaje y qué vende de verdad, investigado, no en plantilla.
   Aquí sí puedes extenderte: el contexto informa sin dictar palabras.
2. **INSTRUCCIONES.** Describe la **función** de cada parte, nunca sus palabras. «Cierra
   devolviéndoles la pregunta», no «pregunta QUIÉN se encarga».
3. **IDIOMA.** Solo los idiomas en los que vas a mandar de verdad. Ninguno «por si acaso».
4. **EJEMPLOS.** Tres, cortos, de sectores distintos, que abran de formas visiblemente
   diferentes, más una línea diciendo que ilustran la FORMA y que reutilizar sus sustantivos,
   sus situaciones o su primera línea está prohibido.
5. **PROHIBIDO POR REPETICIÓN.** Las frases literales que **mediste**, no las que te imaginas.
   Y si el bloque no existe, no lo menciones: hubo cuatro prompts comprobando contra una lista
   que nunca estuvo ahí.

## Cómo se audita un lote

Nunca por muestreo. **Una muestra de 10 miente.**

```bash
python3 medir-colapso.py mis-mensajes.csv
```

Encuentra solo las columnas de texto y de empresa. Si las nombras tú (`--columna`, `--empresa`)
y no existen, para en vez de medir otra. **Lee siempre la cabecera del informe**, que dice sobre
qué columnas ha medido: es donde se ve si has medido lo que creías.

Bloquea al 15% de repetición de apertura. El cierre y el 4-grama interno solo informan, porque
un cierre es formulario por naturaleza. Y ejecuta siempre la prueba de **pares de compañeros**,
que es la que más colapso destapa: son los únicos que pueden comparar sus mensajes de verdad.

## Guardrails

- **NUNCA metas en el prompt las palabras que quieres leer en el mensaje.** Es la ley, y ha
  mordido seis veces.
- **NUNCA arregles un colapso prohibiendo más fuerte.** Con 50 instrucciones compitiendo, la
  51 es ruido: una prohibición explícita se saltó 82 veces. Quita la munición, no añadas reglas.
- **NUNCA des por bueno un arreglo sin volver a medir.** Prohibir frases mueve el colapso: al
  banear los cierres viejos apareció uno nuevo al 41%.
- **NUNCA inventes un dato del contacto.** Uno solo destruye la credibilidad al notarse.
- **NUNCA uses raya larga.** Ni en el prompt, ni en los ejemplos, ni en el mensaje.
- **NUNCA rotes variantes con una regla aritmética dentro del prompt.** Cumplió 2 de 10.
