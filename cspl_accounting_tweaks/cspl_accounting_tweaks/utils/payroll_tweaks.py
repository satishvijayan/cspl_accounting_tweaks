# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
import datetime, math

from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words, formatdate, get_first_day
from frappe.model.naming import make_autoname
from frappe.utils.background_jobs import enqueue

from frappe import msgprint, _
from erpnext.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.payroll.doctype.additional_salary.additional_salary import get_additional_salaries
from erpnext.payroll.doctype.payroll_period.payroll_period import get_period_factor, get_payroll_period
from erpnext.payroll.doctype.employee_benefit_application.employee_benefit_application import get_benefit_component_amount
from erpnext.payroll.doctype.employee_benefit_claim.employee_benefit_claim import get_benefit_claim_amount, get_last_payroll_period_benefits
from erpnext.loan_management.doctype.loan_repayment.loan_repayment import calculate_amounts, create_repayment_entry
from erpnext.accounts.utils import get_fiscal_year
from erpnext.hr.utils import validate_active_employee
from six import iteritems
from erpnext.payroll.doctype.salary_slip.salary_slip import get_year_to_date_period, calculate_component_amounts, 


def calculate_net_pay(self):
	if self.salary_structure:
		self.calculate_component_amounts("contribution")
	self.gross_pay = self.get_component_totals("earnings", depends_on_payment_days=1)
	self.base_gross_pay = flt(flt(self.gross_pay) * flt(self.exchange_rate), self.precision('base_gross_pay'))

	if self.salary_structure:
		self.calculate_component_amounts("deductions")

	self.set_loan_repayment()
	self.set_component_amounts_based_on_payment_days()
	self.set_net_pay()

def set_totals(self):
	self.gross_pay = 0.0
	if self.salary_slip_based_on_timesheet == 1:
		self.calculate_total_for_salary_slip_based_on_timesheet()
	else:
		self.total_deduction = 0.0
		if hasattr(self, "earnings"):
			for earning in self.earnings:
				self.gross_pay += flt(earning.amount, earning.precision("amount"))
		if hasattr(self, "deductions"):
			for deduction in self.deductions:
				self.total_deduction += flt(deduction.amount, deduction.precision("amount"))
		self.net_pay = flt(self.gross_pay) - flt(self.total_deduction) - flt(self.total_loan_repayment)
	self.set_base_totals()
def set_base_totals(self):
	self.base_gross_pay = flt(self.gross_pay) * flt(self.exchange_rate)
	self.base_total_deduction = flt(self.total_deduction) * flt(self.exchange_rate)
	self.rounded_total = rounded(self.net_pay)
	self.base_net_pay = flt(self.net_pay) * flt(self.exchange_rate)
	self.base_rounded_total = rounded(self.base_net_pay)
	self.set_net_total_in_words()		

def set_component_amounts_based_on_payment_days(self):
		joining_date, relieving_date = frappe.get_cached_value("Employee", self.employee,
			["date_of_joining", "relieving_date"])

		if not relieving_date:
			relieving_date = getdate(self.end_date)

		if not joining_date:
			frappe.throw(_("Please set the Date Of Joining for employee {0}").format(frappe.bold(self.employee_name)))

		
		for d in self.get("contribution"):
			d.amount = flt(self.get_amount_based_on_payment_days(d, joining_date, relieving_date)[0], d.precision("amount"))

def compute_component_wise_year_to_date(self, method):
		period_start_date, period_end_date = self.get_year_to_date_period()

		for key in ('contribution'):
			for component in self.get(key):
				year_to_date = 0
				component_sum = frappe.db.sql("""
					SELECT sum(detail.amount) as sum
					FROM `tabSalary Detail` as detail
					INNER JOIN `tabSalary Slip` as salary_slip
					ON detail.parent = salary_slip.name
					WHERE
						salary_slip.employee_name = %(employee_name)s
						AND detail.salary_component = %(component)s
						AND salary_slip.start_date >= %(period_start_date)s
						AND salary_slip.end_date < %(period_end_date)s
						AND salary_slip.name != %(docname)s
						AND salary_slip.docstatus = 1""",
						{'employee_name': self.employee_name, 'component': component.salary_component, 'period_start_date': period_start_date,
							'period_end_date': period_end_date, 'docname': self.name}
				)

				year_to_date = flt(component_sum[0][0]) if component_sum else 0.0
				year_to_date += component.amount
				component.year_to_date = year_to_date