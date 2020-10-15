# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
from datetime import date
import logging
_logger = logging.getLogger(__name__)


class PlanningPendingReport(models.Model):
    _name = 'psdc_project.plannings_pending_report'
    _auto = False
    _order = 'id'

    id = fields.Integer(string='ID')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'psdc_project_plannings_pending_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW psdc_project_plannings_pending_report AS
            SELECT
                PPP.id AS id
            FROM
                psdc_project_planning PPP
            WHERE
                PPP.state LIKE 'pending'
                AND PPP.start_on = '{0}'
            ORDER BY
                PPP.id
                        """.format(date.today().strftime('%Y-%m-%d')))

    @api.multi
    def start_planning(self):
        """
        Change all pending planning to active state
        """
        for item in self.env['psdc_project.plannings_pending_report'].search([]):
            planning = self.env['psdc_project.planning'].browse(item.id) or False
            if planning:
                planning.write({'state': 'active'})


class PlanningActiveReport(models.Model):
    _name = 'psdc_project.plannings_active_report'
    _auto = False
    _order = 'id'

    id = fields.Integer(string='ID')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'psdc_project_plannings_active_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW psdc_project_plannings_active_report AS
            SELECT
                PPP.id AS id
            FROM
                psdc_project_planning PPP
            WHERE
                PPP.state LIKE 'active'
                AND PPP.end_on = '{0}'
            ORDER BY
                PPP.id
                        """.format(date.today().strftime('%Y-%m-%d')))

    @api.multi
    def complete_planning(self):
        """
        Change all active plannings to finished state
        """
        for item in self.env['psdc_project.plannings_active_report'].search([]):
            planning = self.env['psdc_project.planning'].browse(item.id) or False
            if planning:
                planning.write({'state': 'finished'})
