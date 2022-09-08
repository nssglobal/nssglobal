# -*- coding: utf-8 -*-

from odoo import models, fields, api


class arga_transport(models.Model):
    _name = 'app.data'
    _description = 'App data import'

    provider_name = fields.Char("Provider Name")
    provider_phone = fields.Char("Provider Phone No.")
    user_name = fields.Char("User Name")
    user_phone = fields.Char("User Phone No.")
    service = fields.Char("Services")
    segment = fields.Char("Segment")
    price_type = fields.Char("Price Type")
    service_date = fields.Char("Service Date")
    booking_date = fields.Char("Booking Date")
    payment_method = fields.Char("Payment Method")
    cart_amount = fields.Char("Cart Amount")
    tax = fields.Char("Tax")
    bill = fields.Char("Minimum Booking Bill")
    amount_paid = fields.Char("Final Amount Paid")
    driver_earning = fields.Char("Driver Earning")
    merchant_earning = fields.Char("Merchant Earning")
    service_area = fields.Char("Service Area")
    status = fields.Char("Status")
    drop_location = fields.Char("Drop Location")

