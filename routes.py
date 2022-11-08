# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import datetime
import logging
import os

from jinja2 import Environment, FileSystemLoader
from werkzeug.exceptions import abort
from werkzeug.wrappers import Response

from trytond.wsgi import app
from trytond.protocols.wrappers import (
    allow_null_origin, user_application, with_pool, with_transaction)
from trytond.transaction import Transaction


logger = logging.getLogger(__name__)


DATEFORMAT = "%d.%m.%Y"
TIMEFORMAT = "%H:%M"


def format_date(value, format=None):
    if not format:
        format = DATEFORMAT
    return datetime.date.strftime(value, format)


def format_datetime(value, format=None):
    if not format:
        format = DATEFORMAT + " " + TIMEFORMAT
    return datetime.datetime.strftime(value, format)


template_path = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = Environment(
    loader=FileSystemLoader(template_path), autoescape=True)
jinja_env.globals['format_date'] = format_date
jinja_env.globals['format_datetime'] = format_datetime


@app.route('/<database_name>/tinta/wotd', methods=['GET'])
@allow_null_origin
@with_pool
@with_transaction()
def wotd(request, pool):
    t = jinja_env.get_template("wotd.html")

    Date = pool.get('ir.date')
    WOTD = pool.get('tinta.word.wotd')
    wotds = WOTD.search([
        ('date', '=', Date.today()),
        ], limit=1)
    wotds_next = WOTD.search([
        ('state', 'in', ['open', 'draft']),
        ('date', '>', Date.today()),
        ], limit=1, order=[('date', 'ASC')])
    wotds_active = WOTD.search([
        ('date', '<', Date.today()),
        ('state', '=', 'open'),
        ])
    wotds_previous = WOTD.search([
        ('date', '<', Date.today()),
        ('state', '=', 'closed'),
        ])
    wotd = None
    wotd_next = None
    if wotds:
        wotd = wotds[0]
    if wotds_next:
        wotd_next = wotds_next[0]

    return Response(
        t.render(
            today=Date.today(),
            wotd_today=wotd, wotd_next=wotd_next,
            wotds_active=wotds_active, wotds_previous=wotds_previous),
        mimetype="text/html")
    return str([{'date': wotd.date, 'word': wotd.word.name} for wotd in wotds])
