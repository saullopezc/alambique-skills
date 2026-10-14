# QA — criterio de pruebas

La calidad se mide contra la **especificación**, no contra la implementación: las pruebas se
derivan del requisito. Cómo se cierra un cambio cuando no hay suite, y dónde va la
evidencia: `validacion.md`.

| Cuándo | Regla |
|---|---|
| Antes de implementar | **Cada criterio tiene resultado observable y entrada concreta;** si no, se señala y no se implementa. **Cada requisito mapea a una prueba;** matriz requisito × caso: camino feliz, límite (vacío, duplicado, corrupto, frontera, concurrencia) y fallo. |
| Diseño | **Unitaria para el núcleo, integración para los adaptadores, extremo a extremo solo en los flujos principales.** Un comportamiento por prueba, determinista e independiente: sin estado compartido ni azar. |
| Diseño | **Datos mínimos, nunca de producción.** Se afirma sobre el resultado y solo se simulan las fronteras externas. **Las pruebas negativas son obligatorias:** entrada inválida rechazada, acción prohibida denegada. |
| Instrumento | **Un instrumento no vale hasta verlo DETECTAR:** el check se prueba con el fallo real delante, y toda afirmación negativa lleva control positivo. Se valida el efecto real, no un proxy cómodo (contador, marca de tiempo, código de retorno, un «OK»). |
| Ejecución | **Suite completa en cada cambio, con lint, formato y tipos, y nunca avanzar en rojo.** Una prueba inestable es un bug: se arregla o se aísla con ticket, jamás se reintenta hasta que pase. La cobertura es señal, no objetivo. |

**Defectos.** Se reproducen con un caso mínimo; el reporte lleva pasos, esperado frente a
obtenido, entorno, severidad y requisito afectado. **Todo bug recibe una prueba de regresión
antes del arreglo, y tiene que fallar primero.** Se cierra determinando qué control debió
impedirlo y por qué no lo hizo; a la segunda vez pasa a mecanismo (R-12 del marco alambique).

**Informe final.** Requisito → prueba → resultado, y veredicto: la especificación se cumple o
no, con sus huecos.
