# -*- coding: utf-8 -*-
from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    notification_type = fields.Selection([
        ('email', 'Par e-mails'),
        ('inbox', 'Dans VEID'),
    ], string="Notification", required=True, default='email')
