# Base de datos

Cada motor tiene su instrumento para cada paso del método de abajo. En la versión
instalada se comprueba cuál es, qué permisos pide y si hay que activarlo antes de medir,
con reinicio o sin él.

**Activar un instrumento, cambiar la configuración del motor, reiniciarlo o construir un
índice es escribir sobre él.** En un servidor que no es el local se propone y se ejecuta
solo con autorización explícita (R-06 del marco alambique); lo que no se deshace con una
orden lleva antes un punto de restauración verificado (R-07). Donde se pueda, se mide en
una copia y no en producción.

## Esquema

- **El tipo correcto desde el principio** —dinero en decimal exacto, fechas con zona—:
  cambiarlo después cuesta una migración.
- **Las restricciones son parte del diseño:** lo que la base no declara, la aplicación lo
  incumple.
- **Normalizar por defecto;** desnormalizar solo con una medida delante.

## Índices

Árbol B por defecto (igualdad y rango); compuesto, con la columna de igualdad antes que
la de rango; parcial, para un subconjunto de filas; especializado, para texto completo,
documentos anidados o geometría.

**No se añade** en tabla pequeña, columna de baja cardinalidad, mucha escritura con poca
lectura o prefijo ya cubierto: cada índice se paga en cada escritura. **Toda clave
foránea necesita índice:** sin él, borrar el padre recorre la tabla hija entera.

## Método de rendimiento

En orden: saltarse un paso lleva a conclusiones falsas.

| Paso | Qué se hace | Trampa |
|---|---|---|
| **1. Dónde se va el tiempo** | Estadística de sentencias, ordenada por tiempo **total**, no por media: lo breve muy repetido pesa más. | Un instrumento que solo cuenta la sentencia de nivel superior no ve las que corren dentro de funciones: se comprueba, y se le pide que las cuente. |
| **2. Por qué es lenta** | El plan **real**, también el de las sentencias anidadas, leído por sus señales. | Juzgar por intuición. |
| **3. ¿Serviría un índice?** | Simularlo antes de construirlo y preguntar al planificador si lo usaría. | Lo no simulable se construye, y exige A/B del proceso entero. |
| **4. Qué índice falta** | Los predicados que se ejecutan de verdad y su selectividad, según la carga real. | Decidirlo según quién mira. |
| **5. Chequeo periódico** | Con catálogos: tablas leídas enteras, índices sin uso, claves foráneas sin índice, consulta más cara en total, estadísticas rancias. | — |

Señales del plan: filas estimadas frente a reales (si difieren en órdenes de magnitud, el
planificador decide al azar); condición de índice frente a filtro (el filtro lee y
descarta); filas descartadas; veces que se ejecuta un nodo (una por fila del padre);
páginas por fila (más de unas decenas: el índice no sirve).

Cinco reglas:

1. **Repetir la medida:** la primera ejecución mide el disco; se compara caliente contra
   caliente, y el plan dice qué salió de caché.
2. **Medir el todo, no la parte:** una consulta más rápida dentro de un plan peor sale
   perdiendo.
3. **El banco se parece a producción** en volumen, distribución y tamaño de lote, o
   cambia la respuesta.
4. **Separar lo medido de lo deducido, y desconfiar del indicador antes que del
   sistema:** saber qué mide exactamente antes de concluir.
5. **Cuestionar la premisa:** si el mismo cuello de botella reaparece tras cada arreglo,
   falla una decisión de diseño que nadie mira.

## N+1

Una consulta por cada fila del resultado anterior: carga anticipada por unión, en dos
pasos por lista de claves o por lotes. Se detecta contando consultas por petición, no
leyendo el código.

## Transacciones y acceso

- Transacción **corta**: nunca abierta mientras se espera E/S externa o al usuario.
- Aislamiento elegido a propósito, no el de por defecto.
- Un reintento exige operación **idempotente**, o se cobra dos veces.
- El dueño del pool de conexiones se crea **una vez por proceso**; la sesión, una por
  petición.
- Pool dimensionado a la concurrencia real: agotado, da esperas antes que un error claro.
- Migraciones **reversibles** y por herramienta versionada, nunca a mano contra producción.
- Si algo falla a mitad, se deshace **explícitamente** y se relanza el error original
  (G-03, `../SKILL.md`); si deshacer también falla, ese segundo error se registra sin tapar
  el primero.
