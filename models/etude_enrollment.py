from odoo import models, fields, api, _



class EtudeEnrollment(models.Model):
    _name = 'etude.enrollment'



    name = fields.Char(string="Name", compute="_compute_name", store=True)

    student_id = fields.Many2one('etude.student', string="student", required=True)
    subject_id = fields.Many2one('etude.subject', string="Subject", required=True)
    group_id = fields.Many2one('etude.group', string="Group", domain="[('subject_id', '=', subject_id)]", required=True)
    monthly_fee = fields.Float(related="subject_id.monthly_fee", store=True)

    start_date = fields.Date(String="Start Date", required=True)
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




    @api.depends("student_id", "group_id", "start_date")
    def _compute_name(self):
        for rec in self:
            rec.name = "New Enrollment"
            if rec.student_id and rec.group_id and rec.start_date and rec.id:
                rec.name = f"{rec.student_id.name} / {rec.group_id.name} / {rec.id}"

    @api.depends("sessions_remaining")
    def _compute_state(self):
        for rec in self:
            if rec.sessions_remaining > 0 and rec.state == 'expired':
                rec.state = 'active'
                rec.add_student_to_group()
            elif rec.sessions_remaining == 0 and rec.state == 'active':
                rec.state = 'expired'
                rec.remove_student_from_group()

    
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
    
    def add_student_to_group(self):
        for rec in self:
            if rec.group_id and rec.student_id:
                if rec.student_id not in rec.group_id.student_ids: #Mouch lezma khater odoo ken yal9a deja fama relation mayaaml chy
                    rec.group_id.write({
                        'student_ids': [(4, rec.student_id.id)]
                    })
                    #rec.group_id.student_ids += rec.student_id
    
    def remove_student_from_group(self):
        for rec in self:
            if rec.group_id and rec.student_id:
                if rec.student_id in rec.group_id.student_ids:
                    rec.group_id.write({
                        'student_ids': [(3, rec.student_id.id)]
                    })
                    #rec.group_id.student_ids -= rec.student_id

    
    
    
    
