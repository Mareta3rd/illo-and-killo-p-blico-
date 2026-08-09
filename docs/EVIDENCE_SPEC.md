# Especificación de Evidence v0.2

## Propósito

La capa Evidence proporciona una representación inmutable y auditable
de los hechos observables existentes en el repositorio.

Evidence observa el estado del repositorio. No modifica el canon, no crea
hechos, no inventa intención creativa y no aprueba reutilizaciones.

---

## Principios fundamentales

1. Evidence no es la verdad; es evidencia sobre el estado del repositorio.
2. Toda evidencia debe conservar su procedencia.
3. La ausencia de evidencia no equivale a evidencia de ausencia.
4. La información desconocida debe permanecer como UNKNOWN.
5. Evidence nunca debe modificar el repositorio.
6. El uso histórico no debe inferirse simplemente porque un recurso exista.
7. Mencionado, utilizado e incierto son estados diferentes.
8. Las evidencias contradictorias no deben resolverse silenciosamente.
9. El canon y el uso histórico son conceptos separados.
10. HUMAN_REVIEW es un resultado normal del sistema, no un error.

---

## Elemento de evidencia

Cada elemento de evidencia histórica representa una relación observable
entre un recurso y una fuente del repositorio.

Campos conceptuales:

- asset
- gag
- status
- role
- source
- provenance
- confidence

---

## Estados históricos

Los estados históricos permitidos son:

- mentioned
- used
- uncertain

UNKNOWN no se almacena como evidencia histórica.

Si una consulta no encuentra evidencia suficiente para un recurso,
el resultado de la consulta puede ser UNKNOWN.

---

## Canon

Los invariantes canónicos son restricciones autorizadas por el repositorio.

Ejemplo conceptual:

killo:
  invariants:
    - clavel

Un invariante no es simplemente una aparición histórica.

El canon tiene prioridad sobre las inferencias derivadas del historial.

---

## Procedencia

Cada elemento de evidencia debe identificar su fuente.

Como mínimo debe conservar:

- tipo de fuente
- ubicación de la fuente

Ejemplo conceptual:

provenance:
  source_type: gag
  source: gags/002_pesca.md

---

## Confianza

La confianza utilizará niveles cualitativos:

- HIGH
- MEDIUM
- LOW

La confianza debe incluir una razón explícita.

No se requieren porcentajes decimales arbitrarios en Evidence v0.2.

---

## UNKNOWN

UNKNOWN significa:

El repositorio no contiene evidencia suficiente para determinar
el hecho consultado.

UNKNOWN no debe convertirse automáticamente en FALSE.

---

## CONFLICT

Cuando existan evidencias contradictorias, el sistema debe representar:

CONFLICT

El sistema no debe elegir silenciosamente una de las fuentes.

Un conflicto debería conducir normalmente a HUMAN_REVIEW.

---

## Identidad de los recursos

Los recursos deberán evolucionar hacia identificadores canónicos estables.

Los nombres visibles y los alias pueden variar.

Ejemplo conceptual:

canonical_id: mosquito_tigre
display_name: Mosquito tigre
aliases:
  - mosquito tigre
  - mosquito-tigre

La normalización debe ser conservadora.

---

## Evidence frente a Decision

Evidence describe el estado del repositorio.

Una Decision modifica el estado del repositorio.

El flujo previsto es:

Repositorio
    ↓
Evidence
    ↓
Evaluación
    ↓
Decision
    ↓
Cambio en el repositorio
    ↓
Nueva Evidence

Evidence no debe realizar escrituras en el repositorio.

---

## Interacción con los loops

Los loops pueden refinar un candidato, pero Evidence permanece en modo
de solo lectura.

Todo loop debe tener:

- un criterio de evaluación definido
- un límite máximo de iteraciones
- una condición válida de salida
- HUMAN_REVIEW como posible escalado

El objetivo de un loop es alcanzar una condición válida de salida,
no continuar indefinidamente.

---

## Human Review

La revisión humana es un estado normal del sistema.

Los posibles resultados de evaluación incluyen:

- PASS
- FAIL
- REVISE
- HUMAN_REVIEW
- CONFLICT
- BLOCKED

Un resultado HUMAN_REVIEW debe incluir una razón y la evidencia relevante.

---

## Versión

Este documento define la Especificación de Evidence v0.2.

Los cambios en este contrato deben documentarse y probarse antes de
integrarse en la implementación.