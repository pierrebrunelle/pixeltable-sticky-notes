"""The notes table, declared as a Python class on a Pixeltable model base."""
import pixeltable as pxt
import pixeltable.functions as pxtf

from udfs import blurb

TableModel = pxt.model_base()


class Notes(TableModel, name='notes'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    title: pxt.String
    body: pxt.String
    tag: pxt.String | None

    title_upper = pxtf.string.upper(title)   # built-in string function
    blurb = blurb(body)                       # our UDF from udfs.py
