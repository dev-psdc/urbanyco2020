# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)
"""

PRINT_STATUS_TYPES = [
    ('pending', 'Por imprimir'),
    ('in_progress', 'Imprimiendo...'),
    ('completed', 'Factura impresa'),
    ('failed', 'Impresión fallida')
]


DOCUMENTS_TYPES_PRINTED = [
    ('account_invoice', 'Factura de Venta'),
    ('pos_order', 'Orden de pedido')
]


class ErrorMessages:
    PRINTER_NOT_ASSIGNED = "No se ha podido imprimir el documento ya que el usuario no tiene una impresora fiscal asignada."
    PRINTING_IN_PROGRESS = 'La factura se encuentra en proceso de impresión'
    PRINTING_COMPLETED = 'El documento ya ha sido impreso por la impresora fiscal asignada, el mismo no se puede volver a imprimir.'
    PRINTING_DENIED = 'La Nota de Crédito no se puede imprimir debido a que la factura de venta todavia no ha sido impresa por la impresora fiscal asignada.'
    CANCEL_PRINTING_NOT_ALLOWED = "No se puede cancelar la impresión mientras este en proceso."


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
    employee_id = fields.Many2one(
        'res.users',
        string='Asignado a',
        required=True,
        translate=True)

    @api.model
    def create(self, vals):
        p = super(FpiPrinter, self).create(vals)
        p.user_id = self.write_uid.id
        return p


class FpiRecords(models.Model):
    _name = 'fpi.records'
    _rec_name = 'number'
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Factura de Venta',
        default=None,
        required=True)
    printer_id = fields.Many2one(
        'fpi.printer',
        string='Impresora',
        required=True)
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
    fiscal_invoice_number = fields.Integer(
        string='Número de Factura Fiscal',
        default=0)
    printer_serial_number = fields.Char(
        string='Numero serial de la impresora',
        required=True,
        size=100)
    documents_type_printed = fields.Selection(
        DOCUMENTS_TYPES_PRINTED,
        string='Tipo de documento impreso',
        required=False,
        default='account_invoice')
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
    payments_total = fields.Float(
        string='Total en pagos realizados',
        default=0.00,
        required=False)
    cash_payment_total = fields.Float(
        string='Total en pagos realizados en efectivo',
        default=0.00,
        required=False)
    bank_payment_total = fields.Float(
        string='Total en pagos realizados en transacciones bancarias',
        default=0.00,
        required=False)
    credit_card_payment_total = fields.Float(
        string='Total en pagos realizados en Tarjetas de crédito',
        default=0.00,
        required=False)
    debit_card_payment_total = fields.Float(
        string='Total en pagos realizados en Tarjetas de débito',
        default=0.00,
        required=False)
    amount_total = fields.Float(
        string='Total general de la factura (incluye impuestos)',
        default=0.00,
        required=False)
    amount_untaxed = fields.Float(
        string='Total de la factura (sin impuestos)',
        default=0.00,
        required=False)
    amount_tax = fields.Float(
        string='Total en impuestos aplicados',
        default=0.00,
        required=False)
    discount_total = fields.Float(
        string='Total en descuentos',
        default=0.00,
        required=False)
    tax_percentage = fields.Float(
        string='Porcentaje de impuesto aplicado',
        default=0.00,
        required=False)
    invoice_type = fields.Char(
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
    parent_invoice_fiscal_invoice_number = fields.Integer(
        string='Numero de factura fiscal asignado a la factura origen de la nota de credito',
        default=0,
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
        related='invoice_id.number')
    serial = fields.Char(
        related='printer_id.serial')

    @api.multi
    def unlink(self):
        for record in self:
            if 'in_progress' in record.print_status:
                raise UserError(ErrorMessages.CANCEL_PRINTING_NOT_ALLOWED)
            else:
                if 'account_invoice' in record.documents_type_printed:
                    if record.invoice_id:
                        invoice = self.env['account.invoice'].browse(record.invoice_id.id)
                        if invoice:
                            invoice.write({'fpi_record_id': None})
        return super(FpiRecords, self).unlink()


class FpiInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    fpi_record_id = fields.Many2one(
        'fpi.records',
        string='Impresión',
        default=None,
        required=False)
    print_status = fields.Selection(
        related='fpi_record_id.print_status')
    fiscal_invoice_number = fields.Integer(
        related='fpi_record_id.fiscal_invoice_number')

    @api.model
    def create(self, vals):
        r = super(FpiInvoice, self).create(vals)
        r.fpi_record_id = None
        return r

    @api.one
    def send_fiscal_printer_action(self):
        if self.fpi_record_id:
            if self.print_status in ['pending', 'in_progress']:
                raise UserError(ErrorMessages.PRINTING_IN_PROGRESS)
            elif 'completed' in self.print_status and self.fiscal_invoice_number > 0:
                raise UserError(ErrorMessages.PRINTING_COMPLETED)
        else:
            printer = self.env['fpi.printer'].search([('employee_id', '=', self.write_uid.id)])
            if not printer:
                raise UserError(ErrorMessages.PRINTER_NOT_ASSIGNED)
            else:
                parent_invoice_filename_assigned = None
                parent_invoice_fiscal_printer_serial = None
                parent_invoice_fiscal_invoice_number = 0
                refund_type = None
                refund_note = None
                refund_date = None
                refund_time = None
                invoice_type = self.type
                partner_address = None 
                if 'out_refund' in self.type:
                    invoice_parent = self.env['account.invoice'].search([('id', '=', self.refund_invoice_id.id)])
                    if invoice_parent.fpi_record_id:
                        if invoice_parent.fiscal_invoice_number == 0:
                            raise UserError(ErrorMessages.PRINTING_DENIED)
                        else:
                            parent_invoice_filename_assigned = invoice_parent.fpi_record_id.filename_assigned
                            parent_invoice_fiscal_printer_serial = invoice_parent.fpi_record_id.serial
                            parent_invoice_fiscal_invoice_number = invoice_parent.fpi_record_id.fiscal_invoice_number
                    else:
                        raise UserError(ErrorMessages.PRINTING_DENIED)
                    refund_info = self.env['account.invoice.refund'].search([('description', '=', self.name)])
                    if refund_info:
                        refund_type = refund_info.filter_refund
                        refund_note = refund_info.description
                        if refund_info.date_invoice:
                            refund_date_object = refund_info.date_invoice.split("-")
                            refund_date = "{0}/{1}/{2}".format(
                                refund_date_object[2], refund_date_object[1], refund_date_object[0])
                        if refund_info.create_date:
                            import datetime
                            refund_time_object = datetime.datetime.strptime(refund_info.create_date, "%Y-%m-%d %H:%M:%S")
                            refund_time = "{0}:{1}".format(refund_time_object.hour, refund_time_object.minute)
                partner_street = self.partner_id.street if self.partner_id.street else ""
                partner_zip = self.partner_id.zip if self.partner_id.zip else ""
                partner_province = self.partner_id.province_id.name if self.partner_id.province_id else ""
                partner_district = self.partner_id.district_id.name if self.partner_id.district_id else ""
                partner_sector = self.partner_id.sector_id.name.encode('utf-8') if self.partner_id.sector_id else ""
                partner_country = self.partner_id.neonety_country_id.name if self.partner_id.neonety_country_id else ""
                payments_total = 0.00
                cash_payment_total = 0.00
                bank_payment_total = 0.00
                credit_card_payment_total = 0.00
                debit_card_payment_total = 0.00
                tax_percentage = 0.00
                if len(self.payment_ids) > 0:
                    payments_total = sum( map(lambda x: x.amount, self.payment_ids))
                    cash_payment_total = sum( map(lambda x: x.amount if 'cash-' in x.journal_id.code else 0.00, self.payment_ids))
                    bank_payment_total = sum( map(lambda x: x.amount if 'bank-' in x.journal_id.code else 0.00, self.payment_ids))
                    credit_card_payment_total = sum( map(lambda x: x.amount if 'tc-' in x.journal_id.code else 0.00, self.payment_ids))
                    debit_card_payment_total = sum( map(lambda x: x.amount if 'td-' in x.journal_id.code else 0.00, self.payment_ids))
                invoice_tax = self.env['account.invoice.tax'].search([('invoice_id', '=', self.id)])
                if invoice_tax:
                    tax_percentage = invoice_tax.tax_id.amount if invoice_tax.tax_id else 0.00
                new_printer_record = self.env['fpi.records'].create({
                    'user_id': self.write_uid.id,
                    'printer_id': printer.id,
                    'printer_serial_number': printer.serial,
                    'documents_type_printed': 'account_invoice',
                    'invoice_id': self.id,
                    'partner_name': self.partner_id.name,
                    'partner_ruc': self.partner_id.ruc if self.partner_id.ruc else 'N/D',
                    'partner_street': partner_street,
                    'partner_zip': partner_zip,
                    'partner_province': partner_province,
                    'partner_district': partner_district,
                    'partner_sector': partner_sector,
                    'partner_country': partner_country,
                    'payments_total': payments_total,
                    'cash_payment_total': cash_payment_total,
                    'bank_payment_total': bank_payment_total,
                    'credit_card_payment_total': credit_card_payment_total,
                    'debit_card_payment_total': debit_card_payment_total,
                    'amount_total': self.amount_total,
                    'amount_untaxed': self.amount_untaxed,
                    'amount_tax': self.amount_tax,
                    'tax_percentage': tax_percentage,
                    'parent_invoice_filename_assigned': parent_invoice_filename_assigned,
                    'parent_invoice_fiscal_invoice_number': parent_invoice_fiscal_invoice_number,
                    'parent_invoice_fiscal_printer_serial': parent_invoice_fiscal_printer_serial,
                    'refund_type': refund_type,
                    'refund_note': refund_note,
                    'invoice_type': invoice_type,
                    'refund_date': refund_date,
                    'refund_time': refund_time
                })
                if new_printer_record and 'pending' in new_printer_record.print_status:
                    self.fpi_record_id = new_printer_record.id"""