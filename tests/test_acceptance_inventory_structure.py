"""Fast checks of versioned stage templates, print documents, inventory and routes."""
import json
from pathlib import Path
import unittest

R=Path(__file__).resolve().parents[1]
DOC=R/'code_fitout/code_fitout/doctype'


class TestAcceptanceInventory(unittest.TestCase):
    def test_stage_templates_cover_every_supplier_work_category(self):
        from ast import parse, literal_eval, Assign, Name
        syntax=parse((R/'code_fitout/setup/install.py').read_text())
        cats=[]
        for node in syntax.body:
            if isinstance(node,Assign) and any(isinstance(t,Name) and t.id=='CATEGORIES' for t in node.targets):
                cats=literal_eval(node.value)
        stages=json.loads((R/'code_fitout/data/stage_templates.json').read_text())
        self.assertEqual(set(cats),{s['work_category'] for s in stages})
        self.assertEqual(len(stages),122)
        self.assertEqual(len({s['stage_code'] for s in stages}),len(stages))
        for cat in cats:
            selected=[s for s in stages if s['work_category']==cat]
            self.assertEqual([s['stage_order'] for s in selected],list(range(1,len(selected)+1)))
            self.assertTrue(all(len(s['checklist'])>=3 for s in selected))
            self.assertTrue(all('criterion_ar' in item for s in selected for item in s['checklist']))

    def test_handover_schema_and_print_formats(self):
        handover=json.loads((DOC/'cf_stage_handover/cf_stage_handover.json').read_text())
        self.assertTrue(handover['is_submittable'])
        self.assertEqual(next(f for f in handover['fields'] if f['fieldname']=='checklist')['options'],'CF Handover Result')
        final=json.loads((DOC/'cf_trade_handover/cf_trade_handover.json').read_text())
        self.assertTrue(final['is_submittable'])
        for filename in ('cf_stage_handover.html','cf_trade_handover.html'):
            p=R/'code_fitout/templates/print_formats'/filename
            self.assertTrue(p.exists())
            self.assertIn('محضر',p.read_text())
        install=(R/'code_fitout/setup/install.py').read_text()
        self.assertIn('seed_handover_templates()',install)
        self.assertIn('install_print_formats()',install)

    def test_owner_inventory_stays_separate_from_native_company_stock(self):
        mode=json.loads((DOC/'cf_site_store/cf_site_store.json').read_text())
        op=next(f for f in mode['fields'] if f['fieldname']=='stock_mode')['options']
        self.assertIn('Owner-Owned Operational Stock',op)
        self.assertIn('Company-Owned ERP Stock',op)
        controller=(DOC/'cf_owner_material_movement/cf_owner_material_movement.py').read_text()
        self.assertIn('SELECT name FROM `tabCF Site Store` WHERE name=%s FOR UPDATE',controller)
        self.assertIn('different owners require separate documented return and receipt',controller)
        self.assertNotIn('Payment Entry',controller)
        self.assertIn('owner_qty',controller)

    def test_reports_and_client_script(self):
        for name in ('cf_handover_progress','cf_owner_material_balance'):
            self.assertTrue((R/'code_fitout/code_fitout/report'/name/(name+'.json')).exists())
        hook=(R/'code_fitout/hooks.py').read_text()
        self.assertIn('"CF Stage Handover": "public/js/cf_stage_handover.js"',hook)
        self.assertIn('"CF Site Store": "public/js/cf_site_store.js"',hook)

if __name__=='__main__':unittest.main()
