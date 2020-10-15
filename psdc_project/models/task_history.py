# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
from pytz import timezone
_logger = logging.getLogger(__name__)


class TaskHistory(models.Model):
    _name = 'psdc_project.task_history'
    date = fields.Date(string='Fecha', required=True, readonly=True)
    time = fields.Char(string='Hora', required=True, readonly=True)
    comments = fields.Text(string='Observaciones', readonly=True)
    latitude = fields.Float(string='Latitud', required=True)
    longitude = fields.Float(string='Longitud', required=True)
    state = fields.Selection([
        ('normal', 'Pendiente'),
        ('done', 'Listo'),
        ('blocked', 'Bloqueado')
        ], required=True, string='Estado', readonly=True)
    task_id = fields.Many2one(
        'project.task',
        string='Tarea / Actividad')
    task_history_image_ids = fields.One2many(
        'psdc_project.task_history_image',
        'task_history_id',
        string='Imagenes adjuntas')

    @api.model
    def create(self, vals):
        """
        by Franklin Sarmiento
        Override the default create() method
        12.2.2019
        """
        if vals['date'] and vals['time']:
            vals['time'] =  '{0:02.0f}:{1:02.0f}'.format(*divmod(vals['time'] * 60, 60))
        history = super(TaskHistory, self).create(vals)
        history.task_id.write({'kanban_state': history.state})
        return history


class TaskHistoryImage(models.Model):
    _name = 'psdc_project.task_history_image'
    image = fields.Binary(string='Imagen')
    task_history_id = fields.Many2one(
        'psdc_project.task_history',
        string='Historia')
    filename = fields.Char('psdc', readonly = True,store = False,compute ='legacy_img_filename')

    @api.one
    def legacy_img_filename(self):
        if len(self.task_history_id) > 0:
            self.filename = 'psdc_project_img.jpg'
        else:
            self.filename = 'psdc_project_img.jpg'
