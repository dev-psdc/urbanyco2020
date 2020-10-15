# -*- coding: utf-8 -*-
from odoo import models, fields, api, osv, tools
from openerp.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning
import logging
_logger = logging.getLogger(__name__)


PRINT_STATUS_TYPES = [
    ('incomplete', 'Factura incompleta'),
    ('pending', 'Por imprimir'),
    ('in_progress', 'Imprimiendo...'),
    ('completed', 'Factura impresa'),
    ('failed', 'Impresión fallida')
]


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


class FpiInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    printer_id = fields.Many2one(
        'fpi.printer',
        string='Impresora',
        default=None,
        required=False)
    print_status = fields.Selection(
        PRINT_STATUS_TYPES,
        string='Estatus de impresión',
        required=False,
        translate=True,
        default='pending')
    print_filename_assigned = fields.Char(
        string='Nombre de impresión asignado',
        required=False,
        default=None,
        size=20)
    fiscal_printer_invoice_id = fields.Integer(
        string='Número Fiscal',
        default=None,
        required=False)
    serial_fiscal_printer = fields.Char(
        string='Numero serial de la impresora',
        required=False,
        default=None,
        size=20)

    @api.model
    def create(self, vals):
        r = super(FpiInvoice, self).create(vals)
        r.printer_id = None
        r.serial_fiscal_printer = None
        r.fiscal_printer_invoice_id = None
        return r

    @api.one
    def send_fiscal_printer_action(self):
        if 'pending' in self.print_status:
            raise UserError('La factura ya esta en impresión.')
        elif 'completed' in self.print_status and self.fiscal_printer_invoice_id > 0:
            raise UserError('La factura ya ha sido impresa y no se puede imprimir otra vez.')
        else:
            printer = self.env['fpi.printer'].search([('employee_id', '=', self.write_uid.id)])
            if not printer:
                raise UserError("""
                    ERROR: Se ha encontrado un error al intentar imprimir el document,
                    Tu cuenta de usuario no tiene una impresora fiscal asignada, debes comunicarte con tu administrador
                    y solicitar que se te asigne una impresora a tu perfil.""")
            if 'out_refund' in self.type:
                invoice_parent = self.env['account.invoice'].search([('id', '=', self.refund_invoice_id.id)])
                if invoice_parent is not None:
                    if invoice_parent.serial_fiscal_printer is None or invoice_parent.fiscal_printer_invoice_id <= 0:
                        raise UserError("""
                            Esta Nota de crédito no puede ser impresa porque la factura de origen todavía no ha sido impresa con la 
                            impresora fiscal asignada.""")
            self.print_status = 'pending'
            self.printer_id = printer.id
            self.serial_fiscal_printer = printer.serial

    @api.one
    def send_fiscal_printer_pos_action(self, _user_id=None):
        if 'pending' in self.print_status:
            raise UserError('La factura ya esta en impresión.')
        elif 'completed' in self.print_status:
            raise UserError('La factura ya ha sido impresa y no se puede imprimir otra vez.')
        else:
            printer = self.env['fpi.printer'].search([('employee_id', '=', _user_id)])
            if not printer:
                raise UserError("""
                    ERROR: Se ha encontrado un error al intentar imprimir el document,
                    Tu cuenta de usuario no tiene una impresora fiscal asignada, debes comunicarte con tu administrador
                    y solicitar que se te asigne una impresora a tu perfil.""")
            self.print_status = 'pending'
            self.printer_id = printer.id

    @api.multi
    def cancel_printing(self):
        if 'in_progress' in self.print_status:
            raise UserError('No se puede cancelar la impresión.')
        else:
            self.printer_id = None
            self.print_status = 'incomplete'
            self.fiscal_printer_invoice_id = None
            self.serial_fiscal_printer = None
            return {
                'type': 'ir.actions.client',
                'tag': 'reload'}


class FpiInvoicesPrintMainListReport(models.Model):
    _name = 'fpi.printer.invoices.print.main.list.report'
    _auto = False
    id = fields.Char(
        string='ID', readonly=True, size=20)
    account_invoice_id = fields.Integer(
        string='ID de la factura', readonly=True)
    account_invoice_number = fields.Char(
        string='Numero de factura', readonly=True, size=50)
    account_invoice_state = fields.Char(
        string='Estado de la factura', readonly=True, size=20)
    account_invoice_print_status = fields.Char(
        string='Estado de la impresión', readonly=True, size=20)
    partner_street = fields.Char(
        string='Ubicación', readonly=True, size=150)
    partner_sector = fields.Char(
        string='Corregimiento', readonly=True, size=150)
    partner_district = fields.Char(
        string='Distrito', readonly=True, size=150)
    partner_province = fields.Char(
        string='Provincia', readonly=True, size=150)
    partner_zip = fields.Char(
        string='Codigo postal', readonly=True, size=150)
    partner_name = fields.Char(
        string='Nombre del cliente', readonly=True, size=80)
    partner_ruc = fields.Char(
        string='RUC del cliente', readonly=True, size=15)
    account_invoice_discount = fields.Float(
        string='Total de descuento',
        readonly=True)
    amount_total_payed = fields.Float(
        string='total en pagos', readonly=True)
    account_invoice_amount_total = fields.Float(
        string='Total en la factura', readonly=True)
    account_invoice_tax = fields.Float(
        string='Total en cargos', readonly=True)
    tax_percentage_amount = fields.Float(
        string='Porcentaje de cargo aplicado', readonly=True)
    cash_total_amount = fields.Float(
        string='Total en efectivo', readonly=True)
    bank_total_amount = fields.Float(
        string='Total en banco o cheque', readonly=True)
    print_filename_assigned = fields.Char(
        string='Nombre de impresión asignado',
        readonly=True,
        size=20)
    fpi_fiscal_printer_serial = fields.Char(
        string='Nombre de impresión asignado',
        readonly=True,
        size=255)
    
    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'fpi_printer_invoices_print_main_list_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW fpi_printer_invoices_print_main_list_report AS
            SELECT
                row_number() over() AS id,
                AI.id AS account_invoice_id,
                AI.number AS account_invoice_number,
                AI.state AS account_invoice_state,
                AI.print_status AS account_invoice_print_status,
                RP.street AS partner_street,
                NS.name AS partner_sector,
                ND.name AS partner_district,
                NP.name AS partner_province,
                RP.zip AS partner_zip,
                RP.name AS partner_name,
                RP.ruc AS partner_ruc,
                AI.print_filename_assigned AS print_filename_assigned,
                FPI.serial AS fpi_fiscal_printer_serial,
                0.00 AS account_invoice_discount,
                (
                    SELECT
                        SUM(AP.amount)
                    from
                        account_payment AP
                    WHERE
                        AP.communication LIKE AI.number
                        OR AP.communication LIKE AI.reference
                ) AS amount_total_payed,
                AI.amount_total AS account_invoice_amount_total,
                AI.amount_tax AS account_invoice_tax,
                7.00 AS tax_percentage_amount,
                (
                    SELECT
                        SUM(AP1.amount)
                    FROM
                        account_payment AP1
                        INNER JOIN
                            account_journal AJ
                            ON AJ.id = AP1.journal_id
                            AND AJ.type LIKE 'cash'
                    WHERE
                        AP1.communication LIKE AI.number
                        OR AP1.communication LIKE AI.reference
                ) AS cash_total_amount,
                (
                    SELECT
                        SUM(AP2.amount)
                    FROM
                        account_payment AP2
                        INNER JOIN
                            account_journal AJ1
                            ON AJ1.id = AP2.journal_id
                            AND AJ1.type LIKE 'bank'
                    WHERE
                        AP2.communication LIKE AI.number
                        OR AP2.communication LIKE AI.reference
                ) AS bank_total_amount
            FROM
                account_invoice AI
                INNER JOIN
                    res_partner RP
                    ON RP.id = AI.partner_id
                INNER JOIN
                    fpi_printer FPI
                    ON FPI.id = AI.printer_id
                LEFT JOIN
                    neonety_province NP
                    ON NP.id = RP.province_id
                LEFT JOIN
                    neonety_district ND
                    ON ND.id = RP.district_id
                LEFT JOIN
                    neonety_sector NS
                    ON NS.id = RP.sector_id
            WHERE
                AI.state IN ('open', 'paid')
                AND AI.printer_id IS NOT NULL
                AND AI.print_status LIKE 'pending'
                AND AI.type LIKE 'out_invoice'
            ORDER BY
                    id ASC, account_invoice_number ASC""")


class FpiInvoicesPrintMainCompletedListReport(models.Model):
    _name = 'fpi.printer.invoices.print.main.completed.list.report'
    _auto = False
    id = fields.Char(
        string='ID', readonly=True, size=20)
    account_invoice_id = fields.Integer(
        string='ID de la factura', readonly=True)
    account_invoice_number = fields.Char(
        string='Numero de factura', readonly=True, size=50)
    account_invoice_state = fields.Char(
        string='Estado de la factura', readonly=True, size=20)
    account_invoice_print_status = fields.Char(
        string='Estado de la impresión', readonly=True, size=20)
    print_filename_assigned = fields.Char(
        string='Nombre de impresión asignado',
        readonly=True,
        size=20)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'fpi_printer_invoices_print_main_completed_list_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW fpi_printer_invoices_print_main_completed_list_report AS
            SELECT
                row_number() over() AS id,
                AI.id AS account_invoice_id,
                AI.number AS account_invoice_number,
                AI.state AS account_invoice_state,
                AI.print_status AS account_invoice_print_status,
                AI.print_filename_assigned AS print_filename_assigned
            FROM
                account_invoice AI
            WHERE
                AI.state IN ('open', 'paid')
                AND AI.printer_id IS NOT NULL
                AND AI.print_status LIKE 'in_progress'
                AND AI.type LIKE 'out_invoice'
            ORDER BY
                    id ASC, account_invoice_number ASC""")


class FpiInvoicesPrintDetailsListReport(models.Model):
    _name = 'fpi.printer.invoices.print.details.list.report'
    _auto = False
    id = fields.Char(
        string='ID', readonly=True, size=20)
    account_invoice_id = fields.Integer(
        string='ID de la factura', readonly=True)
    account_invoice_number = fields.Char(
        string='Numero de factura', readonly=True, size=50)
    product_id = fields.Integer(
        string='ID del producto', readonly=True)
    product_code = fields.Char(
        string='ID del producto', readonly=True, size=50)
    product_code_2 = fields.Char(
        string='ID del producto', readonly=True, size=50)
    product_name = fields.Char(
        string='ID del producto', readonly=True, size=80)
    product_price = fields.Float(
        string='total en pagos', readonly=True)
    account_invoice_line_quantity = fields.Float(
        string='total en pagos', readonly=True)
    unit_type = fields.Char(
        string='ID del producto', readonly=True, size=20)
    group_type = fields.Integer(
        string='Field Label',readonly=True)
    tax_percentage = fields.Float(
        string='total en pagos', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'fpi_printer_invoices_print_details_list_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW fpi_printer_invoices_print_details_list_report AS
            SELECT
                row_number() over() AS id,
                AI.number AS account_invoice_number,
                AIL.invoice_id AS account_invoice_id,
                PP.id AS product_id,
                PT.default_code AS product_code,
                PP.default_code AS product_code_2,
                PT.name AS product_name,
                AIL.price_unit AS product_price,
                AIL.quantity AS account_invoice_line_quantity,
                'UNIDADES' as unit_type,
                2 AS group_type,
                AT.amount AS tax_percentage
            FROM
                account_invoice_line AIL
                INNER JOIN
                    account_invoice AI
                    ON AI.id = AIL.invoice_id
                    AND AI.state IN ('open', 'paid')
                    AND AI.printer_id IS NOT NULL
                    AND AI.print_status LIKE 'pending'
                    AND AI.type LIKE 'out_invoice'
                INNER JOIN
                    product_product PP
                    ON PP.id = AIL.product_id
                INNER JOIN 
                    product_template PT
                    ON PT.id = PP.product_tmpl_id
                left join
                    account_invoice_line_tax AILT
                    ON AILT.invoice_line_id = AIL.id
                LEFT JOIN
                    account_tax AT
                    ON AT.id = AILT.tax_id""")


class FpiInvoicesRefundPrintMainListReport(models.Model):
    _name = 'fpi.printer.invoices.refund.print.main.list.report'
    _auto = False
    id = fields.Char(
        string='ID', readonly=True, size=20)
    account_invoice_id = fields.Integer(
        string='ID de la factura', readonly=True)
    account_invoice_number = fields.Char(
        string='Numero de factura', readonly=True, size=50)
    account_invoice_state = fields.Char(
        string='Estado de la factura', readonly=True, size=20)
    account_invoice_print_status = fields.Char(
        string='Estado de la impresión', readonly=True, size=20)
    partner_street = fields.Char(
        string='Ubicación', readonly=True, size=150)
    partner_sector = fields.Char(
        string='Corregimiento', readonly=True, size=150)
    partner_district = fields.Char(
        string='Distrito', readonly=True, size=150)
    partner_province = fields.Char(
        string='Provincia', readonly=True, size=150)
    partner_zip = fields.Char(
        string='Codigo postal', readonly=True, size=150)
    partner_name = fields.Char(
        string='Nombre del cliente', readonly=True, size=80)
    partner_ruc = fields.Char(
        string='RUC del cliente', readonly=True, size=15)
    account_invoice_refund_amount_untaxed = fields.Float(
        string='Total neto', readonly=True)
    account_invoice_refund_amount_tax = fields.Float(
        string='Total impuesto', readonly=True)
    print_filename_assigned = fields.Char(
        string='Nombre de impresión asignado',
        readonly=True,
        size=20)
    parent_fiscal_invoice_number = fields.Char(
        string='Numero de factura de origen',
        readonly=True,
        size=20)
    parent_invoice_fiscal_invoice_id = fields.Char(
        string='Numero fiscal de la factura de origen',
        readonly=True,
        size=20)
    parent_invoice_serial_fiscal_printer = fields.Char(
        string='Numero serial de la impresora de la factura de origen',
        readonly=True,
        size=20)
    account_invoice_refund_type = fields.Char(
        string='Tipo de Nota Credito',
        readonly=True,
        size=20)
    account_invoice_refund_note = fields.Char(
        string='Nota o motivo de la Nota Credito',
        readonly=True,
        size=20)
    account_invoice_refund_date = fields.Char(
        string='Fecha de solicitud de facturacion Nota Credito',
        readonly=True,
        size=20)
    account_invoice_refund_time = fields.Char(
        string='Hora de solicitud de facturacion Nota Credito',
        readonly=True,
        size=20)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'fpi_printer_invoices_refund_print_main_list_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW fpi_printer_invoices_refund_print_main_list_report AS
            SELECT
                row_number() over() AS id,
                AI.id AS account_invoice_id,
                AI.number AS account_invoice_number,
                AI.state AS account_invoice_state,
                AI.print_status AS account_invoice_print_status,
                RP.street AS partner_street,
                NS.name AS partner_sector,
                ND.name AS partner_district,
                NP.name AS partner_province,
                RP.zip AS partner_zip,
                RP.name AS partner_name,
                RP.ruc AS partner_ruc,
                AI.print_filename_assigned AS print_filename_assigned,
                AI2.fiscal_printer_invoice_id AS parent_invoice_fiscal_invoice_id,
                AI2.serial_fiscal_printer AS parent_invoice_serial_fiscal_printer,
                AI2.print_filename_assigned AS parent_fiscal_invoice_number,
                AI.amount_untaxed AS account_invoice_refund_amount_untaxed,
                AI.amount_tax AS account_invoice_refund_amount_tax,
                (
                    SELECT
                        AIR.filter_refund
                    FROM
                        account_invoice_refund AIR
                    WHERE
                        AI.name LIKE AIR.description
                    LIMIT 1
                ) AS account_invoice_refund_type,
                (
                    SELECT
                        AIR.description
                    FROM
                        account_invoice_refund AIR
                    WHERE
                        AI.name LIKE AIR.description
                    LIMIT 1
                ) AS account_invoice_refund_note,
                (
                    SELECT
                        CASE
                            WHEN AIR.date_invoice IS NOT NULL THEN to_char(AIR.date_invoice, 'DD/MM/YYYY')
                            ELSE NULL
                        END
                    FROM
                        account_invoice_refund AIR
                    WHERE
                        AI.name LIKE AIR.description
                    LIMIT 1
                ) AS account_invoice_refund_date,
                (
                    SELECT
                        to_char(AIR.create_date, 'HH24:MI')
                    FROM
                        account_invoice_refund AIR
                    WHERE
                        AI.name LIKE AIR.description
                    LIMIT 1
                ) AS account_invoice_refund_time
            FROM
                account_invoice AI
                INNER JOIN
                    account_invoice AI2
                    ON AI2.id = AI.refund_invoice_id
                        AND AI2.print_status LIKE 'completed'
                        AND AI2.fiscal_printer_invoice_id IS NOT NULL
                        AND AI2.serial_fiscal_printer IS NOT NULL
                INNER JOIN
                    res_partner RP
                    ON RP.id = AI.partner_id
                LEFT JOIN
                    neonety_province NP
                    ON NP.id = RP.province_id
                LEFT JOIN
                    neonety_district ND
                    ON ND.id = RP.district_id
                LEFT JOIN
                    neonety_sector NS
                    ON NS.id = RP.sector_id
            WHERE
                AI.state IN ('open', 'paid')
                AND AI.printer_id IS NOT NULL
                AND AI.print_status LIKE 'pending'
                AND AI.type LIKE 'out_refund'
            ORDER BY
                    id ASC, account_invoice_number ASC""")


class FpiInvoicesRefundPrintMainCompletedListReport(models.Model):
    _name = 'fpi.printer.invoices.refund.print.main.completed.list.report'
    _auto = False
    id = fields.Char(
        string='ID', readonly=True, size=20)
    account_invoice_id = fields.Integer(
        string='ID de la factura', readonly=True)
    account_invoice_number = fields.Char(
        string='Numero de factura', readonly=True, size=50)
    account_invoice_state = fields.Char(
        string='Estado de la factura', readonly=True, size=20)
    account_invoice_print_status = fields.Char(
        string='Estado de la impresión', readonly=True, size=20)
    print_filename_assigned = fields.Char(
        string='Nombre de impresión asignado',
        readonly=True,
        size=20)
    fiscal_printer_invoice_id = fields.Char(
        string='Numero de factura fiscal',
        readonly=True,
        size=20)
    serial_fiscal_printer = fields.Char(
        string='Serial de impresora fiscal',
        readonly=True,
        size=20)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'fpi_printer_invoices_refund_print_main_completed_list_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW fpi_printer_invoices_refund_print_main_completed_list_report AS
            SELECT
                row_number() over() AS id,
                AI.id AS account_invoice_id,
                AI.number AS account_invoice_number,
                AI.state AS account_invoice_state,
                AI.print_status AS account_invoice_print_status,
                AI.print_filename_assigned AS print_filename_assigned,
                AI.fiscal_printer_invoice_id AS fiscal_printer_invoice_id,
                AI.serial_fiscal_printer AS serial_fiscal_printer
            FROM
                account_invoice AI
            WHERE
                AI.state IN ('open', 'paid')
                AND AI.printer_id IS NOT NULL
                AND AI.print_status LIKE 'in_progress'
                AND AI.type LIKE 'out_refund'
            ORDER BY
                    id ASC, account_invoice_number ASC""")


class FpiInvoicesRefundPrintDetailsListReport(models.Model):
    _name = 'fpi.printer.invoices.refund.print.details.list.report'
    _auto = False
    id = fields.Char(
        string='ID', readonly=True, size=20)
    account_invoice_id = fields.Integer(
        string='ID de la factura', readonly=True)
    account_invoice_number = fields.Char(
        string='Numero de factura', readonly=True, size=50)
    product_id = fields.Integer(
        string='ID del producto', readonly=True)
    product_code = fields.Char(
        string='ID del producto', readonly=True, size=50)
    product_code_2 = fields.Char(
        string='ID del producto', readonly=True, size=50)
    product_name = fields.Char(
        string='ID del producto', readonly=True, size=80)
    product_price = fields.Float(
        string='total en pagos', readonly=True)
    account_invoice_line_quantity = fields.Float(
        string='total en pagos', readonly=True)
    unit_type = fields.Char(
        string='ID del producto', readonly=True, size=20)
    group_type = fields.Integer(
        string='Field Label',readonly=True)
    tax_percentage = fields.Float(
        string='total en pagos', readonly=True)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'fpi_printer_invoices_refund_print_details_list_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW fpi_printer_invoices_refund_print_details_list_report AS
            SELECT
                row_number() over() AS id,
                AI.number AS account_invoice_number,
                AIL.invoice_id AS account_invoice_id,
                PP.id AS product_id,
                PT.default_code AS product_code,
                PP.default_code AS product_code_2,
                PT.name AS product_name,
                AIL.price_unit AS product_price,
                AIL.quantity AS account_invoice_line_quantity,
                'UNIDADES' as unit_type,
                2 AS group_type,
                AT.amount AS tax_percentage
            FROM
                account_invoice_line AIL
                INNER JOIN
                    account_invoice AI
                    ON AI.id = AIL.invoice_id
                    AND AI.state IN ('open', 'paid')
                    AND AI.printer_id IS NOT NULL
                    AND AI.print_status LIKE 'pending'
                    AND AI.type LIKE 'out_refund'
                INNER JOIN
                    product_product PP
                    ON PP.id = AIL.product_id
                INNER JOIN
                    product_template PT
                    ON PT.id = PP.product_tmpl_id
                LEFT JOIN
                    account_invoice_line_tax AILT
                    ON AILT.invoice_line_id = AIL.id
                LEFT JOIN
                    account_tax AT
                    ON AT.id = AILT.tax_id""")