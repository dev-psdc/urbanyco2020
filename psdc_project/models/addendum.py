# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning
import logging, datetime
_logger = logging.getLogger(__name__)


class AddendumDescription(models.Model):
    _name = 'psdc_project.addendum_description'
    _rec_name = 'name'
    name = fields.Char(
        string='Nombre',
        required=True)


class Addendum(models.Model):
    _name = 'psdc_project.addendum'
    _rec_name = 'number'
    number = fields.Char(
        string='N de Adenda',
        required=True)
    comments = fields.Text(
        string='Comentarios',
        required=False)
    start_at = fields.Date(
        string='Fecha Inicial',
        required=False)
    end_at = fields.Date(
        string='Fecha Final',
        required=False)
    addendum_date = fields.Date(
        string='Fecha por Adenda',
        required=False)
    project_id = fields.Many2one(
        'project.project',
        string='Proyecto')
    addendum_description_id = fields.Many2one(
        'psdc_project.addendum_description',
        string='Descripción',
        required=True)
    addendum_file = fields.Binary(
        string='Archivo')
    file_name = fields.Char(
        string="File Name")

    def _validate_current_date(self, date, limit=datetime.datetime.now().date(), message='fecha actual'):
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        if date < limit:
            raise ValidationError("La fecha ingresada es inválida, no puede ser menor a la {0}".format(message))

    @api.onchange('end_at')
    @api.depends('start_at')
    def _onchange_end_on(self):
        if self.end_at:
            date_obj = datetime.datetime.strptime(self.start_at, '%Y-%m-%d').date()
            self._validate_current_date(date=self.end_at, limit=date_obj, message='fecha inicial')

    @api.model
    def create(self, vals):
        """Override the default create method"""
        start_on = vals.get('start_at', False)
        end_on = vals.get('end_at', False)
        if start_on and end_on:
            date_obj = datetime.datetime.strptime(start_on, '%Y-%m-%d').date()
            self._validate_current_date(date=end_on, limit=date_obj, message='fecha inicial')
        addendum = super(Addendum, self).create(vals)
        return addendum
