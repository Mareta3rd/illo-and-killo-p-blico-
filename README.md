# Arsa & Pisha

Repositorio de automatización del flujo creativo para el universo **Arsa & Pisha**.

## Propósito
Este repositorio actúa como base de trabajo para:
- Canon visual
- Biblia narrativa
- Model sheets
- Gags canónicos
- Objetos, fauna y patrimonio simplificados
- Preparación de assets para 3D y merchandising
- Automatización del proceso creativo
- Arquitectura semántica y evaluación de candidatos generados por IA

## Canon actual
- **Arsa & Pisha son los personajes protagonistas actuales y canónicos.**
- Ninguna generación debe reinterpretar libremente sus invariantes.
- Toda nueva pieza debe respetar el canon aprobado y las decisiones documentadas.
- La referencia maestra es la documentación canónica vigente y los assets explícitamente marcados como canon.
- El criterio principal es la consistencia entre piezas y la separación estricta entre conocimiento canónico, evidencia externa y decisiones de Core.

## Material histórico
Los nombres **Illo & Killo** corresponden a material de desarrollo anterior. Ese material se conserva como referencia, aprendizaje e inspiración potencial, pero **no forma parte del canon actual** salvo incorporación expresa mediante una decisión documentada.

Conservar material histórico no implica continuidad automática de nombres, diseños, escenas, rasgos ni relaciones.

## Estructura
- `/docs`
- `/assets`
- `/prompts`
- `/model-sheets`
- `/gags`
- `/tools`
- `/exports`
- `/core`
- `/data`
- `/tests`

## Estado de arquitectura
Los proveedores externos actúan como fuentes de evidencia o como generadores de candidatos según el contrato específico; **Core conserva la autoridad sobre canon, evaluación y decisiones finales**.

La arquitectura validada incluye la frontera:

`provider → ExternalEvidenceRecord → ProviderEvidenceObservation → EvidenceSnapshot → Core pipeline/evaluator → Core decision`

Los generadores de candidatos no deben devolver decisiones de Core ni convertir evidencia externa en canon por sí mismos.

## Mesa de revisión local

1. Abre [`tools/revision-colaboracion.html`](tools/revision-colaboracion.html) desde tu copia del repositorio con el navegador. El ejemplo incluido funciona sin conexión.
2. Para revisar una ejecución de GitHub, descarga su artefacto, extrae el ZIP y abre `collaboration-record.json` desde **Abrir registro JSON**.
3. Compara el encargo con la propuesta y guarda tus observaciones en **Guardar revisión**. El navegador descarga un JSON independiente. Puedes retomarlo con **Recuperar revisión** cuando esté abierto su registro.

La mesa admite registros de colaboración de versión 1. Para los registros antiguos sin el
encargo literal, muestra el objetivo que se conservó. La procedencia incluye las huellas
declaradas por el archivo y, si la ejecución sigue el formato de GitHub, un enlace para
consultarla. La revisión es humana y las notas permanecen en memoria hasta su descarga.

## Siguiente trabajo
1. Consolidar la documentación vigente de Arsa & Pisha.
2. Completar el contexto semántico que reciben los ejecutores de candidatos.
3. Mantener pruebas y contratos alineados con el canon actual.
4. Validar proveedores reales sin duplicar lógica de Core.
