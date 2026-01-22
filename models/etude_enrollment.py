from odoo import models, fields, api, _



class EtudeEnrollment(models.Model):
    _name = 'etude.enrollment'



    name = fields.Char(strimg="Name", compute="_compute_name", store=True)

    student_id = fields.Many2one('etude.student', string="student", required=True)
    subject_id = fields.Many2one('etude.subject', string="Subject", required=True)
    group_id = fields.Many2one('etude.group', string="Group", domain="[('subject_id', '=', subject_id)]", required=True)

    start_date = fields.Date(String="Start Date")
    end_date = fields.Date(string="End Date")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('expired', 'Expired'),
        ],string='Status', default='draft', required=True, tracking=True, compute="_compute_state", store=True
    )
    sessions_number = fields.Integer(string="Number of Sessions", required=True, default=4)
    sessions_attended = fields.Integer(string="Attended Sessions")
    sessions_remaining = fields.Integer(string="Remaining Sessions", compute="_compute_sessions_remaining", store=True)

    note = fields.Text(string="Notes")

    payment_id = fields.Many2one('etude.payment')




    @api.depends("sessions_remaining")
    def _compute_state(self):
        for rec in self:
            if rec.sessions_remaining > 0 and rec.state == 'expired':
                rec.state = 'active'
                rec.add_student_to_group()
            elif rec.sessions_remaining == 0 and rec.state == 'active':
                rec.state = 'expired'

    
    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.remove_student_from_group()

    def action_active(self):
        for rec in self:
            rec.state = 'active'
            rec.add_student_to_group()
    
    def action_expired(self):
        for rec in self:
            rec.state = 'expired'
            rec.remove_student_from_group()

    @api.depends("sessions_attended", "sessions_number")
    def _compute_sessions_remaining(self):
        for rec in self:
            rec.sessions_remaining = rec.sessions_number - rec.sessions_attended
            rec.sessions_attended = rec.sessions_number - rec.sessions_remaining

    @api.onchange('subject_id')
    def reset_group_id(self):
        for rec in self:
            if rec.subject_id != rec.group_id.subject_id:
                rec.group_id = False

    def create(self, vals):
        record = super().create(vals)

        if record.group_id and record.student_id:
            for student in record.group_id.student_ids:
                if student.id == record.student_id.id:
                    return record
                
            record.group_id.write({
                'student_ids': [(4, record.student_id.id)]
            })

        return record
    
    def add_student_to_group(self):
        for rec in self:
            if rec.group_id and rec.student_id:
                if rec.student_id not in rec.group_id.student_ids:
                    rec.group_id.write({
                        'student_ids': [(4, rec.student_id.id)]
                    })
                    #rec.group_id.student_ids += rec.student_id
    
    def remove_student_from_group(self):
        for rec in self:
            if rec.group_id and rec.student_id:
                if rec.student_id in rec.group_id.student_ids:
                    rec.group_id.write({
                        'student_ids': [(4, rec.student_id.id)]
                    })
                    #rec.group_id.student_ids -= rec.student_id

    
    
    
    
