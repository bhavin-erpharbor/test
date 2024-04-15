# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

from odoo.addons.mail.controllers.discuss import DiscussController


class DiscussControllerElsner(DiscussController):

    @http.route('/mail/init_messaging', methods=['POST'], type='json', auth='public')
    def mail_init_messaging(self, **kwargs):
        if request.env.user.has_group('ehcs_commission.group_partner_user') \
            or request.env.user.has_group('sales_team.group_sale_salesman'):
            return request.env.user.sudo()._init_messaging()
        else:
            return super(DiscussControllerElsner, self).mail_init_messaging(**kwargs)
