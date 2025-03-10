# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CRMOrganization(Document):
		@staticmethod
		def default_list_data():
			columns = [
				{
					'label': 'Organization',
					'type': 'Data',
					'key': 'organization_name',
					'width': '16rem',
				},
				{
					'label': 'Type Of Business',
					'type': 'Link',
					'key': 'type_of_business',
					'width': '16rem',
				},
				{
					'label': 'Organization Status',
					'type': 'Data',
					'key': 'organization_status',
					'width': '14rem',
				},
				{
	                'label': 'Owner/Assigned To',
	                'type': 'Text',
	                'key': '_assign',
	                'width': '10rem',
	            },
				{
					'label': 'Industry',
					'type': 'Link',
					'key': 'industry',
					'options': 'CRM Industry',
					'width': '14rem',
				},
				{
					'label': 'Sector',
					'type': 'Link',
					'key': 'sector',
					'width': '14rem',
				},
				{
					'label': 'City',
					'type': 'Link',
					'key': 'city',
					'width': '14rem',
				},
				{
	                'label': 'Tags',
	                'type': 'Text',
	                'key': 'custom_tags_data',
	                'width': '8rem',
	            },
				# {
				# 	'label': 'Annual Revenue',
				# 	'type': 'Currency',
				# 	'key': 'annual_revenue',
				# 	'width': '14rem',
				# },
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
			]
			rows = [
				"name",
				"organization_name",
				"organization_logo",
				"website",
				"industry",
				"currency",
				"annual_revenue",
				"custom_tags_data"
				"modified",
			]
			return {'columns': columns, 'rows': rows}
