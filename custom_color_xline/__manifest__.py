# -*- coding: utf-8 -*-
{
    'name': "custom_color_xline",

    'summary': """
        Cambio de color para los reportes""",

    'description': """
        Cambio de color para los reportes
    """,

    'author': "PSDC",
    'website': "http://www.psdc.com.pa",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'css':[
        'static/src/css/customxline.scss',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}