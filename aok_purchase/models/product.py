# -*- coding: utf-8 -*-

from odoo import api, fields, models
from html2text import html2text


class ProductSupplierinfoFixedCosts(models.Model):
    _name = 'product.supplierinfo.fixed.costs'
    _rec_name = 'cost_category'

    cost_category = fields.Char(string='Kostenkategorie', translate=True)
    amount = fields.Float(string='Betrag')
    supplier_id = fields.Many2one("product.supplierinfo", string="Supplier")


class ProductSupplierinfoVariableCosts(models.Model):
    _name = 'product.supplierinfo.variable.costs'
    _rec_name = 'cost_category'

    cost_category = fields.Char(string='Kostenkategorie', translate=True)
    amount = fields.Float(string='Betrag')
    supplier_id = fields.Many2one("product.supplierinfo", string="Supplier")


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.depends('min_qty', 'fix_cost_ids', 'variable_cost_ids', 'fix_cost_ids.amount', 'variable_cost_ids.amount')
    def _total_uom_amount(self):
        for record in self:
            min_qty = record.min_qty or 1.0
            record.total_uom_amount = record.price + (sum(record.fix_cost_ids.mapped('amount')) / min_qty) + sum(record.variable_cost_ids.mapped('amount'))

    fix_cost_ids = fields.One2many('product.supplierinfo.fixed.costs', 'supplier_id', string='Fixed Cost', copy=True)
    variable_cost_ids = fields.One2many('product.supplierinfo.variable.costs', 'supplier_id', string='Variable Cost', copy=True)
    total_uom_amount = fields.Monetary(string="Gesamtpreis/ME", compute='_total_uom_amount')
    sim_sales_price = fields.Float(string='Sim Sales Price')
    margin_per = fields.Float(string='Margin (%)')
    margin = fields.Float(compute="_compute_margin", string='Margin (€)')

    @api.onchange('sim_sales_price', 'total_uom_amount', 'margin_per')
    def _onchange_margin(self):
        context = dict(self.env.context or {})
        if context.get('from_sales_price'):
            self.margin_per = ((self.sim_sales_price - self.total_uom_amount) / (self.total_uom_amount or 1.0)) * 100
        if context.get('from_margin'):
            self.sim_sales_price = self.total_uom_amount + self.total_uom_amount * (self.margin_per / 100)

    def _compute_margin(self):
        for record in self:
            record.margin = (record.sim_sales_price - record.total_uom_amount) * record.min_qty

class ProductTemplate(models.Model):
    _inherit = "product.template"

    seller_ids = fields.One2many(copy=True)


class ProductProduct(models.Model):
    _inherit = "product.product"

    checklist_category_id = fields.Many2one('attributes.checklist.category', string='Checklist Category')
    checklist_ids = fields.One2many('product.attributes.checklist', 'product_id', string='Checklist Attribute', copy=True)
    description = fields.Html(string='Additional Information')
    sustained = fields.Boolean(string='Nachhaltig')
    delivery_strategy = fields.Selection([
        ('direktauslieferung', 'Direktauslieferung'),
        ('verteiler', 'Verteiler'),
        ('teil-direktauslieferung', 'Teil-Direktauslieferung'),
        ('einlagerung', 'Einlagerung')], string='Delivery Strategy')

    def add_to_description(self):
        self.ensure_one()
        description = ""
        for checklist in self.checklist_ids:
            description += checklist.name.name or ''
            description += "\t\t\t"
            description += checklist.value or ''
            description += "\n"
        description += "\n\n"
        description += html2text(self.description or '')
        self.write({'description_purchase': description})

    @api.onchange('checklist_category_id')
    def _onchange_checklist_category_id(self):
        self.checklist_ids = False
        if self.checklist_category_id:
            vals = []
            for attribute in self.checklist_category_id.attribute_ids:
                vals.append({'product_id': self.id, 'name': attribute.id, 'require': attribute.require})
            self.checklist_ids = vals
            self.description = self.checklist_category_id.description
