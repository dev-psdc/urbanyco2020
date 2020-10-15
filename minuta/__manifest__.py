# -*- coding: utf-8 -*-
{
    'name': "Minuta",

    'summary': """
        Crear una vista para hacer minutas de reuniones""",

    'description': """
        Crear una vista para hacer minutas de reuniones
    """,

    'author': "PSDC Inc",
    'website': "http://www.psdc.com.pa",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Calendar',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','calendar','project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/minuta_views.xml',
        'views/report_minuta.xml',       
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}