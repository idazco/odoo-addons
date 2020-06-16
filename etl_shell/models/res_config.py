# -*- coding: utf-8 -*-

from odoo import fields, models, api
import os
import hashlib


class OdooEtlShellConfig(models.TransientModel):
    _name = 'odoo_etl_shell.config.settings'
    _inherit = 'res.config.settings'

    @api.model
    def _auto_init(self):
        result = super(OdooEtlShellConfig, self)._auto_init()
        """Making sure the queries are also updated if they changed"""
        # get the last state of the __init__.py file from the DB
        last_init_hash = self.env['ir.config_parameter'].sudo().get_param('odoo_etl_shell.__init__py.hash', default='')
        # get the current state of the same file
        package_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        current_init_hash = OdooEtlShellConfig._hash_of_file(self, package_path + '/../__init__.py')
        # call the database_alterations function if there is a change
        if last_init_hash != current_init_hash:
            from .. import database_alterations
            database_alterations(self._cr, self.env)
            # todo: add other functions as needed
            # save the file state so that we don't needlessly run the init again
            self.env['ir.config_parameter'].set_param('odoo_etl_shell.__init__py.hash', current_init_hash,  groups=['base.group_system'])
        return result

    def _hash_of_file(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()