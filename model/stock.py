from odoo import models, api, fields 


class Stock (models.Model):
    _inherit = "stock.picking"


    weight = fields.Float(string="Peso", readonly=False)