# -*- coding: utf-8 -*-
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import logging
_logger = logging.getLogger(__name__)

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    name_mod = fields.Char(
        'Moderador'
    )
    after_sec = fields.Date(
        string="Sesión Anterior"
    )
    objects = fields.Text(
        string="Objetivos"
    )
    theme_t = fields.Text(
        string="Temas a Tratar"
    )
    notes_m = fields.Text(
        string="Notas"
    )
    theme_pen = fields.Text(
        string="Temas Pendientes"
    )
    prox_reu = fields.Datetime(
        string="Próxima Reunión"
    )
    project_id = fields.Many2one(
        'project.project',
        string='Proyecto',
        required=False,
        default=None
    )

    @api.multi
    def get_report(self):
        """Esta funcion es llamada por 'Generar Reporte'.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'name_mod': self.name_mod,
                'after_sec': self.after_sec,
                'objects': self.objects,
                'theme_t': self.theme_t,
                'notes_m': self.notes_m,
                'theme_pen': self.theme_pen,
                'prox_reu': self.prox_reu,
                'project_id': self.project_id.name,
                'location': self.location,
                'display_start': self.display_start,
                'display_time': self.display_time,
                'duration': self.duration,
                'partner_ids': self.partner_ids,
            },
        }
        return self.env.ref('minuta.recap_report').report_action(self, data=data)

class ReportMinuta(models.Model):
    _name = 'report.minuta.minuta_recap_report_view'

    partners = fields.Many2many(
        'calendar.attendee',
        'display_name',
        'email',
        'state'
    )

    def get_initials(self, fullname):
        xs = (fullname)
        name_list = xs.split()

        initials = ""

        for name in name_list:  # go through each name
            initials += name[0].upper()  # append the initial

        return initials

    @api.model
    def get_report_values(self, docids, data=None):
        name_mod = data['form']['name_mod']
        after_sec = data['form']['after_sec']
        objects = data['form']['objects']
        theme_t = data['form']['theme_t']
        notes_m = data['form']['notes_m']
        theme_pen = data['form']['theme_pen']
        prox_reu = data['form']['prox_reu']
        project_id = data['form']['project_id']
        location = data['form']['location']
        display_start = data['form']['display_start']
        display_time = data['form']['display_time']
        duration = data['form']['duration']
        partner_ids = data['form']['partner_ids']

        docs = []
        i1 = partner_ids.find("(")
        i2 = partner_ids.find(")")
        i3 = partner_ids[1+i1:i2]
        p = i3.split(",")
        print("AQUIIIIII: "+str(p))
        for y in p:
            if (y != ""):
                cod = self.env['res.partner'].search([('id','=',y)]).name
                docs.append({
                    'name': self.env['res.partner'].search([('id','=',y)]).name,
                    'resident': self.env['res.partner'].search([('id','=',y)]).resident_role_id.name,
                    'email': self.env['res.partner'].search([('id','=',y)]).email,
                    'cod': self.get_initials(cod)
                })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'name_mod': name_mod,
            'after_sec': after_sec,
            'objects': objects,
            'theme_t': theme_t,
            'notes_m': notes_m,
            'theme_pen': theme_pen,
            'prox_reu': prox_reu,
            'project_id': project_id,
            'location': location,
            'display_start': display_start,
            'display_time': display_time,
            'duration': duration,
            'partner_ids': partner_ids,
            'docs': docs,
        }