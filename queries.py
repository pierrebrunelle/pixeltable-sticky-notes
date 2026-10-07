"""Queries over the notes table, served as GET routes."""
import pixeltable as pxt

from models import Notes


@pxt.query
def notes_by_tag(tag: str):
    """Notes with a given tag, newest first (UUIDv7 ids sort by creation time)."""
    return Notes.where(Notes.tag == tag).select(Notes.id, Notes.title, Notes.blurb).order_by(Notes.id, asc=False)
