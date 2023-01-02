# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import base64


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    is_whatsapp = fields.Boolean()

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

    def get_message_data(self, model=None):
        odooPayload = {}

        if model == 'sale.order':
            odooPayload['media'] = self.upload_media()
            odooPayload['name'] = self.partner_ids[0].name
            odooPayload['phone_number'] = self.partner_ids[0].phone
            odooSO = self.env['sale.order'].browse(self.env.context['active_id']).exists()
            odooPayload['so_name'] = odooSO.name
            odooPayload['so_amount'] = odooSO.amount_total
        if model == 'purchase.order':
            odooPayload['media'] = self.upload_media()
            odooPayload['name'] = self.partner_ids[0].name
            odooPayload['phone_number'] = self.partner_ids[0].phone
            odooPO = self.env['purchase.order'].browse(self.env.context['active_id']).exists()
            odooPayload['po_name'] = odooPO.name
            odooPayload['po_amount'] = odooPO.amount_total
            odooPayload['company_name'] = odooPO.company_id.name
            odooPayload['receipt_date'] = str(odooPO.date_planned.date())
            odooPayload['symbol'] = odooPO.company_id.currency_id.symbol

        return odooPayload

    def upload_media(self):
        url = "https://waba.360dialog.io/v1/media/"

        media = []
        for attachment in self.attachment_ids:
            payload = base64.b64decode(attachment.datas)
            headers = {
                'D360-API-KEY': 'lEUZCuzYcOyDKSMZSBYs4UngAK',
                'Content-Type': attachment.mimetype
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 201:
                media_id = json.loads(response.text)['media'][0]['id']
                media.append(media_id)
        return media

    def get_payload(self):
        model = self.env.context['default_model']
        payload = None
        if model == 'sale.order':
            payload = self.get_so_payload()
        if model == 'purchase.order':
            payload = self.get_po_payload()

        return payload

    def get_so_payload(self):
        data = self.get_message_data(model='sale.order')

        payload = json.dumps({
            "to": data['phone_number'],
            "type": "template",
            "template": {
                "namespace": "8b7c4f11_04e9_48c3_bf46_b7aea40f910f",
                "language": {
                    "policy": "deterministic",
                    "code": "en"
                },
                "name": "sales_order_template",
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": data['name']
                            },
                            {
                                "type": "text",
                                "text": data['so_name']
                            },
                            {
                                "type": "text",
                                "text": str(data['so_amount'])
                            }
                        ]
                    },
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "document",
                                "document": {
                                    "id": data['media'][0],
                                    "filename": data['so_name'] + '.pdf'
                                }
                            }
                        ]
                    }
                ]
            }
        })
        return payload

    def get_po_payload(self):
        data = self.get_message_data(model='purchase.order')
        payload = json.dumps({
            "to": data['phone_number'],
            "type": "template",
            "template": {
                "namespace": "8b7c4f11_04e9_48c3_bf46_b7aea40f910f",
                "language": {
                    "policy": "deterministic",
                    "code": "en"
                },
                "name": "purchase_order_sendind_template",
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": data['name']
                            },
                            {
                                "type": "text",
                                "text": data['po_name']
                            },
                            {
                                "type": "text",
                                "text": data['symbol'] + " " +str(data['po_amount'])
                            },
                            {
                                "type": "text",
                                "text": str(data['company_name'])
                            },
                            {
                                "type": "text",
                                "text": data['receipt_date']
                            }
                        ]
                    },
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "document",
                                "document": {
                                    "id": data['media'][0],
                                    "filename": data['po_name'] + '.pdf'
                                }
                            }
                        ]
                    }
                ]
            }
        })
        return payload