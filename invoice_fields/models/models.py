# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    is_driver = fields.Boolean('Driver?')


class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    analytic_account_id = fields.Many2one('account.analytic.account')
    driver_id = fields.Many2one('res.partner')

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLineInh, self)._prepare_invoice_line(**optional_values)
        res.update({
            'analytic_account_id': self.analytic_account_id,
            'driver_id': self.driver_id,
        })
        return res

class AccountMoveLineInh(models.Model):
    _inherit = 'account.move.line'

    driver_id = fields.Many2one('res.partner')