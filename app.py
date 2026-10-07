"""Sticky Notes API built with Pixeltable.

    pxt schema update app.py notes
    pxt service run app.py notes
"""
import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

from udfs import blurb

# ---- tables ----
TableModel = pxt.model_base()


class Notes(TableModel, name='notes'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    title: pxt.String
    body: pxt.String
    tag: pxt.String | None

    title_upper = pxtf.string.upper(title)   # built-in string function
    blurb = blurb(body)                       # our UDF from udfs.py


# ---- queries ----
@pxt.query
def notes_by_tag(tag: str):
    """Notes with a given tag, newest first (UUIDv7 ids sort by creation time)."""
    return Notes.where(Notes.tag == tag).select(Notes.id, Notes.title, Notes.blurb).order_by(Notes.id, asc=False)


# ---- routes ----
notes_api = FastAPIRouter(name='notes_api')
notes_api.add_insert_route(Notes, path='/notes', inputs=[Notes.title, Notes.body, Notes.tag],
                           outputs=[Notes.id, Notes.title_upper, Notes.blurb])
notes_api.add_update_route(Notes, path='/notes/update', inputs=[Notes.title], outputs=[Notes.id, Notes.title_upper])
notes_api.add_delete_route(Notes, path='/notes/delete')
notes_api.add_compute_route(Notes, path='/titles', inputs=[Notes.title], outputs=[Notes.title_upper])
notes_api.add_query_route(path='/notes/by-tag', query=notes_by_tag, method='get')
