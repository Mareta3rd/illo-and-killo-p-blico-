# Especificación de saliencia canónica v0.1

## Propósito

La saliencia canónica distingue cuánto importa un elemento para la narración y cuánto domina visualmente la composición.

No es una puntuación de confianza de Evidence y no debe mezclarse con `CONFIRMED`, `CONTRADICTED` o `UNKNOWN`.

## Ejes

### Narrative role

- `primary`: indispensable para comprender o ejecutar la acción narrativa principal.
- `secondary`: participa claramente en la acción o remate, pero no define por sí solo el gag.
- `supporting`: aporta contexto, reacción o información auxiliar.
- `incidental`: decorativo o accesorio; su pérdida no altera el significado principal.

### Visual salience

- `dominant`: atrae primero la atención o define la jerarquía visual.
- `high`: claramente visible y relevante, aunque no domina la composición.
- `medium`: visible pero subordinado.
- `low`: pequeño, periférico o fácilmente ignorado.

## Regla de diseño

Los valores son cualitativos y legibles por humanos. El sistema puede derivar un rango entero ordinal de `0` a `3` para comparaciones deterministas, pero ese número es una implementación derivada y no debe presentarse como una probabilidad ni como una precisión falsa.

## Gag 001

La especificación actual del Gag 001 establece la jerarquía visual `Illo → jamón → reacción de Killo`. Por tanto, los primeros perfiles previstos son:

- Illo: `primary` / `dominant`
- jamón: `primary` / `dominant`
- Killo: `secondary` / `high`
- elementos secundarios o decorativos: `supporting` o `incidental` según su función

Estas etiquetas son metadata canónica y no sustituyen la evidencia perceptual de un proveedor.
