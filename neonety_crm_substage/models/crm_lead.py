# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = 'crm.lead'
    crm_substage_id = fields.Many2one(
        'crm.substage',
        string='Sub Etapa',
        help='Seleccione una sub etapa asociada a la actividad que esta realizando'
    )

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        res = {}
        if self.stage_id:
            res['domain'] = {'crm_substage_id': [('crm_stage_id', '=', self.stage_id.id)]}
        return res
