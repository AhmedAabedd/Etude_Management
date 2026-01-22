from odoo import models, fields, api, _



class EtudeCity(models.Model):
    _name = 'etude.city'


    name = fields.Char(string="Name", placeholder="e.g. Erriadh", required=True)

    student_ids = fields.One2many('etude.student', 'city_id')
    student_count = fields.Integer(string="Students Count", compute="_compute_student_count", store=True)

    lycee_ids = fields.One2many('etude.lycee', 'city_id')
    lycee_count = fields.Integer(string="Lycées Count", compute="_compute_lycee_count", store=True)


    @api.depends("student_ids")
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)
    
    @api.depends("lycee_ids")
    def _compute_lycee_count(self):
        for rec in self:
            rec.lycee_count = len(rec.lycee_ids)
    
    def action_view_student(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Students',
            'res_model': 'etude.student',
            'view_mode': 'list,form',
            'target': 'current', #to open in new view
            'domain': [('city_id', '=', self.id)],
            'context': {
                'default_city_id': self.id,
            }
        }

    def action_view_lycee(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Lycées',
            'res_model': 'etude.lycee',
            'view_mode': 'list,form',
            'target': 'current', #to open in new view
            'domain': [('city_id', '=', self.id)],
            'context': {
                'default_city_id': self.id,
            }
        }
    
