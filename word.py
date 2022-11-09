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
from trytond.transaction import Transaction
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

    @classmethod
    def __setup__(cls):
        super().__setup__()

        t = cls.__table__()
        # Unique words
        cls._sql_constraints = [
            ('word_uniq', Unique(t, t.name),
                'tinta.msg_unique_word'),
            ]


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
        'tinta.word', "Word", select=True,
        states={
            'required': Eval('state').in_(['open', 'closed'])
            },
        ondelete='RESTRICT')
    wotd = fields.Function(
        fields.Char("WOTD"),
        'get_wotd')

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

    def check_word(self):
        if not self.word:
            raise WordError(
                gettext(
                    "tinta.msg_word_required",
                    date=self.date))

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    def get_wotd(cls, ids, names):
        res = {}
        for name in names:
            res[name] = {}

        for wotd in ids:
            for name in names:
                if name == 'wotd':
                    res[name][wotd.id] = None
                    if wotd.word:
                        res[name][wotd.id] = wotd.word.name
        return res

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
        for wotd in ids:
            wotd.check_word()

    @staticmethod
    def generate():
        pool = Pool()
        Word = pool.get('tinta.word')
        WordOTD = pool.get('tinta.word.wotd')

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

        return words[0]

    @staticmethod
    def create_day(date):
        pool = Pool()
        Config = pool.get('tinta.configuration')
        config = Config(1)
        WordOTD = pool.get('tinta.word.wotd')

        # Check if date already exists
        wotds = WordOTD.search([
            ('date', '=', date)
            ])
        if wotds:
            # Skip if it does
            return

        # Create new date if it does not
        wotd = WordOTD()
        wotd.date = date
        wotd.start_date = datetime.datetime.combine(
            wotd.date, config.word_publish_time,
            tzinfo=datetime.timezone.utc)
        wotd.end_date = wotd.start_date + config.word_submission_time
        wotd.save()

    @classmethod
    def generate_days(cls):
        pool = Pool()
        Config = pool.get('tinta.configuration')
        config = Config(1)
        Date = pool.get('ir.date')
        WordOTD = pool.get('tinta.word.wotd')

        if config.word_frequency == 'dailly':
            WordOTD.create_day(Date.today())
        elif config.word_frequency == 'weekly':
            if Date.today().weekday() in config.word_weekday:
                WordOTD.create_day(Date.today())

    @classmethod
    def populate_days(cls):
        pool = Pool()
        WordOTD = pool.get('tinta.word.wotd')

        # Get current datetime
        in_one_hour = datetime.datetime.now() + datetime.timedelta(hours=1)

        # Get days to be populated
        wotds = WordOTD.search([
            ('state', '=', 'draft'),
            ('start_date', '<=', in_one_hour)
            ])
        if wotds:
            for wotd in wotds:
                wotd.word = wotd.generate()
                wotd.save()

    @classmethod
    def publish_days(cls):
        pool = Pool()
        WordOTD = pool.get('tinta.word.wotd')

        # Get current datetime
        in_one_hour = datetime.datetime.now() + datetime.timedelta(hours=1)
        wotds = WordOTD.search([
            ('state', '=', 'draft'),
            ('start_date', '<=', in_one_hour),
            ('word', '!=', None),
            ])
        if wotds:
            for wotd in wotds:
                delta = wotd.start_date - datetime.datetime.now()
                with Transaction().set_context(queue_scheduled_at=delta):
                    WordOTD.__queue__.open([wotd])

    @classmethod
    def close_days(cls):
        logger.info("Closing days...")
        pool = Pool()
        WordOTD = pool.get('tinta.word.wotd')

        # Get current datetime
        in_one_hour = datetime.datetime.now() + datetime.timedelta(hours=1)
        wotds = WordOTD.search([
            ('state', '=', 'open'),
            ('end_date', '<=', in_one_hour),
            ])
        if wotds:
            logger.info("Found WOTDs to close: %s" % wotds)
            for wotd in wotds:
                delta = wotd.end_date - datetime.datetime.now()
                with Transaction().set_context(queue_scheduled_at=delta):
                    WordOTD.__queue__.close([wotd])

        logger.info("Days closing complete.")

    @classmethod
    def generate_wotd(cls, ids=None, date=None):
        pool = Pool()
        Date = pool.get('ir.date')

        if not date:
            date = Date.today()

        wotd = WordOTD()
        wotd.date = date
        wotd.word = WordOTD.generate()
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


class ImportWordStart(ModelView):
    """Tinta Import Words Start"""
    __name__ = 'tinta.word.import.start'

    words = fields.Text(
        "Words", required=True,
        help="One word per line.")


class ImportWord(Wizard):
    """Tinta Import Words"""
    __name__ = 'tinta.word.import'

    start_state = 'start'

    start = StateView(
        'tinta.word.import.start',
        'tinta.word_import_start_view', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Import', 'import_', 'tryton-ok', default=True),
            ])

    import_ = StateTransition()

    def transition_import_(self):
        Word = Pool().get('tinta.word')

        for word in self.start.words.split('\n'):
            logger.info("Found word: %s")

            try:
                w = Word()
                w.name = word.strip()
                w.save()
            except Exception as e:
                logger.warning("Exception was raised %s: %s" % (type(e), e))
                continue

        return 'end'
