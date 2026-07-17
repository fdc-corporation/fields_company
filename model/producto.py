# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)


class CodeProductTemplate(models.Model):
    _name = "code.product.template"
    _description = "Codigos adicionales de producto"
    _rec_name = "name"

    name = fields.Char(
        string="Codigo",
        required=True,
        index=True,
    )
    product_temp_id = fields.Many2one(
        "product.template",
        string="Producto",
        ondelete="cascade",
    )


class ProductTemplate(models.Model):  # ← nombre correcto
    _inherit = "product.template"     # ← inherit correcto

    n_ref = fields.One2many(
        "code.product.template",
        "product_temp_id",
        string="Codigos de producto",
    )

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=100, name_get_uid=None):
        args = args or []
        _logger.warning(">>> product.template _name_search | name=%s", name)

        if name:
            # Buscar IDs de template por código extra
            codes = self.env["code.product.template"].sudo().search([
                ("name", operator, name)
            ])
            template_ids = codes.mapped("product_temp_id").ids

            search_domain = expression.OR([
                [("name", operator, name)],
                [("default_code", operator, name)],
                [("barcode", operator, name)],
                [("id", "in", template_ids)],   # ← directo, estamos en product.template
            ])
            args = expression.AND([args, search_domain])

        return super()._name_search(
            name="",        # el domain ya contiene la búsqueda por nombre
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )


# Mantener también product.product por si alguna vista usa ese modelo
class ProductProduct(models.Model):   # ← nombre correcto
    _inherit = "product.product"      # ← inherit correcto

    @api.model
    def _name_search(self, name="", args=None, operator="ilike", limit=100, name_get_uid=None):
        args = args or []
        _logger.warning(">>> product.product _name_search | name=%s", name)

        if name:
            codes = self.env["code.product.template"].sudo().search([
                ("name", operator, name)
            ])
            template_ids = codes.mapped("product_temp_id").ids

            extra_ids = []
            if template_ids:
                extra_ids = self.sudo().search([
                    ("product_tmpl_id", "in", template_ids)
                ]).ids

            search_domain = expression.OR([
                [("name", operator, name)],
                [("default_code", operator, name)],
                [("barcode", operator, name)],
                [("product_tmpl_id.name", operator, name)],
                [("id", "in", extra_ids)],
            ])
            args = expression.AND([args, search_domain])

        return super()._name_search(
            name="",
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )