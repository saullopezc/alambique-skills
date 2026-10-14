# Seguridad

**La amenaza se modela sobre el diseño, no sobre el código terminado:** seis preguntas
(STRIDE) por cada frontera que cruza un dato. Cada control que sale pasa a ser criterio de
aceptación. Se hace al diseñar y se revisa cuando cambia una frontera.

- **Suplantación:** ¿quién dice ser quién? Autenticación.
- **Manipulación:** ¿se altera en tránsito o en reposo? Firma, integridad.
- **Repudio:** ¿se demuestra quién hizo qué? Auditoría.
- **Divulgación:** ¿quién más puede leerlo? Cifrado, mínimo privilegio.
- **Denegación:** ¿y si llega mil veces? Límites, cuotas.
- **Elevación:** ¿hace más de lo suyo? Autorización por objeto.

## Los fallos de siempre

Por tema, sin numeración: la lista, su orden y sus nombres los da la edición vigente del
OWASP Top 10 (owasp.org), que cambia cada pocos años. La tabla no reproduce esa
lista: agrupa reglas por tema. Un hallazgo cita la lista por edición y código.

| Fallo | La regla |
|---|---|
| Acceso | Autorizar **por objeto**, no por ruta; denegar por defecto |
| Criptografía | Contraseñas con hash lento; sal e IV nunca constantes; ningún algoritmo roto (MD5, SHA-1, DES); tokens con aleatoriedad criptográfica |
| Inyección | Parametrizar **siempre**, también el lenguaje de consulta de un ORM. Orden externa con lista de argumentos, nunca con una cadena para un shell. Un dato no se evalúa como código ni se carga código cuyo nombre venga de fuera |
| Diseño | El control sale del modelado, no de un parche |
| Configuración | Sin depuración en producción; permisos mínimos; cabeceras de seguridad puestas; CORS restrictivo |
| Dependencias | Versiones fijadas con fichero de bloqueo; escaneo en cada build |
| Autenticación | Sesiones con caducidad, rotación del token de refresco y límite de intentos. El de acceso, corto y en memoria; el de refresco, en cookie `httpOnly`, `secure` y `sameSite` |
| Integridad | No deserializar lo que no se controla; verificar lo descargado |
| Registro | Eventos de seguridad, sin credenciales ni datos personales |
| Peticiones salientes | Destinos de una lista blanca, nunca la URL recibida tal cual |

## Validar en la frontera

Lo inválido se rechaza, no se limpia.

- **Entrada:** tipo, rango, longitud y formato en el borde; el formato, con
  **coincidencia completa**: en muchos motores el ancla de fin acepta un salto de línea
  final.
- **Fichero:** el tipo, por contenido y no por extensión; tamaño limitado; se guarda fuera
  del árbol servido.
- **Salida:** codificada según el destino.
- **Ruta con entrada externa:** se **resuelve** contra el sistema de ficheros y se compara
  con el directorio permitido, también resuelto y seguido del separador; normalizar el
  texto no es validar.
- **Argumento externo:** tras el separador de fin de opciones.
- **Expresión regular sobre entrada externa:** su coste se mide y la entrada se acota.

## Secretos

Ninguno en el repositorio: marcadores y `*.example`. Uno que llegó a un commit se
**rota**. Jerarquía de configuración: valores por defecto en código → fichero versionado
sin secretos → entorno → gestor de secretos. **Alias siempre**; el dato real, en
`_local/` (R-03 del marco alambique).

Las etapas de seguridad del pipeline (`tooling.md`) son puertas: ante un hallazgo crítico,
para. Un cambio con implicación de seguridad dice **qué dato toca, quién puede verlo y qué
control lo limita**; si amplía quién ve qué, se declara en la entrega.
