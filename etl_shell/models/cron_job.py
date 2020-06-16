from odoo import fields, models, api, modules
from subprocess import Popen


class JobSteps(models.Model):
    """ Defines sequential script steps for ETL routines
    The target script will be in charge of running the
    next steps using a xml-rpc call on the step object
    """

    _name = 'etl.step'

    name = fields.Char('Step Name', required=True)
    default_timeout = fields.Integer('Default Timeout(s)', help='Default timeout in seconds')
    parent_id = fields.Many2one('etl.step', string='Parent Step')
    # will not be used if parent_id=False because on startup we use
    # config param: odoo_etl_shell.script_path
    script_path = fields.Char('Script Path')

    @api.model
    def run_steps(self, reference):
        ir_model_data = self.env['ir.model.data']
        args = reference.split('.')
        step_id = ir_model_data.get_object_reference(args[0], args[1])[1]
        get_param = self.env['ir.config_parameter'].sudo().get_param
        start_step = self.env['etl.step'].search([('id', '=', step_id)])
        # If parent_id=False then we must run the ir.config_parameter
        if start_step:
            cron_job = self.env['ir.cron'].sudo().search([('args', 'ilike', reference)])
            script_path = start_step.script_path.format(base_demo_path=get_param('odoo_etl_shell.base_demo_path'))
            if script_path:
                # First argument of the script ($1) will be the step_id
                p = Popen([script_path, str(start_step.id)])
                self.env['ir.cron.instance'].sudo().create({
                    'name': start_step.name,
                    'step_id': start_step.id,
                    'cron_id': cron_job.id,
                    'pid': p.pid
                })
                return True

    @api.model
    def get_etl_config(self, etl_module_name):
        """This is an abstract method that needs to be extended
        by all ETL modules

        :param etl_module_name:
        :return: dict()
        """
        return {}

class IRCron(models.Model):
    _inherit = 'ir.cron'

    instance_ids = fields.One2many('ir.cron.instance', 'cron_id', string='Job Instances')
