# -*- coding: utf-8 -*-
from odoo import fields, models

import base64

from odoo.http import request


class RedirectLink(models.TransientModel):
    _name = 'redirect.link'
    _description = 'Redict To Link'

    def action_redict_to_link(self):
        """redict to link"""
        url = "https://estimationtool.elsnerdev.com/sso/"
        user = self.env.user
        login_str = user.login+'|'+user.name+'|'+'Elsner23'
        # Convert into bytes
        login_str_bytes = login_str.encode("ascii")  
        base64_bytes = base64.b64encode(login_str_bytes)
        base64_string = base64_bytes.decode("ascii")
        # added bytes in url
        url_return = url + '%s/'% base64_string
        return {
            'type': 'ir.actions.act_url',
            'url':  url_return
        }
