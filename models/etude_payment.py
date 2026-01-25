from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning



class EtudePayment(models.Model):
    _name = 'etude.payment'


    name = fields.Char(string="Name", compute="_compute_name", store=True)
    enrollment_id = fields.Many2one('etude.enrollment', string="Enrollment")
    student_id = fields.Many2one('etude.student', string="Student")
    total_amount = fields.Float(string="Total")
    paid_amount = fields.Float(string="Paid Amount")
    payment_date = fields.Date(string="Payment Date")


    @api.depends("student_id", "enrollment_id", "payment_date")
    def _compute_name(self):
        for rec in self:
            rec.name = "New Payment"
            if rec.id:
                date_str = fields.Datetime.to_string(rec.payment_date)[:10]
                rec.name = f"{rec.student_id.name} / {rec.enrollment_id.subject_id.name} / {date_str} / Payment {rec.id}"

    def create(self, vals):
        record = super().create(vals)

        if record.paid_amount == record.total_amount:
            record.enrollment_id.write({
                'payment_status': 'paid',
                'unpaid_amount': 0.0
            })
        elif record.paid_amount < record.total_amount:
            unpaid_amount = record.total_amount - record.paid_amount
            record.enrollment_id.write({
                'payment_status': 'partial',
                'unpaid_amount': unpaid_amount
            })
        else:
            raise UserError(f"Paid Amount cannot exceed Total Amount ({record.total_amount})")

        return record