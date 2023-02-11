# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import ValidationError, AccessError, UserError
from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import format_date



class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'


    def _check_undefined_slots(self, work_entries, payslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            calendar_start = pytz.utc.localize(datetime.combine(max(contract.date_start, payslip_run.date_start), time.min))
            calendar_end = pytz.utc.localize(datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), time.max))
            outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[False] - work_entries._to_intervals()
            
class HrPayslip(models.Model):

    _inherit = 'hr.payslip'

    def _get_worked_day_lines_values(self, domain=None):
        self.ensure_one()
        res = []
        hours_per_day = self._get_worked_day_lines_hours_per_day()
        work_hours = self.contract_id._get_work_hours(self.date_from, self.date_to, domain=domain)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            attendance_line = {
                'sequence': work_entry_type.sequence,
                'work_entry_type_id': work_entry_type_id,
                'number_of_days': 26,
                'number_of_hours': hours,
            }
            res.append(attendance_line)
        return res

    def action_edit_payslip_lines(self):
        self.ensure_one()
        if not self.user_has_groups('hr_payroll.group_hr_payroll_manager'):
            raise UserError(_('This action is restricted to payroll managers only.'))
        if self.state == 'done':
            raise UserError(_('This action is forbidden on validated payslips.'))
        wizard = self.env['hr.payroll.edit.payslip.lines.wizard'].create({
            'payslip_id': self.id,
            'line_ids': [(0, 0, {
                'sequence': line.sequence,
                'code': line.code,
                'name': line.name,
                'note': line.note,
                'salary_rule_id': line.salary_rule_id.id,
                'contract_id': line.contract_id.id,
                'employee_id': line.employee_id.id,
                'amount': line.amount,
                'quantity': line.quantity,
                'rate': line.rate,
                'slip_id': self.id}) for line in self.line_ids],
            'worked_days_line_ids': [(0, 0, {
                'name': line.name,
                'sequence': line.sequence,
                'code': line.code,
                'work_entry_type_id': line.work_entry_type_id.id,
                'number_of_days': 26,
                'number_of_hours': line.number_of_hours,
                'amount': line.amount,
                'slip_id': self.id}) for line in self.worked_days_line_ids]
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Edit Payslip Lines'),
            'res_model': 'hr.payroll.edit.payslip.lines.wizard',
            'view_mode': 'form',
            'target': 'new',
            'binding_model_id': self.env['ir.model.data']._xmlid_to_res_id('hr_payroll.model_hr_payslip'),
            'binding_view_types': 'form',
            'res_id': wizard.id
        }

    def _get_worked_days_line_number_of_days(self, code):
        return 26

class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    number_of_days = fields.Float(compute='get_no_of_day_val')

    def get_no_of_day_val(self):
        for rec in self:
            rec.number_of_days = 26
        return


class HrPayrollEditPayslipWorkedDaysLine(models.TransientModel):
    _inherit = 'hr.payroll.edit.payslip.worked.days.line'

    def _export_to_worked_days_line(self):
        return [{
            'name': line.name,
            'sequence': line.sequence,
            'code': line.code,
            'work_entry_type_id': line.work_entry_type_id.id,
            'number_of_days': 26,
            'number_of_hours': line.number_of_hours,
            'amount': line.amount,
            'payslip_id': line.slip_id.id
        } for line in self]
