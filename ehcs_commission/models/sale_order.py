from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_user_id = fields.Many2one('res.users', string='Partner', default=lambda self: self.env.user)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.partner_user_id = self.partner_id.partner_user_id

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({
            'partner_user_id': self.partner_user_id.id,
        })
        return res


class ResCompany(models.Model):
    _inherit = 'res.company'

    user_ids = fields.Many2many(comodel_name='res.users', string='Users', required=False)
    partner_ids = fields.Many2many(comodel_name='res.partner', string='Partners CC Email', required=False)
