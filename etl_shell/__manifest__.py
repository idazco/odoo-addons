# -*- coding: utf-8 -*-
{
    'name': "Odoo ETL Shell",

    'application': False,

    'summary': """
        A rudimentary framework that serves as a basis for creating complex Odoo ETL modules""",

    'description': """
        A rudimentary framework that serves as a basis for creating complex Odoo ETL modules
    """,

    'author': "community",
    'website': "https://github.com/idazco/odoo_etl_shell",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Utilities',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'decimal_precision', 'analytic'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/data_mapping.xml',
        'views/res_config.xml',
    ],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [
    ],
    'post_init_hook': 'database_alterations',
}