from odoo import models, fields, api, _



class EtudePayment(models.Model):
    _name = 'etude.payment'


    name = fields.Char(string="Name", required=True)