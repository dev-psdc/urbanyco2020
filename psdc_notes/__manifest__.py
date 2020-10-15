# -*- coding: utf-8 -*-
{
    "name": "PSDC - Notas",
    "summary": "Módulo para agregar Notas o documentos a proyectos",
    "description": """
        Módulo que permite agregar notas o documentos a proyectos, estos documentos también pueden ser impresos o enviados por correo.
    """,
    "author": "PSDC Innova",
    "website": "https://psdc.com.pa/",
    "category": "Projects",
    "version": "1.1.0",
    "depends": ['base', 'contacts', 'mail'],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/psdc_note_sequence.xml',
        'views/psdc_note_views.xml',
        'report/psdc_notes_report.xml',
        'report/psdc_notes_report_templates.xml',
        'data/mail_template_data.xml',
    ],
    'qweb': [],
    "demo": [],
    'installable': True,
    'application': True
}
