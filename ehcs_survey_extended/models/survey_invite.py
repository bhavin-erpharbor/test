import logging

_logger = logging.getLogger(__name__)

from odoo import models, fields


class SurveyInvite(models.TransientModel):
    _inherit = 'survey.invite'

    def _send_mail(self, answer):
        """ Create mail specific for recipient containing notably its access token """
        subject = self._render_field('subject', answer.ids)[answer.id]
        body = self._render_field('body', answer.ids, post_process=True)[answer.id]
        mail_server = self.env['ir.mail_server'].sudo().search([('active', '=', True)], limit=1).smtp_user
        # post the message
        mail_values = {
            'email_from': mail_server,
            'author_id': self.author_id.id,
            'model': None,
            'res_id': None,
            'subject': subject,
            'body_html': body,
            'attachment_ids': [(4, att.id) for att in self.attachment_ids],
            'auto_delete': True,
        }
        if answer.partner_id:
            mail_values['recipient_ids'] = [(4, answer.partner_id.id)]
        else:
            mail_values['email_to'] = answer.email

            # optional support of default_email_layout_xmlid in context
        email_layout_xmlid = self.env.context.get('default_email_layout_xmlid', self.env.context.get('notif_layout'))
        if email_layout_xmlid:
            template_ctx = {
                'message': self.env['mail.message'].sudo().new(
                    dict(body=mail_values['body_html'], record_name=self.survey_id.title)),
                'model_description': self.env['ir.model']._get('survey.survey').display_name,
                'company': self.env.company,
            }
            body = self.env['ir.qweb']._render(email_layout_xmlid, template_ctx, minimal_qcontext=True,
                                               raise_if_not_found=False)
            if body:
                mail_values['body_html'] = self.env['mail.render.mixin']._replace_local_links(body)
            else:
                _logger.warning(
                    'QWeb template %s not found or is empty when sending survey mails. Sending without layout',
                    email_layout_xmlid)

        return self.env['mail.mail'].sudo().create(mail_values)


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    state = fields.Selection([
        ('new', 'Not started yet'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed')], string='Status', default='in_progress', readonly=True)


