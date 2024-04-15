from odoo import api, models


class Users(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super(Users, self).create(vals_list)
        for user in users:
            # Set login user
            user.partner_id.user_id = user
            user.partner_id.partner_user_id = user
        return users
