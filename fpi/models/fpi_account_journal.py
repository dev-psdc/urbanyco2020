from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sel_payment_form = fields.Selection([
        ('CSH1','Efectivo'), 
        ('BNK1', 'Cheque'), 
        ('TC-','Tarjeta de Credito'), 
        ('TD-','Tarjeta de Debito')
    ])