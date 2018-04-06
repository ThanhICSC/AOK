# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'AOK Inventory',
    'category': 'Warehouse',
    'sequence': 60,
    'summary': 'AOK Inventory',
    'description': "",
    'website': 'https://www.odoo.com/',
    'depends': ['delivery', 'purchase'],
    'data': [
        'views/sale_views.xml',
        'views/stock_picking_views.xml',
        'views/product_template_views.xml',
        'views/stock_move_line_views.xml',
        'views/stock_location_views.xml',
        'report/report_stockpicking_operations.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}