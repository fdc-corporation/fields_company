import base64

from odoo import fields, models
from odoo.tools import file_open


class AccountMove(models.Model):
    _inherit = "account.move"

    report_top_line = fields.Binary(compute="_compute_report_top_line")

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
