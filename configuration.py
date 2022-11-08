# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import logging

from trytond.model import (
    ModelView, ModelSQL, MultiValueMixin, ValueMixin, ModelSingleton, fields)
from trytond.pool import Pool
from trytond.pyson import Eval


__all__ = ['Configuration', 'ConfigurationWord']

logger = logging.getLogger(__name__)


word_frequency = fields.Selection([
    ('dailly', "Dailly"),
    ('weekly', "Weekly"),
    ], "Frequency")
word_weekday = fields.MultiSelection(
    'get_days', "Days of week",
    states={
        'invisible': ~Eval('word_frequency').in_(['weekly']),
        'required': Eval('word_frequency').in_(['weekly']),
        },
    sort=False)
word_publish_time = fields.Time("Publish time", format="%H:%M")
word_submission_time = fields.TimeDelta("Submission in")


def get_days():
    Day = Pool().get('ir.calendar.day')
    return [(day.index, day.name) for day in Day.search([])]


class Configuration(ModelSingleton, ModelSQL, ModelView):
    """Tinta Configuration"""
    __name__ = 'tinta.configuration'

    word_frequency = word_frequency
    word_weekday = word_weekday
    word_publish_time = word_publish_time
    word_submission_time = word_submission_time

    @staticmethod
    def get_days():
        return get_days()

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field.startswith('word_'):
            return pool.get('tinta.configuration.word')
        return super(Configuration, cls).multivalue_model(field)


class ConfigurationWord(ModelSQL, ValueMixin):
    """Tinta Word Configuration"""
    __name__ = 'tinta.configuration.word'

    word_frequency = word_frequency
    word_weekday = word_weekday
    word_publish_time = word_publish_time
    word_submission_time = word_submission_time

    @staticmethod
    def get_days():
        return get_days()
