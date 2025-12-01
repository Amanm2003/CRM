from datetime import datetime

from requests import request
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo import _



class LeadFollowup(models.Model):
    _name = 'lead.followup'
    _description = 'Lead Followups'

    lead_id = fields.Many2one('crm.lead', string='Lead', required=True, ondelete='cascade')
    mobile = fields.Char(related='lead_id.phone', string='Lead Mobile', store=True, readonly=True)
    alternate_mobile = fields.Char('Lead Alternate Mobile')
    next_followup_date = fields.Date('Next Followup Date')
    followup_description = fields.Html('Followup Description')
    stage_id = fields.Many2one(related='lead_id.stage_id', string='Lead Stage', store=True, readonly=True)
    followup_history = fields.Text('Previous Followups')
    lead_model = fields.Text(string="Model")
    shaft = fields.Selection([
        ('Metal','Metal'),
        ('Platform_lift','Platform lift'),
        ('Civil','Civil')
    ],string = 'Lead Shaft')
    won_note = fields.Text('Note (Visible in Won stage only)')



    def write(self, vals):
        for rec in self:
            history = rec.followup_history or ''
            current_date = fields.Date.today().strftime('%d-%m-%Y')
            changes = []

            # Always add the new followup description if provided
            new_description = vals.get('followup_description')
            from bs4 import BeautifulSoup
            plain_text = BeautifulSoup(new_description or '', 'html.parser').get_text()

            if new_description:
                changes.append(f"Description: {plain_text}")
            new_date_str = vals.get('next_followup_date')
            # If followup date changed
            if 'next_followup_date' in vals:
                new_date_str = vals.get('next_followup_date')
                if new_date_str:  # Check that the string is not empty
                    new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
                    changes.append(f"Entered Date: {new_date.strftime('%d-%m-%Y')}")

            # If stage changed
            if 'stage_id' in vals:
                new_stage_id = int(vals.get('stage_id'))
                if new_stage_id:    
                    new_stage = self.env['crm.stage'].sudo().browse(new_stage_id)
                    changes.append(f"Stage: {new_stage.name}")

            if 'stage_id' in vals and vals.get('stage_id'):
                    new_stage = self.env['crm.stage'].browse(vals.get('stage_id'))
                    doc_exists = self.env['ir.attachment'].sudo().search_count([
                        ('res_model', '=', 'lead.followup'),
                        ('res_id', '=', rec.id),
                        ('name', 'ilike', rec.lead_id.name),  
                        ('name', 'ilike', 'Quotation')  
                    ]) > 0
                    # namee =vals.get('stage_id').name 
                    if not doc_exists and new_stage.name == 'Won':
                        raise ValidationError(_("Please attach a Quotation document before setting the stage to 'Won'."))

                    if new_stage.name == 'Won' and rec.lead_id:
                        existing_client = self.env['crm.client'].search([
                            ('lead_id', '=', rec.lead_id.id)
                        ], limit=1)
                        crm_won_stage = self.env['crm.stage'].search([
                            ('name', '=', 'Won'),
                            ('stage','=','crm')
                        ], limit=1)
                        if not existing_client:
                            self.env['crm.client'].create({
                                'lead_id': rec.lead_id.id,
                                'location': rec.lead_id.city or '',
                                'order_taken_by': rec.lead_id.user_id.name if rec.lead_id.user_id else '',
                                'date':new_date_str,
                                'stage_id': crm_won_stage.id,
                            })
                            client_idd = self.env['crm.client'].search([
                            ('lead_id', '=', rec.lead_id.id)
                        ], limit=1)
                            self.env['production.client'].create({
                                'crm_client_id':client_idd.id,
                                'order_taken_by': rec.lead_id.user_id.name if rec.lead_id.user_id else ''
                            })
            if changes:
                rec.followup_history = (history + f"\n[{current_date}] " + " | ".join(changes)).strip()

        return super(LeadFollowup, self).write(vals)
    




    
