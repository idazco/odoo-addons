# -*- coding: utf-8 -*-
from dicttoxml import dicttoxml


class DB:

    @staticmethod
    # type: (object, str, [str]) -> [dict]
    def all(cr, sql, params=None):
        cr.execute(sql, params)
        return cr.dictfetchall()

    @staticmethod
    def one(cr, sql, params=None):
        cr.execute(sql, params)
        return cr.dictfetchone()

    @staticmethod
    def one_xml(cr, sql, params=None):
        data = DB.one(cr, sql, params)
        if not data:
            return None
        return dicttoxml(data)

    @staticmethod
    def all_xml(cr, sql, params=None):
        data = DB.all(cr, sql, params)
        if not data:
            return None
        return dicttoxml(data)

    @staticmethod
    def name(cr):
        cr.execute("SELECT current_database();")
        return cr.dictfetchone()['current_database']

    @staticmethod
    def ir_config_parameter(cr, key):
        r = DB.one(cr, "SELECT value FROM ir_config_parameter WHERE key = %s", [key])
        if r:
            if 'value' in r:
                return r['value']
        return None

    @staticmethod
    def exists(cr, table_name, where_clause, where_params):
        """
        This is the fastest method checking if a record simply exists and MUST
        be used over any Odoo ORM methods for checking if a record exists.
        See https://stackoverflow.com/questions/7471625/fastest-check-if-row-exists-in-postgresql

        Example usage in an Odoo model:

            exists = DB.exists(
                self.env.cr,
                'some_db_table',
                'field_one=%s AND field_two=%s',
                ['foo', 2]
            )

        :param cr: environment cursor
        :param table_name: name of the table to check
        :param where_clause: the parameterized WHERE clause, *excluding* the WHERE statement
        :param where_params: array of parameters for the parameterized WHERE clause
        :return:
        """
        sql = "SELECT exists(SELECT 1 FROM %s WHERE %s)" % (table_name, where_clause)
        r = DB.one(cr, sql, where_params)
        return r['exists']
