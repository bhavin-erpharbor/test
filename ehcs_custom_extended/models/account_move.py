from odoo import models, fields, api



class AccountMove(models.Model):
    _inherit = 'account.move'

    zoho_id = fields.Char('Zoho Record ID')
    subject = fields.Char('Subject')
    technology_id = fields.Many2one('crm.technology', 'Technology')
    project_type_id = fields.Many2one('sale.order.project.type', 'Project Type')
    move_state_relation = fields.Char('Relation')
    sale_order_relation = fields.Char('Ref.')
    invoice_no = fields.Char('Invoice Number')
    tax = fields.Monetary('Tax', store=True)
    sale_id = fields.Many2one('sale.order', 'Sale')
    team_member_id = fields.Many2one('res.users', 'BA')

    @api.depends('line_ids.sale_line_ids')
    def _compute_origin_so_count(self):
        res = super(AccountMove, self)._compute_origin_so_count()
        if self.sale_order_relation:
            sale_order_id = self.env['sale.order'].search([
                ('zoho_id', '=', self.sale_order_relation)
            ])
            for move in self:
                move.sale_order_count = len(sale_order_id)
        else:
            for move in self:
                sale_orders = self.env['sale.order'].search_count([
                    '|', ('invoice_ids', '=', move.id),
                    ('copy_move_ids', '=', move.id)
                ])
                move.sale_order_count = sale_orders
        return res

    def _must_check_constrains_date_sequence(self):
        return False

    # def _get_unbalanced_moves(self, container):
    #     return False

    def action_view_source_sale_orders(self):
        copy_orders = self.env['sale.order'].search([
            ('copy_move_ids', '=', self.id)
        ])
        result = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')
        if self.sale_order_relation:
            source_orders = self.env['sale.order'].search([
                ('zoho_id', '=', self.sale_order_relation)
            ])
            if len(source_orders) > 1:
                result['domain'] = [('id', 'in', source_orders.ids)]
            elif len(source_orders) == 1:
                result['views'] = [(self.env.ref('sale.view_order_form', False).id, 'form')]
                result['res_id'] = source_orders.id
            else:
                result = {'type': 'ir.actions.act_window_close'}
            return result
        if copy_orders:
            if len(copy_orders) > 1:
                result['domain'] = [('id', 'in', copy_orders.ids)]
            elif len(copy_orders) == 1:
                result['views'] = [(self.env.ref('sale.view_order_form', False).id, 'form')]
                result['res_id'] = copy_orders.id
            else:
                result = {'type': 'ir.actions.act_window_close'}
            return result
        else:
            return super(AccountMove, self).action_view_source_sale_orders()

    def copy(self, default=None):
        res = super(AccountMove, self).copy(default)
        sale_order = self.line_ids.sale_line_ids.order_id or self.sale_id
        sale_order.write({
            'copy_move_ids': [(4, res.id)]
        })
        res.write({'sale_id':sale_order.id})
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    zoho_id = fields.Char('Zoho Record ID')


class AccountTax(models.Model):
    _inherit = 'account.tax'


class ResBank(models.Model):
    _inherit = 'res.bank'

    # zoho_id = fields.Char('Zoho Record ID')
    description = fields.Html('Description')


class ResUsers(models.Model):
    _inherit = 'res.users'

    zoho_id = fields.Char('Zoho Record ID')


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    acc_number = fields.Char(required=False)
    zoho_id = fields.Char('Zoho Record ID')

