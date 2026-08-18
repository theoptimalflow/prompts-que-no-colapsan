# El colapso de plantilla: el fallo que no ves leyendo tres ejemplos

Cualquier prompt puede pasar la prueba de escritura humana en un mensaje suelto y aun así ser
un mail merge a lo largo del lote. **El colapso es una propiedad del lote, no del mensaje.**
Solo se encuentra contando.

Todo lo de aquí está medido sobre tres campañas propias de 2026, 296 mensajes reales.

---

## 1. La ley: lo que escribes en el prompt, el modelo lo escribe en el mensaje

Ha mordido **seis veces**, cada una con un disfraz distinto. El patrón siempre es el mismo:
algún texto del prompt aporta las *palabras*, y el modelo las reutiliza.

| # | Qué había en el prompt | Qué salió | Tasa |
|---|---|---|---|
| 1 | Frases ancla listadas como «buenas aperturas» | Esas frases exactas | casi todo el lote |
| 2 | Una lista de «cierres válidos alternativos» | Las alternativas, literales | 4 de 10 |
| 3 | Un EJEMPLO rico y vívido | El ejemplo, casi palabra por palabra | 9 de 10 |
| 4 | La palabra «punto» dentro de INSTRUCCIONES | «hay un punto que...» | 8 de 10 |
| 5 | `"Pregunta QUIÉN se encarga de que eso no pase"` | «quién se encarga de...» | **47 de 49** |
| 6 | Un EJEMPLO que abría `"Marta, te escribo por aquí por si..."` | Esa apertura | **10 de 10** |

**Los casos 4 y 5 son los importantes.** Prueban que la contaminación no vive solo en el bloque
de EJEMPLOS, que es donde mira todo el mundo: **las INSTRUCCIONES enseñan igual de fuerte.** Un
prompt que dice «pregunta QUIÉN se encarga» no describe un objetivo, dicta una frase.

### La distinción que lo arregla

- **Las restricciones positivas dictan palabras.** «Pregunta QUIÉN se encarga», «abre con lo
  que has aprendido», «empieza la pregunta por con qué, dónde o qué usáis». Producen mensajes
  idénticos. **Fuera.**
- **Las negativas separan variantes sin dictar.** «NO empieces la pregunta por quién, esa forma
  es de otra variante». Son baratas y seguras. **Se quedan.**

Describe la **función** («cierra devolviéndoles la pregunta») y deja que el modelo elija las
palabras. Y luego añade un bloque de PROHIBIDO POR REPETICIÓN con las **frases literales que
mediste**, no con las que te imaginas.

> ⚠️ No escribas un prompt que se refiera a una lista de prohibiciones que no existe. Cuatro
> prompts terminaban diciendo *«comprueba que no has usado ninguna fórmula de la lista PROHIBIDO
> POR REPETICIÓN»* y **esa lista nunca estuvo en el prompt**. Comprobaban contra nada.

### Lo que NO funciona

- **Prohibir más fuerte.** La v2 de un prompt decía explícitamente que afirmar cierta cosa
  estaba PROHIBIDO, y el modelo lo hizo **82 veces**. Con 50 instrucciones compitiendo, la 51
  es ruido. El arreglo fue **quitar la munición** (los atributos que se la daban), no prohibir
  más.
- **Rotar ángulos con una regla dentro del prompt.** Cuatro ángulos asignados por el número de
  letras del nombre: cumplió **2 veces de 10**. Los modelos no hacen aritmética de forma
  fiable. Si necesitas variedad de *forma*, ramifica **fuera** del prompt, con una condición
  de la secuencia.
- **Prohibir frases a secas.** Mueve el colapso, no lo quita. Tras banear los cierres viejos,
  una variable se inventó uno nuevo y lo usó en el **41%** del lote. **Vuelve a medir siempre
  después de un arreglo.**

---

## 2. Segmentar concentra la repetición

La contraintuitiva. Partir un prompt en cuatro variantes por segmento te compra determinismo
(el mensaje correcto llega a la persona correcta, decidido por un campo y no por el modelo)
pero **empeora la repetición dentro de cada segmento**, porque ahora 49 personas comparten un
prompt en vez de tirar de un pool general.

Y empeora más si haces las variantes distinguibles **fijándole a cada una su forma de
pregunta**, que es justo la manera intuitiva de hacerlo, y justo lo que produjo el 95%.

Distingue las variantes por **de qué realidad hablan** y por **tono**. Nunca por un comienzo
de frase fijo.

---

## 3. Cómo se mide

Tres sitios, porque cada uno tiene su punto ciego:

- **Apertura**: primeras 8 palabras. 🔴 **Punto ciego: si la parte que varía va primero, diez
  mensajes con el mismo esqueleto pasan por distintos.** En español pasa siempre, porque
  delante van el saludo y el nombre. Hay que quitarlos antes de contar.
- **Cierre**: últimas 5 palabras.
- **Interno**: el 4-grama más repetido en cualquier parte del cuerpo.

### Umbrales, calibrados sobre 296 mensajes reales, no elegidos a ojo

| | lotes malos | lotes buenos | veredicto |
|---|---|---|---|
| **apertura** | 26 / 33 / 95 % | 1 / 2 / 3 / 4 / 5 % | **bloquea al 15%** |
| interno (4-grama) | 41 / 83 / 95 % | 18 a 38 % | solo avisa |
| cierre | | ~34 % en lotes que se leen bien | solo avisa |

**La apertura separa limpio; las otras dos no.** Un cierre es formulario por naturaleza y un
4-grama repetido al 25% es lenguaje normal. Aplicar el 15% a las tres hacía saltar todas las
variables a la vez, y una alarma que suena siempre deja de informar. Bloquea por la apertura,
informa del resto.

### 🔴 Mide el lote entero, y mide entre compañeros

- **Una muestra de 10 miente.** Las muestras decían 10-30% cuando la verdad sobre 49 mensajes
  era del 95%. Con menos de 8 el porcentaje no significa nada.
- **La prueba más dura es entre dos contactos de la misma empresa**, porque son los únicos que
  pueden comparar sus mensajes de verdad. Una repetición agregada de apertura del 2% escondía
  que el **77% de los pares de compañeros compartían las dos primeras palabras**, y el 14% las
  cinco primeras. Arreglar el prompt lo dejó en **0%**.

Todo esto lo cuenta `medir-colapso.py`, incluida la prueba de pares.

---

## 4. El bloque de EJEMPLOS, bien hecho

Efecto medido, tres iteraciones, cambiando una sola cosa cada vez:

1. Un ejemplo rico → **90%** copiado.
2. Tres ejemplos cortos de sectores distintos → **30%**.
3. Quitar además el sustantivo contaminante de las INSTRUCCIONES → **10%**.

Así que: **tres ejemplos cortos, de sectores distintos, que empiecen de formas visiblemente
diferentes**, más una línea explícita diciendo que los ejemplos ilustran la FORMA y que está
prohibido reutilizar sus sustantivos, sus situaciones o su primera línea.

Si los tres ejemplos abren con el mismo movimiento, el modelo aprende el movimiento aunque no
copie ninguna frase.
