# https://discuss.erpnext.com/t/api-erpnext-setup-utils-get-exchange-rate-unable-to-find-exchange-rate/29914
# https://about.lovia.life/docs/infrastructure/erpnext/erpnext-custom-doctypes-actions-and-links/
# https://discuss.erpnext.com/t/database-transaction-in-api-method/49091/6
# https://stackoverflow.com/questions/61331968/setting-a-value-in-frappe-application-isnt-reflected-in-erpnext-gui/61414160#61414160
# https://discuss.erpnext.com/t/help-needed-with-custom-script/25195
# https://discuss.erpnext.com/t/how-to-insert-child-table-records-link-to-existing-parent-table-row/25825/2
# https://discuss.erpnext.com/t/redirecting-to-new-doc/25980/7
#  https://discuss.erpnext.com/t/erpnext-v12-3-1-new-doctype-doctype-action-doctype-link-child-table/56659/6
#  https://about.lovia.life/docs/infrastructure/erpnext/erpnext-custom-doctypes-actions-and-links/
#  https://discuss.erpnext.com/t/tutorial-add-custom-action-button-custom-menu-button-custom-icon-button-in-form-view/45260
#  https://discuss.erpnext.com/t/add-custom-button-in-child-table/47405/4
#  https://github.com/frappe/frappe/wiki/Developer-Cheatsheet
#  https://discuss.erpnext.com/t/how-create-and-insert-a-new-document-through-custom-script/39158/6
#  https://discuss.erpnext.com/t/get-singles-value-in-js/18389/4
#  https://programtalk.com/python-examples/frappe.db.get_default/
#  https://discuss.erpnext.com/t/client-side-doc-creation-posting-date/49243/3
#  https://discuss.erpnext.com/t/redirecting-to-new-doc/25980/4
# https://discuss.erpnext.com/t/map-frappe-model-mapper-get-mapped-doc-doctype-with-other-s-doctype-child-table/29556/3
# https://discuss.erpnext.com/t/how-to-fetch-child-tables/12348/31
# https://github.com/frappe/frappe/blob/develop/frappe/email/doctype/auto_email_report/auto_email_report.py
from __future__ import unicode_literals
import frappe, math
from frappe import _
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document

@frappe.whitelist()
def create_payment_entry_bank_transaction(bank_transaction_name, payment_row_doc_type, payment_entry=None):
    B = bank_transaction_name
    P = payment_row_doc_type
    bt_doc = frappe.get_doc("Bank Transaction",  bank_transaction_name)
    dt = bt_doc.date
    ref = bt_doc.reference_number if bt_doc.reference_number else "None"
    desc = bt_doc.description if bt_doc.description else "No Description Provided"
    pay = bt_doc.withdrawal
    receive = bt_doc.deposit
    Bank=bt_doc.bank_account
    DefComp=bt_doc.company
    DefBank= frappe.get_value('Bank Account',{"name": Bank},  'account', )
    DefExp = frappe.get_value('Company',{"name": DefComp},  'unreconciled_expenses_account')
    # frappe.msgprint(DefBank)
    # frappe.msgprint(P)
    # frappe.msgprint(bt_doc.payment_entry(payment_row_idx).payment_document)
    
    BT_URL=frappe.utils.get_url_to_form(bt_doc.doctype, bt_doc.name)
    # frappe.msgprint(payment_entry)
    # frappe.msgprint(not payment_entry)

    if  not payment_entry:
        if P == 'Journal Entry' :
            doc = frappe.new_doc(P)
            doc.voucher_type= 'Bank Entry'
            doc.posting_date = dt
            doc.cheque_no=ref
            doc.cheque_date= dt
            doc.reference= ref
            doc.clearance_date= dt
            doc.user_remark= desc \
                            + "\n\n<b>Bank Statement Details:</b>" \
                            + "\n 1. Tx Amount: " + str(pay+receive) \
                            + "\n 2. Tx Date: " + str(frappe.utils.formatdate(dt,"dd-MMM-yyyy"))  \
                            + "\n 3. Bank Ref: " + ref  \
                            + "\n 4. Bank Transaction Document Reference: " + "<a href=" + BT_URL + ">" + bt_doc.name + "</a>" \
                            + "\n\nEntry generated from Bank Transaction using 'Create Button' on: " + str(frappe.utils.formatdate(frappe.utils.nowdate(), "dd-MMM-yyyy"))
            
            row = doc.append( "accounts",
                        {
                            'account': DefBank,
                            'debit_in_account_currency': pay,
                            'credit_in_account_currency': receive
                        }
                    )
            row = doc.append( "accounts",
                        {
                            'account': DefExp,
                            'debit_in_account_currency': receive,
                            'credit_in_account_currency': pay
                        })
            doc.insert(ignore_permissions=True)
            # frappe.msgprint("JV")
            return doc.as_dict()


        elif P == 'Payment Entry':
            doc = frappe.new_doc(P)        
            doc.posting_date= dt

            doc.mode_of_payment= frappe.get_value('Company',{"name": DefComp},  'default_payment_mode')
            doc.bank_account=DefBank
            doc.received_amount= doc.paid_amount = pay + receive
            # doc.total_allocated_amount = doc.base_total_allocated_amount =0
            doc.paid_from_account_currency=doc.paid_to_account_currency =frappe.get_value('Company',{"name": DefComp},  'default_currency')
            doc.source_exchange_rate=doc.target_exchange_rate=1
            doc.reference_no=bt_doc.name
            doc.reference_date=dt
            doc.custom_remarks=1 # custom remarks describing the information avl in bank statement
            doc.remarks=  "<b>Bank Statement Details:</b>" \
                            + "\n 1. Amount: " + str(doc.paid_amount) \
                            + "\n 2. Date: " + str(frappe.utils.formatdate(dt,"dd-MMM-yyyy"))  \
                            + "\n 3. Bank Ref: " + ref  \
                            + "\n 4. Bank Transaction Document Reference: " + "<a href=" + BT_URL + ">" + bt_doc.name + "</a>" \
                            + "\n\nEntry generated from Bank Transaction using 'Create Button' on: " + str(frappe.utils.formatdate(frappe.utils.nowdate(), "dd-MMM-yyyy"))
            if receive>0:
                doc.payment_type = 'Receive'
                doc.paid_from = frappe.get_value('Company',{"name": DefComp},  'default_receivable_account')
                doc.paid_to =   DefBank
                doc.party_type = "Customer"
                doc.party=frappe.get_value('Company',{"name": DefComp},  'default_customer_for_bank_transaction')
                
            else :
                doc.payment_type = 'Pay'
                doc.paid_from = DefBank
                doc.paid_to =   frappe.get_value('Company',{"name": DefComp},  'default_payable_account')
                doc.party_type = "Supplier"
                doc.party=frappe.get_value('Company',{"name": DefComp},  'default_supplier_for_bank_transaction')            

            doc.insert(ignore_permissions=True)            
            
            return doc

        elif P == 'Expense Claim':
            return None


    return None




# + " ref:" + D['reference_number'].value + \
#     " desc:" + D['description'].value + " pay:" + D['withdrawal'].value " receive:" + D['deposit'].value

# def make_timesheet(source_name, target_doc = None):
# doc = get_mapped_doc(“Task”, source_name, 
#     {
#         “Task”: {“doctype”: “Timesheet”,},
#         “Task”:{“doctype”:“Timesheet Detail”,
#             “field_map”:{“name”:“task”, “expected_time”:“hours”},
#             },
#         }, 
#         target_doc)