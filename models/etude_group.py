from odoo import models, fields, api, _



class EtudeGroup(models.Model):
    _name = 'etude.group'




    name = fields.Char(string="Name", required=True)
    level_id = fields.Many2one('etude.level', string="Level")
    subject_id = fields.Many2one('etude.subject', string="Subject", required=True)
    note = fields.Text(string="Notes")

    student_ids = fields.Many2many(
        'etude.student',
        'etude_group_student_rel',
        'group_id',
        'student_id'
    )
    student_count = fields.Integer(string="Students Count", compute="_compute_student_count", store=True)

    session_ids = fields.One2many('etude.session', 'group_id')
    session_count = fields.Integer(string="Sessons Count", compute="_compute_session_count")



    @api.depends("student_ids")
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)
    
    @api.depends("session_ids")
    def _compute_session_count(self):
        for rec in self:
            rec.session_count = len(rec.session_ids)
    
    def action_view_session(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Sessions',
            'res_model': 'etude.session',
            'view_mode': 'list,form',
            'target': 'current', #to open in new view
            'domain': [('group_id', '=', self.id)],
            'context': {
                'default_group_id': self.id,
            }
        }