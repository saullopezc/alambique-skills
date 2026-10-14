# Guía de desarrollo — Python

Los principios propios de Python que evitan los fallos caros, para todo fichero `.py`, `.pyw`
o `.pyi`. Lo general no se repite: está en los `G-nn` de `../../SKILL.md` y en `../seguridad.md`, `../arquitectura.md`,
`../base-datos.md`, `../qa.md`, `../logging.md`, `../git.md` y `../documentacion-codigo.md`.
La tabla es la lista de revisión: cada principio se cita por su identificador, con los
niveles de `../revision.md`.

| # | Principio | Cómo falla | Nivel |
|---|-----------|------------|-------|
| **PY-01** | **`pickle` solo lee lo que el propio sistema escribió; YAML, con el cargador seguro.** Un modelo serializado cuenta como `pickle`. | Cargar es ejecutar lo que traiga el dato. | BLOQUEANTE |
| **PY-02** | **`async def` solo si todo lo que llama es asíncrono.** Lo síncrono o de CPU va en una función síncrona. | Bloquea el bucle de eventos: una llamada lenta detiene todas las peticiones. | BLOQUEANTE |
| **PY-03** | **Las excepciones recogidas como valores (`return_exceptions=True`) se registran antes de filtrar.** | Fallo en silencio: vuelven menos resultados y nadie sabe por qué. | BLOQUEANTE |
| **PY-04** | **El contexto de una petición viaja en `contextvars`,** no en globales ni por hilo. | En el bucle de eventos las peticiones comparten hilo y se pisan los datos. | BLOQUEANTE |
| **PY-05** | **Un `except` sin tipo no se escribe;** al envolver una excepción, `raise ... from e`. | Atrapa `SystemExit` y `KeyboardInterrupt`; sin `from` la traza presenta el origen como un segundo error, no como la causa (G-03). | BLOQUEANTE |
| **PY-06** | **Ningún valor por defecto mutable:** `None` y crear dentro; en una `dataclass`, `default_factory`. | Se evalúa una vez y lo comparten todas las llamadas. | DEBERÍA |
| **PY-07** | **Lo público se anota, incluido el `None` posible, y lo que entra por una frontera se valida:** una anotación no comprueba nada en ejecución. | Un `None` o un dato crudo estalla lejos de su origen. | DEBERÍA |
| **PY-08** | **Una fábrica solo pasa a cada clase los argumentos que su constructor acepta,** y una prueba crea cada tipo registrado. | `TypeError` solo al crear ese tipo, en ejecución. | BLOQUEANTE |
| **PY-09** | **El logging se configura una vez al arrancar, sin desactivar los loggers existentes, y se lee una línea real de su salida.** | Los módulos ya importados callan sin error; el logger estructurado escribe para humanos hasta que se configura. | DEBERÍA |
| **PY-10** | **El modo estricto del comprobador de tipos, solo sobre código tipado.** | Sobre código sin anotar acaba apagado. | DEBERÍA |
| **PY-11** | **Un fichero con caracteres no ASCII para la serie 2 declara su codificación en la línea 1 o 2.** | El intérprete rechaza el fichero entero; basta una tilde en un comentario. | BLOQUEANTE |
| **PY-12** | **Idioma del lenguaje:** comprensiones, `enumerate`, generadores para lo grande, f-strings (nunca en SQL). | Código más largo y memoria que crece con el dato. | DETALLE |

**Según el contexto.** Un script vive aparte del paquete importable y sigue los mismos
principios. En ciencia de datos y modelos, lo que se repite sale del cuaderno a módulos con
pruebas, entrenamiento e inferencia van separados, el preprocesado viaja con el modelo, y
este se carga una vez por proceso, como el pool de conexiones de `../base-datos.md`, tras un manejador síncrono (PY-02). En un
intérprete antiguo (serie 2), la división entre enteros redondea hacia abajo e `input()` evalúa lo
tecleado; la migración se hace con herramienta, no a mano, y la que traía el intérprete
falta en sus versiones recientes.

**Herramientas.** Formateador y analizador: `../tooling.md`; el comprobador de tipos lo elige el proyecto. Sus opciones se leen en la
versión instalada, y los códigos de regla de un analizador no se citan de memoria.
