"""SQLite smoke checks for SELECT-only report queries (not a MariaDB integration test)."""
import ast
import pathlib
import re
import sqlite3
import unittest

BASE = pathlib.Path(__file__).resolve().parents[1] / 'code_fitout/code_fitout/report'


def report_sql(report):
    p = BASE / report / (report + '.py')
    tree = ast.parse(p.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'sql':
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                return node.args[0].value
    raise AssertionError('No SQL found: ' + report)


class TestReportSQL(unittest.TestCase):
    def setUp(self):
        c = self.conn = sqlite3.connect(':memory:')
        c.execute('CREATE TABLE `tabCF Cost Record` (name TEXT, supplier TEXT, project TEXT, docstatus INTEGER, amount REAL, work_category TEXT, cost_type TEXT, work_order TEXT)')
        c.execute('CREATE TABLE `tabCF Payment` (name TEXT, supplier TEXT, project TEXT, docstatus INTEGER, amount REAL, total_allocated REAL, unallocated_amount REAL, paid_by TEXT, funding_source TEXT, payment_method TEXT, transfer_reference TEXT, payment_date TEXT)')
        c.execute('CREATE TABLE `tabCF Payment Allocation` (parent TEXT, cost_record TEXT, project TEXT, allocated_amount REAL)')
        c.execute('CREATE TABLE `tabCF Work Order` (name TEXT, project TEXT, supplier TEXT, docstatus INTEGER, committed_amount REAL, retention_percent REAL)')
        c.execute('CREATE TABLE `tabCF BOQ` (name TEXT, project TEXT, docstatus INTEGER)')
        c.execute('CREATE TABLE `tabCF BOQ Line` (parent TEXT, work_category TEXT, cost_type TEXT, amount REAL)')
        c.execute('INSERT INTO `tabCF Cost Record` VALUES (?,?,?,?,?,?,?,?)', ('COST1','CONTRACTOR','APT-001',1,1000,'HVAC / Air Conditioning','Labor','WO1'))
        c.execute('INSERT INTO `tabCF Payment` VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', ('PAY1','CONTRACTOR','APT-001',1,700,700,0,'Property Owner','Owner Paid Directly','InstaPay','T100','2026-11-15'))
        c.execute('INSERT INTO `tabCF Payment Allocation` VALUES (?,?,?,?)', ('PAY1','COST1','APT-001',700))

    def tearDown(self):
        self.conn.close()

    def run_query(self, name, bindings):
        sql = report_sql(name)
        sql = re.sub(r'%\((\w+)\)s', r':\1', sql)
        if "%s" in sql:
            sql = sql.replace("%s", "?")
            bindings = (bindings["project"],)
        return self.conn.execute(sql, bindings).fetchall()

    def test_contractor_balance_1000_minus_700(self):
        rows = self.run_query('cf_contractor_balances', {'supplier':None})
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0][0], 'CONTRACTOR')
        self.assertEqual(rows[0][1],1000)
        self.assertEqual(rows[0][2],700)
        self.assertEqual(rows[0][-1],300)

    def test_project_statement_aggregates_paid_once(self):
        rows = self.run_query('cf_project_statement', {'project':'APT-001'})
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0][5:8],(1000,700,300))

    def test_payment_register_no_double_count(self):
        rows = self.run_query('cf_payment_register', {'supplier':None,'project':None})
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0][5],700)

    def test_budget_versus_actual(self):
        self.conn.execute('INSERT INTO `tabCF BOQ` VALUES (?,?,?)',('BOQ1','APT-001',1))
        self.conn.execute('INSERT INTO `tabCF BOQ Line` VALUES (?,?,?,?)',('BOQ1','HVAC / Air Conditioning','Labor',1200))
        rows = self.run_query('cf_boq_budget', {'project':'APT-001'})
        self.assertEqual(rows[0][2:5],(1200,1000,200))

    def test_work_order_contract_versus_approved(self):
        self.conn.execute("INSERT INTO `tabCF Work Order` VALUES (?,?,?,?,?,?)",('WO1','APT-001','CONTRACTOR',1,1200,5))
        rows = self.run_query('cf_contract_commitments', {'supplier':None,'project':None})
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0][3:8],(1200,1000,700,300,200))
