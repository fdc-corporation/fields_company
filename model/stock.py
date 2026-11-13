import base64

from odoo import models, fields
from odoo.tools import file_open


class Stock (models.Model):
    _inherit = "stock.picking"

    weight = fields.Float(string="Peso", readonly=False)
    report_top_line = fields.Binary(compute="_compute_report_top_line")
    report_qr_sunat = fields.Binary(compute="_compute_report_qr_sunat")

    def _compute_report_top_line(self):
        try:
            with file_open(
                "fields_company/static/src/img/report/fdc-top-line.png", "rb"
            ) as asset_file:
                top_line = base64.b64encode(asset_file.read())
        except (FileNotFoundError, OSError):
            top_line = False
        for picking in self:
            picking.report_top_line = top_line

    def _compute_report_qr_sunat(self):
        barcode_service = self.env["ir.actions.report"]
        for picking in self:
            qr_image = False
            try:
                qr_value = picking._l10n_pe_edi_get_qr()
                if qr_value:
                    qr_image = base64.b64encode(
                        barcode_service.barcode(
                            "QR", qr_value, width=300, height=300, quiet=0
                        )
                    )
            except Exception:
                qr_image = False
            picking.report_qr_sunat = qr_image

class StockMove(models.Model):
    _inherit = "stock.move"

    nota = fields.Text(string="Nota", readonly=False)
