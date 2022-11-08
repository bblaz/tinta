# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import logging

from flask import (
    current_app, g, session,
    request, render_template, redirect, url_for)
from flask_babel import gettext

from .. import babel
from .. import tryton
from . import main


logger = logging.getLogger(__name__)


Date = tryton.pool.get('ir.date')
WOTD = tryton.pool.get('tinta.word.wotd')


@babel.localeselector
def get_locale():
    # if url arg lang is set
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
        return session.get('lang', request.accept_languages.best_match(
            ['ru', 'sl', 'en']))
    # if session lang is set
    if session.get('lang'):
        return session.get('lang', request.accept_languages.best_match(
            ['ru', 'sl', 'en']))
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        session['lang'] = user.locale
        return user.locale
    return request.accept_languages.best_match(['ru', 'sl', 'en'])


@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


@main.route('/')
@main.route('/home')
@tryton.transaction()
def home():
    current_app.logger.debug(request.headers)
    wotds = WOTD.search([
        ('state', 'in', ['open', 'draft']),
        ('date', '=', Date.today()),
        ], limit=5)
    wotds_next = WOTD.search([
        ('state', 'in', ['open', 'draft']),
        ('date', '>', Date.today()),
        ], limit=1, order=[('date', 'ASC')])
    wotds_active = WOTD.search([
        ('date', '<', Date.today()),
        ('state', '=', 'open'),
        ])
    wotds_previous = WOTD.search([
        ('date', '<=', Date.today()),
        ('state', '=', 'closed'),
        ])
    wotd = None
    wotd_next = None
    if wotds:
        wotd = wotds[0]
    if wotds_next:
        wotd_next = wotds_next[0]

    return render_template(
        'wotd.html', title=gettext("Word of the Day"),
        today=Date.today(),
        wotd_today=wotd, wotd_next=wotd_next,
        wotds_active=wotds_active, wotds_previous=wotds_previous)


@main.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))
