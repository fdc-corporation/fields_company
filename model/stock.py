from odoo import models, api, fields 


class Stock (models.Model):
    _inherit = "stock.picking"


    weight = fields.Float(string="Peso", readonly=False)

class StockMove(models.Model):
    _inherit = "stock.move"

    nota = fields.Text(string="Nota", readonly=False)