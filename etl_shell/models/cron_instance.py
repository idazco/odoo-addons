# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from subprocess import Popen


class IRCronInstance(models.Model):
    _name = 'ir.cron.instance'
    _description = 'Scheduled Action Instance'

    # Basic info
    name = fields.Char('Job Instance ID', required=True)
    step_id = fields.Many2one('etl.step', string='Related Step')
    pid = fields.Integer('Process ID')
    progress = fields.Integer('Progress')
    # Need to check every 1 sec if its running
    run_state = fields.Selection([('start', 'Start'),
                                  ('run', 'Run'),
                                  ('stop',  'Stop'),
                                  ('pause', 'Pause')], string='Run State', default='start')
    cron_id = fields.Many2one('ir.cron', string='Scheduled Action')
    date_start = fields.Datetime('Instance Start', default=lambda self: fields.datetime.now())
    date_end = fields.Datetime('Instance End', help='if not empty, it means that the job is completed')

    @api.model
    def run_next_steps(self, step_ids):
        """ This method must be instantiated from the xml-rpc
        Using the correct parent step_id

        :return:
        """
        step_id = step_ids[0] if len(step_ids) > 0 else False
        get_param = self.env['ir.config_parameter'].sudo().get_param
        print step_id
        next_steps = self.env['etl.step'].search([('parent_id', '=', step_id)])
        for step in next_steps:
            step.date_end = fields.datetime.now()
            script_path = step.script_path.format(base_demo_path=get_param('odoo_etl_shell.base_demo_path'))
            if script_path:
                p = Popen([script_path, str(step.id)])
                self.env['ir.cron.instance'].sudo().create({
                    'name': step.name,
                    'step_id': step.id,
                    'pid': p.pid
                })
                return True
