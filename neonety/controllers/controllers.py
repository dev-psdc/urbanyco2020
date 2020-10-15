# -*- coding: utf-8 -*-
from odoo import http

# class Neoneti-micellaneous(http.Controller):
#     @http.route('/neoneti-micellaneous/neoneti-micellaneous/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/neoneti-micellaneous/neoneti-micellaneous/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('neoneti-micellaneous.listing', {
#             'root': '/neoneti-micellaneous/neoneti-micellaneous',
#             'objects': http.request.env['neoneti-micellaneous.neoneti-micellaneous'].search([]),
#         })

#     @http.route('/neoneti-micellaneous/neoneti-micellaneous/objects/<model("neoneti-micellaneous.neoneti-micellaneous"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('neoneti-micellaneous.object', {
#             'object': obj
#         })