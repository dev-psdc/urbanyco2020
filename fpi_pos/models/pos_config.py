# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'
    iface_fiscal_printer_button = fields.Boolean(
        string='Print on Fiscal Printer', help="This allows you to print a currently receipt on Fiscal printer.")
    iface_fiscal_printer_optional = fields.Boolean(
        default=False,
        string='Preguntar si desea imprimir en la impresora fiscal',
        help='Si habilita esta opcion, se le preguntará al usuario antes de validar la orden en el POS.')