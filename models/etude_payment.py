from odoo import models, fields, api, _



class EtudePayment(models.Model):
    _name = 'etude.payment'


    name = fields.Char(string="Name", required=True)
    enrollment_id = fields.Many2one('etude.enrollment', string="Enrollment")
    student_id = fields.Many2one('etude.student', string="Student")
    total_amount = fields.Float(related="enrollment_id.total_amount", store=True)
    payment_date = fields.Date(string="Payment Date")