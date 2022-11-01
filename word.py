# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import datetime
import logging
import random

from trytond.i18n import gettext
from trytond.model import (
    ModelSQL, ModelView, Workflow, fields,
    Unique, )
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.wizard import Wizard, StateView, StateTransition, Button

from .exceptions import OutOfWordsError, WordError

__all__ = [
    'Word', 'WordOTD',
    'GenerateWOTD',
    ]


logger = logging.getLogger(__name__)


class Word(ModelSQL, ModelView):
    """Tinta Words"""
    __name__ = 'tinta.word'

    name = fields.Char("Name", required=True)
    wotds = fields.One2Many(
        'tinta.word.wotd', 'word', "Words of the Day",
        readonly=True)


WOTD_STATES = [
    ('draft', "Draft"),
    ('open', "Open"),
    ('closed', "Closed"),
    ]


class WordOTD(Workflow, ModelSQL, ModelView):
    """Tinta Word of the Day"""
    __name__ = 'tinta.word.wotd'
    _transition_state = 'state'

    state = fields.Selection(WOTD_STATES, "State", readonly=True)
    date = fields.Date("Date", required=True)
    word = fields.Many2One(
        'tinta.word', "Word", required=True, select=True,
        ondelete='RESTRICT')

    start_date = fields.DateTime("Start date", format="%H:%M")
    end_date = fields.DateTime("End date", format="%H:%M")

    @classmethod
    def __setup__(cls):
        super().__setup__()

        t = cls.__table__()
        # Unique dates
        cls._sql_constraints = [
            ('date_uniq', Unique(t, t.date),
                'tinta.msg_unique_date'),
            ]

        cls._buttons.update({
            'draft': {},
            'open': {},
            'close': {},
            })

        cls._transitions |= set((
            ('draft', 'open'),
            ('open', 'closed'),
            ('open', 'draft'),
            ('closed', 'open'),
            ))

        # Record order
        cls._order.insert(0, ('date', 'DESC'))

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    @Workflow.transition('closed')
    def close(cls, ids):
        pass

    @classmethod
    @Workflow.transition('draft')
    def draft(cls, ids):
        pass

    @classmethod
    @Workflow.transition('open')
    def open(cls, ids):
        pass

    @classmethod
    def generate_wotd(cls, ids=None, date=None):
        pool = Pool()
        Date = pool.get('ir.date')
        Word = pool.get('tinta.word')
        WordOTD = pool.get('tinta.word.wotd')

        if not date:
            date = Date.today()

        words = Word.search_count([])
        wotds = WordOTD.search_count([])
        if words == wotds:
            logger.warning("All words used up!")
            raise OutOfWordsError(
                gettext('party.msg_word_ran_out'))

        n = random.randint(1, words-wotds)

        logger.info(
            "Have %i words, have %i wotds, got %i as random." %
            (words, wotds, n))

        words = Word.search([
            ('wotds', '=', None),
            ], limit=1, offset=n-1)

        if not words:
            logger.warning("Word not found!")
            raise WordError(
                gettext('party.msg_word_not_found'))

        logger.info("Found unassigned words: %s" % words)

        wotd = WordOTD()
        wotd.date = date
        wotd.word = words[0]
        wotd.save()


class GenerateWOTD(Wizard):
    """Tinta Generate Word of the Day"""
    __name__ = 'tinta.word.wotd.generate'

    start_state = 'generate'

    generate = StateTransition()

    def transition_generate(self):
        logger.info("Generating WOTD...")
        WordOTD = Pool().get('tinta.word.wotd')
        WordOTD.generate_wotd()
        logger.info("WOTD done.")
        return 'end'
