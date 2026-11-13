import base64

from odoo import models, fields, api
from odoo.tools import file_open


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
    mostrar_url = fields.Boolean(
        string="Mostrar URL del producto",
        default=False,
        help="Indica si se debe mostrar la URL del producto en las líneas de la cotización."
    )
    partner_id = fields.Many2one(domain="[('parent_id', '==', False)]")
    partner_shipping_id = fields.Many2one(domain="[('parent_id', '==', partner_id)]")
    report_top_line = fields.Binary(compute='_compute_report_assets')
    report_logo_storage = fields.Binary(compute='_compute_report_assets')
    report_logo_chicago = fields.Binary(compute='_compute_report_assets')
    report_logo_pneumatech = fields.Binary(compute='_compute_report_assets')

    def _compute_report_assets(self):
        asset_files = {
            'report_top_line': 'fdc-top-line.png',
            'report_logo_storage': 'storage-compat.png',
            'report_logo_chicago': 'chicago-pneumatic.png',
            'report_logo_pneumatech': 'pneumatech.png',
        }
        values = {}
        for field_name, filename in asset_files.items():
            with file_open(
                f'fields_company/static/src/img/report/{filename}', 'rb'
            ) as asset:
                values[field_name] = base64.b64encode(asset.read())
        for record in self:
            for field_name, value in values.items():
                record[field_name] = value

    @api.model
    def create(self, vals):
        res = super().create(vals)
        for record in res:
            user = self.env.user

            # Buscar el gerente del usuario actual
            empleado = self.env["hr.employee"].sudo().search([("user_id", "=", user.id)], limit=1)
            gerente = empleado.parent_id.user_id if empleado else False

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
