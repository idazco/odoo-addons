# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval


class MappingContexts(models.Model):
    _name = 'odoo_etl_shell.etl_context'
    _description = 'Possible ETL Contexts'
    _order = 'name'

    module_name = fields.Char('Module Name', required=True)
    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True, translate=True)


class DataMapping(models.Model):
    _name = 'odoo_etl_shell.data_mapping'
    _description = 'Data mapping table'

    # Basic info
    module_name = fields.Char('Module Name', required=True)
    direction = fields.Selection([('in', 'Import'), ('out', 'Export'), ('any', 'Import/ExportExport')], string='Mapping Direction',
                                 default='in', required=True)
    etl_context = fields.Many2one('odoo_etl_shell.etl_context', string='Mapping Context')
    from_value = fields.Text('From value')
    to_value = fields.Text('To value')
    custom_exp = fields.Text('Custom Expression', help="Custom expressions that can be used in any way you need")
