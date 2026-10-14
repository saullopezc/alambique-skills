# Logging

| Nivel | Cuándo |
|---|---|
| `DEBUG` | Desarrollo y depuración |
| `INFO` | Evento normal de negocio |
| `WARN` | Anomalía recuperable |
| `ERROR` | Falla una operación; el sistema continúa |
| `FATAL` | El servicio no puede continuar |

Los nombres son los de la biblioteca: el del nivel máximo cambia de una a otra, y alguna
no lo tiene. El criterio, no.

**Se registra:** inicio y fin de operaciones críticas, errores con contexto, eventos de
seguridad, cambios de estado, duración de lo lento y reintentos. **No se registra:**
secretos, datos personales o confidenciales, trazas de pila al usuario final, ni `DEBUG`
o peticiones completas en producción.

**Quien oculta datos sensibles** recorre la estructura entera, a cualquier profundidad y
sin distinguir mayúsculas en la clave; si no, el secreto anidado queda en claro.

**Estructurado, en producción.** Una línea por evento, legible por una máquina. Campos habituales: marca
de tiempo con zona, nivel, servicio, identificador de traza, evento y sus datos, cada uno
en su campo.

**Identificador de traza.** Único por petición, en todos sus registros y propagado a
otros servicios. El del cliente es una entrada más (`seguridad.md`): se acepta solo con
coincidencia completa de 1 a 64 letras, dígitos o guiones —un ancla de fin puede admitir
un salto de línea—; si no, se genera uno propio.

**Antipatrones.** Un secreto en el mensaje; un mensaje sin contexto; un error capturado y
descartado (G-03, `../SKILL.md`); y un mensaje que se construye aunque su nivel esté
apagado: los datos se pasan como argumentos, sin interpolarlos antes.
