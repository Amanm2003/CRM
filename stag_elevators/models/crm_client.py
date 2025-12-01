from datetime import datetime
from odoo import models, fields

class CRMClient(models.Model):
    _name = 'crm.client'
    _description = 'CRM Client'

    lead_id = fields.Many2one('crm.lead', string='Name', required=True, ondelete='cascade')
    contact_no = fields.Char(related='lead_id.phone',string='Contact Number')
    email = fields.Char(related='lead_id.email_from',string='Email')
    location = fields.Char(string='Location')
    contact_address = fields.Text(string='Contact Address')
    order_taken_by = fields.Char(string='Order Taken By')
    assign_to = fields.Many2one('res.users',string='Assigned to')

    stage_id = fields.Many2one(
        'crm.stage',
        string='Stage',
        domain="[('stage', '=','crm')]",
        help="Only CRM-specific stages will appear here."
    )

    # model_no = fields.Selection([
    #     ('SE01', 'SE01'), ('SE02', 'SE02'), ('SE03', 'SE03'),('X3','X3')
    # ], string='Model No')

    lead_model = fields.Text(string="Model")

    # floor = fields.Selection([
    #     ('G+1', 'G+1'), ('G+2', 'G+2'), ('G+3', 'G+3')
    # ], string='Floor')
    floor = fields.Text(string="Floor")

    shaft = fields.Selection([
        ('Metal','Metal'),
        ('Platform_lift','Platform lift'),
        ('Civil','Civil')
    ],string = 'Lead Shaft')

    followup_description = fields.Text(string='Follow-up Description')
    followup_history = fields.Text('Previous Followups')
    date = fields.Date(string='Reminder Date')

    stage = fields.Selection([
        ('draft', 'Draft'),
        ('stage1', 'Stage 1'),
        ('stage2', 'Stage 2'),
        ('stage3', 'Stage 3'),
        ('stage4', 'Stage 4'),
        ('done', 'Done')
    ], string="Stage", default='draft')

    site_visit_done = fields.Boolean(string="Site Visit - Confirmation")
    site_visit = fields.Boolean()
    # toggle_site_visit_checkbox = fields.Boolean()

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

    finishes_form = fields.Boolean(string="Finishes Forms")
    finishes_remarks = fields.Text(string="Stage 4 Remark")


    redinessform  = fields.Boolean(string="Rediness Form")
    stage3_attachment_id = fields.Many2one('ir.attachment', string="Stage 3 Attachment")

    cop_accent = fields.Many2one('ir.attachment', string="COP Accent Attachment")
    cabin_interiors = fields.Many2one('ir.attachment')
    doors = fields.Many2one('ir.attachment')
    ceiling = fields.Many2one('ir.attachment')
    cabin_rel_color = fields.Many2one('ir.attachment')
    flooring = fields.Many2one('ir.attachment')
    glass_wall_1 = fields.Many2one('ir.attachment')
    glass_wall_2 = fields.Many2one('ir.attachment')
    outer_shaft_color = fields.Many2one('ir.attachment')
    others = fields.Many2one('ir.attachment')

    redinessform_attachment = fields.Many2one('ir.attachment')

    drawing_sent_attachment = fields.Many2one('ir.attachment', string="Drawing Sent File")
    rev_1_attachment = fields.Many2one('ir.attachment', string="Revision 1 File")
    rev_2_attachment = fields.Many2one('ir.attachment', string="Revision 2 File")
    rev_3_attachment = fields.Many2one('ir.attachment', string="Revision 3 File")
    rev_4_attachment = fields.Many2one('ir.attachment', string="Revision 4 File")
    rev_5_attachment = fields.Many2one('ir.attachment', string="Revision 5 File")

    readiness_notification = fields.Boolean("Readiness Notification")

    advance_paid_percentage = fields.Integer()
    advance_paid_checkbox = fields.Boolean()
    advance_paid_amount = fields.Integer()
    advance_paid_attachment = fields.Many2one('ir.attachment')

    readiness_collected_percentage = fields.Integer()
    readiness_collected_checkbox = fields.Boolean()
    readiness_collected_amount = fields.Integer()
    readiness_collected_attachment = fields.Many2one('ir.attachment')

    handover_percentage = fields.Integer()
    handover_checkbox = fields.Boolean()
    handover_amount = fields.Integer()
    handover_attachment = fields.Many2one('ir.attachment')

    balance_percentage = fields.Integer()
    balance_checkbox = fields.Boolean()
    balance_amount = fields.Integer()
    balance_attachment = fields.Many2one('ir.attachment')

    

    material_dispatch = fields.Boolean("Material Dispatch")
    material_dispatch_date = fields.Date("Material Dispatch Date")
    material_dispatch_attachment = fields.Many2one('ir.attachment', string="eBay Bill")

    material_delivery = fields.Boolean("Material Delivery")
    material_delivery_date = fields.Date("Material Delivery Date")
    
    preinstallation_amount = fields.Integer()
    start_installation = fields.Selection([('yes', 'yes'),('no', 'no')], string="Start Installation")

    preinstallation_attachment = fields.Many2one('ir.attachment')
    
    ongoing = fields.Boolean()
    completed = fields.Boolean()
    handover = fields.Boolean()
    handover_date = fields.Date()
    attachment_handover = fields.Many2one('ir.attachment')
    amc = fields.Boolean()
    amc_start_date = fields.Date()
    amc_end_date = fields.Date()
    service = fields.Boolean(default=True)

    renew = fields.Boolean()
    not_renew = fields.Boolean()
    renew_date = fields.Date()

    stage11_attachment = fields.Many2one('ir.attachment')

   

    

    


    stage1 = fields.Boolean(string="Stage 1")
    stage2 = fields.Boolean(string="Stage 2")
    stage3 = fields.Boolean(string="Stage 3")
    stage4 = fields.Boolean(string="Stage 4")
    stage5 = fields.Boolean(string="Stage 5")
    stage6 = fields.Boolean(string="Stage 6")
    stage7 = fields.Boolean(string="Stage 7")
    stage8 = fields.Boolean(string="Stage 8")
    stage9 = fields.Boolean(string="Stage 9")
    

    
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
            if 'date' in vals:
                new_date_str = vals.get('date')
                if new_date_str:  
                    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
                    changes.append(f"Entered Date: {new_date.strftime('%d-%m-%Y')}")

            if 'stage1' in vals and vals['stage1'] and self.stage1!=True:
                changes.append("Stage 1 completed")
            if 'stage2' in vals and vals['stage2'] and self.stage2!=True:
                changes.append("Stage 2 completed")
            if 'stage3' in vals and vals['stage3'] and self.stage3!=True:
                changes.append("Stage 3 completed")
            if 'stage4' in vals and vals['stage4'] and self.stage4!=True:
                changes.append("Stage 4 completed")
            if 'stage5' in vals and vals['stage5'] and self.stage5!=True:
                changes.append("Stage 5 completed")
            if 'stage6' in vals and vals['stage6'] and self.stage6!=True:
                changes.append("Stage 6 completed")
            if 'stage7' in vals and vals['stage7'] and self.stage7!=True:
                changes.append("Stage 7 completed")
            if 'stage8' in vals and vals['stage8'] and self.stage8!=True:
                changes.append("Stage 8 completed")
            if 'stage9' in vals and vals['stage9'] and self.stage9!=True:
                changes.append("Stage 9 completed")


            if changes:
                rec.followup_history = (history + f"\n[{current_date}] " + " | ".join(changes)).strip()

        return super(CRMClient, self).write(vals)






class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    attachment_category = fields.Selection([
        ('cop_accent', 'COP/Accent'),
        ('cabin_interiors', 'Cabin/Interiors'),
        ('doors', 'Doors'),
        ('ceiling', 'Ceiling'),
        ('cabin_rel_color', 'CabinRel Color'),
        ('flooring', 'Flooring'),
        ('glass_wall_1', 'Glass Wall 1'),
        ('glass_wall_2', 'Glass Wall 2'),
        ('outer_shaft_color', 'Outer Shaft Color'),
        ('others', 'Others'),
    ], string='Attachment Category')
