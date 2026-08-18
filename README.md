# Prompts de outbound que no colapsan en plantilla

Puedes leer tres mensajes generados por IA, ver que los tres suenan a persona, y estar
mandando el mismo mensaje 47 veces. **El colapso es una propiedad del lote, no del mensaje.**
Solo se encuentra contando.

Esto es el método para escribir prompts que no colapsan, más un medidor para comprobarlo antes
de lanzar.

## 1. Qué hace

- **`references/colapso-de-plantilla.md`**: los seis disfraces con los que este fallo aparece,
  cada uno con su tasa medida, y la distinción que lo arregla de verdad.
- **`references/reglas-de-escritura.md`**: las reglas de redacción que sobreviven a escala.
- **`medir-colapso.py`**: lee tus mensajes ya generados y te dice si el lote colapsó, con
  umbrales calibrados sobre 296 mensajes reales.
- **`SKILL.md`**: si usas Claude con skills, esto se instala como skill y te acompaña a
  escribir el prompt.

## 2. Qué necesita

| | |
|---|---|
| El medidor | **Python 3.8 o superior. Nada más.** Solo librería estándar, sin dependencias |
| La skill | Claude con soporte de skills (Claude Code, por ejemplo) |
| Cuentas, tokens, API | **Ninguno.** No se conecta a ningún sitio |

Eso vale para todo lo que hay aquí dentro. Lo que sí necesita cuenta es el paso siguiente,
llevarte el prompt a tu plataforma de outbound, y ahí conviene leer antes la sección 7.

## 3. Cómo se instala

Todo vive en la carpeta `prompts-que-no-colapsan/`, que es autocontenida.

**El medidor**, que no necesita instalación:

```bash
cd prompts-que-no-colapsan && python3 medir-colapso.py ejemplo-lote.csv
```

**La skill**, si usas Claude Code:

```bash
cp -R prompts-que-no-colapsan ~/.claude/skills/
```

Abre una sesión nueva y pídele «ayúdame a escribir el prompt de mi secuencia de outbound».
Antes de la primera vez, rellena `references/tu-contexto.md`.

## 4. Qué esperar la primera vez

Corre el medidor sobre el lote de ejemplo, que viene colapsado a propósito:

```bash
cd prompts-que-no-colapsan && python3 medir-colapso.py ejemplo-lote.csv
```

Tiene que darte **APERTURA 80,0% 🔴 BLOQUEA**, veredicto NO LANZAR y código de salida 1. Si te
da eso, funciona.

Sobre tus mensajes de verdad, en CSV con una fila por mensaje:

```bash
python3 medir-colapso.py mis-mensajes.csv
```

Si tus columnas se llaman `mensaje` y `empresa` (o `message` y `company`), las encuentra solas.
Si se llaman de otra forma, dilo:

```bash
python3 medir-colapso.py mis-mensajes.csv --columna texto_final --empresa cuenta
```

**Una regla para las dos banderas: si nombras una columna que no existe, el medidor para.** No
te busca un sustituto, porque hacerlo sería medir otra cosa sin decírtelo. Para también si el
nombre de una de las columnas **que va a medir** aparece repetido en tu cabecera, porque
entonces ese nombre no identifica ninguna columna y mediría la última sin que se notara. Los
nombres repetidos en columnas que no mide no le estorban: tu export puede traer dos `Email` y
lo mide igual. Y la cabecera del informe **te dice siempre sobre qué columnas ha medido**:

```
  COLAPSO DE PLANTILLA · 296 mensajes
  texto: 'mensaje'   ·   empresa: 'empresa'
```

Mírala. Es la línea que te dice de un vistazo si has medido lo que creías.

Un lote sano se va al 1-5% de apertura. Un lote roto se va al 26%, al 33% o al 95%.

## 5. Modo de prueba y topes

**El medidor solo lee.** No escribe archivos, no sale a la red y no toca ninguna plataforma.
No hay nada que pueda romper, y por eso no lleva dry-run: es dry-run entero.

Devuelve **código de salida 1 si bloquea**, para que puedas encadenarlo en un guion de
pre-lanzamiento:

```bash
python3 medir-colapso.py lote.csv || echo "no lanzar"
```

⚠️ Un **VEREDICTO PARCIAL**, que es el que sale cuando pasa la apertura pero no hay datos de
empresa para correr la prueba de pares, **también devuelve 0** y la cadena lo deja pasar. Es a
propósito: bloquear por falta de datos convertiría esto en una alarma que suena siempre, y una
alarma que suena siempre deja de informar. Si tu guion de pre-lanzamiento exige la medición
entera, lo que tiene que hacer es darle la columna de empresa, no confiar en el código de
salida.

## 6. Dónde NO funciona

- **Con menos de 8 mensajes el porcentaje no significa nada.** Una muestra de 10 llegó a decir
  10-30% cuando la verdad sobre 49 mensajes era del 95%. El medidor te avisa, pero no te lo
  impide.
- **Los umbrales están calibrados sobre campañas en español.** En otro idioma, con otro modelo
  o con otro formato de mensaje hay que volver a medir antes de fiarse del 15%.
- **El recorte de saludo está afinado para saludos en español e inglés.** Si tus mensajes
  abren de otra forma, revisa la lista `SALUDOS` dentro del script.
- **No arregla la entregabilidad.** Un mensaje perfecto desde un dominio quemado no llega
  igual.
- **No mide si el mensaje convierte.** Mide si es el mismo mensaje repetido. Son cosas
  distintas: un lote sano puede convertir fatal por otras razones.
- **No sirve para variables de scoring ni de cualificación.** Solo texto de mensaje.

## 7. Si luego lo creas en Enginy

Este paquete no toca Enginy: escribe el prompt y mide el lote, y ahí se acaba. Pero cuando te
lleves el prompt a la plataforma para crear la variable por API o por MCP, hay cosas que
te van a morder. Las pongo aquí porque descubrirlas a mitad de camino cuesta una tarde.

**Cada una lleva de dónde sale**, porque no están verificadas igual y eso importa más que el
aviso en sí.

### `{previousMessage}`: comprueba dónde funciona antes de diseñar la secuencia

La especificación pública dice que los marcadores genéricos de conversación como
`previousMessage` **no se admiten**. Lo que no queda claro es **sobre qué entidad**: el texto
aparece descrito sobre la de investigación, que es justo la que NO se usa para copy de
outbound.

O sea que puede ser una restricción menor o puede tumbarte todos los follow-ups que citan el
mensaje anterior. **Compruébalo con una llamada antes de diseñar una secuencia que dependa de
ello**, porque si falla, esos pasos hay que hacerlos en el editor de campaña.

> Comprobado el 17-ago-2026 contra la especificación pública. **No verificado en producto, y
> el alcance real está sin zanjar.** Este aviso decía en su primera versión que los follow-ups
> «no se pueden crear desde fuera», dicho en plano. Se ha suavizado al ver que la restricción
> podía ser de otra entidad: es el fallo de comprobar la métrica que uno supone en vez de la
> que el texto usa.

### Son cuatro entidades distintas, y se parecen mucho

No hay una cosa llamada «AI Variable». Hay cuatro, y confundirlas da error:

| Entidad | Para qué es |
|---|---|
| `ai-variables` | Investigación sobre el contacto o la empresa |
| `ai-messages` | **El copy de outbound.** Es la que quieres para esto |
| `ai-snippets` | Fragmentos reutilizables |
| `message-templates` | Plantillas de mensaje |

El error típico es escribir un prompt de mensaje y crearlo como `ai-variables`, que es el
nombre que suena a lo que quieres y es el que no lo es.

> Comprobado el 17-ago-2026 contra la especificación pública de la API.
> **No verificado en producto.**

### Las tres últimas devuelven 403 sin el «AI variable split»

`ai-messages`, `ai-snippets` y `message-templates` responden **403** si el workspace no tiene
activada esa función. Y el mensaje es explícito: `AI variable split is not enabled for this
workspace`.

Si te sale, no es un problema de permisos ni de tu clave: es una función que no está activa en
tu espacio, y se pide.

> **Este sí está verificado en producto**, con ese 403 literal recibido en una cuenta real.
> Es el único de los tres del que puedo decir eso.

### Y una advertencia de permisos si conectas por MCP

Si conectas el servidor MCP desde un cliente de agentes, comprueba **qué ámbitos pide antes de
aprobar**: algunos clientes no dejan elegirlos y piden todos los que el servidor publique. En
una cuenta que gestione varios espacios de clientes, eso puede incluir el permiso de **saltar
entre cuentas**, que nunca debería estar vivo en una sesión de agente.

**El mínimo real para lo de esta guía son tres ámbitos:** escritura de AI Variables, que
arrastra la lectura, más lectura de contactos y de empresas, que son la única forma de
descubrir qué tokens de campo existen. Y conviene saber la cesión que eso implica: esos dos
permisos de lectura **abren todos tus contactos y todas tus empresas**, no solo el catálogo de
campos. No hay ámbito más estrecho. Lo digo aquí en vez de escondértelo.

> Comprobado el 17-ago-2026 contra los metadatos que publica el servidor. **La lista real de
> herramientas no la ha visto nadie todavía**, así que no te fíes de ningún nombre concreto de
> herramienta hasta conectarte y pedirla.

## Sobre los datos

Las tasas y los umbrales salen de tres campañas propias de 2026, medidos sobre 296 mensajes
reales. **Son datos míos, no una norma del sector.** Mídelos en tu cuenta antes de tratarlos
como tuyos.
