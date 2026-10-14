# C — principios

Los principios propios de C que evitan los fallos caros. Aplica a `.c`, `.h`, firmware
y todo código que gestione a mano memoria o búferes. Lo general no se repite: los
`G-nn` de `../../SKILL.md` y `../seguridad.md`, `../arquitectura.md`, `../qa.md`, `../logging.md`,
`../documentacion-codigo.md`.
La tabla es la lista de revisión; hallazgo y veredicto, en `../revision.md`.

| # | Principio | Cómo falla | Nivel |
|---|-----------|------------|-------|
| **C-01** | **Toda escritura en un búfer comprueba antes que cabe, terminador incluido.** `strcpy`, `strcat`, `sprintf` y `gets` no se usan: no reciben el tamaño del destino. | Corrompe la memoria; con entrada externa es explotable | BLOQUEANTE |
| **C-02** | **La capacidad restante se comprueba restando, nunca sumando.** | La suma da la vuelta en `size_t`: con una longitud enorme la comprobación pasa | BLOQUEANTE |
| **C-03** | **El retorno de `snprintf` se compara con el tamaño del destino** donde truncar no es aceptable. | Trunca en silencio y el dato parece válido | DEBERÍA |
| **C-04** | **Cada reserva se libera exactamente una vez, en todos los caminos; tras `free`, el puntero a nulo.** | Fuga, uso tras liberar o doble liberación: fallo intermitente | BLOQUEANTE |
| **C-05** | **El retorno de `malloc` y `realloc` se comprueba; el de `realloc` va a un temporal.** | Desreferencia de nulo; sobre el mismo puntero se pierde el bloque original | BLOQUEANTE |
| **C-06** | **Un valor externo se valida antes de usarlo como tamaño, índice o contador.** El desbordamiento con signo es indefinido; ningún comparador se escribe restando. | Un tamaño que da la vuelta reserva un búfer diminuto y la copia escribe fuera | BLOQUEANTE |
| **C-07** | **Ningún comportamiento indefinido «porque aquí funciona»:** variables inicializadas, desplazamientos menores que el ancho del tipo, bytes reinterpretados con `memcpy` y no por un puntero de otro tipo. | Funciona sin optimizar y falla optimizado o en otra arquitectura | BLOQUEANTE |
| **C-08** | **A las funciones de `<ctype.h>` se les pasa el carácter convertido a `unsigned char`,** siempre: el signo de `char` depende de la plataforma. | Un byte con el bit alto llega negativo: indefinido, con datos no ASCII | BLOQUEANTE |
| **C-09** | **La cadena de formato es siempre un literal;** el dato externo va como argumento. | Permite leer y escribir memoria desde fuera | BLOQUEANTE |
| **C-10** | **Un búfer que contuvo un secreto se borra con un borrado que el optimizador no elimine** (`memset_explicit` desde C23, `explicit_bzero` como extensión, o escritura por un puntero `volatile`). | Un `memset` justo antes de `free` desaparece del binario | DEBERÍA |
| **C-11** | **Sin excepciones, el retorno se comprueba en cada llamada; con varios recursos, un único punto de limpieza** (`goto` a una etiqueta final, en orden inverso). Es la forma de G-03 y G-04 en C. | Sigue con estado inválido; las fugas nacen en los `return` tempranos | BLOQUEANTE |
| **C-12** | **`exit` no es segura en un manejador de señal:** este solo levanta un indicador `volatile sig_atomic_t` que consulta el bucle principal o, si debe terminar ahí, llama a `_exit`. | Ejecuta `atexit` y vacía `stdio` sobre un estado a medio modificar: bloqueo ocasional | BLOQUEANTE |
| **C-13** | **Lo que no es de ISO C exige declarar la macro de características o el dialecto extendido, y decir cuál,** antes del primer `#include`: reloj monotónico, dormir, ruta real, `explicit_bzero` y, antes de C23, hora reentrante. | La función queda como declaración implícita (aviso o error según el compilador) aunque exista, y una constante, sin declarar | DEBERÍA |
| **C-14** | **Ninguna función se llama sin declarar:** ese aviso nunca se silencia y, si se puede, se eleva a error. | Se le supone retorno `int`; es lo único que delata el `#include` que falta | BLOQUEANTE |
| **C-15** | **Se compila con cero avisos, y las pruebas corren con detectores de memoria y de comportamiento indefinido.** Estándar y dialecto se declaran en el build (G-08). | Una prueba pasa con la memoria corrupta; el build elige el dialecto extendido sin decidirlo nadie | DEBERÍA |
| **C-16** | **Una macro de varias sentencias va en `do { ... } while (0)`; una variádica lleva el formato dentro de la lista variable.** | Solo la primera sentencia queda bajo el `if`; sin argumentos variables no es portable en C11 estricto | DEBERÍA |

**El contexto cambia lo que se exige.** *Embebido o de tiempo real:* una interrupción solo anota
el hecho y despierta a una tarea —sin bloqueo, memoria dinámica ni formato de texto—, y un sistema
crítico no usa memoria dinámica. *Heredado:* manda el estándar del compilador del destino; C89 no
tiene comentarios `//`, declaraciones fuera del inicio del bloque, `<stdint.h>` ni macros
variádicas, y el cambio se compila en el destino real antes de integrarlo (sin framework de
pruebas: `../validacion.md`). *C++:* los recursos se atan al tiempo de vida de un objeto, sin `new` ni
`delete` directos.

**Herramientas y normas.** Qué analizador y qué formateador usar: `../tooling.md`; el detector de memoria lo elige el proyecto. Si el
proyecto declara una norma de codificación (MISRA-C, CERT C), el hallazgo cita además su regla.
