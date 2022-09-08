# -*- coding: utf-8 -*-
# from odoo import http


# class ArgaTransport(http.Controller):
#     @http.route('/arga_transport/arga_transport', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/arga_transport/arga_transport/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('arga_transport.listing', {
#             'root': '/arga_transport/arga_transport',
#             'objects': http.request.env['arga_transport.arga_transport'].search([]),
#         })

#     @http.route('/arga_transport/arga_transport/objects/<model("arga_transport.arga_transport"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('arga_transport.object', {
#             'object': obj
#         })
