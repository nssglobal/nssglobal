# -*- coding: utf-8 -*-
# from odoo import http


# class HubspotConnector(http.Controller):
#     @http.route('/hubspot_connector/hubspot_connector', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hubspot_connector/hubspot_connector/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hubspot_connector.listing', {
#             'root': '/hubspot_connector/hubspot_connector',
#             'objects': http.request.env['hubspot_connector.hubspot_connector'].search([]),
#         })

#     @http.route('/hubspot_connector/hubspot_connector/objects/<model("hubspot_connector.hubspot_connector"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hubspot_connector.object', {
#             'object': obj
#         })
