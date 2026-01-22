from odoo import models, fields, api, _



class EtudeAttendance(models.Model):
    _name = 'etude.attendance'



    session_id = fields.Many2one('etude.session', string="Session")
    student_id = fields.Many2one('etude.student', string="Student")
    enrollment_id = fields.Many2one('etude.enrollment', string="Enrollment")
    sessions_remaining = fields.Integer(related="enrollment_id.sessions_remaining", store=True)
    status = fields.Boolean(string="Present", default=False, required=True)

    