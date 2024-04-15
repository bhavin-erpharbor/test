from odoo import api, models, fields

from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    skype = fields.Char('Skype ID')
    lead_source = fields.Char('Lead Source')
    twitter = fields.Char('Twitter')
    user_type_id = fields.Many2one('crm.user.type', 'User Type')
    technology_id = fields.Many2one('crm.technology', 'Technology')
    source_id = fields.Many2one('utm.source', 'Source')
    home_phone = fields.Char('Home Phone')
    other_phone = fields.Char('Other Phone')
    assistant = fields.Char('Assistant')
    assistant_phone = fields.Char('Asst. Phone')
    linkedin_profile = fields.Char('LinkedIn Profile')
    campaign_id = fields.Many2one('utm.campaign', 'Campaign')
    zoho_id = fields.Char('Zoho Record ID')
    secondary_email_ids = fields.One2many('secondary.email', 'partner_id', 'Secondary Email')

    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        res['user_id'] = self.env.user.id
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('email'):
                exist_record = self.env['res.partner'].search([('email', '=', vals.get('email'))])
                if exist_record:
                    raise ValidationError("This email already exists.")
        return super(ResPartner, self).create(vals_list)

    def write(self, vals):
        if vals.get('email'):
            exist_record = self.env['res.partner'].search([('email', '=', vals.get('email'))])
            if exist_record:
                raise ValidationError("This email already exists.")
        return super(ResPartner, self).write(vals)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    zoho_id = fields.Char('Zoho Record ID')
    priority = fields.Char('Priority')


class MailMessage(models.Model):
    _inherit = 'mail.message'

    zoho_id = fields.Char('Zoho Record ID')


class SecondaryEmail(models.Model):
    _name = "secondary.email"
    _description = "Secondary Email"

    name = fields.Char('Email')
    partner_id = fields.Many2one('res.partner')
