# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import flask_babel as babel

from flask import current_app as app


@app.template_filter()
def format_date(value, format='medium'):
    return babel.format_date(value, format)


@app.template_filter()
def format_datetime(value, format='short'):
    return babel.format_datetime(value, format)
