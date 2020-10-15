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


DOCUMENTS_TYPES_PRINTED = [
    ('account_invoice', 'Factura de Venta'),
    ('pos_order', 'Orden de pedido')
]


INVOICE_TYPES_PRINTED = [
    ('out_invoice', 'Factura por Venta'),
    ('out_refund', 'Nota de Crédito')
]

printers = [
    ('bixolon', 'Bixolon'),
    ('dascon', 'Dascon'),
    ('bematech', 'Bematech'),
    ('star', 'Star'),
    ('oki', 'Oki')
]

printer_states = [
    ('on', 'Encendida'),
    ('off', 'Apagada')
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
    PRINTING_NOT_ALLOWED = "No se puede imprimir esta factura en la impresora fiscal, su monto total es menor o igual a cero"

class FpiPrinter(models.Model):
    _name = 'fpi.printer'
    _rec_name = 'printer_model'
    printer_model = fields.Selection(
        printers,
        string='Modelo de impresora',
        default='bixolon',
        required=True)
    serial = fields.Char(
        string='Serial de impresora',
        size=13,
        required=True)
    is_available = fields.Boolean(
        string='Impresora activa y disponible',
        required=False,
        default=True,
        translate=True)
    printer_state = fields.Selection(
        printer_states,
        string='Estado de impresora',
        default='off')
    last_conn = fields.Date(
        string = 'Última conección',
        readonly = True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Creado por')
    merge_invoices_orders = fields.Boolean(
        string='Mezclar Ordenes y Facturas en la misma instancia',
        required=False,
        default=False)
    employee_id = fields.Many2one(
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
        if 'employee_id' in vals:
            if pk > 0:
                counter = self.env['fpi.printer'].search_count(
                    [('employee_id', '=', vals['employee_id']), ('id', '!=', pk)])
            else:
                counter = self.env['fpi.printer'].search_count([('employee_id', '=', vals['employee_id'])])
            if counter > 0:
                raise ValidationError("El usuario seleccionado ya tiene una impresora asignada")


    @api.model
    def create(self, vals):
        self._check_printer_assigned_exists(vals=vals)
        p = super(FpiPrinter, self).create(vals)
        p.user_id = self.write_uid.id
        return p

    @api.multi
    def write(self, vals):
        p = super(FpiPrinter, self).write(vals)
        self._check_printer_assigned_exists(vals=vals, pk=self.id)
        return p

    @api.multi
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
        string='Número de Factura Fiscal',
        default=0)
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
    invoice_id = fields.Many2one(
        'account.invoice',
        string='Factura de Venta',
        default=None,
        required=False)
    document_printed_date = fields.Char(
        string = 'Fecha de impresion del documento')

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

    ## INICIO DE SECCION DE PAGOS ##
    pay_type = fields.Char(
        string = 'Tipo de pago, puede tener los siguientes valores: 01 para Efectivo, 02 para Tarjeta de credito, 03 para Tarjeta de debito, 04 para Cheque, 05 para Otro, 06 para Otro, 07 para nota de credito, 08 para credito (sin pagos recibidos), 09 para Otro',
        size = 2
    )
    pay_amt = fields.Float(
        string = 'Monto pagado'
    )
    pay_descri = fields.Char (
        string = 'Descripcion del pago',
        size = 20
    )
    ##  FIN DE LA SECCION DE PAGOS ##

    ## SECCION DE TRAILER (PIE DE PAGINA) ##
    trailer_id = fields.Integer(
        string = 'Identificador de linea'
    )
    trailer_value = fields.Char(
        string = 'Texto informativo de la linea',
        size = 50
    )
    # serial = env['fpi.printer'].search([('employee_id', '=', uid)]).serial
    # env['fpi.document'].create({'printer_id': 1,'printer_user_id':uid, 'doc_type' : 'X', 'parent_invoice_fiscal_printer_serial': serial, 'number':'REPORTE-X-0001'})

    @api.model
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

    @api.multi
    def unlink(self):
        for document in self:
            if 'in_progress' in document.print_status:
                raise UserError(ErrorMessages.CANCEL_PRINTING_NOT_ALLOWED)
            else:
                if 'account_invoice' in document.documents_type_printed:
                    if document.invoice_id:
                        invoice = self.env['account.invoice'].browse(document.invoice_id.id)
                        if invoice:
                            invoice.write({'fpi_document_id': None})
        return super(FpiDocument, self).unlink()




class FpiInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
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

    @api.model
    def create(self, vals):
        obj = super(FpiInvoice, self).create(vals)
        obj.fpi_document_id = None
        obj.printer_user_id = None
        return obj

    @api.one
    def send_fiscal_printer_action(self):
        if self.amount_total <= 0 and 'out_invoice' in self.type:
            raise UserError(ErrorMessages.PRINTING_NOT_ALLOWED)
        else:
                printer = self.env['fpi.printer'].search([('employee_id', '=', self.write_uid.id)])
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
                    invoice_parent = self.env['fpi.printer'].search([('employee_id', '=', self.write_uid.id)])
                    print(invoice_parent)
                    parent_invoice_fiscal_printer_serial = invoice_parent.serial
                    print(parent_invoice_fiscal_printer_serial)
                    partner_address = None
                    if 'out_refund' in self.type:
                        invoice_parent = self.env['account.invoice'].search([('id', '=', self.refund_invoice_id.id)])
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
                    payments_total = 0.00
                    cash_payment_total = 0.00
                    bank_payment_total = 0.00
                    credit_card_payment_total = 0.00
                    debit_card_payment_total = 0.00
                    tax_percentage = 0.00
                    discount_total = 0.00
                    partner_address = str(partner_district) + ', ' + str(partner_sector) + ', ' + str(partner_street)
                    invoice_number = ''
                    if self.type == 'out_invoice':
                        doc_type = 'F'
                        invoice_number = self.number
                    elif self.type == 'out_refund':
                        doc_type = 'C'
                        invoice_number = self.number
                    
                    
                    if len(self.payment_ids) > 0:
                        payments_total = sum( map(lambda x: x.amount, self.payment_ids))
                        cash_payment_total = sum( map(lambda x: x.amount if 'CSH1' in x.journal_id.sel_payment_form else 0.00, self.payment_ids))
                        bank_payment_total = sum( map(lambda x: x.amount if 'BNK1' in x.journal_id.sel_payment_form else 0.00, self.payment_ids))
                        credit_card_payment_total = sum( map(lambda x: x.amount if 'TC-' in x.journal_id.sel_payment_form[:3] else 0.00, self.payment_ids))
                        debit_card_payment_total = sum( map(lambda x: x.amount if 'TD-' in x.journal_id.sel_payment_form[:3] else 0.00, self.payment_ids))
                    invoice_tax = self.env['account.invoice.tax'].search([('invoice_id', '=', self.id)])
                    if invoice_tax:
                        tax_percentage = invoice_tax.tax_id.amount if invoice_tax.tax_id else 0.00
                    if len(self.invoice_line_ids) > 0:
                        for line in self.invoice_line_ids:
                            discount = (line.price_unit*line.discount)/100
                            discount_total = discount_total + discount
                    new_printer_obj = self.env['fpi.document'].create({
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
                        'discount_total': discount_total,
                        'parent_invoice_filename_assigned': parent_invoice_filename_assigned,
                        'parent_invoice_fiscal_invoice_number': parent_invoice_fiscal_invoice_number,
                        'parent_invoice_fiscal_printer_serial': parent_invoice_fiscal_printer_serial,
                        'refund_type': refund_type,
                        'refund_note': refund_note,
                        'invoice_type': invoice_type,
                        'refund_date': refund_date,
                        'refund_time': refund_time,
                        'number': self.number,
                        ##campos de webpos ##
                        'doc_type': doc_type,
                        'doc_number': self.number,
                        'customer_name': self.partner_id.name,
                        'customer_ruc': self.partner_id.ruc if self.partner_id.ruc else 'N/D',
                        'customer_address': partner_address,
                        'invoice_number': invoice_number,
                        'printer_user_id': self.write_uid.id})
                    if new_printer_obj and 'pending' in new_printer_obj.print_status:
                        self.fpi_document_id = new_printer_obj.id


class FpiDocumentLine(models.Model):
    _name = 'fpi.document.line'
    _rec_name = 'item_descri'


    ## ITEMS SECTION  ##
    invoice_id = fields.Integer(
        string = 'Id de factura'
    )

    item_id = fields.Integer(
        string = 'Id de producto'
    )
    item_qty = fields.Float(
        string = 'Cantidad de producto'
    )
    item_price = fields.Float(
        string = 'Precio de producto'
    )
    item_code = fields.Char(
        string = 'Codigo del producto',
        size = 14
    )
    item_descri = fields.Char(
        string = 'Descripcion del producto',
        size = 50
    )
    item_tax = fields.Integer(
        string = 'Tipo de impuesto, puede ser 0 para excento, 1 para 7%, 2 para 10% y 3 para 15%'
    )
    item_comment = fields.Char(
        string = 'Comentarios adicionales del producto',
        size = 200
    )
    item_dperc = fields.Char(
        string = 'Porcentaje de descuento para el producto, debe incluir el signo de porcentaje (%).',
        size = 4
    )
    item_damt = fields.Float(
        string = 'Cantidad descontada al producto'
    )
    ## FIN DE SECION DE ITEM ##


class FpiInvoiceLine(models.Model):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    @api.onchange ('product_id')
    def equalizer(self):
        self.env['fpi.document.line'].create({
            'item_id' : self.product_id,
            'item_qty' : self.quantity,
            'item_price' : self.price_unit,
            'item_code' : self.product_id,
            'item_descri' : self.name,
            'item_tax' : 1,
            'item_comment' : '',
            'item_dperc' : str(self.discount)+'%',
            'item_damt' : self.price_unit - self.price_subtotal,
            # 'invoice_id' : int(self.invoice_id)

        })

