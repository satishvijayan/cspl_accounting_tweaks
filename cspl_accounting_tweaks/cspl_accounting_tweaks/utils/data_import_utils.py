from __future__ import unicode_literals
import frappe, math
from frappe import _
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from erpnext.accounts.doctype.tax_rule.tax_rule import get_tax_template
from erpnext.accounts.party import get_party_account
from erpnext.controllers.accounts_controller import AccountsController


#######SHOULD THIS BE HERE OR IN NEXDHA? CURRENTLY DUPLICATING########################################
@frappe.whitelist() 
def populate_invoice_taxes(doc, method=None):
    inv=doc  #todo: refactor inv to doc
    frappe.msgprint("data_import_utils->populate_invoice_taxes" + str(len(inv.taxes)))
    if len(doc.taxes)>0:
        return

	# tax_type= 'Sales' if doc.doctype=='Sales Invoice' else 'Purchase'
    items_tax={}
    if inv.doctype=='Sales Invoice':
        tax_type='Sales'
        customer = frappe.get_cached_doc('Customer', inv.customer)
        customer_group = customer.customer_group
        tax_category=customer.tax_category
        supplier_group=None
    elif inv.doctype=='Purchase Invoice':
        tax_type='Purchase'
        supplier = frappe.get_cached_doc('Supplier', inv.supplier)
        tax_category=supplier.tax_category
        supplier_group = supplier.supplier_group
        customer_group = None
    else:
        return

    items_taxes={}
    #Iterating through the items in invoice
    for item_line in inv.items:
        item_group= frappe.get_cached_doc('Item', item_line.item_code).item_group
        frappe.msgprint("Company:" + inv.company \
                    + "transaction dt:" + str(inv.posting_date) \
                    + "tax category" + tax_category \
                    + "item" + item_line.item_code)
        items_taxes[item_line.item_code]=get_taxes( company=inv.company, transaction_date = inv.posting_date \
									, tax_category = tax_category, tax_type=tax_type\
									, item_group=item_group, item=item_line.item_code \
									, item_line_amount = item_line.amount, amt_inclusive_of_sales_tax=False\
									, supplier_group=supplier_group, customer_group=customer_group)
    

    taxes={}
    # for key, item_line in items_taxes.items():
    #     for key1, item1 in item_line.items():
    #         for key2, item2 in item1.items():
    #             frappe.msgprint("item_line key"+str(key2) + ", value: "+ str(item2))
    total_taxes_and_charges=0
    for key, item_line in items_taxes.items():
        for key1, item_tax_line in item_line.items():
            if item_tax_line['tax_account'] in taxes.keys():
                taxes[item_tax_line['tax_account']]['tax_amount']+=item_tax_line['tax_amount']
            else:
                taxes[item_tax_line['tax_account']]= {
                                            'charge_type': item_tax_line['charge_type']
                                            , 'account_head': item_tax_line['tax_account']
                                            , 'rate': item_tax_line['rate']*100
                                            , 'tax_amount': item_tax_line['tax_amount']
                                            , 'included_in_print_rate': item_tax_line['included_in_print_rate']
                                            , 'add_deduct_tax': item_tax_line['add_deduct_tax']
                                            , 'included_in_paid_amount': item_tax_line['included_in_paid_amount']
                                            , 'category': item_tax_line['category']
                                        }
            
            total_taxes_and_charges+=item_tax_line['tax_amount']

            # frappe.msgprint("inside tax dict: Tax Acct : " + item_tax_line['tax_account'] \
            #                 + "\n tax_amount: " + str(item_tax_line['tax_amount'])\
            #                 + "\n Charge Type: "+ item_tax_line['charge_type'])
    
    
    base_total=inv.base_net_total
    # frappe.msgprint("Base Total: "+ str(inv.base_net_total))
    # for key, tax in taxes.items():
    #     for key1, tax1 in tax.items():
    #             frappe.msgprint(" \nKey: " + key1 + " | tax2 : " + str(tax1))


    add_deduct_tax=category=included_in_paid_amount=included_in_print_rate=None
    for key, tax in taxes.items():
        base_total+=tax['tax_amount']
        # frappe.msgprint("included: " + )        
        row = inv.append("taxes",{
                    'charge_type': tax['charge_type']
                    , 'account_head':tax['account_head']
                    , 'rate': tax['rate']
                    , 'tax_amount': tax['tax_amount']
                    , 'description': "Account Head: " + tax['account_head'] + "| @Rate: " + str(tax['rate']) + "%"
                    , 'included_in_print_rate': tax['included_in_print_rate']
                    , 'included_in_paid_amount': tax['included_in_paid_amount']
                    , 'category': tax['category'] if tax_type=='Purchase' else ''
                    , 'add_deduct_tax': tax['add_deduct_tax']
            })

    # inv.total_taxes_and_charges=total_taxes_and_charges
    # inv.grand_total   
    inv.validate()

@frappe.whitelist() 
def get_taxes(  company, transaction_date, tax_type, tax_category=None, item_group=None, item=None \
                ,qty=1, item_line_amount=0.00,  amt_inclusive_of_sales_tax=False \
                , customer_group=None,supplier_group=None):
    
    invoice_amount=item_line_amount # to be refactored
    if item ==None or invoice_amount==0:
        frappe.msgprint("get_taxes - None")
        return

    if item_group == None:
        frappe.get_cached_doc('Item', item_line.item_code).item_group



    args = {
            'item_group': item_group,
            'tax_category': tax_category,
            'company': company,
            'tax_type': tax_type,
            'customer_group':customer_group,
            'supplier_group': supplier_group
        }

    # frappe.msgprint("Item_group: " + args['item_group'] +  "| posting_date: " + str(args['posting_date']) + " | tax_type: " + args['tax_type'])
    
    tax_template_name = get_tax_template(transaction_date, args)
    # frappe.msgprint(tax_template_name)
    if tax_type=='Sales':
        tax_template = frappe.get_cached_doc("Sales Taxes and Charges Template", tax_template_name)
    else:
        tax_template = frappe.get_cached_doc("Purchase Taxes and Charges Template", tax_template_name)

    # for row in tax_template.taxes:
        # frappe.msgprint("Tax_Template")
        # frappe.msgprint("\nfield :" + row.name + "\n add/deduct tax: "+ str(row.add_deduct_tax) \
        #                 + "\ncategory:"+ row.category \
        #                 + "\nincluded_in_print_rate: "+ str(row.included_in_print_rate))

    i=0
    tot_tax = 0.00
    tot_tax_rate=0.00
    tax={}

    for row in tax_template.taxes: 
        frappe.msgprint("included_in_print_rate: "+ str(row.included_in_print_rate))
        tax[i] = {
            'item': item
            , 'item_group': item_group
            , 'charge_type': row.charge_type
            , 'tax_account': row.account_head
            , 'rate': flt(row.rate/100)
            , 'qty':qty
            , 'tax_amount':row.tax_amount
            , 'invoice_amount':0
            , 'tot_tax_amount':0
            , 'included_in_print_rate': row.included_in_print_rate
            , 'add_deduct_tax': ''
            , 'included_in_paid_amount': row.included_in_paid_amount
            , 'category': ''
            }
        if tax_type=='Purchase':
            # tax[i]['included_in_print_rate']=row.included_in_print_rate
            tax[i]['add_deduct_tax']=row.add_deduct_tax
            tax[i]['category']=row.category
            # tax[i]['included_in_paid_amount']=row.included_in_paid_amount

        i+=1
        tot_tax_rate += flt(row.rate/100)
        
    invoice_amount = round(invoice_amount/(1+tot_tax_rate),2) if amt_inclusive_of_sales_tax else round(invoice_amount,2)
    tot_tax_amount = round(invoice_amount*tot_tax_rate,2)
    # tot_tax= flt(invoice_amt*tot_tax_rate)
    for key,value in tax.items():
        #some taxes are based on a flat amount, this amount is captured in the 'sales taxes and charges' doc
        value['tax_amount']=value['tax_amount'] if value['tax_amount']>0 else round(flt(invoice_amount*value['rate']),2) 
        value['invoice_amount']=invoice_amount
        value['tot_tax_amount']=tot_tax_amount
        
        frappe.msgprint("key:"+ str(key) + " Type " + tax_type + " tax_account:" + value['tax_account'] \
                        + " tax rate: " + str(value['rate']) + " tax_amount: " + str(value['tax_amount']) \
                        + " invoice_amount: " + str(value['invoice_amount']) \
                        + "included_in_print_rate :" + str(value['included_in_print_rate']))

    return tax
