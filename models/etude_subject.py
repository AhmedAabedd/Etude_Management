from odoo import models, fields, api, _




class EtudeSubject(models.Model):
    _name = 'etude.subject'


    name = fields.Char(string="Name", required=True)
    monthly_fee = fields.Float(String="Monthly Fee", required=True)
    description = fields.Text(string="Description", placeholder="You can describe this subject here ...")
    active = fields.Boolean(String="Active", default=True)
    
    group_ids = fields.One2many('etude.group', 'subject_id')
    group_count = fields.Integer(string="Groups Count", compute="_compute_group_count", store=True)

    @api.depends("group_ids")
    def _compute_group_count(self):
        for rec in self:
            rec.group_count = len(rec.group_ids)
    
    def action_view_group(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'View Groups',
            'res_model': 'etude.group',
            'view_mode': 'list,form',
            'target': 'current', #to open in new view
            'domain': [('subject_id', '=', self.id)],
            'context': {
                'default_subject_id': self.id,
            }
        }
