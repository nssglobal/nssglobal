# -*- coding: utf-8 -*-
{
    'name': "arga_transport",

    'summary': """
        App data import""",

    'description': """
       App data import
    """,

    'author': "EI",
    'website': "http://www.haksolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': 'v15 enterprise',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
         'security/ir.model.access.csv',
         'views/views.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
