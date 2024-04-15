from odoo import api, models, fields, _
from odoo.tools.mail import is_html_empty

from odoo.exceptions import ValidationError
from datetime import date


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    skype = fields.Char('Skype ID')
    twitter = fields.Char('Twitter')
    linkedin = fields.Char('Linkedin')
    lost_feedback = fields.Html(
        'Closing Note', sanitize=True
    )
    technology_id = fields.Many2one('crm.technology', 'Technology')
    user_type_id = fields.Many2one('crm.user.type', 'User Type')
    zoho_id = fields.Char('Zoho Record ID')
    priority = fields.Selection(selection='_get_priority', string='Priority',
                                     compute='_get_priority', readonly=False, store=True, default='low')

    @api.model
    def _get_priority(self):
        selection = [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ]
        return selection

    def action_set_lost(self, **additional_values):
        res = super(CrmLead, self).action_set_lost(**additional_values)
        lost_stages = self._stage_find(domain=[('is_lost', '=', True)], limit=None)
        self.write({'stage_id': lost_stages.id})
        return res

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        res = super(CrmLead, self)._prepare_customer_values(partner_name, is_company=is_company, parent_id=parent_id)
        res.update({
            'user_type_id': self.user_type_id.id,
            'source_id': self.source_id.id,
        })
        return res

    def _get_lead_quotation_domain(self):
        return [('state', 'in', ('draft', 'sent', 'cancel'))]

    def _handle_partner_assignment(self, force_partner_id=False, create_missing=True):
        res = super(CrmLead, self)._handle_partner_assignment(force_partner_id, create_missing)
        for lead in self:
            if lead.partner_id:
                lead.partner_id.write({
                    'user_type_id': self.user_type_id.id,
                    'source_id': self.source_id.id,
                })
        return res

    def send_email_reminder_lead_activities(self):
        activity = self.env['mail.activity'].search([('res_model', '=', 'crm.lead'), ('date_deadline', '=', date.today())])
        lead_activities = self.search([('activity_ids', 'in', activity.ids)])
        for la in lead_activities:
            template = self.env.ref('ehcs_custom_extended.mail_template_creation_crm_lead_reminder_due_activities')
            template.send_mail(la.id, force_send=True)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('email_from'):
                exist_record = self.env['crm.lead'].search([('email_from', '=', vals.get('email_from'))])
                if exist_record:
                    raise ValidationError("This email already exists.")
        return super(CrmLead, self).create(vals_list)

    def write(self, vals):
        if vals.get('email_from'):
            exist_record = self.env['crm.lead'].search([('email_from', '=', vals['email_from'])])
            if exist_record:
                raise ValidationError("This email already exists.")
        return super(CrmLead, self).write(vals)


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    is_lost = fields.Boolean('Is Lost Stage?')


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    state = fields.Selection([
        ('overdue', 'Overdue'),
        ('today', 'Today'),
        ('planned', 'Planned')], 'State',
        compute='_compute_state', store=False)

class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    def action_lost_reason_apply(self):
        self.ensure_one()
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        sale_crm = self.env['sale.order'].search([('opportunity_id', '=', leads.ids)])
        for order in sale_crm:
            order.write({'state': 'cancel'})
        if not is_html_empty(self.lost_feedback):
            leads._track_set_log_message(
                '<div style="margin-bottom: 4px;"><p>%s:</p>%s<br /></div>' % (
                    _('Lost Comment'),
                    self.lost_feedback
                )
            )
        res = leads.action_set_lost(lost_reason_id=self.lost_reason_id.id, lost_feedback=self.lost_feedback)
        return res
