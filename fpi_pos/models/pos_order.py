# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

POS_ORDER_TYPES = [
    ('order', 'Orden de compra'),
    ('refund', 'Devolución')
]

class ErrorMessages:
    PRINTER_NOT_ASSIGNED = "No se ha podido imprimir el documento ya que el usuario no tiene una impresora fiscal asignada."
    PRINTING_IN_PROGRESS = 'La factura se encuentra en proceso de impresión'
    PRINTING_COMPLETED = 'El documento ya ha sido impreso por la impresora fiscal asignada, el mismo no se puede volver a imprimir.'
    PRINTING_DENIED = 'La Nota de Crédito no se puede imprimir debido a que la factura de venta todavia no ha sido impresa por la impresora fiscal asignada.'
    CANCEL_PRINTING_NOT_ALLOWED = "No se puede cancelar la impresión mientras este en proceso."


class PosOrder(models.Model):
    _inherit = 'pos.order'
    fpi_document_id = fields.Many2one(
        'fpi.document',
        string='Impresión asociada',
        default=None,
        required=False)
    parent_pos_order_id = fields.Integer(
        string='Orden de origen',
        default=0)
    pos_order_type = fields.Char(
        string='Tipo de orden',
        size=20, 
        default='order')
    document_print_status = fields.Selection(
        related='fpi_document_id.print_status')
    document_fiscal_invoice_number = fields.Integer(
        related='fpi_document_id.fiscal_invoice_number')
    fiscal_printer_allowed = fields.Boolean(
        string='Permitir el uso de impresión fiscal',
        default=False)
    # loyalty_points = fields.Float(
    #    string='Orden de origen',
    #    default=0.00)

    @api.model
    def create(self, vals):
        order = super(PosOrder, self).create(vals)
        order.fpi_record_id = None
        order.pos_order_type = 'order'
        order.fiscal_printer_allowed = False
        return order

    @api.model
    def _process_order(self, pos_order):
        order = super(PosOrder, self)._process_order(pos_order)
        fiscal_printer_allowed = False
        if 'fiscal_printer_allowed' in pos_order:
            fiscal_printer_allowed = pos_order['fiscal_printer_allowed']
        if order.config_id.iface_fiscal_printer_button \
            and not order.config_id.iface_fiscal_printer_optional and not fiscal_printer_allowed:
            fiscal_printer_allowed = True
        order.fiscal_printer_allowed = fiscal_printer_allowed
        if order.config_id.iface_fiscal_printer_button and order.fiscal_printer_allowed:
            order.send_fiscal_printer_action()
        return order

    @api.multi
    def refund(self):
        values = super(PosOrder, self).refund()
        order = self.env['pos.order'].browse(values['res_id'])
        order_parent = self.env['pos.order'].search([
            ('pos_reference', 'like', order.pos_reference),
            ('state', '=', 'paid')], limit=1, order='id desc')
        if len(order_parent) > 0:
            order.write({
                'pos_order_type': 'refund',
                'parent_pos_order_id': order_parent.id,
                'fpi_document_id': 0})
        return values

    @api.one
    def send_fiscal_printer_action(self):
        if 'refund' in self.pos_order_type or ('order' in self.pos_order_type and self.amount_total > 0):
            if self.fpi_document_id:
                if self.document_print_status in ['pending', 'in_progress']:
                    raise UserError(ErrorMessages.PRINTING_IN_PROGRESS)
                elif 'completed' in self.document_print_status and self.document_fiscal_invoice_number > 0:
                    raise UserError(ErrorMessages.PRINTING_COMPLETED)
            else:
                printer = self.env['fpi.printer'].search([('employee_id', '=', self.write_uid.id)])
                if not printer:
                    raise UserError(ErrorMessages.PRINTER_NOT_ASSIGNED)
                else:
                    invoice_type = 'out_invoice' if 'order' in self.pos_order_type else 'out_refund'
                    parent_order_filename_assigned = None
                    parent_order_fiscal_printer_serial = None
                    parent_order_fiscal_invoice_number = 0
                    refund_type = None
                    refund_note = None
                    refund_date = None
                    refund_time = None
                    partner_address = None
                    if 'refund' in self.pos_order_type and self.parent_pos_order_id:
                        order_parent = self.env['pos.order'].browse(self.parent_pos_order_id)
                        if not order_parent or not order_parent.fpi_document_id:
                            raise UserError(ErrorMessages.PRINTING_DENIED)
                        else:
                            if order_parent.document_fiscal_invoice_number == 0:
                                raise UserError(ErrorMessages.PRINTING_DENIED)
                            else:
                                parent_order_filename_assigned = order_parent.fpi_document_id.master_filename_assigned
                                parent_order_fiscal_printer_serial = order_parent.fpi_document_id.serial
                                parent_order_fiscal_invoice_number = order_parent.fpi_document_id.fiscal_invoice_number
                                refund_note = 'Devolución'
                                if self.write_date:
                                    import datetime
                                    refund_date_object = datetime.datetime.strptime(self.write_date, "%Y-%m-%d %H:%M:%S")
                                    day_formatted = refund_date_object.day if refund_date_object.day >= 10 else '0{0}'.format(
                                        refund_date_object.day)
                                    month_formatted = refund_date_object.month if refund_date_object.month >= 10 else '0{0}'.format(
                                        refund_date_object.month)
                                    hour_formatted = refund_date_object.hour if refund_date_object.hour >= 10 else '0{0}'.format(
                                        refund_date_object.hour)
                                    minute_formatted = refund_date_object.minute if refund_date_object.minute >= 10 else '0{0}'.format(
                                        refund_date_object.minute)
                                    refund_time = "{0}:{1}".format(hour_formatted, minute_formatted)
                                    refund_date = "{0}/{1}/{2}".format(day_formatted, month_formatted, refund_date_object.year)
                    partner_street = self.partner_id.street if self.partner_id.street else ""
                    partner_zip = self.partner_id.zip if self.partner_id.zip else ""
                    partner_province = self.partner_id.province_id.name if self.partner_id.province_id else ""
                    partner_district = self.partner_id.district_id.name if self.partner_id.district_id else ""
                    partner_sector = self.partner_id.sector_id.name.encode('utf-8') if self.partner_id.sector_id else ""
                    partner_country = self.partner_id.neonety_country_id.name if self.partner_id.neonety_country_id else ""
                    payments_total = 0.00
                    amount_untaxed = 0.00
                    cash_payment_total = 0.00
                    bank_payment_total = 0.00
                    credit_card_payment_total = 0.00
                    debit_card_payment_total = 0.00
                    tax_percentage = 0.00
                    discount_total = 0.00
                    if len(self.statement_ids) > 0:
                        payments_total = sum(map(lambda x: x.amount if x.amount > 0.00 else 0.00, self.statement_ids))
                        cash_payment_total = sum(map(lambda x: x.amount if 'CSH1' in x.journal_id.code else 0.00, self.statement_ids))
                        bank_payment_total = sum(map(lambda x: x.amount if 'BNK1' in x.journal_id.code else 0.00, self.statement_ids))
                        credit_card_payment_total = sum(map(lambda x: x.amount if 'TC-' in x.journal_id.code[:3] else 0.00, self.statement_ids))
                        debit_card_payment_total = sum(map(lambda x: x.amount if 'TD-' in x.journal_id.code[:3] else 0.00, self.statement_ids))
                    invoice_tax = self.env['account.invoice.tax'].search([('invoice_id', '=', self.id)])
                    if len(self.lines) > 0:
                        if self.amount_tax > 0.00:
                            for item in self.lines:
                                if len(item.tax_ids) > 0:
                                    for tax in item.tax_ids:
                                        if tax and tax.amount > 0:
                                            tax_percentage = tax.amount
                                            break
                                    if tax_percentage > 0:
                                        break
                        for line in self.lines:
                            subtotal = line.price_unit * line.qty
                            discount = (subtotal * line.discount)/100
                            discount_total = discount_total + discount
                    if 'refund' in self.pos_order_type:
                        amount_untaxed = self.amount_total - self.amount_tax
                    new_printer_obj = self.env['fpi.document'].create({
                        'user_id': self.write_uid.id,
                        'printer_id': printer.id,
                        'printer_serial_number': printer.serial,
                        'documents_type_printed': 'pos_order',
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
                        'amount_untaxed': amount_untaxed,
                        'amount_tax': self.amount_tax,
                        'tax_percentage': tax_percentage,
                        'discount_total': discount_total,
                        'parent_invoice_filename_assigned': parent_order_filename_assigned,
                        'parent_invoice_fiscal_invoice_number': parent_order_fiscal_invoice_number,
                        'parent_invoice_fiscal_printer_serial': parent_order_fiscal_printer_serial,
                        'refund_type': 'refund',
                        'refund_note': refund_note,
                        'invoice_type': invoice_type,
                        'refund_date': refund_date,
                        'refund_time': refund_time,
                        'number': self.name,
                        'order_id': self.id})
                    if new_printer_obj and 'pending' in new_printer_obj.print_status:
                        self.write({
                            'fpi_document_id': new_printer_obj.id,
                            'fiscal_printer_allowed': True})