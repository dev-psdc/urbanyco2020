# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError
import logging, qrcode, random, base64
from io import BytesIO
_logger = logging.getLogger(__name__)


class Project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    def _compute_qr_token(self):
        return random.randrange(1000000,9999999,2)

    def _get_plannings_count(self):
        for project in self:
            project.plannings_count = len(project.plannings_ids)

    resident_id = fields.Many2one(
        'res.partner',
        string='Residente del proyecto',
        domain=[('is_resident','=','True')])
    date_start = fields.Date(
        string='Fecha de Inicio',
    )
    date_end = fields.Date(
        string='Fecha Final',
    )
    no_contra = fields.Char(
        string='No. Contrato'
    )
    addendum_ids = fields.One2many(
        'psdc_project.addendum',
        'project_id',
        string='Adenda')
    policy_ids = fields.One2many(
        'psdc_project.policy',
        'project_id',
        string='Póliza')
    bail_ids = fields.One2many(
        'psdc_project.bail',
        'project_id',
        string='Fianza')
    qr_token = fields.Integer(
        string='Token para generar Código QR',
        default=_compute_qr_token)
    qr_code = fields.Binary(
        string='Código QR',
        required=False)
    qr_code_filename = fields.Char(
        string='Nombre del archivo del codigo QR',
        required=False)
    plannings_count = fields.Integer(
        string='Planificaciones del proyecto',
        compute='_get_plannings_count')
    plannings_ids = fields.One2many(
        'psdc_project.planning',
        'project_id',
        string='Fianza')
    inspector_name = fields.Char(
        string='Nombre del inspector del proyecto',
        required=False)

    @api.multi
    @api.depends('qr_token', 'name')
    def _qr_code_generator(self):
        """
        Adding the default QR code generator
        """
        for project in self:
            try:
                qr = qrcode.QRCode(
                    version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=20,border=4)
                qr.add_data(project.qr_token)
                qr.make(fit=True)
                img = qr.make_image()
                qr_buffer = BytesIO()
                img.save(qr_buffer, format='PNG')
                img_str=base64.b64encode(qr_buffer.getvalue())
                project.write({
                    'qr_code': img_str,
                    'qr_code_filename': '{0}_qrcode.png'.format(project.name)})
            except BaseException as e:
                _logger.error(e)
                raise UserError("Ah ocurrido un error tratando de generar el código QR al proyecto")

    @api.model
    def create(self, vals):
        """
        Override the default create method
        """
        project = super(Project, self).create(vals=vals)
        if not project.qr_code:
            project._qr_code_generator()
        return project


class Task(models.Model):
    _name = "project.task"
    _inherit = 'project.task'

    def _compute_qr_token(self):
        return random.randrange(1000000,9999999,2)

    task_history_ids = fields.One2many(
        'psdc_project.task_history',
        'task_id',
        string='Historial')
    subproject_id = fields.Many2one(
        'psdc_project.subproject',
        string='Subproyecto')
    progress = fields.Float(
        string='% Avance',
        default=0.00)
    qr_token = fields.Integer(
        string='Token para generar Código QR',
        default=_compute_qr_token)
    qr_code = fields.Binary(
        string='Código QR',
        required=False)
    task_histories_map = fields.Char(
        string='Map',
        required=False)

    @api.multi
    @api.depends('qr_token')
    def _qr_code_generator(self):
        """
        Adding the default QR code generator
        """
        for task in self:
            try:
                qr = qrcode.QRCode(
                    version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=20,border=4)
                qr.add_data(task.qr_token)
                qr.make(fit=True)
                img = qr.make_image()
                qr_buffer = BytesIO()
                img.save(qr_buffer, format='PNG')
                img_str=base64.b64encode(qr_buffer.getvalue())
                task.write({'qr_code': img_str})
            except BaseException as e:
                _logger.error(e)
                raise UserError("Ah ocurrido un error tratando de generar el código QR de la tarea")

    @api.model
    def create(self, vals):
        """
        Override the default create method
        """
        task = super(Task, self).create(vals=vals)
        if not task.qr_code:
            task._qr_code_generator()
        return task
