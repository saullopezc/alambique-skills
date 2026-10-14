# Guía de Desarrollo — Java

Los principios necesarios de Java y de la JVM: los que evitan fallos caros y son propios del
lenguaje o de su plataforma. Aplica a ficheros `.java` y a servicios con contenedor de
inyección de dependencias, ORM o ejecución asíncrona. Lo que vale para cualquier lenguaje no
se repite: está en los `G-nn` de `../../SKILL.md` y en `../seguridad.md`, `../arquitectura.md`, `../base-datos.md`, `../qa.md`,
`../logging.md` y `../documentacion-codigo.md`.

La tabla es la lista de revisión: cada hallazgo cita su `J-xx` y hereda su nivel. Orden,
forma del hallazgo y veredicto: `../revision.md`.

| # | Principio | Cómo falla | Nivel |
|---|---|---|---|
| **J-01** | **Las dependencias obligatorias entran por el constructor, a campos `final`.** | Inyectadas sobre campos quedan ocultas, y nulas fuera del contenedor: la clase no se prueba sin él. | DEBERÍA |
| **J-02** | **Lo que depende de un valor inyectado se construye en el constructor.** El inicializador de un campo se evalúa antes de la inyección. | Un «null» incrustado —en una cabecera de autorización— que solo rechaza el otro extremo. | BLOQUEANTE |
| **J-03** | **Un componente gestionado es una instancia compartida entre hilos: no guarda estado mutable,** ni en sus campos ni en `static`. | Datos de una petición aparecen en otra, solo bajo carga. | BLOQUEANTE |
| **J-04** | **Un mapa de implementaciones por nombre exige que cada una declare su nombre;** la clave desconocida da un error explícito. | La clave se deriva del nombre de la clase y la búsqueda devuelve nulo. | BLOQUEANTE |
| **J-05** | **Una anotación no hace nada si su mecanismo no está activado,** ni en una llamada dentro de la misma clase. Se comprueba por su efecto. | Autorización, validación, transacción o asincronía que parecen puestas y no actúan. | BLOQUEANTE |
| **J-06** | **El acceso a datos devuelve «puede no estar» (`Optional`) y quien llama decide.** | Un `null` aplaza el fallo hasta un `NullPointerException` lejos de su causa. | DEBERÍA |
| **J-07** | **Una sola colección hija por consulta;** la segunda, por lotes o en otra consulta. | Dos de golpe dan un producto cartesiano o un error del ORM. | BLOQUEANTE |
| **J-08** | **Las relaciones a muchos se cargan de forma diferida.** | La carga inmediata se paga en cada lectura, se necesite o no. | DEBERÍA |
| **J-09** | **No se deserializa con `ObjectInputStream` nada que venga de fuera, y todo analizador XML desactiva tipos de documento y entidades externas.** | Leer el flujo ya ejecuta código del classpath; el analizador, por defecto, lee ficheros del servidor. | BLOQUEANTE |
| **J-10** | **Identidad e identificador se comparan en el mismo tipo.** | `equals` entre `String` y `Long` nunca es cierto: se deniega al propietario legítimo, sin error. | BLOQUEANTE |
| **J-11** | **Toda ejecución asíncrona declara su ejecutor.** | `CompletableFuture` sin ejecutor usa el `ForkJoinPool` común de toda la JVM; el del contenedor puede crear un hilo por tarea. | DEBERÍA |
| **J-12** | **La configuración de logging no referencia un destino que solo existe en un perfil,** tampoco sin perfil activo. | El servicio corre sin escribir una línea. | DEBERÍA |
| **J-13** | **Inmutable por defecto:** `record` y colecciones no modificables. | Un objeto compartido cambia a espaldas de quien lo recibió. | DETALLE |
| **J-14** | **`switch` como expresión y sin rama por defecto** sobre enumerados y tipos sellados. | Con rama por defecto, una variante nueva pasa sin que el compilador la señale. | DETALLE |

Formateador, analizador estático y escáner de dependencias: `../tooling.md`.
