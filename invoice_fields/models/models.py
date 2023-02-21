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


class SaleReportInh(models.Model):
    _inherit = "sale.report"

    driver_id = fields.Many2one('res.partner', string="Driver", readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['driver_id'] = ", l.driver_id as driver_id"
        groupby += ', l.driver_id'
        return super(SaleReportInh, self)._query(with_clause, fields, groupby, from_clause)


class AccountMoveLineInh(models.Model):
    _inherit = 'account.move.line'

    driver_id = fields.Many2one('res.partner')


class AccountInvoiceReportInh(models.Model):
    _inherit = "account.invoice.report"

    driver_id = fields.Many2one('res.partner')

    def _select(self):
        return super(AccountInvoiceReportInh, self)._select() + ", line.driver_id as driver_id"

    def _group_by(self):
        return super(AccountInvoiceReportInh, self)._group_by() + ", line.driver_id"