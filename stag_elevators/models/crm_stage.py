from odoo import api, models, fields
# from odoo.addons.crm_sale_subscription.models.crm_lead import CrmLead

class CrmStage(models.Model):
    _inherit = 'crm.stage'

    order = fields.Integer(string="Order By", default=1)
    is_final = fields.Boolean(string="Is Final Stage")
    description = fields.Text()
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')])
    is_crm= fields.Boolean("Is CRM")
    stage = fields.Selection([('sales','sales'),('crm','crm'),('production','production')])
    

class Leads(models.Model):
    _inherit ='crm.lead'

    lead_id = fields.Char(string="Lead Id")
    lead_platform = fields.Char(string="Lead Platform")
    type_of_construction = fields.Char(string="Type of construction")
    no_of_floor = fields.Char(string="No of floor")
    pre_comment = fields.Text()
    prospect_hit = fields.Char()
    lead_comment = fields.Text()
    lift_model = fields.Selection([
    ('SE1', 'SE1'),
    ('SE2', 'SE2'),
    ('SE3','SE3')
], string="Lift Model")
    followup_ids = fields.One2many('lead.followup', 'lead_id', string="Followups")
    is_duplicate = fields.Boolean(
        string="Is Duplicate",
        compute="_compute_is_duplicate",
        store=True
    )

    @api.depends('phone')
    def _compute_is_duplicate(self):
        for lead in self:
            if lead.phone:
                # Find all leads with the same number (sorted by create_date)
                all_same = self.search([
                    ('phone', '=', lead.phone)
                ], order='create_date asc')

                # If more than one exists → mark all except first as duplicates
                if len(all_same) > 1:
                    # First record (oldest) is not duplicate
                    first = all_same[0]
                    for l in all_same:
                        l.is_duplicate = (l != first)
                else:
                    lead.is_duplicate = False
            else:
                lead.is_duplicate = False

    @api.model
    def create(self, vals):
        # lead = super(CrmLead, self).create(vals)
        lead = super().create(vals)
        self.env['lead.followup'].create({
            'lead_id': lead.id,
        })
        # self.env['crm.client'].create({
        #     'lead_id': lead.id,
        # })
        return lead
    
    @api.onchange('stage_id')
    def _onchange_stage_id_create_client(self):
        if self.stage_id and self.stage_id.name == 'Won':
            existing_client = self.env['crm.client'].search([('lead_id', '=', self.id)], limit=1)
            if not existing_client and self.id:
                self.env['crm.client'].create({
                    'lead_id': self.id,
                    'location': self.city or '',
                    'order_taken_by': self.user_id.name or '',
                })

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    installation = fields.Char(string="installation")
    travel_height = fields.Char(string="travel height")
    pit_ramp = fields.Char(string="Pit/Ramp")
    minimum_headroom = fields.Char(string="Minimum Headroom")
    capacity = fields.Char(string="capacity")
    motor = fields.Char(string="motor")
    speed = fields.Char(string="speed")
    power_supply = fields.Char(string="power supply")
    power_absorption = fields.Char(string="power absorption")
    stops = fields.Char(string="stops")
    cop = fields.Char(string="cop")
    cabin_size = fields.Char(string="cabin size")
    flooring = fields.Char(string="flooring")
    cabin_walls = fields.Char(string="cabin walls")
    required_shaft_space = fields.Char(string="required shaft space")
    cabin_panel = fields.Char()
    no_of_floors = fields.Char(string="no of floors")
    warranty = fields.Char(string="warranty")
    x_model = fields.Char(string="Model")


