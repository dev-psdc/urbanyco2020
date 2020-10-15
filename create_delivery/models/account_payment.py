# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    check_name = fields.Char(related='partner_id.name', 
        store=False, 
        string="Cheque a nombre de:", 
        readonly=False)
    
    @api.one
    @api.depends('check_name')
    def _change_name(self):
        self.name_c = self.check_name

    name_c = fields.Char(string="Cheque a nombre de:", 
        readonly=False, 
        store=True,
        compute=_change_name)