# Documentación de Organilab

Documentación Sphinx y micrositio de capacitación de
[Organilab](https://github.com/Solvosoft/organilab). Vivía dentro del repo de la
aplicación, en `docs/`; se separó para que el repo de código no cargue con ~400 MB de
GIFs y para que la documentación tenga su propio ciclo de release.

## Qué hay acá

| Ruta | Qué es |
|---|---|
| `source/*.rst` | Manual en reStructuredText (49 documentos, español) |
| `source/developers/` | Documentación de API: usa `autodoc` contra el código de la aplicación |
| `source/_static/` | Imágenes, GIFs y video. **Casi todo es salida de la suite Selenium de organilab** |
| `source/_extra/capacitacion/` | Micrositio de capacitación: HTML escrito a mano (6 capítulos, Bootstrap por CDN). Sphinx lo copia tal cual vía `html_extra_path` |
| `fix_capacitacion_images.py` | Copia `source/_static/` → `source/_extra/capacitacion/img/` y corrige los `src=` |

## Construir

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
make html          # corre fix_capacitacion_images.py y luego sphinx-build
```

El resultado queda en `build/html/`; la capacitación en `build/html/capacitacion/`.

### `source/developers/` y el código de la aplicación

Esa sección usa `autodoc`, así que necesita importar el código de Organilab. `source/conf.py`
lo busca, en este orden:

1. `$ORGANILAB_SRC`, si está definida
2. `_organilab/src` (el checkout que hace Read the Docs, ver `.readthedocs.yml`)
3. `../organilab/src` (el repo hermano, que es el caso normal en local)

**Si no encuentra ninguno, excluye `source/developers/` y construye todo lo demás igual.**
El build avisa por stdout cuando eso pasa. Para forzar una ruta concreta:

```bash
ORGANILAB_SRC=/ruta/a/organilab/src make html
```

Desde el repo de la aplicación, `make docs` delega acá pasando `ORGANILAB_SRC` solo.

## De dónde salen las imágenes

`source/_static/*.png` y `source/_static/gif/*.gif` **no se escriben a mano**: los genera la
suite Selenium de organilab (`src/organilab_test/tests/base.py`, métodos
`create_screenshot` y `create_gif`). Para regenerarlos, desde el repo de la aplicación:

```bash
make test-selenium-xvfb TEST=organilab_test.tests.selenium_tests.capacitacion
```

Los tests escriben en `DOCS_SOURCE_DIR` (env var `DOCS_STATIC_DIR`), que por defecto apunta
a este repo si está clonado al lado de organilab. Después se commitean acá.

### `source/_extra/capacitacion/img/` no se versiona

Es una copia byte a byte de `source/_static/`. Antes se versionaban las dos (~89 MB
duplicados que se desincronizaban entre sí). Ahora la genera `fix_capacitacion_images.py`,
que corre como paso previo al build: `make images`, `make html`, y `build.jobs.pre_build`
en Read the Docs.

Si publicás el sitio por otro medio, **ese script tiene que correr antes del build** o la
capacitación sale sin imágenes.
