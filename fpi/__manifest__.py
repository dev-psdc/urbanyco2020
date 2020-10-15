# -*- coding: utf-8 -*-
{
    'name': "Impresoras Fiscales(integración)",
    'summary': "Integración y uso de impresora fiscales.",
    'description': "Integración y uso de impresora fiscales",
    'author': "PSDC Inc. & Eric Dominguez",
    'website': "http://www.psdc.com.pa",
    'category': 'Administration',
    'version': '1.0',
    'depends': ['base', 'neonety', 'account_invoicing', 'account_accountant'],
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',
        'views/fpi_invoice_views.xml',
        'views/fpi_views.xml',
        'views/fpi_account_journal.xml',
        'views/accounting_reports.xml',
    ],
}
