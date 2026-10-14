# Guía de desarrollo — Perl

Los principios que evitan los fallos caros y son propios de Perl, para escribir o revisar
`.pl`, `.pm` y `.t`. Lo general no se repite: está en los `G-nn` de `../../SKILL.md` y en `../seguridad.md`,
`../base-datos.md`, `../arquitectura.md`, `../qa.md`, `../logging.md` y
`../documentacion-codigo.md`. La tabla es la lista de revisión: un hallazgo cita su
identificador y parte de su nivel (`../revision.md`).

| # | Principio | Cómo falla | Nivel |
|---|-----------|------------|-------|
| **PL-01** | **`use strict` y `use warnings` en todo fichero,** pruebas incluidas. | Un nombre mal escrito es una variable global nueva y vacía, sin error. | BLOQUEANTE |
| **PL-02** | **Orden externa con lista de argumentos, nunca con cadena;** una lista de un elemento cuenta como cadena. | Con cadena, `system`, `exec`, `qx` y `open` de tubería pasan el dato a un shell. | BLOQUEANTE |
| **PL-03** | **`open` con tres argumentos y manejador léxico.** | Con dos, un nombre acabado en barra vertical ejecuta una orden y uno que empieza por redirección trunca un fichero. | BLOQUEANTE; DETALLE si el nombre es literal |
| **PL-04** | **Una ruta con entrada externa se resuelve con la ruta real de `Cwd`** antes de compararla (`../seguridad.md`); indefinida, se rechaza. | La normalización de `File::Spec` es textual: no resuelve `..` ni enlaces simbólicos. | BLOQUEANTE |
| **PL-05** | **Modo taint (`-T`) en todo programa que recibe datos externos;** la captura que desmarca es una lista blanca anclada con `\A` y `\z`. | Taint obliga a capturar, no valida; `$` admite un salto de línea final. | BLOQUEANTE |
| **PL-06** | **En un patrón, el texto externo se escapa con `quotemeta` y el coste se mide,** con la entrada acotada (`../seguridad.md`). | El motor amortigua muchos anidamientos clásicos, pero las retrorreferencias y ciertos anidamientos siguen siendo exponenciales o cuadráticos. | DEBERÍA |
| **PL-07** | **Toda llamada al sistema se comprueba, con `$!` en el mensaje;** una orden, por `$?` o por el `close` de su tubería. | Un `open` fallido deja leer cero líneas como si el fichero estuviera vacío. | BLOQUEANTE |
| **PL-08** | **De un `eval` de bloque se comprueba el valor de retorno, no `$@`.** | `$@` puede llegar falso aunque hubo error: es un objeto que evalúa a falso o, en un intérprete anterior a 5.14, lo pisó un destructor. | DEBERÍA |
| **PL-09** | **Un error se devuelve con `return` sin valor, no con `undef` explícito.** | En contexto de lista, `undef` es una lista de un elemento: verdadera. | DEBERÍA |
| **PL-10** | **El valor por defecto se pone con `//`, no con `\|\|`.** | Cero, la cadena vacía y `"0"` son falsos: un valor legítimo se sustituye sin aviso. | DEBERÍA |
| **PL-11** | **`$1` se lee solo tras comprobar la coincidencia.** | Si el patrón no coincide, conserva el valor anterior. | DEBERÍA |
| **PL-12** | **La capa de acceso a datos no lanza excepciones ni agrupa sentencias por defecto:** se activan los errores como excepción y, con más de una sentencia, se desactiva la confirmación automática (`../base-datos.md`). | Una llamada sin comprobar sigue adelante; un fallo en la segunda sentencia deja la primera aplicada. | BLOQUEANTE |
| **PL-13** | **Un cliente asíncrono vive tanto como quien espera su respuesta.** | Como variable local, el recuento de referencias lo destruye al salir de la función y cancela la petición pendiente. | BLOQUEANTE |
| **PL-14** | **Un rol que exige un atributo solo se aplica a una clase que ya lo declara.** | La composición se ejecuta donde está escrita: antes, la carga falla. | DEBERÍA |
| **PL-15** | **Los tipos se importan en el paquete que los usa.** | Son funciones importadas: sin ellas, el paquete no compila bajo `strict`. | DEBERÍA |
| **PL-16** | **La suite corre contra el árbol de trabajo,** y cada fichero de prueba termina con `done_testing`. | Contra una copia instalada, pasa probando la versión anterior. | DEBERÍA |
| **PL-17** | **En un módulo, los errores de uso se lanzan con `croak`.** | `die` señala una línea interna del módulo, no la del llamador. | DETALLE |

Las herramientas de cada papel están en `../tooling.md` y la lista previa a un cambio, en
`../git.md`. La comprobación de sintaxis del intérprete (`-c`) ejecuta `BEGIN` y `use`: no
es inocua sobre código ajeno. En código heredado, modernizar es un cambio aparte.
