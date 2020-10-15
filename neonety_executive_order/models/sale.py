# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
import logging
import re
_logger = logging.getLogger(__name__)


TAG_RE = re.compile(r'<[^>]+>')


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    executive_order = fields.Text(
        string='Presupuesto ejecutivo',
        default=None
    )

    @api.multi
    def print_executive_order(self):
        eo = TAG_RE.sub('', self.executive_order) if self.executive_order else None
        eo = eo.replace('&nbsp;', '')
        if not eo:
            raise ValidationError("Todavía no se ha llenado la información asociada al presupuesto ejecutivo.")
        return self.env.ref('neonety_executive_order.action_report_saleorder').report_action(self)
