from odoo import fields, models


class WizCommissionTransaction(models.TransientModel):
    _name = 'wiz.commission.transaction'

    payout = fields.Float('Payout')
    transaction_id = fields.Char('Transaction Details')

    def action_submit(self):
        active_id = self._context.get('active_ids')
        commission_payment = self.env['commission.payment'].browse(active_id)
        commission_payment.write({'transaction_id': self.transaction_id})
        return True