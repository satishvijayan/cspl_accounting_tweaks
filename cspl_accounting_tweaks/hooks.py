from . import __version__ as app_version

app_name = "cspl_accounting_tweaks"
app_title = "CSPL Accounting Tweaks"
app_publisher = "Charioteer Software Pvt Ltd"
app_description = "Accounting tweaks to ERPnext. eg: autogen document on bank recon. etc"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "satish@charioteersoftware.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/cspl_accounting_tweaks/css/cspl_accounting_tweaks.css"
# app_include_js = "/assets/cspl_accounting_tweaks/js/cspl_accounting_tweaks.js"

# include js, css files in header of web template
# web_include_css = "/assets/cspl_accounting_tweaks/css/cspl_accounting_tweaks.css"
# web_include_js = "/assets/cspl_accounting_tweaks/js/cspl_accounting_tweaks.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "cspl_accounting_tweaks/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "cspl_accounting_tweaks.utils.jinja_methods",
# 	"filters": "cspl_accounting_tweaks.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "cspl_accounting_tweaks.install.before_install"
# after_install = "cspl_accounting_tweaks.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "cspl_accounting_tweaks.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"cspl_accounting_tweaks.tasks.all"
# 	],
# 	"daily": [
# 		"cspl_accounting_tweaks.tasks.daily"
# 	],
# 	"hourly": [
# 		"cspl_accounting_tweaks.tasks.hourly"
# 	],
# 	"weekly": [
# 		"cspl_accounting_tweaks.tasks.weekly"
# 	],
# 	"monthly": [
# 		"cspl_accounting_tweaks.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "cspl_accounting_tweaks.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "cspl_accounting_tweaks.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "cspl_accounting_tweaks.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"cspl_accounting_tweaks.auth.validate"
# ]

