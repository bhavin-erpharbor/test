# -*- coding: utf-8 -*-
from odoo import api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lead_into_oppor_template_id = fields.Many2one('mail.template', string='Lead Into Opportunity',
                                                  config_parameter='ehcs_commission.lead_into_oppor_template_id')
    opportunity_into_quote_template_id = fields.Many2one('mail.template', string='Opportunity Into Quotation',
                                                         config_parameter='ehcs_commission.opportunity_into_quote_template_id')
    quote_into_so_template_id = fields.Many2one('mail.template', string='Quotation Into Sale Order',
                                                config_parameter='ehcs_commission.quote_into_so_template_id')
    user_ids = fields.Many2many(comodel_name='res.users', readonly=False, related='company_id.user_ids', string='Users')
    partner_ids = fields.Many2many(comodel_name='res.partner', readonly=False, related='company_id.partner_ids', string='Partners CC Email')

    # def set_values(self):
    #     res = super(ResConfigSettings, self).set_values()
    #     # self.env['ir.config_parameter'].sudo().set_param('ehcs_commission.user_ids', str(self.user_ids.ids))
    #     self.env['ir.config_parameter'].sudo().set_param('ehcs_commission.partner_ids', str(self.partner_ids.ids))
    #     return res
    #
    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     # user_ids = self.env['ir.config_parameter'].sudo().get_param('ehcs_commission.user_ids')
    #     partner_ids = self.env['ir.config_parameter'].sudo().get_param('ehcs_commission.partner_ids')
    #     # if user_ids:
    #     #     res.update(
    #     #         user_ids=[(6, 0, literal_eval(user_ids))],
    #     #     )
    #     if partner_ids:
    #         res.update(
    #             user_ids=[(6, 0, literal_eval(partner_ids))],
    #         )
    #     return res
