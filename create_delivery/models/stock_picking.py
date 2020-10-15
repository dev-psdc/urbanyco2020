# # -*- coding: utf-8 -*-
# # Part of Odoo. See LICENSE file for full copyright and licensing details.

# from collections import namedtuple
# import json
# import time

# from itertools import groupby
# from odoo import api, fields, models, _
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
# from odoo.tools.float_utils import float_compare, float_is_zero, float_round
# from odoo.exceptions import UserError
# from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
# from operator import itemgetter


# class Picking(models.Model):
#     _inherit = 'stock.picking'
#     verif = fields.Integer(string='Verificado:')
    
#     def verific_none(self):
#         print(self.env['account.invoice'].browse(self.name))
#         if self.env['account.invoice'].browse(self.name) is None:
#             self.verif = 0
#         else:
#             self.verif = 1
