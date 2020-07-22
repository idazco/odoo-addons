# -*- coding: utf-8 -*-
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import _, api, fields, models
from math import modf


class Task(models.Model):
    _inherit = 'project.task'

    # for deadlines that must occur on a specific time
    time_deadline = fields.Float('Deadline time', required="False", help="Optional. 24H format.")
    # how long deadline delivery takes, or lead time  (HH:mm)
    duration_deadline = fields.Float(
        'Deadline duration', help="Optional. Lead-time or follow-time for a deadline (hours:minutes).")
    # for display
    time_deadline_display = fields.Char()
    duration_deadline_minutes = fields.Integer()


    @api.model
    def create(self, vals):
        vals = self.__validate(vals)
        return super(Task, self).create(vals)

    def write(self, vals):
        vals = self.__validate(vals)
        return super(Task, self).write(vals)

    def __validate(self, vals):
        # check format
        def check(val, as_duration=False):
            if not val:
                return False
            mnt, hr = modf(val)
            mnt = int(abs(mnt) * 60)
            hr = abs(int(hr))
            if mnt > 59:
                return False
            if not as_duration:
                if hr > 23:
                    return False
                vals["time_deadline_display"] = "%s:%s" % (hr, mnt)
            else:
                vals["duration_deadline_minutes"] = (hr * 60) + mnt
            return hr + round(mnt / 60, 2)

        # time is being changed
        if "time_deadline" in vals:
            vals["time_deadline"] = check(vals["time_deadline"])
            time = vals["time_deadline"]
        else:
            time = self.time_deadline or 0

        # duration is being changed
        if "duration_deadline" in vals:
            if time:
                vals["duration_deadline"] = check(vals["duration_deadline"], True)
                if not vals["duration_deadline"]:
                    vals["duration_deadline_minutes"] = False
            else:
                vals["duration_deadline"] = False  # duration without time is invalid
                vals["duration_deadline_minutes"] = False
        return vals
