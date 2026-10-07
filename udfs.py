"""Pixeltable UDFs for the sticky-notes API (recorded by module path, e.g. `udfs.blurb`)."""
import pixeltable as pxt


@pxt.udf
def blurb(body: str, max_chars: int = 48) -> str:
    """First line of the body, trimmed to max_chars with an ellipsis."""
    first = (body or '').strip().splitlines()[0] if (body or '').strip() else ''
    return first if len(first) <= max_chars else first[: max_chars - 1].rstrip() + '…'
