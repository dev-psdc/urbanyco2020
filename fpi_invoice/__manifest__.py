# -*- coding: utf-8 -*-
{
    'name': "Impresion de Facturas de Venta en impresora Fiscal",
    'summary': """Integración y uso de impresora fiscales en el módulo de contabilidad y facturación.""",
    'description': """Integración y uso de impresora fiscales en el módulo de contabilidad y facturación""",
    'author': "Neonety",
    'website': "http://www.neonety.com",
    'category': 'Administration',
    'version': '1.0.0',
    'depends': ['base', 'account', 'fpi'],
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',
        'views/fpi_invoice_views.xml',
        'views/fpi_account_journal.xml',
        'views/accounting_reports.xml',
    ],
}
