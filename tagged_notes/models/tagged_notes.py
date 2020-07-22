# -*- coding: utf-8 -*-
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import _, fields, models


class NotesTags(models.Model):
    _name = 'notes.tag'
    _description = 'Tags for notes'

    # fields
    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True, required=True)
    internal = fields.Boolean('Internal Notes Only', default=False, required=True)

    _sql_constraints = [
        ('notes_tags_uniq', 'unique(name)', 'You cannot have duplicate tags for notes'),
    ]


class NotesTagged(models.Model):
    _name = 'notes.tagged'
    _description = 'Tagged notes'

    # fields
    note = fields.Char('Note', required=True)
    tag_id = fields.Many2one('notes.tag', string='Note Tag', required=True, ondelete='restrict', delegate=True)
    # - support versioning
    original_note_id = fields.Many2one('notes.tagged', string='Replaces', ondelete='restrict')
    # - soft deletable
    active = fields.Boolean('Active', default=True, required=True)
    # - this is basically the same paradigm from Odoo's mail.message - used to link to other data
    model = fields.Char('Related Document Model', index=True)
    res_id = fields.Many2oneReference('Related Document ID', index=True, model_field='model')


class ProjectTaggedNotes(models.Model):
    _inherit = 'project.project'

    def action_open_notes_tagged(self):
        self.ensure_one()
        project_id = self.id
        return {
            'name': 'Notes',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('tagged_notes.project_notes_tree').id,
            'view_mode': 'tree',
            'res_model': 'notes.tagged',
            'context': {'default_res_id': self.id, 'default_model': 'project.project'},
            'domain': [('res_id', '=', project_id), ('model', '=', 'project.project')],
        }

