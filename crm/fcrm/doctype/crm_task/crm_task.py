# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.desk.form.assign_to import add as assign, remove as unassign
from crm.fcrm.doctype.crm_notification.crm_notification import notify_user


class CRMTask(Document):
	def after_insert(self):
		self.assign_to()

	def validate(self):
		if self.is_new() or not self.assigned_to:
			return

		if self.get_doc_before_save().assigned_to != self.assigned_to:
			self.unassign_from_previous_user(self.get_doc_before_save().assigned_to)
			self.assign_to()

	def unassign_from_previous_user(self, user):
		unassign(self.doctype, self.name, user)

	def assign_to(self):
		if self.assigned_to:
			assign({
				"assign_to": [self.assigned_to],
				"doctype": self.doctype,
				"name": self.name,
				"description": self.title or self.description,
			})


	@staticmethod
	def default_list_data():
		columns = [
			{
				'label': 'Title',
				'type': 'Data',
				'key': 'title',
				'width': '16rem',
			},
			{
				'label': 'Reference Doc Type',
				'type': 'Dynamic Link"',
				'key': 'reference_doctype',
				'width': '8rem',
			},
			{
				'label': 'Status',
				'type': 'Select',
				'key': 'status',
				'width': '8rem',
			},
			{
				'label': 'Assigned To',
				'type': 'Link',
				'key': 'assigned_to',
				'width': '10rem',
			},
			{
				'label': 'Priority',
				'type': 'Select',
				'key': 'priority',
				'width': '8rem',
			},
			{
				'label': 'Due Date',
				'type': 'Date',
				'key': 'due_date',
				'width': '8rem',
			},
			
			{
				'label': 'Last Modified',
				'type': 'Datetime',
				'key': 'modified',
				'width': '8rem',
			},
			{
                'label': 'Created On',
                'type': 'Datetime',
                'key': 'creation',
                'width': '8rem',
            },
			# {
			# 	'label': 'Reference Doc Name',
			# 	'type': 'Dynamic Link"',
			# 	'key': 'reference_docname',
			# 	'width': '8rem',
			# },
		]

		rows = [
			"name",
			"title",
			"reference_docname",
			"description",
			"assigned_to",
			"due_date",
			"status",
			"priority",
			"reference_doctype",
			"modified",
		]
		return {'columns': columns, 'rows': rows}

	@staticmethod
	def default_kanban_settings():
		return {
			"column_field": "status",
			"title_field": "title",
			"kanban_fields": '["description", "priority", "creation"]'
		}
