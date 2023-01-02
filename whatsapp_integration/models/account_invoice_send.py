# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import base64


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    is_whatsapp = fields.Boolean()

    def action_send_message(self):
        self.whatsapp_message_post()
        return {'type': 'ir.actions.act_window_close'}

    def whatsapp_message_post(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        api_key = icpsudo.get_param('whatsapp_integration.api_key')
        url = "https://waba.360dialog.io/v1/messages"

        data = self.get_message_data()

        payload = json.dumps({
            "to": data['phone_number'],
            "type": "template",
            "template": {
                "namespace": "8b7c4f11_04e9_48c3_bf46_b7aea40f910f",
                "language": {
                    "policy": "deterministic",
                    "code": "en"
                },
                "name": "invoice_sending_template",
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
                                "text": data['invoice_name']
                            },
                            {
                                "type": "text",
                                "text": data['symbol'] + " " + str(data['invoice_amount'])
                            },
                            {
                                "type": "text",
                                "text": str(data['company_name'])
                            },
                            {
                                "type": "text",
                                "text": str(data['invoice_name'])
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
                                    "filename": data['invoice_name'] + '.pdf'
                                }
                            }
                        ]
                    }
                ]
            }
        })
        headers = {
            'D360-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 201:
            return True
        else:
            raise UserError(response.text)

    def get_message_data(self):
        odooPayload = {}
        odooPayload['media'] = self.upload_media()
        odooPayload['name'] = self.partner_ids[0].name
        odooPayload['phone_number'] = self.partner_ids[0].phone
        odooMove = self.env['account.move'].browse(self.env.context['active_id']).exists()
        odooPayload['invoice_name'] = odooMove.name
        odooPayload['invoice_amount'] = odooMove.amount_total
        odooPayload['company_name'] = odooMove.company_id.name
        odooPayload['symbol'] = odooMove.company_id.currency_id.symbol

        return odooPayload

    def upload_media(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        api_key = icpsudo.get_param('whatsapp_integration.api_key')
        url = "https://waba.360dialog.io/v1/media/"

        media = []
        for attachment in self.attachment_ids:
            payload = base64.b64decode(attachment.datas)
            headers = {
                'D360-API-KEY': api_key,
                'Content-Type': attachment.mimetype
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 201:
                media_id = json.loads(response.text)['media'][0]['id']
                media.append(media_id)
        return media

