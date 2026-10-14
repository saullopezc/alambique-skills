# Docker

| Regla | Cómo falla |
|---|---|
| **Capas de lo que menos cambia a lo que más:** dependencias antes que el código. | Cada cambio de código invalida la caché. |
| **Usuario no root.** | El defecto es root. |
| **Multi-stage:** el build no viaja a la imagen final. | Compilador en producción. |
| **Base oficial, fijada por versión o digest.** | `latest` no es reproducible. |
| **Ningún secreto en la imagen ni en un `ARG`:** se inyecta en ejecución o por montaje de build. | Queda en capas e historial. |
| **`.dockerignore` desde el primer día.** | El contexto arrastra hasta el fichero de entorno. |
| **`HEALTHCHECK` que mire algo real.** | Un proceso vivo puede no responder. |
| **Un proceso por contenedor; registros a la salida estándar,** no a un fichero dentro del contenedor. | Ahí nadie los recoge. |
| **La imagen puede probarse a sí misma:** etapa de test o perfil de QA. | Se prueba un entorno parecido. |
| **Datos de prueba propios; credenciales inyectadas en ejecución.** | Una credencial es `C3`: no entra en el árbol versionado (R-02 del marco alambique). |
| **Escaneo de la imagen construida, como puerta** (`tooling.md`). | Un informe no detiene nada. |
| **Etiqueta con versión y commit, nunca solo `latest`.** | Sin identificar no se puede revertir. |
