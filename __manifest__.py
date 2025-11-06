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
        'base', 'contacts', 'mail', 'sale', 'stock',"web"
    ],
    'data': [
        # SECURITY
        'security/security.xml',
        "security/ir_rule.xml",
        # VIEWS
        "view/view_sale_order.xml",
        "view/layout_report.xml",
        "view/view_company.xml",
        "view/view_crm_lead.xml",
        # REPORTS
        "report/report_inheriit_sale.xml",
        "report/report_guias.xml",
        # "report/report_factura.xml",
    ],
    'auto_install': False,
    'application': False,
}