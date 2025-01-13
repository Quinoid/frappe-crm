import frappe
from frappe import _
from frappe.utils import nowdate, cint
from frappe import db

@frappe.whitelist()
def get_lead_conversion_data(start_date, end_date):

    if not start_date or not end_date:
        frappe.throw(_("Start date and end date are required"))
    
    query = """
        SELECT 
            COALESCE(leads.source, 'N/A') AS LeadSource,
            COUNT(leads.name) AS ConvertedLeads,
            #ROUND(AVG(DATEDIFF(COALESCE(deals.close_date, leads.creation), leads.creation)), 2) AS AvgConversionTime,
            ROUND(
                AVG(
                    CASE
                        WHEN DATEDIFF(COALESCE(deals.close_date, leads.creation), leads.creation) = 0 
                            THEN 1
                        ELSE DATEDIFF(COALESCE(deals.close_date, leads.creation), leads.creation)
                    END
                ), 
                2
            ) AS AvgConversionTime,
            ROUND(SUM(COALESCE(deals.custom_value, 0)), 2) AS TotalDealValue
        FROM 
            `tabCRM Lead` AS leads
        LEFT JOIN 
            `tabCRM Deal` AS deals ON leads.name = deals.lead
        WHERE 
            leads.converted = 1
            AND leads.creation BETWEEN %s AND %s
        GROUP BY 
            leads.source
        ORDER BY 
            ConvertedLeads DESC
    """
    
    data = frappe.db.sql(query, (start_date, end_date), as_dict=True)
    
    return data


@frappe.whitelist()
def get_deal_summary_data(start_date, end_date, category_name="Open"):
    if not start_date or not end_date:
        frappe.throw(_("Start date and end date are required"))
    
    query = """
        SELECT 
            COALESCE(deals.source, 'N/A') AS DealStage,
            COUNT(deals.name) AS TotalDeals,
            ROUND(SUM(deals.custom_value), 2) AS TotalDealValue,
            #ROUND(SUM(deals.custom_value * (deals.deal_probability / 100)), 2) AS WeightedDealValue, #weighted deal value = deal value* (deal probability/100)
            ROUND(SUM(deals.custom_value * (CAST(REPLACE(deals.deal_probability, '%', '') AS DECIMAL) / 100)), 2) AS WeightedDealValue
            ROUND(AVG(deals.deal_probability), 2) AS AvgCloseProbability

        FROM 
            `tabCRM Deal` AS deals
        LEFT JOIN 
            `tabCRM Deal Status` AS deal_status ON deals.status = deal_status.name
        LEFT JOIN 
            `tabDeal Status Category` AS status_category ON deal_status.category_name = status_category.category_name
        WHERE 
            status_category.category_name = %s
            AND deals.close_date BETWEEN %s AND %s
        GROUP BY 
            deals.source
        ORDER BY 
            WeightedDealValue DESC
    """
    
    data = frappe.db.sql(query, (category_name, start_date, end_date), as_dict=True)
    return data



@frappe.whitelist()
def get_task_summary_data(start_date, end_date):

    if not start_date or not end_date:
        frappe.throw(_("Start date and end date are required"))
    
    query = """
        SELECT 
            users.full_name AS AssignedTo,
            COUNT(tasks.name) AS TotalTasks,
            SUM(CASE WHEN tasks.status = 'Done' THEN 1 ELSE 0 END) AS CompletedTasks,
            SUM(CASE WHEN tasks.status = 'Backlog' THEN 1 ELSE 0 END) AS OverdueTasks,
            ROUND(
                AVG(
                    CASE
                        WHEN DATEDIFF(tasks.task_completion_date, tasks.task_assigned_date) = 0 
                            THEN 1
                        ELSE DATEDIFF(tasks.task_completion_date, tasks.task_assigned_date)
                    END
                ),
                2
            ) AS AvgCompletionTime
        FROM 
            `tabCRM Task` AS tasks
        LEFT JOIN 
            `tabUser` AS users ON tasks.assigned_to = users.name
        WHERE 
            tasks.task_completion_date BETWEEN %s AND %s
        GROUP BY 
            users.full_name
        ORDER BY 
            CompletedTasks DESC
        LIMIT 10
    """
    
    data = frappe.db.sql(query, (start_date, end_date), as_dict=True)
    
    return data

#Lag functionality needs to be changed?
@frappe.whitelist()
def get_funnel_data(start_date, end_date):
    # Validate input dates
    if not start_date or not end_date:
        frappe.throw(_("Start date and end date are required"))
    
    query = """
        WITH FunnelData AS (
            SELECT 
                CASE
                    WHEN leads.status = 'New' THEN 'New'
                    WHEN leads.status IN ('Contacted', 'Nurture') THEN 'Engaged'
                    WHEN deals.status IN ('New', 'Qualification') THEN 'Qualified'
                    WHEN deals.status IN ('Follow-up Required', 'Demo/Trial', 'Proposal/Quotation Sent') THEN 'Ongoing'
                    WHEN deals.status IN ('Negotiation', 'Ready to Close') THEN 'Negotiation'
                    WHEN deals.status = 'Closed Won' THEN 'Closed Won'
                END AS FunnelStage,
                COUNT(DISTINCT leads.name) AS TotalLeads,
                SUM(
                    CASE 
                        WHEN deals.status = 'Closed Won' THEN deals.custom_value 
                        ELSE 0 
                    END
                ) AS TotalDealValue
            FROM 
                `tabCRM Lead` AS leads
            LEFT JOIN 
                `tabCRM Deal` AS deals ON leads.name = deals.lead
            WHERE 
                (leads.creation BETWEEN %s AND %s OR leads.creation IS NULL)
                AND (
                    leads.status IN ('New', 'Contacted', 'Nurture')
                    OR deals.status IN (
                        'New', 'Qualification', 'Follow-up Required', 
                        'Demo/Trial', 'Proposal/Quotation Sent', 
                        'Negotiation', 'Ready to Close', 'Closed Won'
                    )
                )

            GROUP BY 
                FunnelStage
        )
        SELECT 
            FunnelStage,
            TotalLeads,
            ROUND(TotalDealValue, 2) AS TotalDealValue,
            LAG(TotalLeads) OVER (ORDER BY FIELD(FunnelStage, 'New', 'Engaged', 'Qualified', 'Ongoing', 'Negotiation', 'Closed Won')) AS PreviousStageLeads,
            ROUND(
                CASE 
                    WHEN LAG(TotalLeads) OVER (ORDER BY FIELD(FunnelStage, 'New', 'Engaged', 'Qualified', 'Ongoing', 'Negotiation', 'Closed Won')) IS NOT NULL 
                    THEN (TotalLeads * 100.0) / LAG(TotalLeads) OVER (ORDER BY FIELD(FunnelStage, 'New', 'Engaged', 'Qualified', 'Ongoing', 'Negotiation', 'Closed Won'))
                    ELSE 100.0
                END, 2
            ) AS ConversionRate,
            ROUND(
                CASE
                    WHEN LAG(TotalLeads) OVER (ORDER BY FIELD(FunnelStage, 'New', 'Engaged', 'Qualified', 'Ongoing', 'Negotiation', 'Closed Won')) IS NOT NULL
                    THEN (((TotalLeads * 100.0) / LAG(TotalLeads) OVER (ORDER BY FIELD(FunnelStage, 'New', 'Engaged', 'Qualified', 'Ongoing', 'Negotiation', 'Closed Won'))) - TotalLeads ) 
                    ELSE 0.0
                END, 2
            ) AS DropOffRate
        FROM 
            FunnelData
        ORDER BY 
            FIELD(FunnelStage, 'New', 'Engaged', 'Qualified', 'Ongoing', 'Negotiation', 'Closed Won');

    """
    
    # Execute the query
    try:
        data = frappe.db.sql(query, (start_date, end_date), as_dict=True)
    except Exception as e:
        frappe.throw(_("An error occurred while fetching funnel data: {0}").format(str(e)))
    
    return data



@frappe.whitelist()
def get_user_summary(start_date, end_date):
    if not start_date or not end_date:
        frappe.throw(_("Start date and end date are required"))
    
    if start_date > end_date:
        frappe.throw(_("Start date cannot be after the end date."))

    query = """
        SELECT 
            users.full_name AS UserName,
            COUNT(DISTINCT tasks.name) AS TotalTasks,
            SUM(CASE WHEN tasks.status = 'Done' THEN 1 ELSE 0 END) AS CompletedTasks,
            COUNT(DISTINCT deals.name) AS TotalDeals,
            SUM(CASE WHEN deals.status = 'Closed Won' THEN deals.custom_value ELSE 0 END) AS TotalDealValue,
            COUNT(DISTINCT CASE WHEN communications.sender = users.email THEN communications.name ELSE NULL END) AS TotalEmailsSent,
            COUNT(DISTINCT calls.name) AS TotalCalls,
            COUNT(DISTINCT CASE 
                WHEN participant_events.link_field = users.email AND events.event_category = 'Meeting' 
                THEN events.name ELSE NULL END) AS TotalMeetings
        FROM 
            `tabUser` AS users
        LEFT JOIN 
            `tabCRM Task` AS tasks ON users.name = tasks.assigned_to
        LEFT JOIN 
            `tabCRM Deal` AS deals ON users.name = deals.deal_owner
        LEFT JOIN 
            `tabCommunication` AS communications ON users.email = communications.sender
        LEFT JOIN 
            `tabCRM Call Log` AS calls ON users.name = calls.owner
        LEFT JOIN 
            `tabEvent` AS events ON events.starts_on BETWEEN %s AND %s
        LEFT JOIN 
            `tabCustom User` AS participant_events ON participant_events.parent = events.name 
        WHERE 
            (participant_events.link_field = users.email AND events.starts_on BETWEEN %s AND %s)
            OR tasks.task_completion_date BETWEEN %s AND %s
            OR deals.close_date BETWEEN %s AND %s
            OR communications.creation BETWEEN %s AND %s
            OR calls.creation BETWEEN %s AND %s
        GROUP BY 
            users.full_name
        ORDER BY 
            CompletedTasks DESC
        LIMIT 10
    """

    data = frappe.db.sql(query, (
        start_date, end_date,  # For events
        start_date, end_date,  # For tasks
        start_date, end_date,  # For deals
        start_date, end_date,  # For communications
        start_date, end_date,  # For call logs
        start_date, end_date   # For participant events
    ), as_dict=True)
    
    return {
        "summary": data,
        "start_date": start_date,
        "end_date": end_date
    }
