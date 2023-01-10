# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class HrWorkEntryInh(models.TransientModel):
    _inherit = 'hr.work.entry.regeneration.wizard'

    def regenerate_work_entries(self):
        diff = self.date_to - self.date_from
        # print(diff.days + 1)
        if (diff.days + 1) > 26:
            raise UserError('Work Entries cannot be greater than 26.')
        return super().regenerate_work_entries()