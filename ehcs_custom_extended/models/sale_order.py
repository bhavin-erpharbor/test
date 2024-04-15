from odoo import models, fields, api

READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'sale', 'done', 'cancel'}
}

LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    subject = fields.Char('Subject')
    reason_cancel = fields.Char('Cancel Reason')
    team_member_id = fields.Many2one('res.users', 'BA')
    technology_id = fields.Many2one('crm.technology', 'Technology', required=True)
    stage_id = fields.Many2one('sale.stage', 'Stage')
    project_type_id = fields.Many2one('sale.order.project.type', 'Project Type', required=True)
    quote_no = fields.Char('Quote Number')
    so_no = fields.Char('SO Number')
    zoho_id = fields.Char('Zoho Record ID')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=False, readonly=False, change_default=True, index=True,
        tracking=1,
        states=READONLY_FIELD_STATES,
        domain="[('type', '!=', 'private'), ('company_id', 'in', (False, company_id))]")
    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_partner_invoice_id',
        store=True, readonly=False, required=False, precompute=True,
        states=LOCKED_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery Address",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False, required=False, precompute=True,
        states=LOCKED_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True, required=False,  # Unrequired company
        states=READONLY_FIELD_STATES,
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")
    copy_move_ids = fields.Many2many('account.move', copy=False)

    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        res = super(SaleOrder, self)._get_invoiced()
        if self.zoho_id:
            invoices = self.env['account.move'].search([
                ('sale_order_relation', '=', self.zoho_id)
            ])
            for order in self:
                order.invoice_ids = invoices
                order.invoice_count = len(invoices)
        else:
            for order in self:
                invoices = order.invoice_ids + order.copy_move_ids
                order.invoice_ids = invoices
                order.invoice_count = len(order.invoice_ids)
        return res

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({
            'technology_id': self.technology_id.id,
            'project_type_id': self.project_type_id.id,
            'team_member_id': self.team_member_id.id,
        })
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    zoho_id = fields.Char('Zoho Record ID')


class SaleStage(models.Model):
    _name = 'sale.stage'

    name = fields.Char('Name', required=1)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    zoho_id = fields.Char('Zoho Record ID')


class SaleOrderProjectType(models.Model):
    _name = 'sale.order.project.type'

    name = fields.Char('Name', required=True)

