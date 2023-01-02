# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import base64


class InheritRP(models.Model):
    _inherit = 'res.partner'

    def _show_hide_whatsapp(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        is_contacts_whatsapp = icpsudo.get_param('whatsapp_integration.is_contacts_whatsapp')
        return True if is_contacts_whatsapp == 'True' else False

    def _show_hide_whatsapp_compute(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        is_contacts_whatsapp = icpsudo.get_param('whatsapp_integration.is_contacts_whatsapp')
        self.is_whatsapp = True if is_contacts_whatsapp == 'True' else False

    is_whatsapp = fields.Boolean(compute="_show_hide_whatsapp_compute", default=_show_hide_whatsapp)


