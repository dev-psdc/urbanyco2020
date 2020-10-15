# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'
    iface_neonety_fields = fields.Boolean(
        string='Habilitar campos agregados en el Módulo de Neonety',
        help="Estos campos comprenden los campos de distribución geográfica de Panamá y el RUC.")
    iface_no_merge_products = fields.Boolean(
        string="No mezclar productos en el POS",
        help='Al seleccionar esta opción los productos no se mezclaran cuando se esten seleccionando en el punto de venta',
        default=False)
    iface_allow_default_partner = fields.Boolean(
        string='Permitir asignar un cliente por defecto',
        default=False)
    iface_default_partner_id = fields.Many2one(
        'res.partner',
        string='Seleccionar cliente por defecto',
        default=None,
        required=False)

    @api.onchange('iface_allow_default_partner')
    def _onchange_iface_allow_default_partner(self):
        if not self.iface_allow_default_partner:
            self.iface_default_partner_id = None