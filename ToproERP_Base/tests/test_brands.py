# -*- coding: utf-8 -*-
from odoo.tests import common

class TestBrands(common.TransactionCase):
    """ This class extends the base TransactionCase, in order to test the
    accounting with localization setups. It is configured to run the tests after
    the installation of all modules, and will SKIP TESTS ifit  cannot find an already
    configured accounting (which means no localization module has been installed).
    """

    post_install = True
    at_install = False


    def test_brands(self):

        self.brands_model = self.env['toproerp.brands']

        self.brands = self.brands_model.create({'brands_no':'ouge','name':u'讴歌'})

        brands = self.brands_model.search([], order="id desc", limit=1)

        self.assertEquals(brands.brands_no,'ouge')
        self.assertEquals(brands.name,u'讴歌')


