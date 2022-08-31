import requests
import json
from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, UserError
import json
import datetime
from datetime import datetime,timedelta

import pytz
# from pickle import TRUE


class ResourceInfo(models.Model):
    _inherit ='resource.resource'

    mobile_no=fields.Char('Mobile no')
    email= fields.Char('Email')
    phone_no = fields.Char('Phone') 
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

class ServiceNote(models.Model):
    _name ="service.note"
    
    name = fields.Char('Service' , required=True)
    name_ar = fields.Char('Service AR')
    
    resource_emp_id = fields.Many2one("resource.resource", string="Employee") 
    service_line_ids = fields.One2many("service.line" ,'service_id')
 
    
class ServiceLine(models.Model):
    _name ="service.line"
    _rec_name ="product_id"
    service_id = fields.Many2one('service.note' ,string='Service')
    product_id = fields.Many2one("product.product",string='Sub Service' ,required=True)
    price = fields.Float(string="Price",related="product_id.lst_price")
    
    
    
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s : %s' % (rec.product_id.name, str(rec.price))))
        return res

class PlanningSlotService(models.Model):
    _inherit = 'planning.slot'
    
    partner_id = fields.Many2one('res.partner' ,string="Customer")
    service_id = fields.Many2one('service.note' ,string="Service")
    sub_service_id =fields.Many2one('service.line' ,string="Sub service")
    sub_service_ids =fields.Many2many('service.line' ,string="Sub service")
    status = fields.Selection([('available', 'Available'),
                              ('not_available', 'Not Available'),
                              ], string='Status' ,compute='getStatus' ,store=True ,readonly = True)
    
    
    
    
    def planning_whatsapp(self):
        if self.env.context.get('to_customer',False) == True:
            record_phone = self.partner_id.mobile
        else:
            if self.env.context.get('to_resource',False) == True:
                record_phone = self.resource_id.mobile_no    
        if not record_phone:
            view = self.env.ref('odoo_whatsapp_integration.warn_message_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = "Please add a mobile number!"
            return {
                'name': 'Mobile Number Field Empty',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'display.error.message',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }
        if not record_phone[0] == "+":
            view = self.env.ref('odoo_whatsapp_integration.warn_message_wizard')
            view_id = view and view.id or False
            context = dict(self._context or {})
            context['message'] = "No Country Code! Please add a valid mobile number along with country code!"
            return {
                'name': 'Invalid Mobile Number',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'display.error.message',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': context
            }
        else:
            if self.env.context.get('to_customer',False) == True:
                return {'type': 'ir.actions.act_window',
                        'name': _('Whatsapp Message'),
                        'res_model': 'whatsapp.wizard',
                        'target': 'new',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'context': {
                            'default_template_id': self.env.ref('odoo_whatsapp_integration.whatsapp_planning_sale_template').id},
                        }
    
    
            if self.env.context.get('to_resource',False) == True:
                # return {'type': 'ir.actions.act_window',
                #         'name': _('Whatsapp Message'),
                #         'res_model': 'whatsapp.wizard',
                #         'target': 'new',
                #         'view_mode': 'form',
                #         'view_type': 'form',
                #         'context': {
                #             'default_template_id': self.env.ref('odoo_whatsapp_integration.whatsapp_planning_resource_template').id},
                #         }
    
                return {
                        'type': 'ir.actions.act_window',
                        'name': _('Whatsapp Message to Resource'),
                        'view_id': self.env.ref('odoo_whatsapp_integration.whatsapp_wizard_resource', False).id,
                        'target': 'new',
                        'res_model': 'whatsapp.wizard',
                        'view_mode': 'form',
                         'view_type': 'form',
                        'context': {
                            'default_template_id': self.env.ref('odoo_whatsapp_integration.whatsapp_planning_resource_template').id},
                        }
                   

    
    
    
    @api.model_create_multi
    def create(self, vals_list):
        res= super(PlanningSlotService, self).create(vals_list)
        if res.partner_id and res.sub_service_ids:
            so=res.createSO(res.id)
            res.actionEmailtoResource()
        return res
    
    
    
    
    
    
    def actionEmailtoResource(self):
        if self.resource_id.email and self.sale_order_id:
            mail_content = "  Hello  *" + self.resource_id.name + "* ,<br>Address :" + str(self.partner_id.street)+ "," + str(self.partner_id.street2) + "<br>" +str(self.partner_id.city)+", "+str(self.partner_id.country_id.name)"<br> <br> Phone:"+\
                            str(self.partner_id.phone) +"<br>Mobile :" +str(self.partner_id.mobile)+"<br>Email :" +str(self.partner_id.email)
            mail_content +=  '<br>Sale Order Number *'+str(self.sale_order_id.name) +'* with amount' + str(self.sale_order_id.amount_total)+str(self.sale_order_id.currency_id.symbol) +'* is confirmed.'
            mail_content += '<div>  Your quotation date and time is' + str(self.sale_order_id.date_order.strftime("%d-%m-%Y")) +"</div>"
            mail_content += '<div> Quotation details are as follows: <br>'
            for li in self.sale_order_id.order_line:
                mail_content += '*Product :' + li.product_id.name +'* <br>'
                mail_content += '*Qty :' + str(li.product_uom_qty) +'* <br>'
                mail_content += '*Price :' + str(li.price_subtotal) +'* <br> </div>'
            mail_content += '<div> If you have any questions, please feel free to contact us.</div>'
            email_values = {
                'body_html': mail_content,
                'subject': "sale order info to resource ",
                'email_from': self.env.user.company_id.email,
                'email_to': self.resource_id.email,
            }
            mail = self.env['mail.mail'].sudo().create(email_values).send()

     
    def action_send(self):
        res = super(PlanningSlotService ,self).action_send()
        # if self.partner_id and self.sub_service_id:
        #     self.createSO(self.id)
        return res
     
    def convert_time_zone(self,time):
        utc_date = pytz.utc.localize(time)

        new_date = utc_date.astimezone(pytz.timezone(self._context.get('tz') or 'UTC'))
        return new_date.date()
    
    @api.constrains('status')
    def ResourceStatus(self):
        for rec in self:
            if rec.status == 'not_available':
                raise UserError('Resource not available in this time slot')
            
            
    @api.depends('start_datetime' ,'end_datetime')
    def getStatus(self):
        for rec in self:
            if rec.resource_id and rec.start_datetime and rec.end_datetime:
                record =self.env['planning.slot'].search([('resource_id','=',rec.resource_id.id)])
                same_date_recs = record.filtered(lambda a,st = rec.start_datetime.date() ,ed = rec.end_datetime.date():a.start_datetime.date() == st and a.end_datetime.date() == ed)
                same_date_recs = same_date_recs-self
                if same_date_recs:
                    avail = False
                    for tm in same_date_recs:
                        if ((rec.start_datetime < tm.start_datetime and rec.end_datetime < tm.start_datetime) or (rec.start_datetime > tm.end_datetime and rec.end_datetime > tm.end_datetime)):
                            avail = True
                        else:
                            avail = False 
                    if avail == True:
                        rec.status = 'available'
                    else:
                        rec.status = 'not_available'    
             
                else: 
                    rec.status = 'available'
    
    
    def createSO(self,id):
        try:
            line_val = []
            for serv_line in self.sub_service_ids:
         
                line_val.append((0, 0, {
                            'product_id': serv_line.product_id.id,
                            'product_uom_qty': 1.0,
                            'price_unit': serv_line.product_id.list_price,
                        }))
            vals = {
                'partner_id': self.partner_id.id,
                'company_id': self.env.company.id,
                'date_order': self.start_datetime,
                'order_line': line_val
            }
            record = self.env['sale.order'].create(vals)
            planning_obj= self.env['planning.slot'].search([("id",'=',id)])
            planning_obj.sale_order_id=record.id
            return record 
        except Exception as e:
            print(e.args)       

class ProductProduct(models.Model):
    _inherit = 'product.product'

    name_ar = fields.Char('Arabic Name')
    
class SaleOrderAutomation(models.Model):
    _inherit= 'sale.order'
    
    
    def action_confirm(self):
        res = super(SaleOrderAutomation , self).action_confirm()
        if self.payment_status == 'paid':
            inv =self._create_invoices(final = True)
            inv.action_post() 
            inv_payment_posted = inv.createPaymentfromSo()
            inv.payment_state ='paid'
        
        return res    
class SO_InvPayment(models.Model):
    _inherit='account.move'
    
        
    def createPaymentfromSo(self):
       
        bank_journal = self.env['account.journal'].search([('name', '=','Bank'),('company_id','=',self.company_id.id)],limit=1)
        vals = {
            'journal_id': bank_journal.id,
            'partner_id': self.partner_id.id,
            'date': datetime.today().date(),
            'amount': self.amount_total,
            'currency_id': self.currency_id.id,
            'ref': self.name,
            'payment_type': 'inbound',
            'user_id': self.user_id.id,
            'partner_type': 'customer',
            'state': 'draft',
        }
        payment = self.env['account.payment'].create(vals)
        payment.action_post()  
        return payment 
