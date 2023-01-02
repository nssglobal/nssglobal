# -*- coding: utf-8 -*-
{
    'name': "Whatsapp Integration",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/account_move.xml',
        'views/purchase_order.xml',
        'views/contact_message.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/mail_compose_message.xml',
        'views/account_invoice_send.xml',
        'views/whatsapp_message.xml',
    ]
}
