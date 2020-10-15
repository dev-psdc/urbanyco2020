# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)


PRINT_STATUS_TYPES = [
    ('incomplete', 'No ha sido impreso'),
    ('pending', 'Por imprimir'),
    ('in_progress', 'Imprimiendo...'),
    ('completed', 'Factura impresa'),
    ('failed', 'Impresión fallida')
]


class ErrorMessages:
    PRINTER_NOT_ASSIGNED = "No se ha podido imprimir el documento ya que el usuario no tiene una impresora fiscal asignada."
    PRINTING_IN_PROGRESS = 'La factura se encuentra en proceso de impresión'
    PRINTING_COMPLETED = 'El documento ya ha sido impreso por la impresora fiscal asignada, el mismo no se puede volver a imprimir.'
    PRINTING_DENIED = 'La Nota de Crédito no se puede imprimir debido a que la factura de venta todavia no ha sido impresa por la impresora fiscal asignada.'
    CANCEL_PRINTING_NOT_ALLOWED = "No se puede cancelar la impresión mientras este en proceso."
    PRINTING_NOT_ALLOWED = "No se puede imprimir esta factura en la impresora fiscal, su monto total es menor o igual a cero"


class FpiDocument(models.Model):
    _name = 'fpi.document'
    _inherit = 'fpi.document'
    invoice_id = fields.Many2one(
        'account.move',
        string='Factura de Venta',
        default=None,
        required=False)

    #campos para el nuevo proveedor 
    doc_type = fields.Char(
        string='Tipo de Documento',
        size = 1
    )
    doc_number = fields.Char(
        string = 'Numero del documento',
    )

    ## INICIO DE SECCION DE DATOS DEL CLIENTE ##
    customer_name = fields.Char(
        string = 'Nombre del cliente',
        size = 40
    )
    customer_ruc = fields.Char(
        string = 'Identificacion unica del cliente',
        size = 22
    )
    customer_address = fields.Char(
        string = 'Direccion del cliente',
        size = 50
    )
    ## FIN DE LA SECCION DE LOS DATOS DEL CLIENTE ##

    invoice_number = fields.Char(
        string = 'Obligatorio para notas de credito y de debito',
        size = 22
    )

    ## INICIO DE SECCION DE DESCUENTOS ##
    disc_perc = fields.Char(
        string = 'Descuentos sobre subtotal en porcentaje, debe incluir el signo de porcentaje (%).',
        size = 4
    )
    disc_amt = fields.Float(
        string = 'Cantidad descontada sobre el subtotal.'
    )
    ## FIN DE SECCION DE DESCUENTOS ##

    ## SECCION DE TRAILER (PIE DE PAGINA) ##
    trailer_id = fields.Integer(
        string = 'Identificador de linea'
    )
    trailer_value = fields.Char(
        string = 'Texto informativo de la linea',
        size = 50
    )

    
    def unlink(self):
        for document in self:
            if 'in_progress' in document.print_status:
                raise UserError(ErrorMessages.CANCEL_PRINTING_NOT_ALLOWED)
            else:
                if 'account_move' in document.documents_type_printed:
                    if document.invoice_id:
                        invoice = self.env['account.move'].browse(document.invoice_id.id)
                        if invoice:
                            invoice.write({'fpi_document_id': None})
        return super(FpiDocument, self).unlink()


class FpiInvoice(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'
    fpi_document_id = fields.Many2one(
        'fpi.document',
        string='Impresión asociada',
        default=None,
        required=False)
    print_status = fields.Selection(
        PRINT_STATUS_TYPES,
        string='Estatus de la impresión',
        required=False,
        default='incomplete')
    printer_user_id = fields.Many2one(
        'res.users',
        string='Impreso por',
        default=None)
    print_filename_assigned = fields.Char(
        string='Nombre de impresión asignado',
        required=False,
        default=None,
        size=100)
    fiscal_printer_invoice_id = fields.Integer(
        string='Número de Factura Fiscal',
        default=0)
    document_print_status = fields.Selection(
        related='fpi_document_id.print_status')
    document_fiscal_invoice_number = fields.Char(
        related='fpi_document_id.fiscal_invoice_number')
    document_fiscal_printed_date = fields.Char(
        related='fpi_document_id.document_printed_date')

    @api.model_create_multi
    def create(self, vals):
        obj = super(FpiInvoice, self).create(vals)
        obj.fpi_document_id = None
        obj.printer_user_id = None
        return obj

    #@api.one
    def send_fiscal_printer_action(self):
        if self.amount_total <= 0 and 'out_invoice' in self.type:
            raise UserError(ErrorMessages.PRINTING_NOT_ALLOWED)
        else:
                printer = self.env['fpi.printer'].search([('employee_id.id', '=', self.write_uid.id)])
                if not printer:
                    raise UserError(ErrorMessages.PRINTER_NOT_ASSIGNED)
                else:
                    invoice = self
                    invoice.write({'printer_user_id': self.write_uid.id})
                    parent_invoice_filename_assigned = None
                    parent_invoice_fiscal_printer_serial = None
                    parent_invoice_fiscal_invoice_number = None
                    refund_type = None
                    refund_note = None
                    refund_date = None
                    refund_time = None
                    invoice_type = self.type
                    if invoice_type == 'out_invoice':
                        doc_type = 'F'
                    invoice_parent = self.env['fpi.printer'].search([('employee_id.id', '=', self.write_uid.id)])
                    print(invoice_parent)
                    parent_invoice_fiscal_printer_serial = invoice_parent.serial
                    print(parent_invoice_fiscal_printer_serial)
                    partner_address = None
                    if 'out_refund' in self.type:
                        invoice_parent = self.env['account.move'].search([('id', '=', self.reversed_entry_id.id)])
                        if invoice_parent.fpi_document_id:
                            #cambio para las pruebas de nota de credito, se cambio == por !=
                            if not invoice_parent.document_fiscal_invoice_number:
                                raise UserError(ErrorMessages.PRINTING_DENIED)
                            else:
                                parent_invoice_filename_assigned = invoice_parent.fpi_document_id.master_filename_assigned
                                parent_invoice_fiscal_printer_serial = invoice_parent.fpi_document_id.serial
                                parent_invoice_fiscal_invoice_number = invoice_parent.fpi_document_id.fiscal_invoice_number
                        else:
                            raise UserError(ErrorMessages.PRINTING_DENIED)
                        refund_type = 'refund'
                        refund_note = self.ref
                        if self.invoice_date:
                            refund_date_object = str(self.invoice_date).split("-")
                            refund_date = "{0}/{1}/{2}".format(
                                refund_date_object[2], refund_date_object[1], refund_date_object[0])
                        if self.create_date:
                            import datetime
                            refund_time_object = datetime.datetime.strptime(str(self.create_date)[:-7], "%Y-%m-%d %H:%M:%S")
                            minute = str(refund_time_object.minute)
                            if refund_time_object.minute < 10:
                                minute = '0{0}'.format(refund_time_object.minute)
                            refund_time = "{0}:{1}".format(refund_time_object.hour, minute)
                    partner_street = self.partner_id.street if self.partner_id.street else ""
                    partner_zip = self.partner_id.zip if self.partner_id.zip else ""
                    partner_province = self.partner_id.province_id.name if self.partner_id.province_id else ""
                    partner_district = self.partner_id.district_id.name if self.partner_id.district_id else ""
                    partner_sector = self.partner_id.sector_id.name if self.partner_id.sector_id else ""
                    partner_country = self.partner_id.neonety_country_id.name if self.partner_id.neonety_country_id else ""
                    partner_address = str(partner_district) + ', ' + str(partner_sector) + ', ' + str(partner_street)
                    invoice_number = ''
                    if self.type == 'out_invoice':
                        doc_type = 'F'
                        invoice_number = self.name
                    elif self.type == 'out_refund':
                        doc_type = 'C'
                        invoice_number = self.name
                    
                    
                    # if len(self.payment_ids) > 0:
                    #     payments_total = sum( map(lambda x: x.amount, self.payment_ids))
                    #     cash_payment_total = sum( map(lambda x: x.amount if 'CSH1' in x.journal_id.sel_payment_form else 0.00, self.payment_ids))
                    #     bank_payment_total = sum( map(lambda x: x.amount if 'BNK1' in x.journal_id.sel_payment_form else 0.00, self.payment_ids))
                    #     credit_card_payment_total = sum( map(lambda x: x.amount if 'TC-' in x.journal_id.sel_payment_form[:3] else 0.00, self.payment_ids))
                    #     debit_card_payment_total = sum( map(lambda x: x.amount if 'TD-' in x.journal_id.sel_payment_form[:3] else 0.00, self.payment_ids))
                    # invoice_tax = self.env['account.move.line'].search([('invoice_id', '=', self.id)])
                    # if invoice_tax:
                    #     tax_percentage = invoice_tax.tax_id.amount if invoice_tax.tax_id else 0.00
                    # if len(self.invoice_line_ids) > 0:
                    #     for line in self.invoice_line_ids:
                    #         discount = (line.price_unit*line.discount)/100
                    #         discount_total = discount_total + discount
                    new_printer_obj = self.env['fpi.document'].create({
                        'write_uid': self.write_uid.id,
                        'printer_id': printer.id,
                        'documents_type_printed': 'account_move',
                        'invoice_id': self.id,
                        'partner_name': self.partner_id.name,
                        'partner_ruc': self.partner_id.ruc if self.partner_id.ruc else 'N/D',
                        'partner_street': partner_street,
                        'partner_zip': partner_zip,
                        'partner_province': partner_province,
                        'partner_district': partner_district,
                        'partner_sector': partner_sector,
                        'partner_country': partner_country,
                        'parent_invoice_filename_assigned': parent_invoice_filename_assigned,
                        'parent_invoice_fiscal_invoice_number': parent_invoice_fiscal_invoice_number,
                        'parent_invoice_fiscal_printer_serial': parent_invoice_fiscal_printer_serial,
                        'refund_type': refund_type,
                        'refund_note': refund_note,
                        'invoice_type': invoice_type,
                        'refund_date': refund_date,
                        'refund_time': refund_time,
                        'number': self.name,
                        ##campos de webpos ##
                        'doc_type': doc_type,
                        'doc_number': self.name,
                        'customer_name': self.partner_id.name,
                        'customer_ruc': self.partner_id.ruc if self.partner_id.ruc else 'N/D',
                        'customer_address': partner_address,
                        'invoice_number': invoice_number,
                        'printer_user_id': self.write_uid.id})
                    if new_printer_obj and 'pending' in new_printer_obj.print_status:
                        self.fpi_document_id = new_printer_obj.id
