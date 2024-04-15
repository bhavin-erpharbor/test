from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    partner_user_id = fields.Many2one('res.users', string='Partner', default=lambda self: self.env.user)
    commission_count = fields.Integer(compute="_compute_commission_count", string='Commission Count')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.partner_user_id = self.partner_id.partner_user_id

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self:
            template = self.env.ref('ehcs_commission.mail_template_creation_account_move')
            template.send_mail(self.id, force_send=True)
        return res

    def _compute_commission_count(self):
        for move in self:
            commission = self.env['commission'].search([('move_id', '=', move.id)])
            move.commission_count = len(commission)

    def action_view_commission(self):
        for move in self:
            commission = self.env['commission'].search([('move_id', '=', move.id)])
            result = self.env['ir.actions.act_window']._for_xml_id('ehcs_commission.action_commission')
            if len(commission) > 1:
                result['domain'] = [('id', 'in', commission.ids)]
            elif len(commission) == 1:
                result['views'] = [(self.env.ref('ehcs_commission.commission_form_view', False).id, 'form')]
                result['res_id'] = commission.id
            else:
                result = {'type': 'ir.actions.act_window_close'}
            return result

    def _compute_payment_state(self):
        res = super(AccountMove, self)._compute_payment_state()
        commission_obj = self.env['commission']
        for invoice in self:
            commission = commission_obj.search([('move_id', '=', invoice.id)], limit=1)
            commission_amount = invoice.technology_id.commission
            amount = (invoice.amount_untaxed * commission_amount) / 100
            if invoice.payment_state == 'paid' and not commission and \
                    invoice.partner_user_id and invoice.partner_user_id.id != 1:
                commission_obj.create({
                    'move_id': invoice.id,
                    'partner_user_id': invoice.partner_user_id.id,
                    'amount': amount,
                    'currency_id': invoice.currency_id.id,
                })
        return res


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self):
        res = super(AccountPaymentRegister, self)._create_payments()
        template = self.env.ref('ehcs_commission.mail_template_paid_invoice')
        for payment in res:
            if payment.reconciled_invoice_ids.payment_state == 'paid':
                emails = self.env.company.partner_ids.mapped('email')
                email = ','.join(emails)
                email_values = {
                    'email_cc': email
                }
                template.send_mail(payment.reconciled_invoice_ids.id, force_send=True, email_values=email_values)
        return res

