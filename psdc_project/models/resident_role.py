# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
import logging
_logger = logging.getLogger(__name__)


class ResidentRole(models.Model):
    _name = 'psdc_project.resident_role'
    _rec_name = 'name'
    name = fields.Char(
        string='Descripción',
        required=True)
