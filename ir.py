# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta


__all__ = ['Cron']


class Cron(metaclass=PoolMeta):
    __name__ = 'ir.cron'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.method.selection.append(
            ('tinta.word.wotd|generate_days',
                "Generate days for Words of the Day"))
        cls.method.selection.append(
            ('tinta.word.wotd|populate_days',
                "Populate days with Words of the Day"))
        cls.method.selection.append(
            ('tinta.word.wotd|publish_days',
                "Publish Words of the Day"))
        cls.method.selection.append(
            ('tinta.word.wotd|close_days',
                "Close Words of the Day"))
