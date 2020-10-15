# -*- coding: utf-8 -*-
{
    "name": "PSDC - Ajustes para Proyectos y Contactos",
    "summary": "Ajustes al módulo de proyectos y contactos",
    "description": """
        PSDC - proyectos y contactos, contiene información para:
            - Definir contactos como residentes
            - Agregar residentes en los proyectos
            - Agregar adendas
            - Agregar fianzas
            - Agregar pólizas
            - Agregar Historias a Tareas
            - Añadir imagenes a Historias de Tareas
            - Campo residente al Proyecto
            - Campo sub proyecto a la Tarea
            - Mapa de información geográfica por posicionamiento al momento de crear historias
    """,
    "author": "PSDC Innova",
    "website": "https://psdc.com.pa/",
    "category": "Projects",
    "version": "1.4.5",
    "depends": ['base', 'contacts', 'project'],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_config_views.xml',
        'views/google_maps_templates.xml',
        'views/res_partner_views.xml',
        'views/planning_views.xml',
        'views/task_history_views.xml',
        'views/subproject_views.xml',
        'views/project_views.xml',
        'views/addendum_views.xml',
        'views/endorsement_views.xml',
        'views/bail_views.xml',
        'views/policy_views.xml',
        'data/addendum_descriptions.xml',
        'data/endorsement_reasons.xml',
        'data/policy_types.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    "demo": []
}
