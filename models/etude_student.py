from odoo import models, fields, api



class EtudeStudent(models.Model):
    _name = 'etude.student'


    name = fields.Char(string="Name", required=True)
    level_id = fields.Many2one('etude.level', string="Level")
    lycee_id = fields.Many2one('etude.lycee', string="Lycée")
    city_id = fields.Many2one('etude.city', string="City")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    note = fields.Text(string="Note")
    active = fields.Boolean(string="Active", default=True)

    group_ids = fields.Many2many(
        'etude.group',
        'etude_group_student_rel',
        'student_id',
        'group_id'
    )
    group_count = fields.Integer(string="Group Counts", compute="_compute_group_count", store=True)

    enrollment_ids = fields.One2many('etude.enrollment', 'student_id')
    enrollment_count = fields.Integer(string="Enrollments Count", compute="_compute_enrollment_count", store=True)

    attendance_ids = fields.One2many('etude.attendance', 'student_id')
    attendance_count = fields.Integer(string="Attendances Count", compute="_compute_attendance_count", store=True)


    @api.depends("group_ids")
    def _compute_group_count(self):
        for rec in self:
            rec.group_count = len(rec.group_ids)
    
    @api.depends("enrollment_ids")
    def _compute_enrollment_count(self):
        for rec in self:
            rec.enrollment_count = len(rec.enrollment_ids)
    
    @api.depends("attendance_ids.status")
    def _compute_attendance_count(self):
        for rec in self:
            rec.attendance_count = len(rec.attendance_ids.filtered(lambda a: a.status == True))
    
    def action_view_group(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Groups',
            'res_model': 'etude.group',
            'view_mode': 'list,form',
            'target': 'current', #to open in new view
            'domain': [('id', 'in', self.group_ids.ids)],
            #'context': {
            #    'default_student_ids': [(4, self.id)], #link this student to the list of students
            #}
        }

    def action_view_enrollment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Enrollments',
            'res_model': 'etude.enrollment',
            'view_mode': 'list,form',
            'target': 'current', #to open in new view
            'domain': [('student_id', '=', self.id)],
            'context': {
                'default_student_id': self.id,
            }
        }
    
    def action_view_session(self):
        self.ensure_one()
        attendance_present = self.attendance_ids.filtered(lambda a: a.status == True)
        session_ids = attendance_present.mapped('session_id').ids

        return {
            'type': 'ir.actions.act_window',
            'name': 'View Attended Sessions',
            'res_model': 'etude.session',
            'view_mode': 'list,form',
            'target': 'current',
            'domain': [('id', 'in', session_ids)],
        }


