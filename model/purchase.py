import base64

from odoo import fields, models
from odoo.tools import file_open


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    report_top_line = fields.Binary(
        compute="_compute_report_top_line",
        string="Franja superior del reporte",
    )

    def _compute_report_top_line(self):
        asset_path = "fields_company/static/src/img/report/fdc-top-line.png"
        try:
            with file_open(asset_path, "rb") as asset_file:
                encoded_asset = base64.b64encode(asset_file.read())
        except (FileNotFoundError, OSError):
            encoded_asset = False

        for order in self:
            order.report_top_line = encoded_asset
