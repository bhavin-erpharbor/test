# -*- coding: utf-8 -*-
import base64
import csv
import io
from datetime import datetime,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

from odoo import fields, models


class WizImportData(models.Model):
    _name = 'wiz.import.data'

    file_name = fields.Binary(string='File')
    model_id = fields.Many2one('ir.model', string='Model')
    is_company = fields.Boolean('Is_company')
    is_sale_order = fields.Boolean('Is Sale Order')

    def import_data(self):
        tag_obj = self.env['crm.tag']
        lost_reason_obj = self.env['crm.lost.reason']
        product_obj = self.env['product.template']
        stage_obj = self.env['crm.stage']
        sale_stage_obj = self.env['sale.stage']
        country_obj = self.env['res.country']
        message_obj = self.env['mail.message']
        state_obj = self.env['res.country.state']
        source_obj = self.env['utm.source']
        users_obj = self.env['res.users']
        techno_obj = self.env['crm.technology']
        user_type_obj = self.env['crm.user.type']
        partner_title_obj = self.env['res.partner.title']
        partner_category_obj = self.env['res.partner.category']
        campaign_obj = self.env['utm.campaign']
        res_partner_industry_obj = self.env['res.partner.industry']
        crm_obj = self.env['crm.lead']
        partner_obj = self.env['res.partner']
        account_payment_obj = self.env['account.payment.term']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        order_obj = self.env['sale.order']
        order_line_obj = self.env['sale.order.line']
        project_type_obj = self.env['sale.order.project.type']
        file = base64.b64decode(self.file_name)
        data = io.StringIO(file.decode("utf-8"))
        csv_reader = csv.reader(data, delimiter=',')
        csv_list = list(csv_reader)
        # Prepare header
        headers_list = []
        for header in csv_list[0]:
            headers_list.append(header)
        if self.model_id.model == 'crm.lead':
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'lead_salesperson_id': headers_list.index('Lead Owner Id'),
                'company_name': headers_list.index('Company'),
                'lname': headers_list.index('Last Name'),
                'fname': headers_list.index('First Name'),
                'name': headers_list.index('Title'),
                'email': headers_list.index('Email'),
                'phone': headers_list.index('Phone'),
                'mobile': headers_list.index('Mobile'),
                'website': headers_list.index('Website'),
                'source': headers_list.index('Lead Source'),
                'lead_status': headers_list.index('Lead Status'),
                'street': headers_list.index('Street'),
                'city': headers_list.index('City'),
                'state_id': headers_list.index('State'),
                'zip': headers_list.index('Zip Code'),
                'country_id': headers_list.index('Country'),
                'description': headers_list.index('Description'),
                'skype': headers_list.index('Skype Id'),
                'twitter': headers_list.index('Twitter'),
                'tag': headers_list.index('Tag'),
                'linkedin': headers_list.index('LinkedIn'),
                'lost_reason': headers_list.index('Lost Reason'),
                'user_type': headers_list.index('Lead Type'),
                'type': headers_list.index('Type'),
                'linkedin_profile': headers_list.index('LinkedIn Profile'),
                'campaign_id': headers_list.index('Campaign'),
                'position': headers_list.index('Job Position'),
            }
            for crm_row in csv_list[1:]:
                campaign_id = False
                source_id = False
                tag_id = False
                state_id = False
                country_id = False
                user_type_id = False
                linkedin = crm_row[headers_dict['linkedin']] or crm_row[headers_dict['linkedin_profile']]
                user_type = crm_row[headers_dict['user_type']] or crm_row[headers_dict['type']]
                lead_salesperson_id = users_obj.search([
                    ('zoho_id', '=', crm_row[headers_dict['lead_salesperson_id']])
                ])
                if lead_salesperson_id.login == 'ubbad@elsner.com':
                    lead_salesperson_id = users_obj.search([
                        ('login', '=', 'ubbad@elsner.com.au')
                    ])
                if crm_row[headers_dict['source']]:
                    source_id = source_obj.search([
                        ('name', '=', crm_row[headers_dict['source']])
                    ])
                    if not source_id:
                        source_id = source_obj.create({
                            'name': crm_row[headers_dict['source']]
                        })
                if crm_row[headers_dict['campaign_id']]:
                    campaign_id = campaign_obj.search([
                        ('name', '=', crm_row[headers_dict['campaign_id']])
                    ])
                    if not campaign_id:
                        campaign_id = campaign_obj.create({
                            'name': crm_row[headers_dict['campaign_id']]
                        })
                if crm_row[headers_dict['country_id']]:
                    country_id = country_obj.search([
                        ('name', '=', crm_row[headers_dict['country_id']])
                    ])
                    if not country_id:
                        country_id = country_obj.create({
                            'name': crm_row[headers_dict['country_id']]
                        })
                if crm_row[headers_dict['state_id']]:
                    state_id = state_obj.search([
                        ('name', '=', crm_row[headers_dict['state_id']])
                    ])
                if crm_row[headers_dict['tag']]:
                    tag_id = tag_obj.search([
                        ('name', '=', crm_row[headers_dict['tag']])
                    ])
                    if not tag_id:
                        tag_id = tag_obj.create({
                            'name': crm_row[headers_dict['tag']]
                        })
                if user_type:
                    user_type_id = user_type_obj.search([
                        ('name', '=', user_type)
                    ])
                    if not user_type_id:
                        user_type_id = user_type_obj.create({
                            'name': user_type
                        })
                stage_id = stage_obj.search([
                    ('name', '=', crm_row[headers_dict['lead_status']])
                ])
                if crm_row[headers_dict['lead_status']] in ('Attempted to Contact', 'Contacted', 'Not Contacted'):
                    stage_id = self.env.ref('crm.stage_lead1')
                if crm_row[headers_dict['lead_status']] == 'Lost Lead':
                    stage_id = self.env.ref('ehcs_custom_extended.stage_lead5')
                if crm_row[headers_dict['lead_status']] == 'Pre-Qualified':
                    stage_id = self.env.ref('crm.stage_lead2')
                existing_partner = partner_obj.search([
                    ('firstname', '=', crm_row[headers_dict['fname']]),
                    ('lastname', '=', crm_row[headers_dict['lname']]),
                    ('email', '=', crm_row[headers_dict['email']])
                ], limit=1)
                if existing_partner:
                    partner = existing_partner
                else:
                    partner = partner_obj.create({
                        'firstname': crm_row[headers_dict['fname']],
                        'lastname': crm_row[headers_dict['lname']],
                        'function': crm_row[headers_dict['position']],
                        'email': crm_row[headers_dict['email']],
                        'phone': crm_row[headers_dict['phone']],
                        'mobile': crm_row[headers_dict['mobile']],
                        'street': crm_row[headers_dict['street']],
                        'city': crm_row[headers_dict['city']],
                        'state_id': state_id and state_id.id or False,
                        'linkedin_profile': linkedin,
                        'country_id': country_id and country_id.id or False,
                        'skype': crm_row[headers_dict['skype']],
                        'twitter': crm_row[headers_dict['twitter']],
                        'zip': crm_row[headers_dict['zip']],
                    })
                existing_lead = crm_obj.search([
                    ('zoho_id', '=', crm_row[headers_dict['zoho_id']])
                ])
                if not existing_lead:
                    leads = crm_obj.create({
                        'zoho_id': crm_row[headers_dict['zoho_id']],
                        'partner_id': partner and partner.id or False,
                        'partner_name': crm_row[headers_dict['company_name']],
                        'name': crm_row[headers_dict['name']],
                        'phone': crm_row[headers_dict['phone']],
                        'mobile': crm_row[headers_dict['mobile']],
                        'website': crm_row[headers_dict['website']],
                        'source_id': source_id and source_id.id or False,
                        'stage_id': stage_id and stage_id.id or False,
                        'street': crm_row[headers_dict['street']],
                        'city': crm_row[headers_dict['city']],
                        'state_id': state_id and state_id.id or False,
                        'user_id': lead_salesperson_id and lead_salesperson_id.id or False,
                        'zip': crm_row[headers_dict['zip']],
                        'country_id': country_id and country_id.id or False,
                        'description': crm_row[headers_dict['description']],
                        'skype': crm_row[headers_dict['skype']],
                        'twitter': crm_row[headers_dict['twitter']],
                        'tag_ids': tag_id and tag_id or False,
                        'linkedin': linkedin,
                        'user_type_id': user_type_id and user_type_id.id or False,
                        'campaign_id': campaign_id and campaign_id.id or False,
                        'function': crm_row[headers_dict['position']]
                    })
                    if crm_row[headers_dict['lead_status']] in ('Lost Lead', 'Lost'):
                        lost_reason_id = lost_reason_obj.search([
                            ('name', '=', crm_row[headers_dict['lost_reason']])
                        ])
                        if not lost_reason_id:
                            lost_reason_id = lost_reason_obj.create({
                                'name': crm_row[headers_dict['lost_reason']]
                            })
                        leads.action_set_lost(lost_reason_id=lost_reason_id.id)
        if self.model_id.model == 'res.partner' and not self.is_company:
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'source': headers_list.index('Lead Source'),
                'lname': headers_list.index('Last Name'),
                'fname': headers_list.index('First Name'),
                'email': headers_list.index('Email'),
                'title': headers_list.index('Title'),
                'tech_id': headers_list.index('Department'),
                'phone': headers_list.index('Phone'),
                'ho_phone': headers_list.index('Home Phone'),
                'other_phone': headers_list.index('Other Phone'),
                'mobile': headers_list.index('Mobile'),
                'assistant': headers_list.index('Assistant'),
                'asst_phone': headers_list.index('Asst Phone'),
                'street': headers_list.index('Mailing Street'),
                'other_street': headers_list.index('Other Street'),
                'city': headers_list.index('Mailing City'),
                'other_city': headers_list.index('Other City'),
                'state_id': headers_list.index('Mailing State'),
                'other_state_id': headers_list.index('Other State'),
                'zip': headers_list.index('Mailing Zip'),
                'other_zip': headers_list.index('Other Zip'),
                'country_id': headers_list.index('Mailing Country'),
                'other_country_id': headers_list.index('Other Country'),
                'description': headers_list.index('Description'),
                'skype': headers_list.index('Skype Id'),
                'twitter': headers_list.index('Twitter'),
                'tag': headers_list.index('Tag'),
                'lk_profile': headers_list.index('LinkedIn Profile'),
                'campaign': headers_list.index('Campaign'),
                'website': headers_list.index('Website'),
                'position': headers_list.index('Job Position'),
                'sales_email': headers_list.index('Salesperson Email'),
                'user_type': headers_list.index('Types'),
                'tax_id': headers_list.index('Tax Id'),
            }
            # Get data from the CSV
            for partner_row in csv_list[1:]:
                campaign_id = False
                source_id = False
                tech_id = False
                user_type_id = False
                title_id = False
                state_id = False
                country_id = False
                tag_id = False
                phone = ''
                if not partner_row[headers_dict['phone']] and partner_row[headers_dict['ho_phone']]:
                    phone = partner_row[headers_dict['ho_phone']]
                if not partner_row[headers_dict['phone']] and not partner_row[headers_dict['ho_phone']] and \
                        partner_row[headers_dict['other_phone']]:
                    phone = partner_row[headers_dict['other_phone']]
                if not partner_row[headers_dict['phone']] and not partner_row[headers_dict['ho_phone']] and not \
                        partner_row[headers_dict['other_phone']] and partner_row[headers_dict['asst_phone']]:
                    phone = partner_row[headers_dict['asst_phone']]
                street = partner_row[headers_dict['street']] or partner_row[headers_dict['other_street']]
                city = partner_row[headers_dict['city']] or partner_row[headers_dict['other_city']]
                state = partner_row[headers_dict['state_id']] or partner_row[headers_dict['other_state_id']]
                country = partner_row[headers_dict['country_id']] or partner_row[headers_dict['other_country_id']]
                zip = partner_row[headers_dict['zip']] or partner_row[headers_dict['other_zip']]
                exist_partner = partner_obj.search([
                    ('zoho_id', '=', partner_row[headers_dict['zoho_id']]),
                ])
                if partner_row[headers_dict['source']]:
                    source_id = source_obj.search([
                        ('name', '=', partner_row[headers_dict['source']])
                    ])
                    if not source_id:
                        source_id = source_obj.create({
                            'name': partner_row[headers_dict['source']]
                        })
                if partner_row[headers_dict['campaign']]:
                    campaign_id = campaign_obj.search([
                        ('name', '=', partner_row[headers_dict['campaign']])
                    ])
                    if not campaign_id:
                        campaign_id = campaign_obj.create({
                            'name': partner_row[headers_dict['campaign']]
                        })
                if partner_row[headers_dict['tag']]:
                    tag_id = partner_category_obj.search([
                        ('name', '=', partner_row[headers_dict['tag']])
                    ])
                    if not tag_id:
                        tag_id = partner_category_obj.create({
                            'name': partner_row[headers_dict['tag']]
                        })
                if partner_row[headers_dict['user_type']]:
                    user_type_id = user_type_obj.search([
                        ('name', '=', partner_row[headers_dict['user_type']])
                    ])
                    if not user_type_id:
                        user_type_id = user_type_obj.create({
                            'name': partner_row[headers_dict['user_type']]
                        })
                if partner_row[headers_dict['tech_id']]:
                    tech_id = techno_obj.search([
                        ('name', '=', partner_row[headers_dict['tech_id']])
                    ])
                    if not tech_id:
                        tech_id = techno_obj.create({
                            'name': partner_row[headers_dict['tech_id']]
                        })
                if partner_row[headers_dict['title']]:
                    title_id = partner_title_obj.search([
                        ('name', '=', partner_row[headers_dict['title']])
                    ])
                    if not title_id:
                        title_id = partner_title_obj.create({
                            'name': partner_row[headers_dict['title']]
                        })
                if country:
                    country_id = country_obj.search([
                        ('name', '=', country)
                    ])
                    if not country_id:
                        country_id = country_obj.create({
                            'name': country
                        })
                if state:
                    state_id = state_obj.search([
                        ('name', '=', state)
                    ])
                users = users_obj.search([
                    ('login', '=', partner_row[headers_dict['sales_email']])
                ])
                if users.login == 'ubbad@elsner.com':
                    users = users_obj.search([
                        ('login', '=', 'ubbad@elsner.com.au')
                    ])
                if not exist_partner:
                    partner_obj.create({
                        'zoho_id': partner_row[headers_dict['zoho_id']],
                        'source_id': source_id and source_id.id or False,
                        'firstname': partner_row[headers_dict['fname']],
                        'lastname': partner_row[headers_dict['lname']],
                        'email': partner_row[headers_dict['email']],
                        'title': title_id and title_id.id or False,
                        'technology_id': tech_id and tech_id.id or False,
                        'phone': partner_row[headers_dict['phone']] if partner_row[headers_dict['phone']] else phone,
                        'home_phone': partner_row[headers_dict['ho_phone']],
                        'other_phone': partner_row[headers_dict['other_phone']],
                        'mobile': partner_row[headers_dict['mobile']],
                        'assistant': partner_row[headers_dict['assistant']],
                        'assistant_phone': partner_row[headers_dict['asst_phone']],
                        'street': street,
                        'city': city,
                        'state_id': state_id and state_id.id or False,
                        'zip': zip,
                        'country_id': country_id and country_id.id or False,
                        'comment': partner_row[headers_dict['description']],
                        'skype': partner_row[headers_dict['skype']],
                        'twitter': partner_row[headers_dict['twitter']],
                        'category_id': tag_id and tag_id or False,
                        'user_type_id': user_type_id and user_type_id.id or False,
                        'linkedin_profile': partner_row[headers_dict['lk_profile']],
                        'campaign_id': campaign_id and campaign_id.id or False,
                        'website': partner_row[headers_dict['website']],
                        'function': partner_row[headers_dict['position']],
                        'vat': partner_row[headers_dict['tax_id']],
                        'user_id': users.id,
                    })
        if self.model_id.model == 'res.partner' and self.is_company:
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'name': headers_list.index('Account Name'),
                'phone': headers_list.index('Phone'),
                'website': headers_list.index('Website'),
                'user_type': headers_list.index('Account Type'),
                'type': headers_list.index('Types'),
                'industry_id': headers_list.index('Industry'),
                'street': headers_list.index('Billing Street'),
                'shipping_street': headers_list.index('Shipping Street'),
                'city': headers_list.index('Billing City'),
                'shipping_city': headers_list.index('Shipping City'),
                'state': headers_list.index('Billing State'),
                'shipping_state': headers_list.index('Shipping State'),
                'zip': headers_list.index('Billing Code'),
                'shipping_zip': headers_list.index('Shipping Code'),
                'country': headers_list.index('Billing Country'),
                'shipping_country': headers_list.index('Shipping Country'),
                'description': headers_list.index('Description'),
                'tag': headers_list.index('Tag'),
                'lk_profile': headers_list.index('LinkedIn Profile'),
                'campaign': headers_list.index('Campaign'),
                'source': headers_list.index('Source'),
                'mobile': headers_list.index('Mobile'),
                'skype': headers_list.index('Skype'),
                'tax_id': headers_list.index('Tax Id'),
                'sales_email': headers_list.index('Salesperson Email'),
                'email': headers_list.index('Email'),
            }
            for company_row in csv_list[1:]:
                campaign_id = False
                source_id = False
                tag_id = False
                state_id = False
                country_id = False
                industry_id = False
                user_type_id = False
                street = company_row[headers_dict['street']] or company_row[headers_dict['shipping_street']]
                city = company_row[headers_dict['city']] or company_row[headers_dict['shipping_city']]
                state = company_row[headers_dict['state']] or company_row[headers_dict['shipping_state']]
                country = company_row[headers_dict['country']] or company_row[headers_dict['shipping_country']]
                zip = company_row[headers_dict['zip']] or company_row[headers_dict['shipping_zip']]
                user_type = company_row[headers_dict['user_type']] or company_row[headers_dict['type']]
                exist_partner = partner_obj.search([
                    ('zoho_id', '=', company_row[headers_dict['zoho_id']]),
                    ('is_company', '=', True),
                ])
                if company_row[headers_dict['source']]:
                    source_id = source_obj.search([
                        ('name', '=', company_row[headers_dict['source']])
                    ])
                    if not source_id:
                        source_id = source_obj.create({
                            'name': company_row[headers_dict['source']]
                        })
                if company_row[headers_dict['campaign']]:
                    campaign_id = campaign_obj.search([
                        ('name', '=', company_row[headers_dict['campaign']])
                    ])
                    if not campaign_id:
                        campaign_id = campaign_obj.create({
                            'name': company_row[headers_dict['campaign']]
                        })
                if company_row[headers_dict['tag']]:
                    tag_id = partner_category_obj.search([
                        ('name', '=', company_row[headers_dict['tag']])
                    ])
                    if not tag_id:
                        tag_id = partner_category_obj.create({
                            'name': company_row[headers_dict['tag']]
                        })
                if user_type:
                    user_type_id = user_type_obj.search([
                        ('name', '=', user_type)
                    ])
                    if not user_type_id:
                        user_type_id = user_type_obj.create({
                            'name': user_type
                        })
                if company_row[headers_dict['industry_id']]:
                    industry_id = res_partner_industry_obj.search([
                        ('name', '=', company_row[headers_dict['industry_id']])
                    ])
                    if not industry_id:
                        industry_id = res_partner_industry_obj.create({
                            'name': company_row[headers_dict['industry_id']]
                        })
                if country:
                    country_id = country_obj.search([
                        ('name', '=', country)
                    ])
                    if not country_id:
                        country_id = country_obj.create({
                            'name': country
                        })
                if state:
                    state_id = state_obj.search([
                        ('name', '=', state)
                    ])
                users = users_obj.search([
                    ('login', '=', company_row[headers_dict['sales_email']])
                ])
                if users.login == 'ubbad@elsner.com':
                    users = users_obj.search([
                        ('login', '=', 'ubbad@elsner.com.au')
                    ])
                if not exist_partner:
                    partner_obj.create({
                        'is_company': True,
                        'zoho_id': company_row[headers_dict['zoho_id']],
                        'name': company_row[headers_dict['name']],
                        'phone': company_row[headers_dict['phone']],
                        'website': company_row[headers_dict['website']],
                        'user_type_id': user_type_id and user_type_id.id or False,
                        'industry_id': industry_id and industry_id.id or False,
                        'street': street,
                        'city': city,
                        'state_id': state_id and state_id.id or False,
                        'zip': zip,
                        'country_id': country_id and country_id.id or False,
                        'comment': company_row[headers_dict['description']],
                        'category_id': tag_id and tag_id or False,
                        'linkedin_profile': company_row[headers_dict['lk_profile']],
                        'campaign_id': campaign_id and campaign_id.id or False,
                        'source_id': source_id and source_id.id or False,
                        'mobile': company_row[headers_dict['mobile']],
                        'skype': company_row[headers_dict['skype']],
                        'vat': company_row[headers_dict['tax_id']],
                        'user_id': users.id,
                        'email': company_row[headers_dict['email']],
                    })
        if self.model_id.model == 'res.users':
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'lname': headers_list.index('Last Name'),
                'fname': headers_list.index('First Name'),
                'email': headers_list.index('Email'),
                'phone': headers_list.index('Phone'),
                'mobile': headers_list.index('Mobile'),
                'website': headers_list.index('Website'),
                'street': headers_list.index('Street'),
                'city': headers_list.index('City'),
                'zip': headers_list.index('Zip Code'),
            }
            for users_row in csv_list[1:]:
                exist_users = users_obj.search([
                    '|',
                    ('zoho_id', '=', users_row[headers_dict['zoho_id']]),
                    ('login', '=', users_row[headers_dict['email']])
                ])
                if exist_users:
                    exist_users.write({
                        'zoho_id': users_row[headers_dict['zoho_id']]
                    })
                else:
                    users = users_obj.create({
                        'zoho_id': users_row[headers_dict['zoho_id']],
                        'firstname': users_row[headers_dict['fname']],
                        'lastname': users_row[headers_dict['lname']],
                        'login': users_row[headers_dict['email']],
                    })
                    if users:
                        exist_partner = partner_obj.search([
                            ('firstname', '=', users_row[headers_dict['fname']]),
                            ('lastname', '=', users_row[headers_dict['lname']]),
                        ])
                        if exist_partner:
                            exist_partner.write({
                                'phone': users_row[headers_dict['phone']],
                                'email': users_row[headers_dict['email']],
                                'mobile': users_row[headers_dict['mobile']],
                                'website': users_row[headers_dict['website']],
                                'street': users_row[headers_dict['street']],
                                'city': users_row[headers_dict['city']],
                                'zip': users_row[headers_dict['zip']]
                            })
        if self.model_id.model == 'mail.message':
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'note': headers_list.index('Note Content'),
                'parent': headers_list.index('Parent Id'),
                'owner_id': headers_list.index('Note Owner Id'),
            }
            for note_row in csv_list[1:]:
                user_id = users_obj.search([
                    ('zoho_id', '=', note_row[headers_dict['owner_id']])
                ])
                lead_lost = crm_obj.search([
                    ('zoho_id', '=', note_row[headers_dict['parent']]),
                    ('active', '=', False)
                ])
                lead = crm_obj.search([
                    ('zoho_id', '=', note_row[headers_dict['parent']])
                ])
                contact = partner_obj.search([
                    ('zoho_id', '=', note_row[headers_dict['parent']])
                ])
                sale = order_obj.search([
                    ('zoho_id', '=', note_row[headers_dict['parent']])
                ])
                move = move_obj.search([
                    ('zoho_id', '=', note_row[headers_dict['parent']])
                ])
                existing_notes = message_obj.search([
                    ('zoho_id', '=', note_row[headers_dict['zoho_id']])
                ])
                if not existing_notes:
                    if lead:
                        message_obj.create({
                            'zoho_id': note_row[headers_dict['zoho_id']],
                            'res_id': lead.id,
                            'model': 'crm.lead',
                            'author_id': user_id.partner_id.id,
                            'body': note_row[headers_dict['note']].replace('\n', '<br/>')
                        })
                    if lead_lost:
                        message_obj.create({
                            'zoho_id': note_row[headers_dict['zoho_id']],
                            'res_id': lead_lost.id,
                            'model': 'crm.lead',
                            'author_id': user_id.partner_id.id,
                            'body': note_row[headers_dict['note']].replace('\n', '<br/>')
                        })
                    if contact:
                        message_obj.create({
                            'zoho_id': note_row[headers_dict['zoho_id']],
                            'res_id': contact.id,
                            'model': 'res.partner',
                            'author_id': user_id.partner_id.id,
                            'body': note_row[headers_dict['note']].replace('\n', '<br/>')
                        })
                    if sale:
                        message_obj.create({
                            'zoho_id': note_row[headers_dict['zoho_id']],
                            'res_id': sale.id,
                            'model': 'sale.order',
                            'author_id': user_id.partner_id.id,
                            'body': note_row[headers_dict['note']].replace('\n', '<br/>')
                        })
                    if move:
                        message_obj.create({
                            'zoho_id': note_row[headers_dict['zoho_id']],
                            'res_id': move.id,
                            'model': 'account.move',
                            'author_id': user_id.partner_id.id,
                            'body': note_row[headers_dict['note']].replace('\n', '<br/>')
                        })
        if self.model_id.model == 'mail.activity':
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'name': headers_list.index('Subject'),
                'date': headers_list.index('Due Date'),
                'related': headers_list.index('Related To'),
                'status': headers_list.index('Status'),
                'description': headers_list.index('Description'),
                'priority': headers_list.index('Priority'),
                'owner_id': headers_list.index('Task Owner Id'),
            }
            for task_row in csv_list[1:]:
                user_id = users_obj.search([
                    ('zoho_id', '=', task_row[headers_dict['owner_id']])
                ])
                task = self.env['mail.activity.type'].search([
                    ('name', '=', task_row[headers_dict['name']])
                ])
                if not task:
                    task = self.env['mail.activity.type'].create({
                        'name': task_row[headers_dict['name']]
                    })
                contact = partner_obj.search([
                    ('zoho_id', '=', task_row[headers_dict['related']])
                ])
                sale = order_obj.search([
                    ('zoho_id', '=', task_row[headers_dict['related']])
                ])
                lead = crm_obj.search([
                    ('zoho_id', '=', task_row[headers_dict['related']])
                ])
                lead_lost = crm_obj.search([
                    ('zoho_id', '=', task_row[headers_dict['related']]),
                    ('active', '=', False)
                ])
                move = move_obj.search([
                    ('zoho_id', '=', task_row[headers_dict['related']])
                ])
                existing_task = self.env['mail.activity'].search([
                    ('zoho_id', '=', task_row[headers_dict['zoho_id']])
                ])
                if not existing_task:
                    if sale:
                        activity = self.env['mail.activity'].create({
                            'zoho_id': task_row[headers_dict['zoho_id']],
                            'activity_type_id': task.id,
                            'date_deadline': datetime.strptime(task_row[headers_dict['date']], '%Y-%m-%d')
                            if task_row[headers_dict['date']] else date.today(),
                            'user_id': user_id.id if user_id else self.env.user.id,
                            'summary': task_row[headers_dict['description']],
                            'res_id': sale.id,
                            'priority': task_row[headers_dict['priority']],
                            'res_model_id': self.env['ir.model']._get_id('sale.order'),
                        })
                        if task_row[headers_dict['status']] == 'Completed':
                            activity.action_done()
                    if contact:
                        activity = self.env['mail.activity'].create({
                            'zoho_id': task_row[headers_dict['zoho_id']],
                            'activity_type_id': task.id,
                            'date_deadline': datetime.strptime(task_row[headers_dict['date']], '%Y-%m-%d')
                            if task_row[headers_dict['date']] else date.today(),
                            'user_id': user_id.id if user_id else self.env.user.id,
                            'summary': task_row[headers_dict['description']],
                            'res_id': contact.id,
                            'priority': task_row[headers_dict['priority']],
                            'res_model_id': self.env['ir.model']._get_id('res.partner'),
                        })
                        if task_row[headers_dict['status']] == 'Completed':
                            activity.action_done()
                    if lead:
                        activity = self.env['mail.activity'].create({
                            'zoho_id': task_row[headers_dict['zoho_id']],
                            'activity_type_id': task.id,
                            'date_deadline': datetime.strptime(task_row[headers_dict['date']], '%Y-%m-%d')
                            if task_row[headers_dict['date']] else date.today(),
                            'user_id': user_id.id if user_id else self.env.user.id,
                            'summary': task_row[headers_dict['description']],
                            'res_id': lead.id,
                            'priority': task_row[headers_dict['priority']],
                            'res_model_id': self.env['ir.model']._get_id('crm.lead'),
                        })
                        if task_row[headers_dict['status']] == 'Completed':
                            activity.action_done()
                    if lead_lost:
                        activity = self.env['mail.activity'].create({
                            'zoho_id': task_row[headers_dict['zoho_id']],
                            'activity_type_id': task.id,
                            'date_deadline': datetime.strptime(task_row[headers_dict['date']], '%Y-%m-%d')
                            if task_row[headers_dict['date']] else date.today(),
                            'user_id': user_id.id if user_id else self.env.user.id,
                            'summary': task_row[headers_dict['description']],
                            'res_id': lead_lost.id,
                            'priority': task_row[headers_dict['priority']],
                            'res_model_id': self.env['ir.model']._get_id('crm.lead'),
                        })
                        if task_row[headers_dict['status']] == 'Completed':
                            activity.action_done()
                    if move:
                        activity = self.env['mail.activity'].create({
                            'zoho_id': task_row[headers_dict['zoho_id']],
                            'activity_type_id': task.id,
                            'date_deadline': datetime.strptime(task_row[headers_dict['date']], '%Y-%m-%d')
                            if task_row[headers_dict['date']] else date.today(),
                            'user_id': user_id.id if user_id else self.env.user.id,
                            'summary': task_row[headers_dict['description']],
                            'res_id': move.id,
                            'priority': task_row[headers_dict['priority']],
                            'res_model_id': self.env['ir.model']._get_id('account.move'),
                        })
                        if task_row[headers_dict['status']] == 'Completed':
                            activity.action_done()


        if self.model_id.model == 'product.template':
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'name': headers_list.index('Product Name')
            }
            for product_row in csv_list[1:]:
                existing_product = product_obj.search([
                    ('zoho_id', '=', product_row[headers_dict['zoho_id']])
                ])
                if not existing_product:
                    product_obj.create({
                        'zoho_id': product_row[headers_dict['zoho_id']],
                        'name': product_row[headers_dict['name']]
                    })
        # if self.model_id.model == 'sale.order' and not self.is_sale_order:
        #     headers_dict = {
        #         'zoho_id': headers_list.index('Record Id'),
        #         'quote_no': headers_list.index('Quote Number'),
        #         'name': headers_list.index('Quote No'),
        #         'contact': headers_list.index('Contact Id'),
        #         'owner_id': headers_list.index('Quote Owner Id'),
        #         'created_id': headers_list.index('Created by Id'),
        #         'tech_id': headers_list.index('Technology'),
        #         'currency_id': headers_list.index('Currency'),
        #         'reason_cancel': headers_list.index('Cancel Reason'),
        #         'stage': headers_list.index('Quote Stage'),
        #         'subject': headers_list.index('Subject'),
        #         'subtotal': headers_list.index('Sub Total'),
        #         'tax': headers_list.index('Tax'),
        #         'grand_total': headers_list.index('Grand Total'),
        #         'discount': headers_list.index('Discount'),
        #         'ba': headers_list.index('Business Analyst'),
        #         'payment_term_id': headers_list.index('Payment Terms'),
        #         'type_id': headers_list.index('Closer Type'),
        #         'note': headers_list.index('Terms and Conditions'),
        #     }
        #     for order_row in csv_list[1:]:
        #         payment = False
        #         tech_id = False
        #         project_type = False
        #         stage_id = False
        #         partner = partner_obj.search([
        #             ('zoho_id', '=', order_row[headers_dict['contact']])
        #         ])
        #         if not partner:
        #             partner = partner_obj.create({
        #                 'name': 'Dummy Partner'
        #             })
        #         currency_id = self.env['res.currency'].search([
        #             ('name', '=', order_row[headers_dict['currency_id']])
        #         ])
        #         print("\n\n\n\n::;currency",currency_id,currency_id.name)
        #         order = order_obj.search([
        #             ('zoho_id', '=', order_row[headers_dict['zoho_id']])
        #         ])
        #         if order:
        #             order.user_id = False
        #             quote_salesperson_id = users_obj.search([
        #                 ('zoho_id', '=', order_row[headers_dict['created_id']])
        #             ])
        #             if quote_salesperson_id.login == 'ubbad@elsner.com':
        #                 quote_salesperson_id = users_obj.search([
        #                     ('login', '=', 'ubbad@elsner.com.au')
        #                 ])
        #             order.write({'user_id': quote_salesperson_id.id})
        #         if order_row[headers_dict['payment_term_id']]:
        #             payment = account_payment_obj.search([
        #                 ('name', '=', order_row[headers_dict['payment_term_id']])
        #             ])
        #             if not payment:
        #                 payment = account_payment_obj.create({
        #                     'name': order_row[headers_dict['payment_term_id']]
        #                 })
        #         if order_row[headers_dict['tech_id']]:
        #             tech_id = techno_obj.search([
        #                 ('name', '=', order_row[headers_dict['tech_id']])
        #             ])
        #             if not tech_id:
        #                 tech_id = techno_obj.create({
        #                     'name': order_row[headers_dict['tech_id']]
        #                 })
        #         if order_row[headers_dict['type_id']]:
        #             project_type = project_type_obj.search([
        #                 ('name', '=', order_row[headers_dict['type_id']])
        #             ])
        #             if not project_type:
        #                 project_type = project_type_obj.create({
        #                     'name': order_row[headers_dict['type_id']]
        #                 })
        #         if order_row[headers_dict['stage']]:
        #             stage_id = sale_stage_obj.search([
        #                 ('name', '=', order_row[headers_dict['stage']])
        #             ])
        #             if not stage_id:
        #                 stage_id = sale_stage_obj.create({
        #                     'name': order_row[headers_dict['stage']]
        #                 })
        #         quote_salesperson_id = users_obj.search([
        #             ('zoho_id', '=', order_row[headers_dict['owner_id']])
        #         ])
        #         if quote_salesperson_id.login == 'ubbad@elsner.com':
        #             quote_salesperson_id = users_obj.search([
        #                 ('login', '=', 'ubbad@elsner.com.au')
        #             ])
        #         existing_order = order_obj.search([
        #             ('zoho_id', '=', order_row[headers_dict['zoho_id']])
        #         ])
        #         if not existing_order:
        #             order_obj.create({
        #                 'zoho_id': order_row[headers_dict['zoho_id']],
        #                 'quote_no': order_row[headers_dict['quote_no']],
        #                 'name': order_row[headers_dict['name']],
        #                 'partner_id': partner and partner.id,
        #                 'currency_id': currency_id.id,
        #                 'technology_id': tech_id and tech_id.id or False,
        #                 'project_type_id': project_type and project_type.id or False,
        #                 'subject': order_row[headers_dict['subject']],
        #                 'user_id': quote_salesperson_id and quote_salesperson_id.id,
        #                 'reason_cancel': order_row[headers_dict['reason_cancel']],
        #                 'state': 'draft',
        #                 'stage_id': stage_id and stage_id.id or False,
        #                 'payment_term_id': payment and payment.id or False,
        #                 'note': order_row[headers_dict['note']]
        #             })
        if self.model_id.model == 'sale.order.line' and not self.is_sale_order:
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'parent': headers_list.index('Parent Id'),
                'product': headers_list.index('Product Id'),
                'description': headers_list.index('Description'),
                'quantity': headers_list.index('Quantity'),
                'amount': headers_list.index('Amount'),
                'unit_price': headers_list.index('List Price'),
                'subtotal': headers_list.index('Total After Discount'),
                'discount': headers_list.index('Discount'),
                'tax': headers_list.index('Tax(%)'),
                'total': headers_list.index('Total'),
            }
            for order_line_row in csv_list[1:]:
                product = product_obj.search([
                    ('zoho_id', '=', order_line_row[headers_dict['product']])
                ])
                order = order_obj.search([
                    ('zoho_id', '=', order_line_row[headers_dict['parent']])
                ])
                existing_line = order_line_obj.search([
                    ('zoho_id', '=', order_line_row[headers_dict['zoho_id']])
                ])
                account_tax = self.env['account.tax'].search([('amount', '=', order_line_row[headers_dict['tax']])],
                                                             limit=1)
                if not existing_line:
                    order_line_obj.create({
                        'zoho_id': order_line_row[headers_dict['zoho_id']],
                        'product_id': product.product_variant_id.id,
                        'name': order_line_row[headers_dict['description']],
                        'product_uom_qty': order_line_row[headers_dict['quantity']],
                        'price_unit': order_line_row[headers_dict['unit_price']],
                        'tax_id': [(6, 0, account_tax.ids)],
                        'order_id': order.id,
                    })
        # if self.model_id.model == 'sale.order' and self.is_sale_order:
        #     headers_dict = {
        #         'zoho_id': headers_list.index('Record Id'),
        #         'so_no': headers_list.index('SO Number'),
        #         'name': headers_list.index('SO No'),
        #         'name_so': headers_list.index('Odoo SO Number'),
        #         'contact': headers_list.index('Contact Id'),
        #         'owner_id': headers_list.index('Sales Order Owner Id'),
        #         'created_id': headers_list.index('Created by Id'),
        #         'tech_id': headers_list.index('Technology'),
        #         'reason_cancel': headers_list.index('Cancel Reason'),
        #         'stage': headers_list.index('Status'),
        #         'subject': headers_list.index('Subject'),
        #         'subtotal': headers_list.index('Sub Total'),
        #         'tax': headers_list.index('Tax'),
        #         'grand_total': headers_list.index('Grand Total'),
        #         'discount': headers_list.index('Discount'),
        #         'ba': headers_list.index('Business Analyst'),
        #         'payment_term_id': headers_list.index('Payment Terms'),
        #         'type_id': headers_list.index('Closer Type'),
        #         'note': headers_list.index('Terms and Conditions'),
        #     }
        #     for order_row in csv_list[1:]:
        #         payment = False
        #         tech_id = False
        #         project_type = False
        #         stage_id = False
        #         partner = partner_obj.search([
        #             ('zoho_id', '=', order_row[headers_dict['contact']])
        #         ])
        #         if not partner:
        #             partner = partner_obj.create({
        #                 'name': 'Dummy Partner'
        #             })
        #         order = order_obj.search([
        #             ('zoho_id', '=', order_row[headers_dict['zoho_id']])
        #         ])
        #         if order:
        #             order.user_id = False
        #             sale_salesperson_id = users_obj.search([
        #                 ('zoho_id', '=', order_row[headers_dict['created_id']])
        #             ])
        #             if sale_salesperson_id.login == 'ubbad@elsner.com':
        #                 sale_salesperson_id = users_obj.search([
        #                     ('login', '=', 'ubbad@elsner.com.au')
        #                 ])
        #             order.write({'user_id': sale_salesperson_id.id})
        #         if order_row[headers_dict['payment_term_id']]:
        #             payment = account_payment_obj.search([
        #                 ('name', '=', order_row[headers_dict['payment_term_id']])
        #             ])
        #             if not payment:
        #                 payment = account_payment_obj.create({
        #                     'name': order_row[headers_dict['payment_term_id']]
        #                 })
        #         if order_row[headers_dict['tech_id']]:
        #             tech_id = techno_obj.search([
        #                 ('name', '=', order_row[headers_dict['tech_id']])
        #             ])
        #             if not tech_id:
        #                 tech_id = techno_obj.create({
        #                     'name': order_row[headers_dict['tech_id']]
        #                 })
        #         if order_row[headers_dict['type_id']]:
        #             project_type = project_type_obj.search([
        #                 ('name', '=', order_row[headers_dict['type_id']])
        #             ])
        #             if not project_type:
        #                 project_type = project_type_obj.create({
        #                     'name': order_row[headers_dict['type_id']]
        #                 })
        #         if order_row[headers_dict['stage']]:
        #             stage_id = sale_stage_obj.search([
        #                 ('name', '=', order_row[headers_dict['stage']])
        #             ])
        #             if not stage_id:
        #                 stage_id = sale_stage_obj.create({
        #                     'name': order_row[headers_dict['stage']]
        #                 })
        #         sale_salesperson_id = users_obj.search([
        #             ('zoho_id', '=', order_row[headers_dict['owner_id']])
        #         ])
        #         if sale_salesperson_id.login == 'ubbad@elsner.com':
        #             sale_salesperson_id = users_obj.search([
        #                 ('login', '=', 'ubbad@elsner.com.au')
        #             ])
        #         existing_order = order_obj.search([
        #             ('zoho_id', '=', order_row[headers_dict['zoho_id']])
        #         ])
        #         if not existing_order:
        #             order_obj.create({
        #                 'zoho_id': order_row[headers_dict['zoho_id']],
        #                 'so_no': order_row[headers_dict['so_no']],
        #                 'name': order_row[headers_dict['name']] or order_row[headers_dict['name_so']],
        #                 'partner_id': partner and partner.id,
        #                 'currency_id': self.env.company.currency_id.id,
        #                 'technology_id': tech_id and tech_id.id or False,
        #                 'project_type_id': project_type and project_type.id or False,
        #                 'subject': order_row[headers_dict['subject']],
        #                 'user_id': sale_salesperson_id and sale_salesperson_id.id,
        #                 'reason_cancel': order_row[headers_dict['reason_cancel']],
        #                 'stage_id': stage_id and stage_id.id or False,
        #                 'payment_term_id': payment and payment.id or False,
        #                 'note': order_row[headers_dict['note']]
        #             }).action_confirm()
        if self.model_id.model == 'sale.order.line' and self.is_sale_order:
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'parent': headers_list.index('Parent Id'),
                'product': headers_list.index('Product Id'),
                'description': headers_list.index('Description'),
                'quantity': headers_list.index('Quantity'),
                'amount': headers_list.index('Amount'),
                'discount': headers_list.index('Discount'),
                'unit_price': headers_list.index('List Price'),
                'subtotal': headers_list.index('Total After Discount'),
                'tax': headers_list.index('Tax(%)'),
                'total': headers_list.index('Total'),
            }
            for order_line_row in csv_list[1:]:
                product = product_obj.search([
                    ('zoho_id', '=', order_line_row[headers_dict['product']])
                ])
                order = order_obj.search([
                    ('zoho_id', '=', order_line_row[headers_dict['parent']])
                ])
                account_tax = self.env['account.tax'].search([('amount', '=', order_line_row[headers_dict['tax']])],
                                                             limit=1)
                existing_line = order_line_obj.search([
                    ('zoho_id', '=', order_line_row[headers_dict['zoho_id']])
                ])
                if not existing_line:
                    order_line_obj.create({
                        'zoho_id': order_line_row[headers_dict['zoho_id']],
                        'product_id': product.product_variant_id.id,
                        'name': order_line_row[headers_dict['description']],
                        'product_uom_qty': order_line_row[headers_dict['quantity']],
                        'price_unit': order_line_row[headers_dict['unit_price']],
                        'tax_id': [(6, 0, account_tax.ids)],
                        'order_id': order.id,
                    })

        # if self.model_id.model == 'account.move':
        #     headers_dict = {
        #         'zoho_id': headers_list.index('Record Id'),
        #         'currency': headers_list.index('Currency'),
        #     }
        #     for invoice_row in csv_list[1:]:
        #         exist_invoices = move_obj.search([
        #             ('zoho_id', '=', invoice_row[headers_dict['zoho_id']])
        #         ])
        #         currency_id = self.env['res.currency'].search([
        #             ('name', '=', invoice_row[headers_dict['currency']])
        #         ])
        #         if invoice_row[headers_dict['currency']] != 'USD':
        #             if exist_invoices.payment_state == 'paid':
        #                 payment = exist_invoices.invoice_payments_widget.get('content')[0].get('account_payment_id')
        #                 self.env['account.payment'].browse(payment).action_cancel()
        #                 exist_invoices.button_draft()
        #                 exist_invoices.write({'currency_id': currency_id.id})
        #                 if exist_invoices.move_state_relation == 'Paid':
        #                     exist_invoices.action_post()
        #                     register_obj = self.env['account.payment.register']
        #                     payment_vals_list = {
        #                         'payment_type': 'inbound',
        #                         'partner_type': 'customer',
        #                         'partner_id': exist_invoices.partner_id.id,
        #                         'amount': exist_invoices.amount_total,
        #                         'payment_date': exist_invoices.invoice_date,
        #                     }
        #                     register_obj.with_context(active_model='account.move', active_ids=exist_invoices.ids). \
        #                         create(payment_vals_list).action_create_payments()
        #             else:
        #                 exist_invoices.write({'currency_id': currency_id.id})


        if self.model_id.model == 'sale.order':
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'currency_id': headers_list.index('Currency')
            }
            for order_row in csv_list[1:]:
                existing_order = order_obj.search([
                    ('zoho_id', '=', order_row[headers_dict['zoho_id']])
                ])
                pricelist = self.env['product.pricelist'].search([
                    ('currency_id', '=', order_row[headers_dict['currency_id']])
                ])
                if order_row[headers_dict['currency_id']] != 'USD':
                    if existing_order and pricelist:
                        existing_order.write({'pricelist_id': pricelist.id})




        # if self.model_id.model == 'account.move':
        #     headers_dict = {
        #         'zoho_id': headers_list.index('Record Id'),
        #         'tax': headers_list.index('Tax'),
        #     }
        #     for invoice_row in csv_list[1:]:
        #         exist_invoices = move_obj.search([
        #             ('zoho_id', '=', invoice_row[headers_dict['zoho_id']])
        #         ])
        #         if exist_invoices:
        #             if exist_invoices.payment_state == 'paid':
        #                 payment = exist_invoices.invoice_payments_widget.get('content')[0].get('account_payment_id')
        #                 self.env['account.payment'].browse(payment).action_cancel()
        #                 exist_invoices.button_draft()
        #                 product_id = self.env.ref('ehcs_wiz_import_data.product_product_zoho')
        #                 zoho_tax = exist_invoices.invoice_line_ids.filtered(lambda line: line.product_id == product_id)
        #                 zoho_t = exist_invoices.line_ids.filtered(lambda line: line.name == 'Zoho Tax')
        #                 if len(zoho_tax) > 1:
        #                     # zoho_tax[-1].unlink()
        #                     zoho_t[-1].unlink()
        #                 if exist_invoices.move_state_relation == 'Paid':
        #                     exist_invoices.action_post()
        #                     register_obj = self.env['account.payment.register']
        #                     payment_vals_list = {
        #                         'payment_type': 'inbound',
        #                         'partner_type': 'customer',
        #                         'partner_id': exist_invoices.partner_id.id,
        #                         'amount': exist_invoices.amount_total,
        #                         'payment_date': exist_invoices.invoice_date,
        #                     }
        #                     register_obj.with_context(active_model='account.move', active_ids=exist_invoices.ids). \
        #                         create(payment_vals_list).action_create_payments()
        #             else:
        #                 if exist_invoices.state == 'posted':
        #                     exist_invoices.button_draft()
        #                     product_id = self.env.ref('ehcs_wiz_import_data.product_product_zoho')
        #                     zoho_tax = exist_invoices.invoice_line_ids.filtered(lambda line: line.product_id == product_id)
        #                     zoho_t = exist_invoices.line_ids.filtered(lambda line: line.name == 'Zoho Tax')
        #                     if len(zoho_tax) > 1:
        #                         # zoho_tax[-1].unlink()
        #                         zoho_t[-1].unlink()
        #                     exist_invoices.action_post()
        #                 else:
        #                     product_id = self.env.ref('ehcs_wiz_import_data.product_product_zoho')
        #                     zoho_tax = exist_invoices.invoice_line_ids.filtered(
        #                         lambda line: line.product_id == product_id)
        #                     zoho_t = exist_invoices.line_ids.filtered(lambda line: line.name == 'Zoho Tax')
        #                     if len(zoho_tax) > 1:
        #                         # zoho_tax[-1].unlink()
        #                         zoho_t[-1].unlink()





        # if self.model_id.model == 'account.move':
        #     headers_dict = {
        #         'zoho_id': headers_list.index('Record Id'),
        #         'tax': headers_list.index('Tax'),
        #     }
        #     for invoice_row in csv_list[1:]:
        #         exist_invoices = move_obj.search([
        #             ('zoho_id', '=', invoice_row[headers_dict['zoho_id']])
        #         ])
        #         if exist_invoices:
        #             if exist_invoices.payment_state == 'paid' and float(invoice_row[headers_dict['tax']]) > 0:
        #                 payment = exist_invoices.invoice_payments_widget.get('content')[0].get('account_payment_id')
        #                 self.env['account.payment'].browse(payment).action_cancel()
        #                 exist_invoices.button_draft()
        #                 if float(invoice_row[headers_dict['tax']]) > 0:
        #                     exist_invoices.write({'invoice_line_ids': [(0, 0, {
        #                             'product_id': self.env.ref('ehcs_wiz_import_data.product_product_zoho').id,
        #                             'quantity': 1,
        #                             'tax_ids': False,
        #                             'price_unit': invoice_row[headers_dict['tax']],
        #                         })],})
        #                 if exist_invoices.move_state_relation == 'Paid':
        #                     exist_invoices.action_post()
        #                     register_obj = self.env['account.payment.register']
        #                     payment_vals_list = {
        #                         'payment_type': 'inbound',
        #                         'partner_type': 'customer',
        #                         'partner_id': exist_invoices.partner_id.id,
        #                         'amount': exist_invoices.amount_total,
        #                         'payment_date': exist_invoices.invoice_date,
        #                     }
        #                     register_obj.with_context(active_model='account.move', active_ids=exist_invoices.ids). \
        #                         create(payment_vals_list).action_create_payments()
        #             else:
        #                 if float(invoice_row[headers_dict['tax']]) > 0:
        #                     exist_invoices.write({'invoice_line_ids': [(0, 0, {
        #                         'product_id': self.env.ref('ehcs_wiz_import_data.product_product_zoho').id,
        #                         'quantity': 1,
        #                         'tax_ids': False,
        #                         'price_unit': invoice_row[headers_dict['tax']],
        #                     })], })

        # if self.model_id.model == 'account.move':
        #     headers_dict = {
        #         'zoho_id': headers_list.index('Record Id'),
        #         'invoice_no': headers_list.index('Invoice Number'),
        #         'sale_order_id': headers_list.index('Sales Order Id'),
        #         'subject': headers_list.index('Subject'),
        #         'name': headers_list.index('Invoice No'),
        #         'contact': headers_list.index('Contact Id'),
        #         'state': headers_list.index('Status'),
        #         'currency': headers_list.index('Currency'),
        #         'invoice_date': headers_list.index('Invoice Date'),
        #         'invoice_date_due': headers_list.index('Due Date'),
        #         'narration': headers_list.index('Terms and Conditions'),
        #         'payment_reference': headers_list.index('Payment Reference'),
        #         'tech_id': headers_list.index('Technology'),
        #         'tax': headers_list.index('Tax'),
        #         'type_id': headers_list.index('Closer Type'),
        #         'owner_id': headers_list.index('Created by Id'),
        #         'payment_term_id': headers_list.index('Payment Terms'),
        #         'method_id': headers_list.index('Payment Method Id'),
        #     }
        #     for invoice_row in csv_list[1:]:
        #         tech_id = False
        #         project_type = False
        #         payment = False
        #         partner = partner_obj.search([
        #             ('zoho_id', '=', invoice_row[headers_dict['contact']])
        #         ])
        #         exist_invoice = move_obj.search([
        #             ('zoho_id', '=', invoice_row[headers_dict['zoho_id']])
        #         ])
        #         if exist_invoice:
        #             partner_bank = self.env['res.partner.bank'].search([
        #                 ('zoho_id', '=', invoice_row[headers_dict['method_id']])
        #             ])
        #             exist_invoice.write({'partner_bank_id': partner_bank.id})
        #         # currency_id = self.env['res.currency'].search([
        #         #     ('name', '=', invoice_row[headers_dict['currency']])
        #         # ])
        #         if invoice_row[headers_dict['tech_id']]:
        #             tech_id = techno_obj.search([
        #                 ('name', '=', invoice_row[headers_dict['tech_id']])
        #             ])
        #             if not tech_id:
        #                 tech_id = techno_obj.create({
        #                     'name': invoice_row[headers_dict['tech_id']]
        #                 })
        #         if invoice_row[headers_dict['type_id']]:
        #             project_type = project_type_obj.search([
        #                 ('name', '=', invoice_row[headers_dict['type_id']])
        #             ])
        #             if not project_type:
        #                 project_type = project_type_obj.create({
        #                     'name': invoice_row[headers_dict['type_id']]
        #                 })
        #         if invoice_row[headers_dict['payment_term_id']]:
        #             payment = account_payment_obj.search([
        #                 ('name', '=', invoice_row[headers_dict['payment_term_id']])
        #             ])
        #             if not payment:
        #                 payment = account_payment_obj.create({
        #                     'name': invoice_row[headers_dict['payment_term_id']]
        #                 })
        #         account_salesperson_id = users_obj.search([
        #             ('zoho_id', '=', invoice_row[headers_dict['owner_id']])
        #         ])
        #         if account_salesperson_id.login == 'ubbad@elsner.com':
        #             account_salesperson_id = users_obj.search([
        #                 ('login', '=', 'ubbad@elsner.com.au')
        #             ])
        #         existing_invoice = move_obj.search([
        #             ('zoho_id', '=', invoice_row[headers_dict['zoho_id']])
        #         ])
        #         if not existing_invoice:
        #             move_obj.create({
        #                 'zoho_id': invoice_row[headers_dict['zoho_id']],
        #                 'sale_order_relation': invoice_row[headers_dict['sale_order_id']],
        #                 'invoice_no': invoice_row[headers_dict['invoice_no']],
        #                 'name': invoice_row[headers_dict['name']],
        #                 'move_type': 'out_invoice',
        #                 'partner_id': partner.id,
        #                 # 'currency_id': currency_id.id,
        #                 'invoice_date': datetime.strptime(invoice_row[headers_dict['invoice_date']], '%Y-%m-%d') if invoice_row[headers_dict['invoice_date']]
        #                 else date.today(),
        #                 'invoice_date_due': datetime.strptime(invoice_row[headers_dict['invoice_date_due']], '%Y-%m-%d') if invoice_row[headers_dict['invoice_date_due']]
        #                 else date.today(),
        #                 'narration': invoice_row[headers_dict['narration']].replace('\n', '<br/>'),
        #                 'move_state_relation': invoice_row[headers_dict['state']],
        #                 'subject': invoice_row[headers_dict['subject']],
        #                 'technology_id': tech_id and tech_id.id or False,
        #                 'project_type_id': project_type and project_type.id or False,
        #                 'invoice_payment_term_id': payment and payment.id or False,
        #                 'invoice_user_id': account_salesperson_id and account_salesperson_id.id or False,
        #                 'payment_reference': invoice_row[headers_dict['payment_reference']],
        #             })
        if self.model_id.model == 'account.move.line':
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'parent': headers_list.index('Parent Id'),
                'product': headers_list.index('Product Id'),
                'description': headers_list.index('Description'),
                'quantity': headers_list.index('Quantity'),
                'discount': headers_list.index('Discount'),
                'tax': headers_list.index('Tax(%)'),
                'unit_price': headers_list.index('List Price'),
            }
            moves_list = []
            for invoice_line_row in csv_list[1:]:
                product = product_obj.search([
                    ('zoho_id', '=', invoice_line_row[headers_dict['product']])
                ])
                account_tax = self.env['account.tax'].search([('amount', '=', invoice_line_row[headers_dict['tax']])],
                                                             limit=1)
                move = move_obj.search([
                    ('zoho_id', '=', invoice_line_row[headers_dict['parent']])
                ])
                moves_list.append(move)
                existing_line = move_line_obj.search([
                    ('zoho_id', '=', invoice_line_row[headers_dict['zoho_id']])
                ])
                if move:
                    if not existing_line:
                        move_line_obj.create({
                            'zoho_id': invoice_line_row[headers_dict['zoho_id']],
                            'product_id': product.product_variant_id.id,
                            'name': invoice_line_row[headers_dict['description']],
                            'quantity': invoice_line_row[headers_dict['quantity']],
                            'price_unit': invoice_line_row[headers_dict['unit_price']],
                            'move_id': move.id,
                            'tax_ids': [(6, 0, account_tax.ids)],
                        })
            moves_list = list(set(moves_list))
            for move in moves_list:
                if move.move_state_relation == 'Open':
                    move.action_post()
                if move.move_state_relation == 'Cancelled':
                    move.button_cancel()
                if move.move_state_relation == 'Paid':
                    move.action_post()
                    register_obj = self.env['account.payment.register']
                    payment_vals_list = {
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': move.partner_id.id,
                        'amount': move.amount_total,
                        'payment_date': move.invoice_date,
                    }
                    register_obj.with_context(active_model='account.move', active_ids=move.ids). \
                        create(payment_vals_list).action_create_payments()
        if self.model_id.model == 'res.partner.bank':
            headers_dict = {
                'zoho_id': headers_list.index('Record Id'),
                'name': headers_list.index('Vendor Name'),
                'phone': headers_list.index('Phone'),
                'email': headers_list.index('Email'),
                'description': headers_list.index('Description'),
                'street': headers_list.index('Street'),
                'city': headers_list.index('City'),
                'country': headers_list.index('Country'),
                'state': headers_list.index('State'),
                'zip': headers_list.index('Zip Code'),
            }
            for payment_row in csv_list[1:]:
                # country_id = False
                # state_id = False
                # if payment_row[headers_dict['country']]:
                #     country_id = country_obj.search([
                #         ('name', '=', payment_row[headers_dict['country']])
                #     ])
                #     if not country_id:
                #         country_id = country_obj.create({
                #             'name': payment_row[headers_dict['country']]
                #         })
                # if payment_row[headers_dict['state']]:
                #     state_id = state_obj.search([
                #         ('name', '=', payment_row[headers_dict['state']])
                #     ])
                bank_id = self.env['res.bank'].create({
                    'name': payment_row[headers_dict['name']],
                    'description': payment_row[headers_dict['description']].replace('\n', '<br/>'),
                })
                existing_payment = self.env['res.partner.bank'].search([
                    ('zoho_id', '=', payment_row[headers_dict['zoho_id']])
                ])
                if not existing_payment:
                    self.env['res.partner.bank'].create({
                        'zoho_id': payment_row[headers_dict['zoho_id']],
                        'partner_id': self.env.company.partner_id.id,
                        # 'name': payment_row[headers_dict['name']],
                        # 'phone': payment_row[headers_dict['phone']],
                        # 'email': payment_row[headers_dict['email']],
                        # 'street': payment_row[headers_dict['street']],
                        # 'city': payment_row[headers_dict['city']],
                        # 'state': state_id and state_id.id or False,
                        # 'country': country_id and country_id.id or False,
                        # 'zip': payment_row[headers_dict['zip']],
                        # 'description': payment_row[headers_dict['description']].replace('\n', '<br/>'),
                        'bank_id': bank_id.id,
                    })

