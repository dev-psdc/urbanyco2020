# -*- coding: utf-8 -*-
{
    'name': "Nombre para cheque",

    'summary': """
        Crear una linea de texto""",

    'description': """
        Creacion de linea de texto para asignarle nombre al cheque
    """,

    'author': "PSDC Inc",
    'website': "http://www.psdc.com.pa",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Payments',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_views.xml'
        #'views/stock_picking_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}