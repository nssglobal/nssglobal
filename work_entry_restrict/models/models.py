# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class HrWorkEntryInh(models.TransientModel):
    _inherit = 'hr.work.entry.regeneration.wizard'

    # def regenerate_work_entries(self):
    #     diff = self.date_to - self.date_from
    #     if (diff.days + 1) > 26:
    #         raise UserError('Work Entries cannot be greater than 26.')
    #     return super().regenerate_work_entries()

    def regenerate_work_entries(self):
        self.ensure_one()
        if not self.env.context.get('work_entry_skip_validation'):
            if not self.valid:
                raise ValidationError(_("In order to regenerate the work entries, you need to provide the wizard with an employee_id, a date_from and a date_to. In addition to that, the time interval defined by date_from and date_to must not contain any validated work entries."))

            if self.date_from < self.earliest_available_date or self.date_to > self.latest_available_date:
                raise ValidationError(_("The from date must be >= '%(earliest_available_date)s' and the to date must be <= '%(latest_available_date)s', which correspond to the generated work entries time interval.", earliest_available_date=self._date_to_string(self.earliest_available_date), latest_available_date=self._date_to_string(self.latest_available_date)))

        date_from = max(self.date_from, self.earliest_available_date) if self.earliest_available_date else self.date_from
        date_to = min(self.date_to, self.latest_available_date) if self.latest_available_date else self.date_to
        work_entries = self.env['hr.work.entry'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date_stop', '>=', date_from),
            ('date_start', '<=', date_to),
            ('state', '!=', 'validated')])

        work_entries.write({'active': False})

        diff = self.date_to - self.date_from
        if (diff.days + 1) != 26:
            date_to = date_from + timedelta(days=25)

        self.employee_id.generate_work_entries(date_from, date_to, True)
        action = self.env["ir.actions.actions"]._for_xml_id('hr_work_entry.hr_work_entry_action')
        return action