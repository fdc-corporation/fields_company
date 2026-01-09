from odoo import models, fields, api, Command  
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
    mostrar_url = fields.Boolean(
        string="Mostrar URL del producto",
        defaullt=False,
        help="Indica si se debe mostrar la URL del producto en las líneas de la cotización."
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


    def _create_invoices(self, grouped=False, final=False, date=None):
        if not self.env['account.move'].has_access('create'):
            try:
                self.check_access('write')
            except AccessError:
                return self.env['account.move']

        # 1) Preparar valores de factura
        invoice_vals_list = []
        invoice_item_sequence = 0
        for order in self:
            if order.partner_invoice_id.lang:
                order = order.with_context(lang=order.partner_invoice_id.lang)
            order = order.with_company(order.company_id)

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if all(line.display_type for line in invoiceable_lines):
                continue

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                if not down_payment_section_added and line.is_downpayment:
                    invoice_line_vals.append(
                        Command.create(order._prepare_down_payment_section_line(sequence=invoice_item_sequence)),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1

                optional_values = {'sequence': invoice_item_sequence}
                if line.is_downpayment:
                    optional_values['quantity'] = -1.0
                    optional_values['extra_tax_data'] = self.env['account.tax']._reverse_quantity_base_line_extra_tax_data(line.extra_tax_data)

                for vals in line._prepare_invoice_lines_vals_list(**optional_values):
                    invoice_line_vals.append(Command.create(vals))
                invoice_item_sequence += 1

            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list and self.env.context.get('raise_if_nothing_to_invoice', True):
            raise UserError(self._nothing_to_invoice_error_message())

        # 2) Agrupación
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(invoice_vals_list, key=lambda x: [x.get(k) for k in invoice_grouping_keys])
            for _keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(k) for k in invoice_grouping_keys]):
                ref_invoice_vals = None
                origins, payment_refs, refs = set(), set(), set()
                for inv_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = inv_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += inv_vals['invoice_line_ids']
                    origins.add(inv_vals['invoice_origin'])
                    payment_refs.add(inv_vals['payment_reference'])
                    refs.add(inv_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Crear facturas
        if len(invoice_vals_list) < len(self):
            for invoice in invoice_vals_list:
                seq = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = self.env['sale.order.line']._get_invoice_line_sequence(new=seq, old=line[2]['sequence'])
                    seq += 1

        # --- PUNTO CRÍTICO ---
        moves = self._create_account_invoices(invoice_vals_list, final)
        
        # Validación de seguridad:
        if not moves:
            # Si llegamos aquí, un módulo de terceros está rompiendo el retorno
            return self.env['account.move']

        # 4) Gestión de notas de crédito si el total es negativo
        if final and (moves_to_switch := moves.sudo().filtered(lambda m: m.amount_total < 0)):
            with self.env.protecting([moves._fields['team_id']], moves_to_switch):
                moves_to_switch.action_switch_move_type()
                self.invoice_ids._set_reversed_entry(moves_to_switch)

        for move in moves:
            move.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': move, 'origin': move.line_ids.sale_line_ids.order_id},
                subtype_xmlid='mail.mt_note',
            )
        return moves