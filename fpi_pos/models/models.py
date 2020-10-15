# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)


class ErrorMessages:
    PRINTER_NOT_ASSIGNED = "No se ha podido imprimir el documento ya que el usuario no tiene una impresora fiscal asignada."
    PRINTING_IN_PROGRESS = 'La factura se encuentra en proceso de impresión'
    PRINTING_COMPLETED = 'El documento ya ha sido impreso por la impresora fiscal asignada, el mismo no se puede volver a imprimir.'
    PRINTING_DENIED = 'La Nota de Crédito no se puede imprimir debido a que la factura de venta todavia no ha sido impresa por la impresora fiscal asignada.'
    CANCEL_PRINTING_NOT_ALLOWED = "No se puede cancelar la impresión mientras este en proceso."


class FpiDocument(models.Model):
    _name = 'fpi.document'
    _inherit = 'fpi.document'
    order_id = fields.Many2one(
        'pos.order',
        string='Orden de pedido',
        default=None,
        required=False)

    @api.multi
    def unlink(self):
        for document in self:
            if 'in_progress' in self.print_status:
                raise UserError(ErrorMessages.CANCEL_PRINTING_NOT_ALLOWED)
            else:
                if 'pos_order' in document.documents_type_printed:
                    if document.order_id:
                        order = self.env['pos.order'].browse(document.order_id.id)
                        if order:
                            order.write({
                                'fpi_document_id': None,
                                'fiscal_printer_allowed': False})
        return super(FpiDocument, self).unlink()