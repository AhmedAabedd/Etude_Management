from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning



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
    sessions_attended = fields.Integer(string="Attended Sessions", compute="_compute_sessions_attended", store=True)
    sessions_remaining = fields.Integer(string="Remaining Sessions", compute="_compute_sessions_remaining", store=True)

    note = fields.Text(string="Notes")

    attendance_ids = fields.One2many('etude.attendance', 'enrollment_id')


    total_amount = fields.Float(string="Total")
    unpaid_amount = fields.Float(string="Unpaid", compute="_compute_unpaid_amount", store=True)
    payment_status = fields.Selection(
        [
            ('paid', 'Paid'),
            ('unpaid', 'Unpaid'),
            ('partial', 'Partial'),
        ], string="Payment Status", default="unpaid", required=True, compute="_compute_payment_status", store=True
    )
    payment_ids = fields.One2many('etude.payment', 'enrollment_id')
    payment_count = fields.Integer(string="Payments Count", compute="_compute_payment_count", store=True)




    @api.depends("student_id", "group_id", "start_date")
    def _compute_name(self):
        for rec in self:
            rec.name = "New Enrollment"
            if rec.student_id and rec.group_id and rec.start_date and rec.id:
                rec.name = f"{rec.student_id.name} / {rec.group_id.name} / {rec.id}"

    @api.depends("sessions_remaining")
    def _compute_state(self):
        for rec in self:
            #Set state to ACTIVE
            if rec.sessions_remaining > 0 and rec.state == 'expired':
                other_active = rec.get_other_active_enrollment()
                if other_active:
                    #raise UserError("Student already has an active enrollment to this group !")
                    action = self.env.ref('etude_management.action_enrollment_form_only').read()[0]
                    action['res_id'] = other_active.id
                    raise RedirectWarning(
                        f"Student already has active enrollment: {other_active.name}",
                        action,
                        f"View Enrollment",
                    )
                else:
                    rec.state = 'active'
                    rec.add_student_to_group()
            #Set state to Expired
            elif rec.sessions_remaining == 0 and rec.state == 'active':
                rec.state = 'expired'
                rec.remove_student_from_group()

    
    def action_draft(self):
        for rec in self:
            if rec.state == 'active':
                rec.remove_student_from_group()
            rec.state = 'draft'

    def action_active(self):
        for rec in self:
            other_active = rec.get_other_active_enrollment()
            if other_active:
                #Raise Warning if other active nerollment exist
                action = self.env.ref('etude_management.action_enrollment_form_only').read()[0]
                action['res_id'] = other_active.id
                raise RedirectWarning(
                    f"Student already has active enrollment: {other_active.name}",
                    action,
                    f"View Enrollment",
                )
            
            else:
                if rec.sessions_remaining > 0:
                    rec.state = 'active'
                    rec.add_student_to_group()
                else:
                    raise ValidationError("Cannot activate enrollment with 0 remaining sessions !")
    
    def action_expired(self):
        for rec in self:
            if rec.state == 'active':
                rec.remove_student_from_group()
            rec.state = 'expired'
    
    @api.depends("attendance_ids", "attendance_ids.status")
    def _compute_sessions_attended(self):
        for rec in self:
            rec.sessions_attended = len(rec.attendance_ids.filtered(lambda a: a.status == True))

    @api.depends("sessions_attended", "sessions_number")
    def _compute_sessions_remaining(self):
        for rec in self:
            rec.sessions_remaining = rec.sessions_number - rec.sessions_attended

    @api.onchange('subject_id')
    def reset_group_id(self):
        for rec in self:
            if rec.subject_id != rec.group_id.subject_id:
                rec.group_id = False
    
    def get_other_active_enrollment(self):
        self.ensure_one()
        other_active = self.student_id.enrollment_ids.filtered(
            lambda e: e.group_id == self.group_id
                    and e.state == 'active'
                    and e.id != self.id
        )

        return other_active[:1]  # Return first or empty recordset
    
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
                    other_active = rec.get_other_active_enrollment()
                    if not other_active:
                        rec.group_id.write({
                            'student_ids': [(3, rec.student_id.id)]
                        })
                    #rec.group_id.student_ids -= rec.student_id

    def action_view_attendance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Attendances',
            'res_model': 'etude.attendance',
            'view_mode': 'list,form',
            'target': 'current', #to open in new view
            'domain': [('enrollment_id', '=', self.id)],
            'context': {
                'search_default_filter_present': 1,  # This activates the filter
            }
        }

    @api.depends("payment_ids")
    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(rec.payment_ids)

    @api.depends("payment_ids", "payment_ids.paid_amount")
    def _compute_payment_status(self):
        for rec in self:
            paid_amount_sum = sum(rec.payment_ids.mapped('paid_amount'))
            if paid_amount_sum == 0:
                rec.payment_status = 'unpaid'
            elif paid_amount_sum < rec.total_amount:
                rec.payment_status = 'partial'
            elif paid_amount_sum == rec.total_amount:
                rec.payment_status = 'paid'
    
    @api.depends("total_amount", "payment_ids", "payment_ids.paid_amount")
    def _compute_unpaid_amount(self):
        for rec in self:
            paid_amount_sum = sum(rec.payment_ids.mapped('paid_amount'))
            rec.unpaid_amount = rec.total_amount - paid_amount_sum
    
    def action_view_payment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Payments',
            'res_model': 'etude.payment',
            'view_mode': 'list,form',
            'target': 'current', #to open in new view
            'domain': [('enrollment_id', '=', self.id)]
        }
    
    def open_create_payment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Payment',
            'res_model': 'etude.payment',
            'view_mode': 'form',
            'target': 'new',   # opens in modal
            'context': {
                'default_enrollment_id': self.id,
                'default_student_id': self.student_id.id,
                'default_total_amount': self.unpaid_amount,
                'default_payment_date': fields.Datetime.now()
            },
        }
    
    

    
    
    
