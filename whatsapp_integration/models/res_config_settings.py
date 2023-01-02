from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError, UserError
import json
import requests
import time
from datetime import datetime, timedelta


class Integration(models.TransientModel):
    _inherit = 'res.config.settings'

    api_key = fields.Char('API Key', help='')
    is_so_whatsapp = fields.Boolean('Send SO io Whatsapp', help='')
    is_po_whatsapp = fields.Boolean('Send PO io Whatsapp', help='')
    is_invoice_whatsapp = fields.Boolean('Send Invoice io Whatsapp', help='')
    is_contacts_whatsapp = fields.Boolean('Send Whatsapp to Contacts', help='')

    def set_values(self):
        res = super(Integration, self).set_values()
        self.env['ir.config_parameter'].set_param('whatsapp_integration.api_key', self.api_key)
        self.env['ir.config_parameter'].set_param('whatsapp_integration.is_so_whatsapp', self.is_so_whatsapp)
        self.env['ir.config_parameter'].set_param('whatsapp_integration.is_po_whatsapp', self.is_po_whatsapp)
        self.env['ir.config_parameter'].set_param('whatsapp_integration.is_invoice_whatsapp', self.is_invoice_whatsapp)
        self.env['ir.config_parameter'].set_param('whatsapp_integration.is_contacts_whatsapp', self.is_contacts_whatsapp)
        return res

    @api.model
    def get_values(self):
        res = super(Integration, self).get_values()
        icpsudo = self.env['ir.config_parameter'].sudo()
        api_key = icpsudo.get_param('whatsapp_integration.api_key')
        is_so_whatsapp = icpsudo.get_param('whatsapp_integration.is_so_whatsapp')
        is_po_whatsapp = icpsudo.get_param('whatsapp_integration.is_po_whatsapp')
        is_invoice_whatsapp = icpsudo.get_param('whatsapp_integration.is_invoice_whatsapp')
        is_contacts_whatsapp = icpsudo.get_param('whatsapp_integration.is_contacts_whatsapp')

        res.update(
            api_key=api_key,
            is_so_whatsapp=True if is_so_whatsapp == 'True' else False,
            is_po_whatsapp=True if is_po_whatsapp == 'True' else False,
            is_invoice_whatsapp=True if is_invoice_whatsapp == 'True' else False,
            is_contacts_whatsapp=True if is_contacts_whatsapp == 'True' else False,
        )
        return res
