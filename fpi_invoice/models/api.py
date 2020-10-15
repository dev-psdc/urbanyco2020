# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools
import logging
_logger = logging.getLogger(__name__)

class FpiApiInvoiceDocumentsPendingList(models.Model):
    _name = 'fpi.invoice.documents.pending.list'
    _auto = False
    position = fields.Integer(string='Field', readonly=True)
    id = fields.Integer(string='Field', readonly=True)
    partner_name = fields.Char(string='Field', readonly=True)
    partner_ruc = fields.Char(string='Field', readonly=True)
    partner_street = fields.Char(string='Field', readonly=True)
    partner_zip = fields.Char(string='Field', readonly=True)
    partner_province = fields.Char(string='Field', readonly=True)
    partner_district = fields.Char(string='Field', readonly=True)
    partner_sector = fields.Char(string='Field', readonly=True)
    partner_country = fields.Char(string='Field', readonly=True)
    invoice_type = fields.Char(string='Field', readonly=True)
    refund_type = fields.Char(string='Field', readonly=True)
    refund_note = fields.Char(string='Field', readonly=True)
    parent_invoice_filename_assigned = fields.Char(string='Field', readonly=True)
    parent_invoice_fiscal_invoice_number = fields.Integer(string='Field', readonly=True)
    parent_invoice_fiscal_printer_serial = fields.Char(string='Field', readonly=True)
    refund_date = fields.Char(string='Field', readonly=True)
    refund_time = fields.Char(string='Field', readonly=True)
    master_filename_assigned = fields.Char(string='Field', readonly=True)
    lines_filename_assigned = fields.Char(string='Field', readonly=True)
    user_login = fields.Char(string='Field', readonly=True)

    #@api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'fpi_invoice_documents_pending_list')
        self._cr.execute("""
            CREATE OR REPLACE VIEW fpi_invoice_documents_pending_list AS
            SELECT
                row_number() over() AS position,
                FD.id AS id,
                FD.partner_name AS partner_name,
                FD.partner_ruc AS partner_ruc,
                FD.partner_street AS partner_street,
                FD.partner_zip AS partner_zip,
                FD.partner_province AS partner_province,
                FD.partner_district AS partner_district,
                FD.partner_sector AS partner_sector,
                FD.partner_country AS partner_country,
                FD.invoice_type AS invoice_type,
                FD.refund_type AS refund_type,
                FD.refund_note AS refund_note,
                FD.parent_invoice_filename_assigned AS parent_invoice_filename_assigned,
                FD.parent_invoice_fiscal_printer_serial AS parent_invoice_fiscal_printer_serial,
                FD.parent_invoice_fiscal_invoice_number AS parent_invoice_fiscal_invoice_number,
                FD.refund_date AS refund_date,
                FD.refund_time AS refund_time,
                FD.master_filename_assigned AS master_filename_assigned,
                FD.lines_filename_assigned AS lines_filename_assigned,
                RU.login AS user_login
            FROM
                fpi_document FD
            INNER JOIN
                account_move AM
                ON AM.id = FD.invoice_id
            INNER JOIN
                res_users RU
                ON RU.id = FD.printer_user_id
            WHERE
                FD.print_status LIKE 'pending'
                AND FD.printer_id IS NOT NULL
                AND FD.documents_type_printed LIKE 'account_move'
                AND AM.state IN ('posted')
                AND FD.fiscal_invoice_number = NULL
            ORDER BY
                FD.create_date""")


# class FpiApiInvoiceLineDocumentsPendingList(models.Model):
#   access_fpi_invoice_line_documents_in_progress_list,fpi.invoice.line.documents.pending.list,model_fpi_invoice_line_documents_pending_list,fpi_invoice_user,1,1,1,1
#     _name = 'fpi.invoice.line.documents.pending.list'
#     _auto = False
#     position = fields.Integer(string='Field', readonly=True)
#     id = fields.Integer(string='Field', readonly=True)
#     fpi_document_id = fields.Integer(string='Field', readonly=True)
#     product_code = fields.Char(string='Field', readonly=True)
#     product_code_2 = fields.Char(string='Field', readonly=True)
#     product_name = fields.Char(string='Field', readonly=True)
#     product_price = fields.Float(string='Field', readonly=True)
#     quantity = fields.Float(string='Field', readonly=True)
#     unit_type = fields.Char(string='Field', readonly=True)
#     group_type = fields.Integer(string='Field', readonly=True)
#     tax_percentage = fields.Float(string='Field', readonly=True)
#     master_filename_assigned = fields.Char(string='Field', readonly=True)
#     lines_filename_assigned = fields.Char(string='Field', readonly=True)
#     user_login = fields.Char(string='Field', readonly=True)

    #@api.model_cr
    # def init(self):
    #     tools.drop_view_if_exists(self._cr, 'fpi_invoice_line_documents_pending_list')
    #     self._cr.execute("""
    #         CREATE OR REPLACE VIEW fpi_invoice_line_documents_pending_list AS
    #         SELECT 
    #             row_number() over() AS position,
    #             AML.id AS id,
    #             FD.id AS fpi_document_id,
    #             PT.default_code AS product_code,
    #             PP.default_code AS product_code_2,
    #             REPLACE(AML.name, '\n', '') AS product_name,
    #             AML.price_unit AS product_price,
    #             AML.quantity AS quantity,
    #             'UNIDADES' as unit_type,
    #             2 AS group_type,
    #             AT.amount AS tax_percentage,
    #             FD.master_filename_assigned AS master_filename_assigned,
    #             FD.lines_filename_assigned AS lines_filename_assigned,
    #             RU.login AS user_login
    #         FROM
    #             account_move_line AML
    #         INNER JOIN
    #             account_move AM
    #             on AM.id = AML.invoice_id
    #         INNER JOIN
    #             fpi_document FD
    #             ON FD.invoice_id = AM.id
    #                 AND FD.print_status LIKE 'pending'
    #                 AND FD.printer_id IS NOT NULL
    #                 AND FD.documents_type_printed LIKE 'account_move'
    #                 AND FD.fiscal_invoice_number = NULL
    #         INNER JOIN
    #             product_product PP
    #             ON PP.id = AML.product_id
    #         INNER JOIN 
    #             product_template PT
    #             ON PT.id = PP.product_tmpl_id
    #         INNER JOIN
    #             res_users RU
    #             ON RU.id = FD.printer_user_id
    #         LEFT JOIN
    #             account_invoice_line_tax AILT
    #             ON AILT.invoice_line_id = AML.id
    #         LEFT JOIN
    #             account_tax AT
    #             ON AT.id = AILT.tax_id""")

