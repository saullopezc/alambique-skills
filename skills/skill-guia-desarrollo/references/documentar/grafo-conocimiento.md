# Grafo de conocimiento — enlazar y validar `docs/`

Nodos, plantillas y frontmatter: `../documentar.md`.

| Regla | Por qué importa |
|---|---|
| **Un nodo es un fichero `docs/<id>.md`:** un tema, y su `id` es su nombre. | El enlace se resuelve por nombre de fichero. |
| **Una arista es un `[[id]]`** en cada mención a otro nodo. | Buscarlo dice quién lo referencia. |
| **Un enlace a un nodo que aún no existe no es un error:** es documentación pendiente declarada. | Lo que falta queda visible. |
| **El índice `docs/README.md` se actualiza en el mismo cambio que crea o modifica un nodo.** | Un nodo que no está en el índice no existe. |

## Validación

Se ejecuta antes de cerrar y su resultado se reporta al terminar. Solo mira la raíz de
`docs/`.

```bash
cd docs
# 1. Aristas: cada [[id]] debe existir como <id>.md; con marcador es plantilla sin rellenar
grep -hoE '\[\[[^] ]+\]\]' *.md | tr -d '[]' | sort -u | while read -r id; do
  case "$id" in
    *'<'*|*YYYY*) echo "ENLACE SIN RELLENAR: $id" ;;
    *) [ -f "$id.md" ] || echo "PENDIENTE: $id" ;;
  esac
done
# 2. Cabecera de TODO nodo, índice incluido: solo cuenta el bloque entre los dos '---'
for f in *.md; do
  awk -v f="$f" -v id="${f%.md}" '
    NR == 1 { if ($0 != "---") exit; next }
    $0 == "---" { cerrada = 1; exit }
    /^[a-z_]+:/ {
      campo = $0; sub(/:.*/, "", campo)
      valor = $0; sub(/^[a-z_]+:[ \t]*/, "", valor)
      sub(/[ \t]+#.*$/, "", valor); sub(/[ \t]+$/, "", valor)
      v[campo] = valor
      if (valor ~ /</ || valor ~ /YYYY/) { print "SIN RELLENAR (" campo "): " f; v[campo] = ""; marcador[campo] = 1 }
    }
    END {
      if (!cerrada) { print "SIN CABECERA: " f; exit }
      n = split("id tipo clasificacion responsable", obligatorio, " ")
      for (i = 1; i <= n; i++) { o = obligatorio[i]; if (v[o] == "" && !(o in marcador)) print "FALTA (" o "): " f }
      if (v["id"] != "" && v["id"] != id) print "ID≠ARCHIVO: " f
      if (v["tipo"] != "" && v["tipo"] !~ /^(indice|resumen|stack|arquitectura|modulo|decision|runbook)$/)
        print "TIPO DESCONOCIDO (" v["tipo"] "): " f
      if (v["clasificacion"] != "" && v["clasificacion"] !~ /^C[0-3]$/)
        print "CLASIFICACION INVALIDA (" v["clasificacion"] "): " f
    }' "$f"
done
# 3. Huérfanos: nodos sin arista entrante desde OTRO nodo (el autoenlace no cuenta)
for f in *.md; do [ "$f" = README.md ] && continue
  grep -lF "[[${f%.md}]]" *.md | grep -vxF "$f" | grep -q . || echo "HUERFANO: $f"
done
```

Solo `PENDIENTE` es aceptable; cualquier otro aviso se corrige. La lista de `tipo` es la
de `../documentar.md`: cambian juntas.

No comprueba los valores de `estado`, que el `responsable` sea una persona, que la
`clasificacion` sea la correcta —solo su forma—, los marcadores que queden en el cuerpo de
un nodo, un enlace cuyo nombre lleve espacios, que cada nodo figure en el índice ni la cabecera de los ficheros de un plan
(`../fases.md`). Eso se lee.
