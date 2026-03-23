from odoo import fields, models, api, _ 
from datetime import timedelta
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner'


    is_contador = fields.Boolean(string='Es contador', default=False)