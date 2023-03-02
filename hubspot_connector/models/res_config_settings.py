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


class Integration(models.TransientModel):
    _inherit = 'res.config.settings'

    hubspot_access_token = fields.Char('Access Token', config_parameter='hubspot_connector.hubspot_key')

    def hubspot_import_contacts(self):
        try:
            if not self.hubspot_access_token:
                raise ValidationError('Please! Enter Credentials, something is missing...')
            else:
                headers = {
                    'content-type': 'application/json',
                    'authorization': 'Bearer %s' % self.hubspot_access_token
                }
                url = "https://api.hubapi.com/crm/v3/objects/contacts"
                next = True
                while next:
                    response = requests.request("GET", url, headers=headers)
                    if response.status_code == 200:
                        contacts_response = json.loads(response.content)
                        contacts = contacts_response['results']
                        self.hubspot_create_contacts(contacts)
                        if 'paging' in contacts_response:
                            url = contacts_response['paging']['next']['link']
                        else:
                            next = False
                    else:
                        raise ValidationError(
                            'Something went wrong. Please! Check your credential and try again!')
                self.env.cr.commit()
        except Exception as e:
            raise ValidationError(e)

    def hubspot_create_contacts(self, contacts):
        contact_object = self.env['res.partner']
        new_contacts = []
        for contact in contacts:
            odooContact = contact_object.search([('hubspot_id', '=', contact['id'])])
            if not odooContact:
                new_contacts.append(self.prepare_hubspot_contact_to_create(contact))
        contact_object.create(new_contacts)

    def prepare_hubspot_contact_to_create(self, contact):
        first_name = contact['properties']['firstname']
        last_name = contact['properties']['lastname']
        email = contact['properties']['email']
        if not first_name and not last_name:
            raise ValidationError('Some contacts has no first name and last name.')
        name = first_name
        if last_name:
            name += " " + last_name
        return {
            'hubspot_id': contact['id'],
            'name': name,
            'email': email
        }