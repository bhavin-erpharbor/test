from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_user_id = fields.Many2one('res.users', string='Partner')

    # def name_get(self):
    #     res = super(ResPartner, self).name_get()
    #     if self.env.context.get('only_email', True):
    #         for partner in self:
    #             res.append((partner.id, partner.email))
    #     return res

    # def name_get(self):
    #     print("\n\n\n\nhelooooo11111111111o", self)
    #     res = []
    #     if self.env.context.get('only_email'):
    #         for partner in self:
    #             res.append((partner.id, partner.name))
    #         return res
    #         # print("\n\n\n\nheloooooo", self)
    #         # return [(partner.id, partner.email) for partner in self]
    #     return super(ResPartner, self).name_get()