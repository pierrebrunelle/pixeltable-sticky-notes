<!-- pixeltable-example-app: 20260921-sticky-notes -->
# Sticky Notes API built with Pixeltable

[![Built with Pixeltable](https://img.shields.io/badge/built%20with-Pixeltable-5b4bff)](https://pixeltable.com)
[![PyPI - pixeltable](https://img.shields.io/pypi/v/pixeltable?label=pixeltable)](https://pypi.org/project/pixeltable/)
[![GitHub stars](https://img.shields.io/github/stars/pixeltable/pixeltable?style=social)](https://github.com/pixeltable/pixeltable)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

The smallest useful Pixeltable backend: a `notes` table with a title, a body and an optional tag. Pixeltable keeps two **computed columns** up to date for every note (an upper-cased title for display and a short preview of the body), and a `FastAPIRouter` publishes create, rename, delete, preview and list-by-tag endpoints with OpenAPI docs. It is a good first project if you want to see how a Python class becomes a typed, persistent REST API.

[Pixeltable](https://pixeltable.com) is open-source, Python-native **multimodal AI data infrastructure**: tables, incremental computed columns, UDFs, indexes and serving in one library, running locally or on Pixeltable Cloud.

> ⭐ **Like this example?** Star [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable) on GitHub. It helps other developers find it.

## What this example shows

- **FastAPI serving**: one `FastAPIRouter` turns tables and `@pxt.query` functions into typed REST routes (insert, update, delete, compute and query) with OpenAPI docs
- **Incremental computed columns** powered by plain Python UDFs (`@pxt.udf`)
- **Importable UDF module**: UDFs in `udfs.py`, tables in `models.py`, queries in `queries.py`, routes in `app.py` (Pixeltable resolves UDFs by module path)
- **`pixeltable.toml`** declares a local database and a **Pixeltable Cloud** database, so the same code deploys with `pxt db update`

## How a note flows through Pixeltable

1. `POST /notes` inserts `title`, `body`, `tag`. Pixeltable assigns a UUIDv7 `id` and computes `title_upper` and `blurb` in the same transaction, then returns them.
2. `POST /notes/update` renames a note by `id`; only `title_upper` is recomputed, because `blurb` doesn't depend on the title.
3. `POST /titles` runs the same expression without storing anything: handy for a live preview in a UI.
4. `GET /notes/by-tag?tag=...` is a `@pxt.query`, so filtering logic lives next to the data instead of in the web layer.

## What's inside

| File | What it is |
|------|------------|
| `app.py` | The API: one `FastAPIRouter` wiring the tables and queries into REST routes |
| `client_demo.py` | Create, preview, rename, list and delete sticky notes through the API |
| `models.py` | Tables declared as Python classes: columns, computed columns, indexes |
| `pixeltable.toml` | Project config: the local database plus a Pixeltable Cloud database (sizing, deploy excludes) |
| `queries.py` | `@pxt.query` functions served as query routes |
| `seed.py` | Seed a handful of sticky notes |
| `udfs.py` | Pixeltable UDFs (`@pxt.udf`) in their own importable module |
| `requirements.txt` / `pyproject.toml` | Dependencies (`pixeltable[serve]>=0.7.14`) |

**Tables**

| Table | Stored columns | Computed columns |
|-------|---------|------------------|
| `notes` | `title`, `body`, `tag` | `id`, `title_upper`, `blurb` |

**API routes** (service `notes_api`)

| Method | Path | Kind | Backed by | Notes |
|--------|------|------|-----------|-------|
| `POST` | `/notes` | insert | `Notes` |  |
| `POST` | `/notes/update` | update | `Notes` |  |
| `POST` | `/notes/delete` | delete | `Notes` |  |
| `POST` | `/titles` | compute | `Notes` |  |
| `GET` | `/notes/by-tag` | query | `notes_by_tag` |  |

## Quickstart

Requires Python 3.11+ and `pixeltable[serve]>=0.7.14`.

```bash
git clone https://github.com/pierrebrunelle/pixeltable-sticky-notes.git
cd pixeltable-sticky-notes
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create the tables in a local catalog directory named `notes`
pxt schema update app.py notes

python seed.py notes
pxt service run app.py notes --port 8000   # open http://localhost:8000/docs
python client_demo.py                     # in another terminal
```

Try it:

```bash
curl -s -X POST localhost:8000/notes -H 'Content-Type: application/json' -d '{"title": "Call the plumber", "body": "Kitchen tap drips", "tag": "home"}'
curl -s 'localhost:8000/notes/by-tag?tag=home'
```

## Deploy to Pixeltable Cloud

The same `app.py` runs on [Pixeltable Cloud](https://pixeltable.com). Sign in (or get a free trial database with `pxt new`), point the second database entry in `pixeltable.toml` at your own database, then deploy:

```bash
pxt login                       # or: export PIXELTABLE_API_KEY=<your-api-key>
# edit pixeltable.toml: name = 'pxt://<your-org>:<your-db>'
pxt db update pxt://<your-org>:<your-db>                 # build the image and upload the project
pxt schema update app.py pxt://<your-org>:<your-db>/notes   # create the tables in the hosted database
pxt service update app.py pxt://<your-org>:<your-db>/notes  # start the API there
pxt service list pxt://<your-org>:<your-db>              # list hosted services
```

Hosted routes require an API key: send it in the `X-api-key` header (for example `-H "X-api-key: $PIXELTABLE_API_KEY"`). Keep keys in environment variables or `pxt secret set`, never in code.

## Code walkthrough

**1. Business logic is plain Python, in `udfs.py`.** A `@pxt.udf` function can be used as a column expression. Pixeltable records UDFs by module path (`udfs.blurb`), so they live in their own importable module rather than inline in the app: the daemon, serving workers and Pixeltable Cloud import it again by that path.

```python
# udfs.py
@pxt.udf
def blurb(body: str, max_chars: int = 48) -> str:
    """First line of the body, trimmed to max_chars with an ellipsis."""
    first = (body or '').strip().splitlines()[0] if (body or '').strip() else ''
    return first if len(first) <= max_chars else first[: max_chars - 1].rstrip() + '…'
```

**2. Tables are Python classes (`models.py`).** Annotated attributes are stored columns; attributes assigned an expression are **computed columns** (`id`, `title_upper`, `blurb`), evaluated incrementally on every insert or update and recomputed when their inputs change.

```python
# models.py
class Notes(TableModel, name='notes'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    title: pxt.String
    body: pxt.String
    tag: pxt.String | None

    title_upper = pxtf.string.upper(title)   # built-in string function
    blurb = blurb(body)
```

**3. Queries are functions (`queries.py`).** `@pxt.query` wraps a Pixeltable query so it can be called from Python or exposed as a route:

```python
# queries.py
@pxt.query
def notes_by_tag(tag: str):
    """Notes with a given tag, newest first (UUIDv7 ids sort by creation time)."""
    return Notes.where(Notes.tag == tag).select(Notes.id, Notes.title, Notes.blurb).order_by(Notes.id, asc=False)
```

**4. One router, a full REST API.** `FastAPIRouter` generates request/response models from the column types, validates input, and publishes OpenAPI docs at `/docs`:

```python
# app.py
notes_api = FastAPIRouter(name='notes_api')
notes_api.add_insert_route(Notes, path='/notes', inputs=[Notes.title, Notes.body, Notes.tag],
                           outputs=[Notes.id, Notes.title_upper, Notes.blurb])
notes_api.add_update_route(Notes, path='/notes/update', inputs=[Notes.title], outputs=[Notes.id, Notes.title_upper])
notes_api.add_delete_route(Notes, path='/notes/delete')
notes_api.add_compute_route(Notes, path='/titles', inputs=[Notes.title], outputs=[Notes.title_upper])
notes_api.add_query_route(path='/notes/by-tag', query=notes_by_tag, method='get')
```

## Learn more

- 🌐 Website: https://pixeltable.com
- 📚 Docs: https://docs.pixeltable.com
- 💻 Source: https://github.com/pixeltable/pixeltable (⭐ star it if Pixeltable is useful to you)
- 📦 PyPI: https://pypi.org/project/pixeltable/

---

<sub>Built as part of a daily series of Pixeltable example apps · Pixeltable 0.7.14 · Python, FastAPI, incremental computed columns · Licensed under Apache-2.0.</sub>
