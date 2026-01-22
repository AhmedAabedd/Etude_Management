from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class EtudeSession(models.Model):
    _name = 'etude.session'
    #_inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Name", compute="_compute_name", store=True)
    group_id = fields.Many2one('etude.group', string="Group", required=True)
    subject_id = fields.Many2one(related="group_id.subject_id", string="Subject", store=True)
    session_number = fields.Integer(string="Session Number", required=True)
    date = fields.Date(string="Date", required=True)
    start_time = fields.Datetime(string="Start Time", compute="_compute_start_time", store=True)
    end_time = fields.Datetime(string="End Time", compute="_compute_end_time", store=True)
    display_status = fields.Selection(
        [
            ('upcoming', 'Upcoming'),
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed'),
        ], string="Display Status", default="upcoming", required=True, compute="_compute_display_status"
    )
    stored_status = fields.Selection(
        [
            ('upcoming', 'Upcoming'),
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed'),
        ], string="Stored Status", default="upcoming", required=True, store=True, index=True #Index is used for faster filtering
    )
    note = fields.Text(string="Notes")

    attendance_line_ids = fields.One2many('etude.attendance', 'session_id')


    
    @api.depends('group_id', 'session_number', 'date')
    def _compute_name(self):
        for rec in self:
            rec.name = "New Session"
            if rec.group_id and rec.date:
                date_str = fields.Datetime.to_string(rec.date)[:10]
                rec.name = f"{rec.group_id.name} / S{rec.session_number} / {date_str}"
    
    @api.depends('date')
    def _compute_start_time(self):
        for rec in self:
            if rec.date and rec.start_time:
                rec.start_time = rec.start_time.replace(
                    year = rec.date.year,
                    month = rec.date.month,
                    day = rec.date.day
                )
            else: #if not rec.start_time (rec.date always True (required))
                rec.start_time = rec.date
    
    @api.depends('date')
    def _compute_end_time(self):
        for rec in self:
            if rec.date and rec.end_time:
                rec.end_time = rec.end_time.replace(
                    year = rec.date.year,
                    month = rec.date.month,
                    day = rec.date.day
                )
            else: #if not rec.end_time (rec.date always True (required))
                rec.end_time = rec.date

    def _compute_display_status(self):
        for rec in self:
            rec.display_status = 'upcoming'
            now = fields.Datetime.now()
            if rec.end_time :
                if now >= rec.start_time and now < rec.end_time:
                    rec.display_status = 'ongoing'
                elif now >= rec.end_time:
                    rec.display_status = 'completed'
    
    def _cron_update_session_status(self):
        """
        This method will be called automatically every 15 minutes
        to update the stored_status field for all sessions
        Note : self is the model class, not records,
               You need to first get the records
        """

        now = fields.Datetime.now()
        
        # 1- Find sessions that should be marked as ONGOING
        ongoing_sessions = self.search([
            ('start_time', '<=', now),
            ('end_time', '>', now),
            ('stored_status', '!=', 'ongoing') #Update only the changed
        ])

        if ongoing_sessions:
            ongoing_sessions.write({
                'stored_status': 'ongoing'
            })
        
        # 2- Find sessions that should be marked as COMPLETED
        completed_sessions = self.search([
            ('end_time', '<=', now),
            ('stored_status', '!=', 'completed'),
        ])

        if completed_sessions:
            completed_sessions.write({
                'stored_status': 'completed'
            })

        # 3- Find sessions that should be marked as UPCOMING
        upcoming_sessions = self.search([
            ('start_time', '>', now),
            ('stored_status', '!=', 'upcoming'),
        ])

        if upcoming_sessions:
            upcoming_sessions.write({
                'stored_status': 'upcoming'
            })
    
    def create(self, vals):

        session = super().create(vals)

        attendance_lines = []

        for student in session.group_id.student_ids:
            enrollment = student.enrollment_ids.filtered(
                lambda e: e.state == 'active' and e.group_id == session.group_id and e.subject_id == session.subject_id
            )
            
            if enrollment:
                attendance_lines.append((
                    0, 0, {
                            #'session_id': session.id, odoo set it automatically (reversed field of the relation One2many)
                            'student_id': student.id,
                            'enrollment_id': enrollment[0].id,
                            'status': False
                          }
                ))
        
        session.attendance_line_ids = attendance_lines
        
        return session

    #@api.model
    #def generate_attendance_lines(self, session):
            #"""Class method - can be called on model or record"""

            #attendance_lines = []

            #for student in session.group_id.student_ids:
            #    enrollment = student.enrollment_ids.filtered(
            #        lambda e: e.state == 'active' and e.group_id == session.group_id and e.subject_id == session.subject_id
            #    )

            #    if enrollment:
            #        attendance_lines.append((
            #            0, 0, {
                                #'session_id': session.id, odoo set it automatically (reversed field of the relation One2many)
            #                    'student_id': student.id,
            #                    'enrollment_id': enrollment[0].id,
            #                    'status': False
            #                }
            #        ))
                
            #    else:
            #        attendance_lines.append((
            #            0, 0, {
                                #'session_id': session.id, odoo set it automatically (reversed field of the relation One2many)
            #                    'student_id': student.id,
            #                    'enrollment_id': False,
            #                    'status': False
            #                }
            #        ))

            #return attendance_lines
    
    def refresh_attendance_lines(self):
        """Instance method that works on the record(s)"""
        
        for rec in self:  # Now works on self (the recordset)

            for line in rec.attendance_line_ids:
                if line.status == True:
                    raise UserError("Cannot refresh attendance list if a student is marked present !")

            attendance_lines = []

            for student in rec.group_id.student_ids:
                enrollment = student.enrollment_ids.filtered(
                    lambda e: e.state == 'active' and e.group_id == rec.group_id and e.subject_id == rec.subject_id
                )
                
                if enrollment:
                    attendance_lines.append((
                        0, 0, {
                                #'session_id': session.id, odoo set it automatically (reversed field of the relation One2many)
                                'student_id': student.id,
                                'enrollment_id': enrollment[0].id,
                                'status': False
                            }
                    ))
            
            # Remove ALL attendance lines
            rec.attendance_line_ids = [(5, 0, 0)]

            rec.attendance_line_ids = attendance_lines
        
    @api.onchange('attendance_line_ids')
    def calculate_sessions_attended(self):
        for rec in self:
            for attendance in rec.attendance_line_ids:
                if attendance.status == True:
                    if attendance.sessions_remaining == 0:
                        raise UserError("Enrollment expired !")
                    else:
                        attendance.enrollment_id.sessions_attended += 1
                else:
                    attendance.enrollment_id.sessions_attended -= 1

