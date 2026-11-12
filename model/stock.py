from odoo import models, api, fields 


class Stock (models.Model):
    _inherit = "stock.picking"

    weight = fields.Float(string="Peso", readonly=False)
    tarea_id = fields.Many2one(
        "tarea.mantenimiento",
        string="Tarea de mantenimiento",
        ondelete="set null",
        help="Compatibilidad con las vistas logísticas de pmant.",
    )
    len_tarea = fields.Integer(
        string="Número de tareas",
        compute="_compute_len_tarea",
    )
    is_requerimiento = fields.Boolean(
        string="¿Es un requerimiento de repuesto?",
        default=False,
    )
    is_devolucion_repuesto = fields.Boolean(
        string="¿Es una devolución de repuesto?",
        default=False,
    )

    @api.depends("tarea_id")
    def _compute_len_tarea(self):
        for record in self:
            record.len_tarea = 1 if record.tarea_id else 0

    def action_view_tarea(self):
        self.ensure_one()
        if not self.tarea_id:
            return False
        return {
            "name": "Tarea de mantenimiento",
            "type": "ir.actions.act_window",
            "res_model": "tarea.mantenimiento",
            "view_mode": "form",
            "res_id": self.tarea_id.id,
        }

class StockMove(models.Model):
    _inherit = "stock.move"

    nota = fields.Text(string="Nota", readonly=False)


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    tarea_id = fields.Many2one(
        "tarea.mantenimiento",
        string="Tarea de mantenimiento",
        ondelete="set null",
        help="Compatibilidad con las vistas logísticas de pmant.",
    )
