# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning
import logging, re
_logger = logging.getLogger(__name__)


TAG_RE = re.compile(r'<[^>]+>')


EMPTY_SEQUENCE = 'Borrador'

incount = 0

NOTE_STATES_LIST = [
    ('draft', 'Borrador'),
    ('validated','Confirmado'),
    ('print', 'Impreso'),
    ('sent', 'Enviado por correo electrónico'),
    ('canceled', 'Cancelado')
]


class Note(models.Model):
    _name = 'psdc_notes.note'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _rec_name = 'number'
    number = fields.Char(
        string='Código',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: EMPTY_SEQUENCE)
    state = fields.Selection(
        NOTE_STATES_LIST,
        default='draft',
        track_visibility='onchange')
    name = fields.Char(
        string='Nombre',
        required=True)
    date = fields.Date(
        string='Fecha de la Nota',
        required=True)
    client_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True)
    project_id = fields.Many2one(
        'project.project',
        string='Proyecto',
        required=False,
        default=None)
    body = fields.Text(
        string='Contenido',
        required=True)
    company = fields.Char(
        string="Compañia",
        required=False,
        default=lambda self: EMPTY_SEQUENCE
    )
    id_company = fields.Char(
        string='Codigo de Compañia',
        required=True,
        default=lambda self: self.env.user.company_id.id
    )
    crm_id = fields.Many2one(
        'crm.lead',
        string='Oportunidad',
        required=False,
        default=None)

    @api.onchange('client_id')
    def _onchange_client_id(self):
        res = {}
        if self.client_id:
            res['domain'] = {'project_id': [('partner_id', '=', self.client_id.id)]}
        return res

    @api.multi
    def action_validate(self):
        return self.write({'state': 'validated'})

    @api.multi
    def action_print(self):
        self.write({'state': 'print'})
        return self.env.ref('psdc_notes.action_report_note').report_action(self)

    @api.multi
    def action_send(self):
        self.ensure_one()
        template = self.env.ref('psdc_notes.note_email_template', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='psdc_notes.note',
            default_res_id=self.ids[0],
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_so_as_sent=True,
            custom_layout="psdc_notes.note_email_notification",
            force_email=True
            )
        self.write({'state': 'sent'})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'canceled'})

    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        id_com = self.env.user.company_id.id
        if (id_com == 3):
            vals['company'] = id_com
            vals['number'] = self.env['ir.sequence'].next_by_code('psdc_note_inco') or EMPTY_SEQUENCE
        else:
            vals['company'] = id_com
            vals['number'] = self.env['ir.sequence'].next_by_code('psdc_note') or EMPTY_SEQUENCE
        eo = TAG_RE.sub('', vals['body']) if vals['body'] else None
        eo = eo.replace('&nbsp;', '')
        if not eo:
            raise ValidationError("Debe agregar un contenido a la nota.")
        note = super(Note, self).create(vals)
        return note

    @api.multi
    def unlink(self):
        for note in self:
            if not note.state in ['draft', 'canceled']:
                raise UserError("Solo las notas en estado \"Borrador\" pueden ser borradas.")
        return super(Note, self).unlink()
