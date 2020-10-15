# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning
import logging, datetime
_logger = logging.getLogger(__name__)


class Bail(models.Model):
    _name = 'psdc_project.bail'
    _rec_name = 'number'
    number = fields.Char(
        string='N de Fianza',
        required=True)
    issue_date = fields.Date(
        string='Fecha de Emisión',
        required=True)
    expired_at = fields.Date(
        string='Fecha de Fencimiento',
        required=True)
    insurer_id = fields.Many2one(
        'res.partner',
        string='Aseguradora',
        required=True,
        domain=[('is_insurer', '=', 'True')])
    endorsement_ids = fields.One2many(
        'psdc_project.endorsement',
        'bail_id',
        string='Endosos')
    project_id = fields.Many2one(
        'project.project',
        string='Proyecto')
    bail_file = fields.Binary(
        string='Archivo')
    file_name = fields.Char(
        string="File Name")

    def _validate_current_date(self, date, limit=datetime.datetime.now().date(), message='fecha actual'):
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        if date < limit:
            raise ValidationError("La fecha ingresada es inválida, no puede ser menor a la {0}".format(message))

    @api.onchange('expired_at')
    @api.depends('issue_date')
    def _onchange_end_on(self):
        if self.expired_at:
            date_obj = datetime.datetime.strptime(self.issue_date, '%Y-%m-%d').date()
            self._validate_current_date(date=self.expired_at, limit=date_obj, message='fecha de emisión')

    @api.model
    def create(self, vals):
        """Override the default create method"""
        start_on = vals.get('issue_date', False)
        end_on = vals.get('expired_at', False)
        if start_on and end_on:
            date_obj = datetime.datetime.strptime(start_on, '%Y-%m-%d').date()
            self._validate_current_date(date=end_on, limit=date_obj, message='fecha inicial')
        bail = super(Bail, self).create(vals)
        return bail
