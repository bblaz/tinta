# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import Pool

from . import configuration
from . import ir
from . import tinta
from . import word

from . import routes


__all__ = ['register', 'routes']


def register():
    Pool.register(
        configuration.Configuration,
        configuration.ConfigurationWord,
        ir.Cron,
        word.ImportWordStart,
        word.Word,
        word.WordOTD,
        module='tinta', type_='model')
    Pool.register(
        word.ImportWord,
        word.GenerateWOTD,
        module='tinta', type_='wizard')
    Pool.register(
        module='tinta', type_='report')
