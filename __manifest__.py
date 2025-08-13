# -*- coding: utf-8 -*-
{
    'name': '4SureERP Base',
    'version': '1.0',
    'summary': 'Core module providing login, dashboard, and base framework for 4SureERP',
    'description': """
    4SureERP Base Module
    --------------------
    This module provides:
    - Login page with Crow Golfer mascot
    - Owner dashboard (dark/light toggle)
    - Placeholder chatbot
    - Base structure for expanding into modules
    """,
    'category': 'Base',
    'author': '4SureERP Development',
    'website': 'https://4sureerp.com',
    'depends': [],
    'data': [
        'views/templates/login.html',
        'views/templates/dashboard.html',
    ],
    'assets': {
        'web.assets_frontend': [
            '4sureERP_base/static/css/style.css',
            '4sureERP_base/static/css/dashboard.css',
            '4sureERP_base/static/js/dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
}
