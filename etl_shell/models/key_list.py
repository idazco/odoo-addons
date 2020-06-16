# -*- coding: utf-8 -*-

from odoo import models, fields


class KeyList(models.Model):
    _name = 'odoo_etl_shell.key_list'
    _description = 'Key List'

    list_name = fields.Char('List Name', required=True, default='white_list', invisible=True)
    name = fields.Char('Value Name', required=True)
    is_active = fields.Boolean('Activate', required=True, default=False)
    module_name = fields.Char('Module', required=True)
