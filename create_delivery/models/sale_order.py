# # -*- coding: utf-8 -*-
# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError, UserError
# from odoo.tools import float_compare
# from datetime import date, datetime, timedelta
# import logging
# _logger = logging.getLogger(__name__)

# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
    
#     @api.multi
#     def n_action_confirm(self):
#         super(SaleOrder, self)._action_confirm()

#     #call the function to create the shipment, buttom: id=run_action_launch_procurement
#     @api.multi
#     def run_action_launch_procurement(self):
#       for order in self:
#           order.order_line._action_launch_procurement_rule()

    