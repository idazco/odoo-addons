# -*- coding: utf-8 -*-

import odoo.addons.decimal_precision as dp
from odoo import models, fields, api, _
from ..lib.db import DB
from odoo.exceptions import ValidationError
import json


class ImportLedger(models.Model):
    _name = 'odoo_etl_shell.import_ledger'
    _description = 'Imported ledger data'

    # Fields that match Odoo's account.analytic.line model
    # This is the data common to all data imports
    name = fields.Char('Description', required=True, readonly=True)
    date = fields.Date('Date', required=True, index=True, readonly=True)
    unit_amount = fields.Float('Quantity', default=0.0, readonly=True)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), readonly=True)
    amount = fields.Monetary('Amount', required=True, readonly=True)

    # Common ledger data (purely from the import source, before linking to any Odoo data)
    source = fields.Char('Source', readonly=True, required=True)
    import_key = fields.Char('Import Key', readonly=True, required=True)
    ref = fields.Char('Reference', readonly=True)
    import_user = fields.Char('User', readonly=True)

    # Linked Odoo data (after data is imported, its processed and linked)
    account_import_key = fields.Char('Account Import Key', readonly=True, required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='File', readonly=True)

    # Required field for amount
    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        default=lambda self: self.env.user.company_id.currency_id.id,
        required=True)

    # Required to know which module is installed for processing rules the data being added here
    sync_module = fields.Many2one('ir.module.module', required=True)
    metadata = fields.Char('Metadata', required=False)
    product_id = fields.Many2one('product.product', required=False)

    # Processing data
    # - This can be added by the sync, or by a user:
    log = fields.Char("Log", help="Note describing why a record was processed this way")
    # - We need to know when the record was processed
    processed = fields.Date("Processed", help="Date this record was processed for importing to an account")
    must_force = fields.Boolean("Force Import", required=True, default=False)
    # - We need to know if a specific rule was applied automatically by any code
    data_mapping_id = fields.Many2one('odoo_etl_shell.data_mapping', string="Mapping rule applied")

    _sql_constraints = [(
        'field_unique', 'unique(sync_module, source, import_key)', 'Record already exists',
    )]

    def module_id(self):
        return self.env['ir.module.module'].search_read([['name', '=', self._module]], ['id'])[0]['id']

    def row_exists(self, import_key):
        return DB.exists(
            self.env.cr,
            'odoo_etl_shell_import_ledger',
            'sync_module=%s AND source=%s AND import_key=%s',
            [self.module_id(), self.sync_source_code(), import_key]
        )

    def _load_record(self, values):
        """This method is meant to be overridable in other modules
        :param values:
        :return:
        """
        return self.env['account.analytic.line'].with_context(etl=True).create(values)

    @api.model
    def load_record(self):
        ids = []
        for row in self:
            vals = row.read()[0]
            account_ids = self.env['project.project'].search([
                ('import_key', '=', row.account_import_key)
            ])
            if len(account_ids) != 1:
                raise ValidationError(_('There is a problem with the account import_key "%s"') % row.account_import_key)
            account_id = account_ids[0].analytic_account_id.id
            values = {
                'price_unit': vals['price_unit'],
                'account_id': vals['analytic_account_id'][0] or account_id,
                'name': vals['ref'],
                'ref': vals['ref'],
                'user_id': self.env.user.id,
                'import_key': vals['import_key'],
                'date': vals['date'],
                'amount': vals['amount'],
                'unit_amount': vals['unit_amount'],
                'product_id': vals['product_id'][0],
            }
            ids.append(row._load_record(values))
        return ids

    def sync_source_code(self):
        """
        You must implement your own functionality for this method and set your own sync source code.
        The sync source code some logical char value you use to uniquely identify what the source system
        or endpoint is for the data being imported.
        :return:
        """
        raise NotImplementedError

    def validate_upsert(self, inputs, new):
        """
        Implement this method to validate or alter your data as needed.
        NOTE: Make sure that your implementation returns the "new" parameter.
        :param inputs: A row of data submitted from the caller to upsert
        :param new: A new row of data to validate / alter, then insert into Odoo
        :return: bool, new | str: Return True and new if validation is OK, else False and error string
        """
        raise NotImplementedError

    def batch_upsert(self, rows):
        inserted = 0
        errors = []
        try:
            if type(rows) is not dict:
                rows = json.loads(rows)
            for row in rows:
                if row['import_key'].strip() == "":
                    return False, "import_key is required"

                # first see if the row exists and if it does then skip it
                if self.row_exists(row['import_key']):
                    continue

                new = {
                    # calculated data
                    "sync_module": self.module_id(),
                    "source": self.sync_source_code(),
                    # user provided data
                    "account_import_key": row['account_import_key'],
                    "import_key": row['import_key'],
                    "name": row['name'],
                    "ref": row['ref'],
                    "date": row['date'],
                    "unit_amount": row['unit_amount'],
                    "price_unit": row['price_unit'],
                    "amount": row['amount'],
                }

                ok, new = self.validate_upsert(row, new)
                if not ok:
                    return ok, new
                self.env['odoo_etl_shell.import_ledger'].sudo().create(new)
                try:
                    self.env.cr.commit()
                    inserted = inserted + 1
                except Exception, e:
                    errors.append(e.message)

        except Exception, e:
            return False, e.message

        if len(errors) > 0:
            return False, errors

        return True, inserted

