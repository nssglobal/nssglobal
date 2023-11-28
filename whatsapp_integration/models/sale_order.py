# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import base64


class InheritSO(models.Model):
    _inherit = 'sale.order'


    is_whatsapp = fields.Boolean(compute="_show_hide_whatsapp")
    attachment_ids = fields.Many2many(
        'ir.attachment', )

    def create_attachment(self,):
        # pdf = self.env['ir.actions.report'].sudo()._render_qweb_pdf('sale.action_report_saleorder', [self.id])[0]
        pdf = self.env.ref('sale.action_report_saleorder').sudo()._render_qweb_pdf([self.id])[0]

        attachment = self.env['ir.attachment'].create({
            'name': 'Sale Order ' + self.name,
            'type': 'binary',
            'datas': base64.b64encode(pdf),
            'res_model': 'crm.lead',
            # 'res_id': self.id
        })
        self.attachment_ids = attachment.ids

    def _show_hide_whatsapp(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        is_so_whatsapp = icpsudo.get_param('whatsapp_integration.is_so_whatsapp')
        for i in self:
            i.is_whatsapp = True if is_so_whatsapp == 'True' else False

    def action_so_send_whatsapp(self):
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        icpsudo = self.env['ir.config_parameter'].sudo()
        is_so_whatsapp = icpsudo.get_param('whatsapp_integration.is_so_whatsapp')
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
            'from_whatsapp_button': True,
            'default_is_whatsapp': True if is_so_whatsapp == 'True' else False
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_confirm(self):
        rec = super().action_confirm()
        self.create_attachment()
        self.whatsapp_message_post()
        return rec


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
            odooPayload['name'] = self.partner_id[0].name
            odooPayload['phone_number'] = self.partner_id[0].phone
            odooSO = self
            odooPayload['so_name'] = odooSO.name
            odooPayload['myfatoorah_link'] = odooSO.myfatoorah_link
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
        model = self._name
        payload = None
        if model == 'sale.order':
            payload = self.get_so_payload()

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
                "name": "fatoorahtemplate",
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
                                "text": str(data['myfatoorah_link'])
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

