# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import base64


class InheritSO(models.Model):
    _inherit = 'sale.order'

    is_whatsapp = fields.Boolean(compute="_show_hide_whatsapp")

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
