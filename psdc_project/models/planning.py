# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from odoo.exceptions import UserError, ValidationError
import logging, datetime
_logger = logging.getLogger(__name__)


class Planning(models.Model):
    _name = 'psdc_project.planning'
    _rec_name = 'id'

    @api.model
    def _get_tasks_ids(self):
        project_id = self.env.context.get('active_id', False)
        domain = []
        if project_id:
            domain.append(('project_id', '=', project_id))
            domain.append(('kanban_state', 'in', ['normal', 'blocked']))
        return domain

    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('active', 'Activo'),
        ('finished', 'Terminado')
        ], string="Estado", default='pending')
    start_on = fields.Date(
        string='Fecha Inicial',
        required=True)
    end_on = fields.Date(
        string='Fecha Final',
        required=True)
    responsible_id = fields.Many2one(
        'res.partner',
        string='Responsable',
        required=True)
    project_id = fields.Many2one(
        'project.project',
        string='Proyecto')
    task_ids = fields.Many2many(
        'project.task',
        string='Tareas',
        domain=_get_tasks_ids)

    @api.onchange('task_ids')
    def _onchange_task_ids(self):
        planning_id = self.env.context.get('planning_id', False)
        for task_id in self.task_ids:
            queryset = [('project_id.id', '=', self.project_id.id)]
            if planning_id:
                queryset.append(('id', '!=', planning_id))
                queryset.append(('state', 'in', ['active', 'pending']))
            queryset.append(('task_ids.id', '=', task_id.id))
            counter = self.env['psdc_project.planning'].search_count(queryset)
            if counter > 0:
                raise ValidationError("Esta tarea ya pertenece a una planificación")

    def _validate_current_date(self, date, limit=datetime.datetime.now().date(), message='fecha actual'):
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        if date < limit:
            raise ValidationError("La fecha ingresada es inválida, no puede ser menor a la {0}".format(message))

    @api.onchange('start_on')
    def _onchange_start_on(self):
        if self.start_on:
            self._validate_current_date(date=self.start_on)

    @api.onchange('end_on')
    @api.depends('start_on')
    def _onchange_end_on(self):
        if self.end_on:
            date_obj = datetime.datetime.strptime(self.start_on, '%Y-%m-%d').date()
            self._validate_current_date(date=self.end_on, limit=date_obj, message='fecha inicial')

    @api.model
    def create(self, vals):
        """Override the default create method"""
        start_on = vals.get('start_on', False)
        end_on = vals.get('end_on', False)
        if start_on and end_on:
            self._validate_current_date(date=start_on)
            date_obj = datetime.datetime.strptime(start_on, '%Y-%m-%d').date()
            self._validate_current_date(date=end_on, limit=date_obj, message='fecha inicial')
        planning = super(Planning, self).create(vals)
        planning.dates_range = 'desde el {0} al {1}'.format(planning.start_on, planning.end_on)
        return planning
