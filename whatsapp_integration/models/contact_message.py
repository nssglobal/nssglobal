# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import base64


class ContactWhatsappMessage(models.TransientModel):
    _name = 'contact.whatsapp.message'

    message = fields.Text()

    def action_send_message(self):
        self.whatsapp_message_post()
        return {'type': 'ir.actions.act_window_close'}

    def whatsapp_message_post(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        api_key = icpsudo.get_param('whatsapp_integration.api_key')
        url = "https://waba.360dialog.io/v1/messages"

        payload = self.get_payload()

        headers = {
            'D360-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 201:
            return True
        else:
            raise UserError(response.text)

    def get_payload(self):
        model = self.env.context['active_model']
        payload = {}
        odooPartner = self.env[model].browse(self.env.context['active_id']).exists()
        payload = json.dumps({
            "preview_url": False,
            "recipient_type": "individual",
            "to": odooPartner.phone,
            "type": "text",
            "text": {
                "body": self.message
            }
        })
        return payload

