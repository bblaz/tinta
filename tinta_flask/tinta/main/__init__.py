# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from flask import Blueprint, url_for

main = Blueprint(
    'main', __name__, template_folder='templates',
    static_folder='static', static_url_path='/main/static')

from . import views     # noqa
