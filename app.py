"""Sticky Notes API built with Pixeltable.

    pxt schema update app.py notes
    pxt service run app.py notes
"""
from pixeltable.serving import FastAPIRouter

from models import Notes, TableModel  # noqa: F401  (TableModel lets `pxt schema` find the models)
from queries import notes_by_tag

notes_api = FastAPIRouter(name='notes_api')
notes_api.add_insert_route(Notes, path='/notes', inputs=[Notes.title, Notes.body, Notes.tag],
                           outputs=[Notes.id, Notes.title_upper, Notes.blurb])
notes_api.add_update_route(Notes, path='/notes/update', inputs=[Notes.title], outputs=[Notes.id, Notes.title_upper])
notes_api.add_delete_route(Notes, path='/notes/delete')
notes_api.add_compute_route(Notes, path='/titles', inputs=[Notes.title], outputs=[Notes.title_upper])
notes_api.add_query_route(path='/notes/by-tag', query=notes_by_tag, method='get')
