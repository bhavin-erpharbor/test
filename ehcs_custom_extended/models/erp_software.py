from odoo import models, fields


class ErpSoftware(models.Model):
    _inherit = 'res.partner'

    
    crm = fields.Selection([
        ('zoho','Zoho'),
        ('salesforce','Salesforce'),
        ('hubspot','Hubspot'),
        ('clickup','Clickup'),
        ('sap','SAP'),
        ('other','Other')],string="CRM")

    erp = fields.Selection([
        ('zoho','Zoho'),
        ('sap','SAP'),
        ('acumatica','Acumatica'),
        ('certinia','Certinia'),
        ('odoo','Odoo'),
        ('sage x3','Sage x3'),
        ('deltek','Deltek'),
        ('other','Other')],string="ERP")

    email_marketing = fields.Selection([
        ('klavio','Klavio'),
        ('mailchimp','Mailchimp'),
        ('dotdigital','Dotdigital'),
        ('zoho campaign','Zoho Campaign'),
        ('campaign monitor','Campaign Monitor'),
        ('other','Other')],string="Email marketing")

    accounting_software = fields.Selection([
        ('zoho_books', 'Zoho Books'),
        ('quickbook','Quickbook'),
        ('xero','Xero'),
        ('freshbooks','Freshbooks'),
        ('tally','Tally'),
        ('other','Other')],string="Accounting Software")

    crm_name = fields.Char("CRM Name")
    erp_name = fields.Char("ERP Name")
    email_marketing_name = fields.Char("Email Marketing Name")
    accounting_software_name = fields.Char("Accounting software Name")
