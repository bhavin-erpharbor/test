from odoo import api, models


class Users(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        print("\n\n\ntest::::::::::::;;;")
        jjdfsdjfjsdkf
        users = super(Users, self).create(vals_list)
        dhsjdiosdjsoid
        for user in users:
            jjsdjksk
            # Set login user
            user.partner_id.user_id = user
            user.partner_id.partner_user_id = user
        return users
