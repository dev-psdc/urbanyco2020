from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sel_payment_form = fields.Selection([
        ('1','Efectivo'), 
        ('2', 'Visa'), 
        ('3','Master Card'), 
        ('4','Amex'),
        ('5','Clave'),
        ('6','Cheque'),
        ('7','Notas de Credito'), 
        ('8','Credito'),
        ('9','Abonos'), 
        ('10','Certificados de Regalo'), 
        ('11','Tranferencias')
    ])