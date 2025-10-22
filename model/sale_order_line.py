from odoo import models, fields



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    img_ref = fields.Binary(
        string='Imagen de Referencia',
        help='Imagen del producto para referencia en la cotización.',
        related='product_id.image_1920',
        store=False
    )