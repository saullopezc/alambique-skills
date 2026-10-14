# Plan por fases — para lo que no cabe en una sesión

Se monta al **iniciar** un proyecto o cambio que no cabe en una sesión, antes de escribir
código; nunca a medio camino, donde cuesta más de lo que ordena.

```
docs/plan_<nombre>/
├── README.md                  # índice del plan y cómo navegarlo
├── REQUERIMIENTO_TECNICO.md   # visión macro, alcance, fuentes (no detalle)
├── CHANGELOG.md               # bitácora cronológica: la verdad de lo hecho
├── fase-1-analisis/checklist.md
├── fase-2-diseno/             # + modelo-datos.md, api-contract.md...
├── fase-3-desarrollo/
├── fase-4-pruebas/
└── fase-5-despliegue/
```

Sus ficheros abren con la cabecera mínima de `documentacion-codigo.md` y nada más: no son
nodos del grafo (`documentar/grafo-conocimiento.md`).

**Se versiona, así que no lleva datos del cliente:** ni salidas reales, ni coordenadas, ni
su nombre (R-02 del marco alambique). Lo que los necesite va a `_local/`, y el plan lo
cita sin copiarlo. Si el puesto lleva su estado en `_local/operacion/`, el plan no se
duplica allí: el item de `planificacion/` apunta a esta carpeta, y el trabajo del plan
sigue en las listas de sus fases.

| Regla | Por qué importa |
|---|---|
| **Cinco fases canónicas: se pueden añadir, nunca quitar ni saltar.** La que no aplica lo dice en su `checklist.md`. Un item crítico abierto bloquea el avance, salvo que el usuario lo marque como diferible. | Una fase omitida en silencio es trabajo que nadie decidió no hacer. |
| **La lista de comprobación de cada fase se acuerda con el usuario:** no se inventan items, y añadir o quitar un bloque entero se discute antes. Se marca solo lo terminado: una prueba fallando deja el item abierto, y lo que queda a medias, abierto con un sub-item que dice qué falta. | Un item marcado sin estarlo esconde lo que falta. |
| **El trabajo nuevo que aparece durante una sesión, si es del item activo, se hace; si no, va a la lista de su fase, nunca a una lista paralela.** El item que queda obsoleto se tacha con su razón; no se borra. | Lo que queda fuera no se ve al iniciar la sesión siguiente. |
| **Cada sesión abre leyendo el índice del plan y el registro de cambios entero, y reporta el estado y el primer item abierto antes de tocar código; cierra con una entrada al inicio del registro,** una por sesión o bloque significativo, no por item trivial. Una fase cerrada se dice. El requerimiento técnico no se edita sin anotarlo en el registro. | Es la verdad de lo hecho, y el usuario puede redirigir antes de tocar código. |
| **La fase 5 prepara el despliegue; no lo ejecuta.** Desplegar, publicar o entregar es otra tarea: una acción irreversible o dirigida al exterior, que necesita aprobación explícita en el turno que la origina (R-08 y R-10 del marco alambique). Tampoco se hace commit salvo que el usuario lo pida. | El permiso dado para una tarea no cubre la siguiente. |

Estado del plan:

```
Plan <nombre> — estado:
- Última entrada del changelog: <fecha + título>
- Fase activa: Fase N — <nombre>
- Próximo item: <texto exacto del checklist>
¿Avanzamos con ese o priorizamos otro?
```

Entrada del registro:

```
## YYYY-MM-DD — Fase N — Título corto
- Resumen del trabajo (1-3 puntos, en pasado)
- Items completados: referencia a fase-N/checklist.md
- Decisiones: solo si hubo trade-offs notables
- Siguiente paso: puntero al próximo item
```

**Diagramas:** en Mermaid antes que dibujados en ASCII, con un párrafo que dice qué
muestran; con más de 15 nodos se dividen o pasan a tabla, y el de calendario, solo con
plazos reales. Uno desactualizado engaña más que uno ausente.
