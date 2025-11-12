from odoo import models, fields
 
class City(models.Model):
    _name = 'res.city'
    _description = 'City'
 
    name = fields.Char('City Name', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='Status', default='active')

    # _sql_constraints = [
    #     ('unique_city_name', 'unique(name)', 'The city name must be unique!'),
    # ]
    
    