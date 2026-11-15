import frappe
from frappe import _


def execute(filters=None):
    project=(filters or {}).get('project')
    if not project:
        frappe.throw(_("Project is required."))
    from code_fitout.finance import owner_balances
    held, personal = owner_balances(project)
    movement_rows=frappe.db.sql("""
      SELECT movement_type,COALESCE(SUM(amount),0) total
      FROM `tabCF Owner Movement` WHERE project=%s AND docstatus=1
      GROUP BY movement_type
    """,(project,),as_dict=True)
    moves={x.movement_type:float(x.total) for x in movement_rows}
    incoming_transfer = frappe.db.sql("""
      SELECT COALESCE(SUM(amount),0) FROM `tabCF Owner Movement`
      WHERE target_project=%s AND docstatus=1
        AND movement_type='Transfer Held Funds to Another Project'
    """,(project,))[0][0]
    pay_rows=frappe.db.sql("""
      SELECT funding_source,COALESCE(SUM(amount),0) total
      FROM `tabCF Payment` WHERE project=%s AND docstatus=1
      GROUP BY funding_source
    """,(project,),as_dict=True)
    payments={x.funding_source:float(x.total) for x in pay_rows}
    columns=[
      {'fieldname':'project','label':_('Project'),'fieldtype':'Link','options':'Project','width':190},
      *[{'fieldname':key,'label':_(label),'fieldtype':'Currency','width':175} for key,label in [
        ('received','Owner Advances Received'),('transfer_in','Transfers In'),('transfer_out','Transfers Out'),('spent_held','Spent from Owner Funds'),
        ('refunded','Refunded to Owner'),('reimbursed_held','Personal Reimbursed (Held)'),
        ('reimbursed_direct','Personal Reimbursed (Direct)'),('personal_spent','Personal Advances'),
        ('held_balance','Owner Funds Held'),('personal_due','Personal Recoverable')]],
    ]
    return columns,[{
      'project':project,
      'received': moves.get('Owner Advance Received',0),
      'transfer_in':float(incoming_transfer or 0),
      'transfer_out':moves.get('Transfer Held Funds to Another Project',0),
      'spent_held':payments.get('Owner Funds Already Received',0),
      'refunded':moves.get('Refund to Owner',0),
      'reimbursed_held':moves.get('Personal Advance Reimbursement - From Held Funds',0),
      'reimbursed_direct':moves.get('Personal Advance Reimbursement - Owner Directly',0),
      'personal_spent':payments.get('Personal Funds - Recoverable',0),
      'held_balance':float(held),'personal_due':float(personal)
    }]
