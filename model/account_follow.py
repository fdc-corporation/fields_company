from odoo import fields, models, api, _, Command
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


# =========================================================
# FOLLOWUP REPORT (AUTOMÁTICO)
# =========================================================
class AccountFollowupReport(models.AbstractModel):
    _inherit = 'account.followup.report'
    _description = "Follow-up Report"

    @api.model
    def _get_email_from(self, options):
        partner = self.env['res.partner'].browse(options.get('partner_id'))

        if options.get('email_from'):
            followup_email_from = options['email_from']
        else:
            followup_line = options.get('followup_line') or partner.followup_line_id
            mail_template = options.get('mail_template') or followup_line.mail_template_id
            followup_email_from = mail_template.email_from

        rendered_email = self.env['mail.composer.mixin'].sudo()._render_template(
            followup_email_from, 'res.partner', [partner.id]
        )[partner.id] or None

        return rendered_email

    @api.model
    def _get_email_recipients(self, options):
        """
        SOLO contactos contadores
        """
        partner = self.env['res.partner'].browse(options.get('partner_id'))

        contactos_factura = self.env['res.partner'].search([
            ('parent_id', '=', partner.id),
            ('is_contador', '=', True),
            ('email', '!=', False)
        ])

        _logger.info("==== FOLLOWUP _get_email_recipients ====")
        _logger.info(f"Partner: {partner.name}")
        _logger.info(f"Contadores: {contactos_factura.mapped('email')}")

        return contactos_factura

    @api.model
    def _send_email(self, options):
        """
        ENVÍO REAL → SOLO CONTADORES
        """
        partner = self.env['res.partner'].browse(options.get('partner_id'))
        followup_line = options.get('followup_line', partner.followup_line_id)

        contactos_factura = self.env['res.partner'].search([
            ('parent_id', '=', partner.id),
            ('is_contador', '=', True),
            ('email', '!=', False)
        ])

        if not contactos_factura:
            raise UserError(_(
                "El cliente '%s' no tiene contactos contadores con email.",
                partner.name
            ))

        # 🔥 CORREOS REALES
        emails = [c.email.strip() for c in contactos_factura if c.email]
        email_to = ",".join(emails)

        _logger.info(f"DESTINATARIOS: {email_to}")

        self = self.with_context(lang=partner.lang or self.env.user.lang)

        body_html = self.with_context(mail=True).get_followup_report_html(options)
        attachment_ids = options.get('attachment_ids')
        author_id = options.get(
            'author_id',
            partner._get_followup_responsible().partner_id.id
        )

        # 🔥 ENVÍO CONTROLADO
        partner.with_context(
            mail_post_autofollow=False,
            lang=partner.lang or self.env.user.lang
        ).message_post(
            partner_ids=[],  # ❌ evitar followers
            email_to=email_to,  # ✅ destino real
            author_id=author_id,
            email_from=self._get_email_from(options),
            body=body_html,
            subject=self._get_email_subject(options),
            reply_to=self._get_email_reply_to(options),
            model_description=_('payment reminder'),
            notify_author=False,
            email_layout_xmlid='mail.mail_notification_light',
            attachment_ids=attachment_ids,
            subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'),
        )

        # (Opcional) suscribir contadores
        partner.message_subscribe(contactos_factura.ids)

        if followup_line and followup_line.additional_follower_ids:
            partner.message_subscribe(
                followup_line.additional_follower_ids.partner_id.ids
            )


# =========================================================
# WIZARD MANUAL (SEND & PRINT)
# =========================================================
class AccountFollowupManualReminder(models.TransientModel):
    _inherit = 'account_followup.manual_reminder'

    @api.depends('template_id', 'partner_id')
    def _compute_email_recipient_ids(self):
        for wizard in self:
            partner = wizard.partner_id

            contactos_factura = self.env['res.partner'].search([
                ('parent_id', '=', partner.id),
                ('is_contador', '=', True),
                ('email', '!=', False)
            ])

            _logger.info("==== WIZARD DESTINATARIOS ====")
            _logger.info(f"Partner: {partner.name}")
            _logger.info(f"Contadores: {contactos_factura.mapped('email')}")

            if contactos_factura:
                wizard.email_recipient_ids = contactos_factura  # ✅ CORRECTO
            else:
                wizard.email_recipient_ids = partner