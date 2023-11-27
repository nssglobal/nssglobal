# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, sql_db, _, tools
from odoo.exceptions import UserError
import requests
import json
import html2text
import base64
import logging, os

_logger = logging.getLogger(__name__)


class WhatsappComposeMessage(models.TransientModel):
    _name = 'whatsapp.compose.message'
    _description = "Whatsapp Message"

    partner_ids = fields.Many2many('res.partner', string='Contacts')
    subject = fields.Char('Subject')
    message = fields.Html('Contents', default='', sanitize_style=True)
    model = fields.Char('Object')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'whatsapp_compose_message_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')
    template_id = fields.Many2one('mail.template', 'Use template', index=True)

    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        res_id = self._context.get('active_id') or 1
        values = self.onchange_template_id(self.template_id.id, self.model, res_id)['value']
        for fname, value in values.items():
            setattr(self, fname, value)

    def onchange_template_id(self, template_id, model, res_id):
        """ - mass_mailing: we cannot render, so return the template values
            - normal mode: return rendered values
            /!\ for x2many field, this onchange return command instead of ids
        """
        if template_id:
            values = self.generate_email_for_composer(template_id, [res_id])[res_id]
        else:
            default_values = self.with_context(default_model=model, default_res_id=res_id).default_get(
                ['model', 'res_id', 'partner_ids', 'message', 'attachment_ids'])
            values = dict((key, default_values[key]) for key in
                          ['subject', 'message', 'partner_ids', 'email_from', 'reply_to', 'attachment_ids',
                           'mail_server_id'] if key in default_values)
        # This onchange should return command instead of ids for x2many field.
        # ORM handle the assignation of command list on new onchange (api.v8),
        # this force the complete replacement of x2many field with
        # command and is compatible with onchange api.v7
        values = self._convert_to_write(values)
        return {'value': values}

    @api.model
    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        """ Call email_template.generate_email(), get fields relevant for
            whatsapp.compose.message, transform email_cc and email_to into partner_ids """
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]

        if fields is None:
            fields = ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to',
                      'attachment_ids', 'mail_server_id']
        returned_fields = fields + ['partner_ids', 'attachments']
        values = dict.fromkeys(res_ids, False)

        template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(
            template_id).generate_email(res_ids, fields=fields)
        for res_id in res_ids:
            res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if
                                 template_values[res_id].get(field))
            # res_id_values['body'] = res_id_values.pop('body_html', '')
            res_id_values['message'] = html2text.html2text(res_id_values.pop('body_html', ''))
            values[res_id] = res_id_values

        return multi_mode and values or values[res_ids[0]]

    @api.model
    def default_get(self, fields):
        result = super(WhatsappComposeMessage, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        active_id = context.get('active_id')
        partners = self.env['res.partner']
        if active_model and active_ids and active_model == 'sale.order':
            odooOrder = self.env[active_model].browse(active_ids)
            if odooOrder.partner_id:
                partners += odooOrder.partner_id
        records = self.env[active_model].browse(active_ids)
        attachments = self.env['ir.attachment']
        for record in records:
            res_name = record.name.replace('/', '_')
            attachments_lst = []
            template = None
            if active_model == 'sale.order':
                template = self.env.ref('sale.email_template_edi_sale')
            if not template.report_template:
                break
            report = template.report_template
            if not report:
                continue
            report_service = report.report_name

            if report.report_type not in ['qweb-html', 'qweb-pdf']:
                raise UserError(_('Unsupported report type %s found.') % report.report_type)
            res, format = report._render_qweb_pdf([record.id])
            res = base64.b64encode(res)
            if not res_name:
                res_name = 'report.' + report_service
            ext = "." + format
            if not res_name.endswith(ext):
                res_name += ext
            attachments_lst.append((res_name, res))
            for attachment in attachments_lst:
                attachment_data = {
                    'name': attachment[0],
                    'store_fname': attachment[0],
                    'datas': attachment[1],
                    'type': 'binary',
                    'res_model': active_model,
                    'res_id': active_id,
                }
                attachments += self.env['ir.attachment'].create(attachment_data)
        template_id = int(self.env['ir.config_parameter'].sudo().get_param('sale.default_confirmation_template'))
        template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
        result['template_id'] = template_id
        result['model'] = active_model
        result['attachment_ids'] = [[6, 0, attachments.ids]] if attachments else []
        result['partner_ids'] = [[6, 0, partners.ids]] if partners else []
        return result

    def whatsapp_message_post(self):
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
                "name": "sales_order_sending_template",
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
        headers = {
            'D360-API-KEY': 'lEUZCuzYcOyDKSMZSBYs4UngAK',
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
        odooSO = self.env['sale.order'].browse(self.env.context['active_id']).exists()
        odooPayload['so_name'] = odooSO.name
        odooPayload['so_amount'] = odooSO.amount_total

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
