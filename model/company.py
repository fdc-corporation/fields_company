from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    icono_document = fields.Binary(
        string='Icono de Documento',
        help='Icono personalizado para documentos de la empresa.'
    )

