from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
from dateutil.relativedelta import relativedelta


class CommissionPayment(models.Model):
    _name = 'commission.payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'partner_user_id'

    name = fields.Char("Name", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    partner_user_id = fields.Many2one('res.users', 'Partner', tracking=True, required=True)
    transaction_id = fields.Char('Transaction Details')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    payment_date = fields.Date(string='Payment Date', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True)
    commission_ids = fields.One2many('commission', 'payment_id', string='Commission Line')

    def send_monthly_payment_of_commission(self):
        today_date = datetime.date.today()
        first = today_date.replace(day=1)
        previous_month_of_first_date = first - relativedelta(days=1)
        previous_month_of_last_date = first - relativedelta(months=1)
        mail_subject = previous_month_of_first_date.strftime("%B %Y")
        cp_obj = self.env['commission.payment']
        commissions_data = self.env['commission'].search([
            ('create_date', '>=', previous_month_of_last_date),
            ('create_date', '<=', previous_month_of_first_date),
            ('state', '!=', 'cancel'),
            ('payment_created', '=', False)
        ])
        invoice_user_data = {}
        for commissions in commissions_data:
            if commissions.partner_user_id.id in invoice_user_data:
                invoice_user_data[commissions.partner_user_id.id] += commissions
            else:
                invoice_user_data[commissions.partner_user_id.id] = commissions
        for key, value in invoice_user_data.items():
            commission_payment = cp_obj.create({
                'partner_user_id': self.env['res.users'].browse(key).id,
            })
            value.update({
                'payment_id': commission_payment.id,
                'payment_created': True
            })
            for cp in commission_payment:
                template = self.env.ref('ehcs_commission.commission_payout_monthly_mail_template')
                template.with_context(mail_subject=mail_subject, commissions=cp.commission_ids).send_mail(cp.id,
                                                                                                    force_send=True)


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('commission.payment.sequence')
        return super(CommissionPayment, self).create(vals)

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_paid(self):
        today_date = datetime.date.today()
        first = today_date.replace(day=1)
        previous_month_of_first_date = first - relativedelta(days=1)
        mail_subject = previous_month_of_first_date.strftime("%B %Y")
        self.write({'state': 'paid', 'payment_date': today_date})
        for commission in self.commission_ids:
            commission.update({'state': 'paid'})
        if len(self.mapped('partner_user_id')) > 1:
            raise UserError("You can't register payments for multiple partner.")
        payout = sum(commission.amount for commission in self.commission_ids)
        for cp in self:
            if cp.partner_user_id:
                template = self.env.ref('ehcs_commission.commission_payout_release_user_mail_template')
                template.with_context(mail_subject=mail_subject, commissions=cp.commission_ids).send_mail(self[0].id, force_send=True)
                user_ids = self.env.company.user_ids
                emails = []
                for user in user_ids:
                    for partner in user.partner_id:
                        if partner.email:
                            emails.append(partner.email)
                email = ','.join(emails)
                admin_template = self.env.ref('ehcs_commission.commission_payout_release_admin_mail_template')
                admin_template.with_context(mail_subject=mail_subject, commissions=cp.commission_ids).send_mail(self[0].id,
                                                                                                   force_send=True,
                                                                                                   email_values={
                                                                                                       'email_to': email})
        form_view_id = self.env.ref("ehcs_commission.wiz_commission_transaction_view").id
        return {
            'name': 'Commission',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.commission.transaction',
            'type': 'ir.actions.act_window',
            'views': [(form_view_id, 'form')],
            'target': 'new',
            'context': {
                'default_payout': payout
            }
        }