# -*- coding: utf-8 -*-
from odoo import http

# class CreateDelivery(http.Controller):
#     @http.route('/create_delivery/create_delivery/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/create_delivery/create_delivery/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('create_delivery.listing', {
#             'root': '/create_delivery/create_delivery',
#             'objects': http.request.env['create_delivery.create_delivery'].search([]),
#         })

#     @http.route('/create_delivery/create_delivery/objects/<model("create_delivery.create_delivery"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('create_delivery.object', {
#             'object': obj
#         })