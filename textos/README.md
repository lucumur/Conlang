# Biblioteca de Textos

La fuente de datos de la sección [Textos](../textos.html) es `textos/index.json`.
Este archivo es **independiente** del índice léxico generado `lexico/index.json`.
Los textos acordados se incorporan a esta colección. El primero es «Marko», con cuatro segmentos paralelos en esperanto y conlang.

## Estructura

```json
{
  "schema_version": 1,
  "textos": [
    {
      "id": "identificador-unico",
      "titulo": "Título que verá el lector",
      "titulo_original": "Título en el idioma original",
      "idioma_original": "Español",
      "autor": "Autor del original",
      "traductor": "Nombre del traductor",
      "fuente": "Referencia bibliográfica o enlace",
      "licencia": "Información de derechos, si procede",
      "notas": "Nota opcional sobre el texto",
      "parrafos": [
        {
          "original": "Primer párrafo en el idioma original.",
          "traduccion": "Primer párrafo en el conlang.",
          "enlaces": [
            {"indice": 0, "vocablo_id": "lexeme-id-existente"}
          ]
        }
      ]
    }
  ]
}
```

El ejemplo anterior **solo ilustra la estructura** y no debe añadirse al
catálogo como traducción canónica. La colección admite varios textos y
varios pares de párrafos por texto. Se conserva el orden de los párrafos.

## Enlaces de las palabras traducidas

La página tokeniza la cadena `traduccion` conservando espacios y puntuación:

- Si la forma de una palabra coincide de manera inequívoca con un vocablo
  registrado en `lexico/index.json` (sin distinguir mayúsculas/minúsculas),
  enlaza directamente a `vocablos.html#lexeme-...`.
- Si la forma no está registrada o existen varias entradas con la misma
  grafía, enlaza a `vocablos.html?q=...` para buscarla sin atribuirle
  arbitrariamente una raíz o un significado.
- Si la forma del texto es una variante, una forma flexionada o una homógrafa,
  se puede fijar la referencia exacta mediante `enlaces`:
  `indice` es el **índice de palabra a partir de 0 dentro de ese párrafo**,
  sin contar espacios ni puntuación, y `vocablo_id` es el identificador
  canónico del vocablo `lexeme-...`. Ese identificador debe existir en el
  léxico. La referencia explícita tiene prioridad sobre la coincidencia
  textual.
- Los textos del idioma original se presentan sin enlaces automáticos,
  porque sus palabras no pertenecen necesariamente al vocabulario del conlang.
- Las formas flexionadas que no figuran como entradas independientes pueden
  enlazar a su **base léxica** mediante `enlaces`: por ejemplo, un plural
  puede enlazar a su singular, o un participio al predicado del que procede.
  Se puede añadir `nota` a la referencia para explicar esa relación en el
  título del enlace.
- Para nombres propios o palabras que deliberadamente no deben abrir ninguna
  búsqueda, añadir `sin_enlace: [{"indice": 0, "motivo": "Nombre propio"}]`
  al párrafo. La palabra se conserva sin enlace en la traducción.

Las traducciones no se generan automáticamente: únicamente se muestran las
que se consignen en este archivo. No duplicar entradas léxicas aquí. Revisar
la autorización para reproducir el texto original y añadir una fuente y una
licencia cuando corresponda.

## Edición desde la página

Con el modo edición activo, la página Textos muestra **+ Nuevo texto** y, en
cada texto, **✎ Editar texto**. El formulario tiene dos columnas, original y
traducción, con una línea por renglón; ambas deben tener el mismo número de
líneas. Debajo, cada palabra de la traducción aparece con su estado de enlace
(fijado, automático, sin identificar, sin enlace o vocablo inexistente); al
pulsarla se puede fijar el vocablo con una nota opcional, marcarla sin enlace
o devolverla a la coincidencia automática. Al editar una línea, los enlaces
fijados de las palabras que no cambiaron se conservan.
