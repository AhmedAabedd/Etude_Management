from odoo import models, fields, api, _



class EtudeLycee(models.Model):
    _name = 'etude.lycee'

    
    name = fields.Char(string="Name", placeholder="e.g. Lycee Ibn Rachik", required=True)
    city_id = fields.Many2one('etude.city', string="City", required=True)

    student_ids = fields.One2many('etude.student' ,'city_id')
    student_count = fields.Integer(string="Students Count", compute="_compute_student_count", store=True)


    @api.depends("student_ids")
    def _compute_student_count(self):
        for rec in self:
            count = 0
            for student in rec.student_ids:
                count += 1
            rec.student_count = count

    def action_view_student(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Students',
            'res_model': 'etude.student',
            'view_mode': 'list,form',
            'target': 'current', #to open in new view
            'domain': [('lycee_id', '=', self.id)],
            'context': {
                'default_lycee_id': self.id,
            }
        }