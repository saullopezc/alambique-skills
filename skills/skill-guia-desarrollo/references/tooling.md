# Herramientas: análisis, editor y pipeline

Aquí se concentran los **productos** de análisis, editor y pipeline, con sus órdenes.
Nombres y órdenes envejecen: una orden se comprueba en la versión instalada antes de
fiarse.

| Herramienta | Propósito | Uso |
|---|---|---|
| Semgrep | Código, por reglas | `semgrep --config <reglas-locales>/ .` |
| Gitleaks | Secretos en **lo preparado** | `gitleaks protect --staged` |
| Gitleaks | Secretos en el **árbol** | `gitleaks detect --no-git --source .` |
| Gitleaks | Secretos en el **historial** | `gitleaks detect --source .` |
| OWASP Dependency-Check | Dependencias vulnerables | `dependency-check --scan .` |
| Trivy | Dependencias vulnerables y secretos en el **árbol** | `trivy fs .` |
| Trivy | Vulnerabilidades de la **imagen** construida | `trivy image <imagen>` |

- **Los subcomandos cambian entre versiones** (en Gitleaks recientes, `detect` y
  `protect` ceden ante `git` y `dir`): se mira `--help`, y un detector se ve **detectar**
  un secreto de prueba antes de fiarse (`qa.md`).
- **Con datos de terceros** no se usan los modos que consultan un servicio externo, como
  `semgrep --config=auto`: reglas locales y escáner con la base ya descargada, también en
  las extensiones del editor.

## Editor (VSCode)

Comunes: `EditorConfig.EditorConfig` y `SonarSource.sonarlint-vscode`.

| Lenguaje | Extensiones | Formatea y analiza |
|---|---|---|
| Java | `vscjava.vscode-java-pack`, `shengchen.vscode-checkstyle` | `redhat.java` y `checkstyle.xml` del proyecto |
| C/C++ | `llvm-vs-code-extensions.vscode-clangd`, `ms-vscode.cmake-tools` | clang-format y clang-tidy (`clang-tidy -p build <fuentes>`) |
| Python | `ms-python.python`, `charliermarsh.ruff` | `ruff check` y `ruff format`, con `select` explícito (G-09) |
| Perl | `bscan.perlnavigator` | perltidy y perlcritic (severidad 3) |

**Ajustes base,** en el editor y en `.editorconfig` (`root = true`): UTF-8, LF, espacios
(4 en Java y C/C++; tabulador en Makefile), sin espacios finales, con salto final de
fichero. El editor formatea y ordena importaciones al guardar.

**Un hook que el proyecto ya tiene se encadena, no se pisa:** antes de instalar otro
(`pre-commit` en Python) se miran `.git/hooks/` y `core.hooksPath`; un gestor que
redirige `core.hooksPath` deja sin ejecutar lo que había.

## Pipeline

Etapas en orden: lint → pruebas unitarias → de integración → seguridad: código y
dependencias → build y escaneo de la imagen (`docker.md`) → despliegue al entorno previo →
pruebas de extremo a extremo → producción, manual o automática según la política.
Automática es una acción sin turno: la política la aprueba antes y acotada —qué despliega,
a dónde, hasta cuándo vale esa aprobación— y cada ejecución queda registrada contra ella
(R-09 del marco alambique).

Las de prueba y las de seguridad son puertas: si una prueba falla o aparece un hallazgo
crítico, el pipeline para, y no se integra en rojo (`qa.md`).

- **El entorno de QA se define junto al de desarrollo,** y **nunca con datos ni
  credenciales de producción**.
- **Sin integración continua,** un script del proyecto ejecuta lint, build, pruebas y
  comparación A/B antes de cada commit.
