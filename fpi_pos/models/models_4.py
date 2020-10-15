# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.exceptions import UserError, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)


class FpiRecords(models.Model):
    _name = 'fpi.records'
    _inherit = 'fpi.records'
    _rec_name = 'number'
    order_id = fields.Many2one(
        'pos.order',
        string='Orden de pedido',
        default=None,
        required=False)
    number = fields.Integer(
        related='order_id.sequence_number')