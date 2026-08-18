# Reglas de escritura

Aplican a todo prompt y a todo mensaje generado desde él, en cualquier campaña y canal.

## La prueba de escritura humana, que es la regla maestra

Antes de dar por bueno cualquier ejemplo o mensaje generado:

> «¿Mandaría un comercial de verdad este mensaje exacto desde su cuenta personal, con su
> nombre puesto, sin editarlo antes?»

Si no, se reescribe. Todas las demás reglas están al servicio de esta.

## Prohibida la raya larga, sin excepciones

Nunca uses una raya larga («—») en un prompt, en un ejemplo ni en un mensaje generado. **Es la
señal más clara de texto escrito por IA.** Sustitúyela por una coma, un punto o una frase
nueva.

(El guion normal está bien en su uso corriente. Lo prohibido es la raya.)

## Aperturas prohibidas

Se reconocen al instante como automatizadas:

- «Espero que este mensaje te encuentre bien»
- «Me he topado con tu perfil»
- «Quería ponerme en contacto contigo»
- «He visto que...» como apertura genérica y pelada
- «Como [cargo], seguramente...»
- Cualquier saludo seguido de una línea de contexto que no dice nada concreto

## Palabras y muletillas prohibidas

Una persona vendiendo en dos minutos no escribe como una nota de prensa:

- innovador, puntero, revolucionar, disruptivo, llevar al siguiente nivel
- sinergia, apalancar, potenciar, empoderar, optimizar (como comodín)
- «encantado de compartir», «me hace mucha ilusión»
- «en el mundo actual, tan cambiante», «ahora más que nunca»
- «tomar un café virtual», «robarte cinco minutos», «picarte la cabeza»

No es una lista cerrada, es la **textura** a evitar. Si una palabra hace que el mensaje suene
a marketing en vez de a persona, fuera.

## Cero invención

Nunca inventes datos sobre el contacto ni sobre su empresa. Si una señal de personalización no
está disponible de verdad, cae a un ángulo por rol.

**Un solo detalle inventado** («me encantó tu post sobre X» cuando no hubo tal post) **destruye
la credibilidad en el instante en que se nota.**

Y el prompt tiene que degradar con elegancia: en producción los datos van a faltar a menudo,
así que las INSTRUCCIONES deben decir qué hacer cuando falten.

## Política de idioma

Orden de decisión, salvo que se fije otra cosa:

1. El idioma que fija la campaña.
2. Si no, el idioma por defecto de quien opera.
3. Si no, el idioma del titular del contacto.
4. Si no, el de su última publicación.
5. Si sigue sin estar claro, inglés.

**Declara solo los idiomas en los que vas a mandar de verdad.** Listar alguno «por si acaso»
no hace la variable más segura, la hace **menos** segura: le da permiso al modelo para cambiar
de idioma con una señal débil, como escribir en francés porque el contacto tiene un apellido
extranjero. Si la campaña es de un solo idioma, dilo y prohíbe cambiar.

## Convenciones naturales en español (España)

Un mensaje tiene que leerse como si **un nativo lo hubiera escrito rápido en el móvil**, no
como una traducción. El español «correcto» de libro suele leerse como automático.

- **Tuteo siempre.** Nunca «usted».
- **Fuera la apertura de `¿` y `¡`**, y se queda solo el cierre. Es la señal más clara de que
  esto lo ha escrito una persona en un chat: `vi que estáis creciendo, tiene sentido?`, no
  `¿Tiene sentido?`.
- **Nada de conectores ni cierres burocráticos**: «Asimismo», «Por consiguiente», «Quedo a la
  espera de su respuesta», «Reciba un cordial saludo». Gritan plantilla.
- Las aperturas naturales sí valen («oye», «te leo mucho sobre...»). Lo que se prohíbe como
  relleno es «aquí tienes» o «te cuento», no un arranque conversacional.
- **Nunca traduzcas literalmente modismos de outbound en inglés.** Si una frase suena a
  traducida, reescríbela como la dirías de verdad.

## Tono y longitud

- Corto gana a largo. Fuera toda palabra que no se gane el sitio.
- **Una idea por mensaje.**
- **Una pregunta como máximo.**
- Cierra de forma natural, sin relleno de despedida.
