# -*- coding: utf-8 -*-
# from odoo import http


# class WhatsappIntegration(http.Controller):
#     @http.route('/whatsapp_integration/whatsapp_integration/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/whatsapp_integration/whatsapp_integration/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('whatsapp_integration.listing', {
#             'root': '/whatsapp_integration/whatsapp_integration',
#             'objects': http.request.env['whatsapp_integration.whatsapp_integration'].search([]),
#         })

#     @http.route('/whatsapp_integration/whatsapp_integration/objects/<model("whatsapp_integration.whatsapp_integration"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('whatsapp_integration.object', {
#             'object': obj
#         })
