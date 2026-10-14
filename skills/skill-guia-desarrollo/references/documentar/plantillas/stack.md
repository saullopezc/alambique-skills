---
id: stack
tipo: stack
proyecto: <nombre-del-proyecto>
actualizado: YYYY-MM-DD
estado: borrador                # borrador | vigente | retirado | reemplazado-por-<id>
version: 0.1                    # menor: corrección · mayor: cambia lo que el documento afirma
clasificacion: <C0-C3>          # clase del dato; sin valor por defecto: se decide antes de escribir
responsable: <persona real>     # nunca una herramienta
revision: YYYY-MM-DD            # cuando toca releerlo (6 meses por defecto)
tags: [stack, build]
---

# Stack de desarrollo

## Tecnologías

| Tecnología | Versión | Rol | Evidencia |
|---|---|---|---|
| <lenguaje/framework> | <versión o rango> | <para qué se usa> | `<archivo que lo delata>` |

<!-- "Evidencia" = el archivo del repo que confirma la tecnología
     (package.json, pom.xml, Makefile, .tool-versions, etc.). -->

## Requisitos del entorno

- <SO / runtime / toolchain mínimo. Placeholders para todo lo específico del host.>

## Construir y ejecutar

```bash
# Build
<comando>
# Test
<comando>
# Ejecutar / desplegar (ver [[runbook-<slug>]] si es más que un comando)
<comando>
```

## Dependencias externas

| Dependencia | Tipo | Notas |
|---|---|---|
| <BD / API / servicio> | <externa/interna> | <cómo se configura — sin credenciales, usar `*.example`> |

Relacionado: [[arquitectura]]
