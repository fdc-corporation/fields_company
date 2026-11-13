import base64

from odoo import fields, models
from odoo.tools import file_open


class AccountMove(models.Model):
    _inherit = "account.move"

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
        for move in self:
            move.report_top_line = top_line

    def _compute_report_qr_sunat(self):
        barcode_service = self.env["ir.actions.report"]
        for move in self:
            qr_image = False
            try:
                extra_values = move._l10n_pe_edi_get_extra_report_values()
                qr_value = extra_values and extra_values.get("qr_str")
                if qr_value:
                    qr_image = base64.b64encode(
                        barcode_service.barcode(
                            "QR", qr_value, width=300, height=300, quiet=0
                        )
                    )
            except Exception:
                qr_image = False
            move.report_qr_sunat = qr_image
