from datetime import datetime
from odoo import models, fields

class ProdClient(models.Model):
    _name = 'production.client'
    _description = 'Production'

    crm_client_id = fields.Many2one(
        'crm.client',
        string='CRM Client',
        ondelete='cascade'
    )
    lead_id = fields.Many2one(related='crm_client_id.lead_id', string="Lead", store=True, readonly=True)
    contact_no = fields.Char(related='crm_client_id.contact_no', string="Contact Number", store=True, readonly=True)
    email = fields.Char(related='crm_client_id.email', string="Email", store=True, readonly=True)
    contact_address = fields.Text(string='Contact Address')
    lead_model = fields.Text(string="Model")
    floor = fields.Text(string="Floor")
    shaft = fields.Text(string = 'Shaft')
    followup_description = fields.Text(string='Follow-up Description')
    followup_history = fields.Text('Previous Followups')
    followup_date = fields.Date(string='Reminder Date')
    stage_id = fields.Many2one('crm.stage')
    order_taken_by = fields.Text()
    assign_to = fields.Many2one('res.users',string='Assigned to')

    stage1 = fields.Boolean(string="Stage 1")
    stage2 = fields.Boolean(string="Stage 2")
    stage3 = fields.Boolean(string="Stage 3")
    stage4 = fields.Boolean(string="Stage 4")
    stage5 = fields.Boolean(string="Stage 5")
    stage6 = fields.Boolean(string="Stage 6")
    stage7 = fields.Boolean(string="Stage 7")
    stage8 = fields.Boolean(string="Stage 8")
    stage9 = fields.Boolean(string="Stage 9")

    # =========== stage 1 fields ==============

    site_visit_person = fields.Char(string="Site Visit Person")
    site_visit_images = fields.Many2many(
        'ir.attachment',
        'prod_client_visit_image_rel',
        'client_id',
        'attachment_id',
        string="Site Visit Images"
    )
    model_no = fields.Selection([
        ('SE1', 'SE1'),
        ('SE2', 'SE2'),
        ('SE3', 'SE3'),
        ('SE3+', 'SE3+'),
        ('X3', 'X3'),
        ('TEZ', 'TEZ'),
        ('others', 'Others')
    ], string="Model No")

    shaft_type = fields.Selection([
        ('glass', 'Glass'),
        ('3_side_wall', '3 Side Wall')
    ], string="Shaft Type")

    # ======= stage 7 fields ==============

    start_installation = fields.Selection([('yes','yes'),('no','no')])
    stage_7_attachment = fields.Many2one('ir.attachment')

    # ======== stage 6 fields ==============

    material_dispatch = fields.Boolean("Material Dispatch")
    material_dispatch_date = fields.Date("Material Dispatch Date")
    material_dispatch_attachment = fields.Many2one('ir.attachment', string="eBay Bill")

    material_delivery = fields.Boolean("Material Delivery")
    material_delivery_date = fields.Date("Material Delivery Date")

    # ========= stage 8 fields ===========

    ongoing = fields.Boolean()
    completed = fields.Boolean()
    handover = fields.Boolean()
    handover_date = fields.Date()
    attachment_handover = fields.Many2one('ir.attachment')

    installation_schedule = fields.Boolean()
    installation_schedule_date = fields.Date()
    installation_schedule_attachment = fields.Many2one('ir.attachment')
    installation_schedule_remark = fields.Text()

    glass_schedule = fields.Boolean()
    glass_schedule_date = fields.Date()
    glass_schedule_attachment = fields.Many2one('ir.attachment')
    glass_schedule_remark = fields.Text()

    # ========== stage 2 fields =============

    drawing_sent = fields.Boolean(string="Drawing Sent")
    rev_1 = fields.Boolean(string="Revision 1")
    rev_2 = fields.Boolean(string="Revision 2")
    rev_3 = fields.Boolean(string="Revision 3")
    rev_4 = fields.Boolean(string="Revision 4")
    rev_5 = fields.Boolean(string="Revision 5")
    

    rev_1_date = fields.Date(string="Date")
    rev_2_date = fields.Date(string="Date")
    rev_3_date = fields.Date(string="Date")
    rev_4_date = fields.Date(string="Date")
    rev_5_date = fields.Date(string="Date")

    drawing_sent_attachment = fields.Many2one('ir.attachment', string="Drawing Sent File")
    rev_1_attachment = fields.Many2one('ir.attachment', string="Revision 1 File")
    rev_2_attachment = fields.Many2one('ir.attachment', string="Revision 2 File")
    rev_3_attachment = fields.Many2one('ir.attachment', string="Revision 3 File")
    rev_4_attachment = fields.Many2one('ir.attachment', string="Revision 4 File")
    rev_5_attachment = fields.Many2one('ir.attachment', string="Revision 5 File")
    

    def write(self, vals):
        for rec in self:
            history = rec.followup_history or ''
            current_date = fields.Date.today().strftime('%d-%m-%Y')
            changes = []

            # Always add the new followup description if provided
            new_description = vals.get('followup_description')
            if new_description:
                changes.append(f"Description: {new_description}")

            # If followup date changed
            if 'followup_date' in vals:
                new_date_str = vals.get('followup_date')
                if new_date_str:  
                    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
                    changes.append(f"Entered Date: {new_date.strftime('%d-%m-%Y')}")

            if 'stage1' in vals and vals['stage1'] and self.stage1!=True:
                changes.append("Stage 1 completed")
            if 'stage2' in vals and vals['stage2'] and self.stage2!=True:
                changes.append("Stage 2 completed")
            if 'stage6' in vals and vals['stage6'] and self.stage6!=True:
                changes.append("Stage 6 completed")
            if 'stage7' in vals and vals['stage7'] and self.stage7!=True:
                changes.append("Stage 7 completed")
            if 'stage8' in vals and vals['stage8'] and self.stage8!=True:
                changes.append("Stage 8 completed")


            if changes:
                rec.followup_history = (history + f"\n[{current_date}] " + " | ".join(changes)).strip()

        return super(ProdClient, self).write(vals)

