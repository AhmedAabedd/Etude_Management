from odoo import models, fields, api, _



class EtudeLevel(models.Model):
    _name = 'etude.level'


    name = fields.Char(string="Name", placeholder="e.g. 3éme année", required=True)
    student_count = fields.Integer(string="Students Count", compute="_compute_student_count")
    group_count = fields.Integer(string="Groups Count", compute="_compute_group_count")


    def _compute_student_count(self):
        for rec in self:
            rec.student_count = self.env['etude.student'].search_count([('level_id', '=', rec.id)])
    
    def _compute_group_count(self):
        for rec in self:
            rec.group_count = self.env['etude.group'].search_count([('level_id', '=', rec.id)])


    def action_view_student(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Students',
            'res_model': 'etude.student',
            'view_mode': 'list,form',
            'target': 'current', #to open in new view
            'domain': [('level_id', '=', self.id)],
            'context': {
                'default_level_id': self.id,
            }
        }

    def action_view_group(self):
        self.ensure_one()

        action = self.env.ref('etude_management.action_etude_group').read()[0]

        action['domain'] = [('level_id', '=', self.id)]
        action['context'] = {
            'default_level_id': self.id,
        }

        return action
    
        #IF THE ACTION ALREADY HAS CONTEXT
        #ctx = dict(self.env.context)
        #ctx.update({
        #    'default_group_id': self.id,
        #})

        #action['context'] = ctx