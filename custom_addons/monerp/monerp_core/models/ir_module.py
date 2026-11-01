# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def update_list(self):
        res = super(IrModuleModule, self).update_list()
        to_buy = self.sudo().search([('to_buy', '=', True)])
        if to_buy:
            to_buy.unlink()
        return res

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        domain = domain or []
        if not any(isinstance(arg, (list, tuple)) and arg[0] == 'to_buy' for arg in domain):
            domain = [('to_buy', '=', False)] + list(domain)
        return super(IrModuleModule, self)._search(domain, offset=offset, limit=limit, order=order, **kwargs)
