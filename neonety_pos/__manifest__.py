{
    'name': 'Neonety ajustes en punto de venta',
    'version': '2.6.1',
    'category': 'Point of Sale',
    'summary': 'Permite agregar los campos del RUC y los de Distribución geográfica de Panamá al CRUD de clientes del Punto de Venta',
    'description': """
        Permite agregar los campos del RUC y los de Distribución geográfica de Panamá al CRUD de clientes del Punto de Venta
        """,
    'depends': ['point_of_sale', 'neonety'],
    'data': [
        'views/neonety_pos_templates.xml',
        'views/neonety_pos_config_views.xml',
    ],
    'qweb': ['static/src/xml/neonety_pos.xml'],
    'installable': True,
    'author': "Neonety",
    'website': "http://www.neonety.com",
}