from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import ValidationError
from datetime import datetime
import datetime
import time
import requests
import json
import urllib
import logging

_logger = logging.getLogger(__name__)


class InheritRP(models.Model):
    _inherit = 'res.partner'

    hubspot_id = fields.Char('Hubspot Id')

    def export_contacts(self):
        icpsudo = self.env['ir.config_parameter'].sudo()
        hubspot_access_token = icpsudo.get_param('hubspot_connector.hubspot_key')
        for contact in self:
            headers = {
                'content-type': 'application/json',
                'authorization': 'Bearer %s' % hubspot_access_token
            }
            url = "https://api.hubapi.com/crm/v3/objects/contacts"
            payload = self.get_contact_properties(contact)

            response = requests.post(url=url, data=json.dumps(payload), headers=headers)
            if response.status_code == 201:
                newContact = json.loads(response.content)
                contact.hubspot_id = newContact['id']
        self.env.cr.commit()

    def get_contact_properties(self, contact):
        return {
            "properties":{
                # "company": "Biglytics",
                "email": contact.email,
                "firstname": contact.name,
                "lastname": None,
                "phone": contact.phone,
                "website": contact.website,
            }
        }
