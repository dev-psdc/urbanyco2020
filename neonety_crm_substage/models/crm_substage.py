# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class Substage(models.Model):
    _name = 'crm.substage'
    _description = "Subetapas de una Etapa"
    _order = "crm_stage_id, sequence, name"
    name = fields.Char(
        string='Descripción',
    )
    sequence = fields.Integer(
        string='Secuencia',
        help='Valor utilizado para ordenar las subetapas, el registro con menor aparecerá primero',
        default=0
    )
    crm_stage_id = fields.Many2one(
        'crm.stage',
        string='Etapa principal'
    )

    @api.model
    def create(self, vals):
        if 'name' in vals and 'crm_stage_id' in vals:
            substages_found = self.env['crm.substage'].search_count([('name', 'ilike', vals['name']), ('crm_stage_id', '=', vals['crm_stage_id'])])
            if substages_found > 0:
                raise ValidationError("Ya existe una sub etapa con el nombre '{0}' asociada a la misma etapa.".format(vals['name']))
        return super(Substage, self).create(vals)


