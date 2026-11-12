from odoo import models, fields, api



class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    img_ref = fields.Binary(
        string='Imagen de Referencia',
        help='Imagen del producto para referencia en la cotización.',
        related='product_id.image_1920',
        store=False
    )


    @api.model
    def create(self, vals):
        line = super().create(vals)

        if line.id_equipo:
            group = self.env.ref('pmant.group_pmant_planner', raise_if_not_found=False)
            if group:
                user = self.env['res.users'].search([
                    ('group_ids', 'in', group.id),
                    ('share', '=', False),
                ], limit=1) if group else False
            else:
                user = self.env['res.users']

            if user and line.order_id:
                # ✅ agrega al M2M sin borrar los existentes
                line.order_id.write({
                    'asesores': [(4, user.id)]
                })

        return line
