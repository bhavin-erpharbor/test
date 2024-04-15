import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from ast import literal_eval
from odoo.addons.auth_signup.models.res_partner import now

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partner_user_id = fields.Many2one('res.users', string='Partner') #, default=lambda self: self.env.user
    # user_id = fields.Many2one(
    #     'res.users', string='Salesperson', default=lambda self: not self.env.user,
    #     domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]",
    #     check_company=True, index=True, tracking=True)
    # source_id = fields.Many2one(ondelete='set null', default = lambda self: self.env.ref('ehcs_commission.utm_source_partner').id)

    def toggle_active(self):
        res = super(CrmLead, self).toggle_active()
        self.write({'lost_feedback': False})
        return res

    def default_get(self, fields):
        res = super(CrmLead, self).default_get(fields)
        if not self.env.user.has_group('sales_team.group_sale_salesman'):
            res['partner_user_id'] = self.env.user
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super(CrmLead, self).create(vals_list=vals_list)
        partner_obj = self.env['res.partner']
        company = False
        for vals in vals_list:
            if vals.get('partner_name'):
                company = partner_obj.search([
                    ('email', '=', vals.get('email_from'))
                ])
                if not company:
                    company = partner_obj.create({
                        'name': vals.get('partner_name'),
                        'partner_user_id': vals.get('partner_user_id'),
                        'email': vals.get('email_from'),
                        'is_company': True
                    })
            contact = partner_obj.search([
                ('email', '=', vals.get('email_from'))
            ])
            if not contact:
                vals = {
                    'name': vals.get('contact_name'),
                    'partner_user_id': vals.get('partner_user_id'),
                    'email': vals.get('email_from'),
                    'street': vals.get('street'),
                    'street2': vals.get('street2'),
                    'city': vals.get('city'),
                    'state_id': vals.get('state_id'),
                    'zip': vals.get('zip'),
                    'country_id': vals.get('country_id'),
                    'parent_id': company and company.id or False
                }
                partner_obj.create(vals)
        group_partner = self.env.user.has_group('ehcs_commission.group_partner_user')
        if group_partner:
            user_ids = literal_eval(self.env['ir.config_parameter'].sudo().get_param('ehcs_commission.user_ids'))
            user_ids = self.env['res.users'].sudo().browse(user_ids)
            emails = []
            for user in user_ids:
                for partner in user.partner_id:
                    if partner.email:
                        emails.append(partner.email)
            email = ','.join(emails)
            template_id = self.env.ref('ehcs_commission.mail_template_creation_crm_lead')
            template_id_user = self.env.ref('ehcs_commission.mail_template_creation_crm_lead_user')
            template_id_user.send_mail(res.id, force_send=True)
            template_id.send_mail(res.id, force_send=True, email_values={'email_to': email})
        return res


    def write(self, vals):
        res = super(CrmLead, self).write(vals=vals)
        if vals.get('stage_id'):
            stage_id = vals.get('stage_id')
            stage = self.env['crm.stage'].browse(stage_id)
            template = self.env.ref('ehcs_commission.mail_template_creation_crm_lead_stage')
            template.with_context(state=stage.name).send_mail(self.id, force_send=True)
        return res


    def _prepare_opportunity_quotation_context(self):
        res = super(CrmLead, self)._prepare_opportunity_quotation_context()
        res.update({
            'default_partner_user_id': self.partner_user_id.id,
            'default_technology_id': self.technology_id.id
        })
        return res


class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get('install_mode', False):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)
        group_partner = self.env.ref('ehcs_commission.group_partner_user')

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if group_partner:
            template = self.env.ref('ehcs_commission.mail_template_creation_partner_user')
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'message_type': 'user_notification',
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            email_values['email_to'] = user.email
            # TDE FIXME: make this template technical (qweb)
            with self.env.cr.savepoint():
                force_send = not(self.env.context.get('import_file', False))
                template.send_mail(user.id, force_send=force_send, raise_exception=True, email_values=email_values)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
