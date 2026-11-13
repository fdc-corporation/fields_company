import base64

from odoo import models, fields
from odoo.tools import file_open


class Stock (models.Model):
    _inherit = "stock.picking"

    weight = fields.Float(string="Peso", readonly=False)
    report_top_line = fields.Binary(compute="_compute_report_top_line")

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

class StockMove(models.Model):
    _inherit = "stock.move"

    nota = fields.Text(string="Nota", readonly=False)
