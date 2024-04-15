from odoo import api, fields, models, _


class Commission(models.Model):
    _name = 'commission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'move_id'

    name = fields.Char("Name", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    partner_user_id = fields.Many2one('res.users', 'Partner', tracking=True, required=True, default=lambda self: self.env.user)
    move_id = fields.Many2one('account.move', 'Invoice', tracking=True, required=True)
    amount = fields.Float('Amount', tracking=True)
    invoice_date = fields.Date(related='move_id.invoice_date', string='Invoice Date', tracking=True)
    invoice_amount = fields.Float(compute='_compute_amount', string='Invoice Total (excl. tax)', tracking=True)
    partner_id = fields.Many2one(related='move_id.partner_id', string='Customer', tracking=True)
    payment_date = fields.Date(string='Payment Date', tracking=True)
    technology_id = fields.Many2one(related='move_id.technology_id', tracking=True)
    transaction_id = fields.Char('Transaction')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        tracking=True,
    )
    payment_created = fields.Boolean()
    payment_id = fields.Many2one('commission.payment', string='Payment')
    commission_amount = fields.Float(related='technology_id.commission', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True)

    @api.depends('move_id.amount_untaxed')
    def _compute_amount(self):
        for com in self:
            com.invoice_amount = com.move_id.amount_untaxed

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('commission.sequence')
        return super(Commission, self).create(vals)

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})