from odoo import models, fields


class CrmTechnology(models.Model):
    _name = 'crm.technology'

    name = fields.Char('Name', required=True)
    commission = fields.Float('Commission(%)')