# Semantic Model v2 · Arsa & Pisha

## Propósito

Este documento define el modelo semántico usado por Core para distinguir identidad canónica, adaptación permitida, variación, recurrencia, condiciones requeridas, contexto, affordances, intención y evidencia.

El modelo protege significado e identidad; no exige reproducción pixel a pixel.

## 1. Prioridad

Cuando varias reglas se solapen, Core debe aplicar este orden:

1. Decisión canónica explícita y documentada.
2. Invariantes canónicos.
3. Restricciones contextuales o de producción explícitas.
4. Condiciones requeridas.
5. Adaptaciones permitidas.
6. Propiedades variables.
7. Preferencias estilísticas o compositivas.

Una preferencia inferior no puede sobrescribir una regla superior.

## 2. Invariante

Un invariante es una propiedad cuya alteración amenaza la identidad o el canon establecido.

Ejemplos actuales:

### Arsa
- pelaje blanco;
- mechón/cresta rubio-amarillo en forma de llama;
- pañuelo verde;
- manos negras de tres dedos;
- pezuñas negras;
- cola corta con forma de llama;
- rasgos equinos reconocibles sin ser caballo literal.

### Pisha
- pelaje rojo;
- lunares negros dentro del rango definido;
- clavel;
- cuernos cortos y redondeados;
- manos negras de tres dedos;
- pezuñas negras;
- rasgos bovinos reconocibles sin ser toro literal.

Brazos/manos y piernas/pezuñas son sistemas anatómicos diferentes. No deben colapsarse en una sola categoría visual.

Un invariante protege el significado canónico, no una geometría idéntica en todas las poses.

## 3. Adaptable

Una propiedad adaptable puede transformarse intencionadamente mientras conserve la identidad.

Ejemplos: vestuario contextual, profesión, periodo histórico, escenario, utilería y presentación específica de una parodia.

Adaptable no significa ilimitado.

## 4. Variable

Una propiedad variable puede cambiar sin constituir por sí misma una alteración de canon, dentro de sus restricciones aplicables.

Ejemplos: pose, expresión, fondo, atmósfera, composición, distribución visual y número de lunares cuando se mantenga dentro del rango canónico.

La variabilidad no elimina requisitos de legibilidad, coherencia o producción.

## 5. Recurrente

La recurrencia crea coherencia esperada, no obligación de presencia.

Fauna, objetos, detalles cómicos o recursos gráficos pueden reaparecer cuando tengan una intención natural. No deben insertarse mecánicamente porque existan en el repositorio.

## 6. Required / Requerido

`Required` describe una condición bajo la cual una propiedad debe estar presente.

Ejemplo: si Pisha está representado y el encuadre permite valorar sus rasgos identitarios, sus lunares y clavel son esperables salvo excepción documentada. Si una característica está completamente oculta por pose o encuadre, la ausencia visible no demuestra su ausencia real.

## 7. Contextual

Una regla contextual depende de las circunstancias: gag, parodia, escena, medio, escala, producción, composición o intención.

Los marcadores anatómicos cómicos de Arsa y Pisha son contextuales y opcionales. Su ausencia no constituye una violación.

## 8. Affordance

Una affordance define una función o uso permitido de un elemento, no una obligación identitaria.

Ejemplo: un jamón puede sostener un gag de boxeo. Esa capacidad no obliga a que el jamón aparezca ni a que todos los gags sean de boxeo.

Identidad y uso permitido son conceptos diferentes.

## 9. Intención

La intención explica por qué un elemento está presente: narrativa, cómica, contextual, estilística, compositiva o de producción.

Una intención válida no autoriza por sí sola una violación de canon.

## 10. Identidad frente a representación

Core debe proteger identidad semántica, no exigir reproducción literal.

Son compatibles con canon, según contexto:
- cambios de pose y perspectiva;
- expresiones diferentes;
- iluminación y variación perceptiva del color;
- oclusiones parciales;
- vestuario contextual;
- escenarios y composiciones diferentes.

La pregunta correcta es si la diferencia contradice un significado protegido.

## 11. Evidencia

Las observaciones semánticas deben distinguir:

`CONFIRMED` — la evidencia apoya la propiedad.

`CONTRADICTED` — la evidencia demuestra una contradicción.

`UNKNOWN` — la evidencia es insuficiente.

`UNKNOWN` nunca debe transformarse silenciosamente en falso.

Cuando una decisión necesaria depende de información desconocida, Core puede escalar a revisión humana.

## 12. Validación

Core debe distinguir al menos:

`VALID`
`VIOLATION`
`UNKNOWN`
`HUMAN_REVIEW`

La validación nunca repara silenciosamente una propuesta.

No debe:
- añadir rasgos que faltan;
- reescribir la intención del usuario;
- sustituir elementos prohibidos;
- alterar el conocimiento canónico;
- inventar evidencia.

## 13. Rangos

Una variable puede tener límites explícitos.

Ejemplo actual: los lunares negros de Pisha tienen un rango canónico de 2 a 8.

Cumplir el rango no garantiza por sí solo adecuación visual: tamaño, distribución, escala y composición siguen siendo relevantes.

## 14. Adecuación visual

Validez canónica y adecuación visual son conceptos diferentes.

Una elección puede cumplir un invariante y resultar visualmente inadecuada por saturación, escala, legibilidad o jerarquía.

## 15. Parodia

La parodia transforma una referencia externa o cultural dentro del universo Arsa & Pisha.

Debe conservar suficiente estructura o reconocimiento para que la referencia resulte legible, pero adaptarse a la identidad propia del universo.

No puede utilizarse como excusa para modificar silenciosamente invariantes.

## 16. Gag

El gag es una unidad principal de lectura cómica.

Reglas operativas actuales:
- un gag principal por ilustración;
- primera lectura inmediata;
- segunda lectura sólo cuando aporte valor;
- escalada absurda desde una lógica reconocible;
- humor físico y gestual capaz de funcionar sin diálogo;
- conflicto lúdico, no malicioso;
- ternura protegida;
- economía compositiva.

## 17. Lenguaje visual

La identidad visual actual es contemporánea y de vanguardia, con simplificación gráfica, deformación caricaturesca controlada y una posible pequeña capa vintage/tebeo.

El vintage debe aportar alma sin convertirse en estética retro dominante ni viejuna.

## 18. Histórico de desarrollo

Illo & Killo y las denominaciones intermedias anteriores son patrimonio histórico del desarrollo. Sus imágenes, gags, soluciones y errores pueden utilizarse como material de aprendizaje y comparación, pero no son canon actual.

El corpus histórico debe permanecer explícitamente separado del conocimiento canónico vigente.

## 19. Regla final

El objetivo del modelo semántico es:

    identidad estable
      + adaptación controlada
      + contexto
      + evidencia explícita
      + revisión humana cuando sea necesaria
      = creatividad amplia sin pérdida de identidad
