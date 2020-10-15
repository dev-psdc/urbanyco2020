# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    is_resident = fields.Boolean(
        string='Residente',
        default=False)
    is_insurer = fields.Boolean(
        string='Aseguradora',
        default=False)
    identity_number = fields.Char(
        string='N de Idoneidad',
        null=True)
    resident_role_id = fields.Many2one(
        'psdc_project.resident_role',
        string='Puesto de Trabajo',
    )
