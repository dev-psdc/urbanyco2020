# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class Subproject(models.Model):
    """
    Sub project class
    """
    _name = 'psdc_project.subproject'
    _rec_name = 'name'

    name = fields.Char(
        string='Descripción', required=True)
