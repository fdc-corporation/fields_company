from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    asesores = fields.Many2many(
        'res.users',
        string='Asesores',
        help='Usuarios que actúan como asesores en la venta.',
        tracking=True
    )
    mostrar_descuento = fields.Boolean(
        string='Mostrar Descuento',
        default=True,
        help='Indica si se debe mostrar el campo de descuento en las líneas de la cotización.'
    )
    mostrar_codigo = fields.Boolean(
        string='Mostrar Código de Producto',
        default=True,
        help='Indica si se debe mostrar el campo de código de producto en las líneas de la cotización.'
    )
    mostrar_img_producto = fields.Boolean(
        string='Mostrar Imagen de Producto',
        default=False,
        help='Indica si se debe mostrar la imagen del producto en las líneas de la cotización.'
    )


    @api.model
    def create(self, vals):
        res = super().create(vals)
        for record in res:
            print("EJECUCIÓN DE MÉTODO CREATE EN SALE ORDER")

            user = self.env.user
            print("USUARIO ACTUAL:", user.name)

            # Buscar el gerente del usuario actual
            empleado = self.env["hr.employee"].sudo().search([("user_id", "=", user.id)], limit=1)
            gerente = empleado.parent_id.user_id if empleado else False

            print("GERENTE ENCONTRADO:", gerente.name if gerente else "No se encontró gerente")

            if gerente:
                # Asignar el gerente como asesor
                record.asesores = [(4, gerente.id)]

        return res

    def write(self, vals):
        res = super().write(vals)
        if 'asesores' in vals:
            for record in self:
                for asesor in record.asesores:
                    record.message_post(
                        body=f"El asesor {asesor.name} fue asignado a esta cotización.",
                        partner_ids=[asesor.partner_id.id],
                        subtype_xmlid='mail.mt_comment',
                    )
        return res