# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)


class PolicyType(models.Model):
    _name = 'psdc_project.policy_type'
    _rec_name = 'name'
    name = fields.Char(
        string='Descripción',
        required=True)


class Policy(models.Model):
    _name = 'psdc_project.policy'
    _rec_name = 'number'
    number = fields.Char(
        string='N de Póliza',
        required=True)
    policy_type_id = fields.Many2one(
        'psdc_project.policy_type',
        string='Tipo de Póliza',
        required=True)
    project_id = fields.Many2one(
        'project.project',
        string='Proyecto')
    issue_date = fields.Date(
        string='Fecha de Emisión',
        required=True)
    expired_at = fields.Date(
        string='Fecha de Vencimiento',
        required=True)
    insurer_id = fields.Many2one(
        'res.partner',
        string='Aseguradora',
        required=True,
        domain=[('is_insurer', '=', 'True')])
    is_renovation = fields.Boolean(
        string='Es renovación',
        required=False,
        default=False)
    policy_file = fields.Binary(
        string='Archivo')
    file_name = fields.Char(
        string="File Name")
    endorsement_ids = fields.One2many(
        'psdc_project.endorsement',
        'bail_id',
        string='Endosos')
