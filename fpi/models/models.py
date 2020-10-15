# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)


PRINT_STATUS_TYPES = [
    ('pending', 'Por imprimir'),
    ('in_progress', 'Imprimiendo...'),
    ('completed', 'Factura impresa'),
    ('failed', 'Impresión fallida')
]


DOCUMENTS_TYPES_PRINTED = [
    ('account_move', 'Factura de Venta'),
    ('pos_order', 'Orden de pedido')
]


INVOICE_TYPES_PRINTED = [
    ('out_invoice', 'Factura por Venta'),
    ('out_refund', 'Nota de Crédito')
]

INVOICES_DOCUMENT_PREFIX = 1
ORDERS_DOCUMENT_PREFIX = 2

class ErrorMessages:
    PRINTER_NOT_ASSIGNED = "No se ha podido imprimir el documento ya que el usuario no tiene una impresora fiscal asignada."
    PRINTING_IN_PROGRESS = 'La factura se encuentra en proceso de impresión'
    PRINTING_COMPLETED = 'El documento ya ha sido impreso por la impresora fiscal asignada, el mismo no se puede volver a imprimir.'
    PRINTING_DENIED = 'La Nota de Crédito no se puede imprimir debido a que la factura de venta todavia no ha sido impresa por la impresora fiscal asignada.'
    CANCEL_PRINTING_NOT_ALLOWED = "No se puede cancelar la impresión mientras este en proceso."
    PRINTER_REMOVE_DENIED = "No se puede borrar esta impresora ya que tiene documentos de impresión realizados."


class FpiPrinter(models.Model):
    _name = 'fpi.printer'
    _rec_name = 'model'
    model = fields.Char(
        string='Modelo de impresora',
        size=255,
        required=True,
        translate=True)
    serial = fields.Char(
        string='Serial de impresora',
        size=255,
        required=True,
        translate=True)
    is_available = fields.Boolean(
        string='Impresora activa y disponible',
        required=False,
        default=True,
        translate=True)
    user_id = fields.Many2one(
        'res.users',
        string='Creado por')
    merge_invoices_orders = fields.Boolean(
        string='Mezclar Ordenes y Facturas en la misma instancia',
        required=False,
        default=False)
    employee_id = fields.Many2many(
        'res.users',
        string='Asignado a',
        required=True,
        translate=True)
    fpi_document_ids = fields.One2many(
        'fpi.document', 'printer_id', string='Documentos')

    def _check_printer_assigned_exists(self, vals, pk=0):
        """
        Check if the printer is already assigned to the user selected before to create / write
        """
        if 'employee_id.id' in vals:
            if pk > 0:
                counter = self.env['fpi.printer'].search_count(
                    [('employee_id.id', '=', vals['employee_id']), ('id', '!=', pk)])
            else:
                counter = self.env['fpi.printer'].search_count([('employee_id.id', '=', vals['employee_id'])])
            if counter > 0:
                raise ValidationError("El usuario seleccionado ya tiene una impresora asignada")


    @api.model_create_multi
    def create(self, vals):
        self._check_printer_assigned_exists(vals=vals)
        p = super(FpiPrinter, self).create(vals)
        p.user_id = self.write_uid.id
        return p

    
    def write(self, vals):
        p = super(FpiPrinter, self).write(vals)
        self._check_printer_assigned_exists(vals=vals, pk=self.id)
        return p

    
    def unlink(self):
        for printer in self:
            if len(printer.fpi_document_ids) > 0:
                raise UserError(ErrorMessages.PRINTER_REMOVE_DENIED)
        return super(FpiPrinter, self).unlink()


class FpiDocument(models.Model):
    _name = 'fpi.document'
    _rec_name = 'number'
    printer_id = fields.Many2one(
        'fpi.printer',
        string='Impresora',
        required=True)
    printer_user_id = fields.Many2one(
        'res.users',
        string='Impreso por',
        default=None)
    print_status = fields.Selection(
        PRINT_STATUS_TYPES,
        string='Estatus de la impresión',
        required=False,
        default='pending')
    filename_assigned = fields.Char(
        string='Nombre de impresión asignado',
        required=False,
        default=None,
        size=100)
    fiscal_invoice_number = fields.Char(
        string='Número de Factura Fiscal')
    documents_type_printed = fields.Selection(
        DOCUMENTS_TYPES_PRINTED,
        string='Tipo de documento impreso',
        required=False,
        default='account_move')
    partner_name = fields.Char(
        string='Nombre del Cliente',
        size=255,
        default=None,
        required=False)
    partner_ruc = fields.Char(
        string='RUC del Cliente',
        size=20,
        default=None,
        required=False)
    partner_street = fields.Char(
        string='Dirección del Cliente',
        size=255,
        default=None,
        required=False)
    partner_zip = fields.Char(
        string='Codigo postal en la Dirección del Cliente',
        size=255,
        default=None,
        required=False)
    partner_province = fields.Char(
        string='Provincia en la Dirección del Cliente',
        size=255,
        default=None,
        required=False)
    partner_district = fields.Char(
        string='Distrito en la Dirección del Cliente',
        size=255,
        default=None,
        required=False)
    partner_sector = fields.Char(
        string='Corregimiento en la dirección del Cliente',
        size=255,
        default=None,
        required=False)
    partner_country = fields.Char(
        string='Pais en la Dirección del Cliente',
        size=255,
        default=None,
        required=False)
    
    invoice_type = fields.Selection(
        INVOICE_TYPES_PRINTED,
        string='Tipo de documento',
        size=20,
        default='out_invoice',
        required=False)
    refund_type = fields.Char(
        string='Tipo de nota de crédito',
        size=20,
        default=None,
        required=False)
    refund_note = fields.Char(
        string='Descripción de la nota de crédito',
        size=255,
        default=None,
        required=False)
    parent_invoice_filename_assigned = fields.Char(
        string='Numero de Factura asignado a la factura origen de la nota de credito',
        size=20,
        default=None,
        required=False)
    parent_invoice_fiscal_printer_serial = fields.Char(
        string='serial de la impresora fiscal usada en la factura origen de la nota de credito',
        size=50,
        default=None,
        required=False)
    parent_invoice_fiscal_invoice_number = fields.Char(
        string='Numero de factura fiscal asignado a la factura origen de la nota de credito',
        required=False)
    refund_date = fields.Char(
        string='Fecha de la nota de crédito',
        size=50,
        default=None,
        required=False)
    refund_time = fields.Char(
        string='Hora de la nota de crédito',
        size=50,
        default=None,
        required=False)
    number = fields.Char(
        string='Documento Nro.',
        size=100,
        required=False)
    filename_serial = fields.Integer(
        string='Serial para el numero de facturación.',
        default=0,
        required=False)
    master_filename_assigned = fields.Char(
        string='Nombre asignado al archivo principal',
        default=0,
        required=False)
    lines_filename_assigned = fields.Char(
        string='Nombre asignado al archivo de movimientos',
        default=0,
        required=False)
    serial = fields.Char(
        related='printer_id.serial')
    document_printed_date = fields.Char(
        string = 'Fecha de impresion del documento')

    @api.model_create_multi
    def create(self, vals):
        document = super(FpiDocument, self).create(vals)
        master_filename_assigned = document.number
        sequence_serial = document.number
        filename_serial = int(sequence_serial[-4:])
        lines_filename_assigned = document.number    
        document.write({
            'filename_serial': filename_serial,
            'master_filename_assigned': master_filename_assigned,
            'lines_filename_assigned': lines_filename_assigned
            })
        return document

    
    def unlink(self):
        for document in self:
            if 'in_progress' in document.print_status:
                raise UserError(ErrorMessages.CANCEL_PRINTING_NOT_ALLOWED)
        return super(FpiDocument, self).unlink()