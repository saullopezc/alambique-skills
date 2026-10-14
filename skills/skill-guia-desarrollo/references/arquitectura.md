# Arquitectura

Lo funcional cabe en casi cualquier arquitectura: la deciden los **atributos de calidad**.

| Antes de elegir patrón | Según la respuesta |
|---|---|
| ¿Dominio? | Simple: capas y repositorio. Rico: hexagonal o clean. |
| ¿Equipo? | Hasta 3: monolito modular. Hasta 10: con límites claros. Más, desplegando por separado: microservicios. |
| ¿Escala? | Baja: no sobrediseñar. Picos: eventos y colas. Lectura dominante: CQRS, cachés, réplicas. |
| ¿Ciclo de vida? | Prototipo: lo más simple. Largo: arquitectura limpia. |
| ¿Auditoría o datos personales? | Auditoría: event sourcing. Datos personales: repositorio aparte, cifrado por campo. |

**Un atributo sin escenario cuantificado —estímulo, sobre qué, respuesta, medida— no es
un requisito.**

| Atributo | Qué preguntar | Cómo se mide | Táctica | Se paga con |
|---|---|---|---|---|
| **Rendimiento** | ¿Latencia o caudal? ¿Percentil? | p95/p99, caudal | Caché, índices, lotes | Coste, frescura |
| **Escalabilidad** | ¿Crece carga o dato? | Caudal por instancia | Sin estado, partición, colas | Simplicidad, consistencia fuerte |
| **Disponibilidad** | ¿Cuánto vale un minuto caído? | Objetivo de servicio | Redundancia, degradación | Consistencia, ante una partición |
| **Fiabilidad** | ¿Y si falla a medias? | Tasa de error | Idempotencia, compensación | Duplicados al reintentar |
| **Seguridad** | ¿Qué dato, quién lo toca? | Superficie, hallazgos | Mínimo privilegio, cifrado | Usabilidad, rendimiento |
| **Mantenibilidad** | ¿Cuánto cuesta el cambio típico? | Ficheros por cambio | Límites claros, pruebas | Simplicidad y velocidad de entrega, por la abstracción |
| **Observabilidad** | ¿Se diagnostica sin reproducir? | Tiempo hasta la causa | Trazas, métricas | Coste, ruido |
| **Portabilidad** | ¿Corre donde debe? | Destinos soportados | Adaptadores | Simplicidad, por la indirección |
| **Coste** | ¿Cuánto por unidad? | Coste por petición | Dimensionar al percentil real | Latencia |

**Se priorizan dos atributos como mucho y se declara cuál se sacrifica,** en un ADR
(`documentar/plantillas/decision.md`); si no, el sacrificio aparece solo, en producción.

**Las dependencias apuntan hacia dentro:** dominio, casos de uso, adaptadores e
infraestructura, que entra por interfaces del núcleo. Se verifica: ¿puedo probar la lógica
de negocio sin base de datos, red ni framework?

**SOLID: señal de violación.** S: nombre con «y». O: un tipo nuevo toca un
condicional. L: subtipo con operaciones sin implementar. I: interfaz con métodos
vacíos. D: la lógica instancia una clase concreta.

**Patrones: cuándo, no cómo.** Strategy: varias formas de lo mismo, elegidas en
ejecución. Observer: varios reaccionan sin que el emisor los conozca. Factory: crear
tiene lógica propia.

**Contratos primero.** La especificación (OpenAPI, AsyncAPI) es la fuente de verdad y el
código se valida contra ella; entre equipos, pruebas dirigidas por el consumidor.
Cambiarla: `contrato-salida.md`.

**Un dato con varias fuentes tiene una jerarquía escrita, con su motivo:** se rellena desde
la más fiable y se baja a la siguiente solo si la anterior no lo aportó. Sin ella, un
cambio invierte la prioridad sin notarse.

**Defensa en profundidad:** una capa no supone que la anterior se ejecutó: repite la
comprobación o exige la marca que aquella deja. Compensa donde un fallo silencioso cuesta
más que un rechazo de más.

**Una condición repetida se extrae declarando si es flexible o estricta** —acepta o
rechaza lo que no reconoce—; si no, cada copia decide distinto.

| Señal de diseño deficiente | Acción |
|---|---|
| Módulo que lo hace todo | Dividir por responsabilidad |
| Dependencia circular; todo conectado con todo | Extraer interfaz; límites de contexto |
| Lógica de negocio en controlador o vista | Moverla a un caso de uso o servicio |
| Dominio solo con getters y setters | Mover la lógica al dominio |
| Un cambio toca ficheros ajenos | Consolidar la responsabilidad dispersa |
| Un cambio rompe algo inesperado | Pruebas antes de refactorizar |
| Solo cadenas y enteros | Tipos de dominio |
| Herencia de cuatro niveles | Composición |
| Constructor con ocho parámetros | Builder u objetos de valor |
