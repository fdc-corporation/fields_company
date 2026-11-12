{
    'name': 'Herramientas Odoo - FDCCORP',
    'version': '1.0',
    'description': 'campos adicionales para empresas',
    'summary': '',
    'author': 'Yostin Palacios Calle',
    'website': 'http://fdc-corporation.com',
    'license': 'LGPL-3',
    'category': 'Uncategorized',
    'depends': [
        "pmant", 'base', 'contacts', 'mail', 'sale', 'stock', 'purchase',
        "web", "account_followup", "account", "crm"
    ],
    'data': [
        # SECURITY
        'security/security.xml',
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        # VIEWS
        "view/layout_report.xml",
        "view/view_company.xml",
        # REPORTS
        "report/report_paperformat.xml",
        "report/report_inheriit_sale.xml",
        "report/report_guias.xml",
        "report/report_factura.xml",
        "report/report_purchase_order.xml",
    ],
    'auto_install': False,
    'application': False,
}
