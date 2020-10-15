# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Punto de Venta integrado con Impresora Fiscal ( Modulo FPI ) ',
    'version': '4.0.0',
    'category': 'Point of Sale',
    'summary': 'Permite imprimir las facturas relacionadas a ordenes en una impresora fiscal ( Modulo FPI )',
    'description': """
        Integra el modulo de impresión de facturas en Impresora Fiscal ( Modulo FPI )
        con el Modulo de Punto de Venta ( POS )\n
        NOTA: Para poder enviar una impresión a la Impresora fiscal ( FPI ), se debe generar al factura a la Orden de Compra
        del módulo de Punto de Ventas ( POS ).
        """,
    'depends': ['point_of_sale', 'pos_custom_discounts', 'fpi'],
    'data': [
        'security/security_data.xml',
        'security/ir.model.access.csv',
        'views/fpi_pos_views.xml',
        'views/fpi_pos_config_views.xml',
        'views/fpi_pos_templates.xml'
    ],
    'installable': True,
    'author': "Neonety",
    'website': "http://www.neonety.com",
}