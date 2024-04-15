from odoo import models, fields


class CrmUserType(models.Model):
    _name = 'crm.user.type'

    name = fields.Char('Name', required=True)