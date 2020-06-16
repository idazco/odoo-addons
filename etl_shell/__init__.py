import models
import logging

_logger = logging.getLogger(__name__)


def database_alterations(cr, registry):
    _logger.info('Implementing database_alterations')

    # Create a compound index for the most common query context which also
    # ensures that from_value is unique per module_name and etl_context
    cr.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS  idx_odoo_etl_shell_data_mapping_compound_1 "
        "ON odoo_etl_shell_data_mapping (module_name, etl_context, from_value);"
    )