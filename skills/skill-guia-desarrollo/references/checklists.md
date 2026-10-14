# Listas de comprobación — complejidad y rendimiento

Solo lo que no tiene otro dueño. Lo demás: los `G-nn` de `../SKILL.md`, `seguridad.md`,
`qa.md` y `arquitectura.md`.

**Complejidad, por función**

- Una responsabilidad; menos de 50 líneas, como referencia.
- Complejidad ciclomática menor que 10 y anidamiento menor que 3 niveles.
- Condiciones complejas, en funciones con nombre; constantes con nombre, sin números
  mágicos.
- Lógica duplicada: se extrae a la tercera aparición.
- Dependencias explícitas, no globales implícitas.

**Rendimiento**

- Sin consultas N+1 dentro de bucles; índices en lo que se consulta a menudo (`base-datos.md`).
- Sin operaciones bloqueantes en el hilo principal.
- Paginación en lo que devuelve listas grandes.
- Caché donde el cálculo es caro o el dato es estático.

Toda optimización se valida por **equivalencia de salida** (`validacion.md`): cambia el
tiempo, no el resultado.
