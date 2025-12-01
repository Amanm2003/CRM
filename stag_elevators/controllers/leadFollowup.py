import base64
import re
from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
import logging
import base64
from werkzeug.utils import secure_filename

_logger = logging.getLogger(__name__)

class LeadFollowupController(http.Controller):

    @http.route('/lead_followups', type='http', auth='user', website=True)
    def lead_followups_list(self, **kwargs):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'lead.followup'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        # access_rule_admin = request.env['ir.model.access'].sudo().search([
        #         ('model_id.model', '=', 'ir.model.access'),
        #         ('group_id', '=', my_groups.id),
        #         ('perm_read', '=', True)
        #     ], limit=1)
        if my_groups.is_admin:
            # followups = request.env['lead.followup'].sudo().search([], order="next_followup_date asc")
            followups = request.env['lead.followup'].sudo().search(
                [
                    ('lead_id.stage_id.name', 'not in', ['Won', 'Lost'])
                ],
                order='next_followup_date asc'
            )

            return request.render('stag_elevators.lead_followups_list_template', {
                'followups': followups,
            })
        else:
            # followups = request.env['lead.followup'].sudo().search([], order="next_followup_date asc")

            request.env.cr.rollback()  # resets the transaction
            user = request.env.user
            followups = request.env['lead.followup'].sudo().search([
                ('lead_id.user_id','=', user.id),
                ('lead_id.stage_id.name', 'not in', ['Won', 'Lost'])
                
            ])
            return request.render('stag_elevators.lead_followups_list_template', {
                'followups': followups,
            })


    # @http.route(['/lead_followups/form', '/lead_followups/<int:lead_id>'], type='http', auth='user', website=True)
    # def lead_followups_form(self, lead_id=None, **kw):

    #     lead = request.env['lead.followup'].sudo().browse(lead_id) if lead_id else None
        

    #     won_stage = request.env['crm.stage'].sudo().search([('name', '=', 'Won')], limit=1)
    #     pending_leads = request.env['crm.lead'].sudo().search([('stage_id', '!=', won_stage.id)])
    #     stages = request.env['crm.stage'].sudo().search([])

    #     return request.render('stag_elevators.lead_followup_template', {
    #         'lead': lead,
    #         'stages': stages,
    #         'pending_leads': pending_leads
    #     })

    # @http.route(['/lead_followups/submit'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
    # def lead_followups_submit(self, **post):
    #     _logger.info("POST Data: %s", post)
    #     request.env['lead.followup'].sudo().create({
    #         'name': post.get('name'),
    #         'mobile': post.get('mobile'),
    #         'alternate_mobile': post.get('alternate_mobile'),
    #         'next_followup_date': post.get('next_followup_date'),
    #         'followup_description': post.get('followup_description'),
    #         'stage_id': int(post.get('stage_id')),
    #     })
    #     return request.redirect('/lead_followups/form')

    @http.route('/lead_followups/edit/<int:followup_id>', type='http', auth='user', website=True)
    def edit_lead_followup(self, followup_id, **kwargs):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'lead.followup'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        
        followup = request.env['lead.followup'].sudo().browse(followup_id)
        lead = request.env['crm.lead'].sudo().search([('id', '=', followup.lead_id.id)], limit=1)
        client = request.env['crm.client'].sudo().search([('lead_id','=',lead.id)])
        prod = request.env['production.client'].sudo().search([('lead_id','=',lead.id)])
        if not followup.exists():
            return request.not_found()

        # Fetch all previous followups for this lead
        previous_followups = request.env['lead.followup'].sudo().search([
            ('lead_id', '=', followup.lead_id.id),
            ('id', '!=', followup.id)
        ], order="next_followup_date asc")

        locations = request.env['res.city'].sudo().search([])

        return request.render('stag_elevators.lead_followup_edit_template', {
            'followup': followup,
            'previous_followups': previous_followups,
            'locations':locations,
            'crm':client,
            'prod':prod,
        })
    
    @http.route('/lead_followups/update', type='http', auth='user', methods=['POST'], csrf=True, website=True)
    def update_followup(self, **kwargs):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'lead.followup'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        followup_id = int(kwargs.get('followup_id'))
        followup = request.env['lead.followup'].sudo().browse(followup_id)
        try:
        
            if followup:
                # Update lead fields separately
                lead = followup.lead_id
                if lead:
                    email = kwargs.get('email')
                    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
                    if email and not re.match(email_regex, email):
                        return request.redirect(f'/lead_followups/edit/{followup_id}?error=email_error')
                    lead.write({
                        'city': kwargs.get('followup.lead_id.city'),
                        'email_from': kwargs.get('email'),
                        
                    })
                # new_date = kwargs.get('next_followup_date')
                # if new_date and followup.next_followup_date:
                #     if new_date < str(followup.next_followup_date):
                #         return request.redirect(f'/lead_followups/edit/{followup_id}?error=followup_date_v')

                # Update followup fields
                if kwargs.get('next_followup_date'):
                    followup.write({
                        'next_followup_date': kwargs.get('next_followup_date'),
                    })
                if kwargs.get('followup_description'):
                    followup.write({
                        'followup_description': kwargs.get('followup_description'),
                    })
                followup.write({
                    'alternate_mobile': kwargs.get('alternate_mobile'),
                    
                    # 'followup_description': kwargs.get('followup_description'),
                    'lead_model':kwargs.get('lead_model'),
                    'shaft':kwargs.get('shaft'),
                    'stage_id': int(kwargs.get('stage_id')) if kwargs.get('stage_id') else False,
                    'won_note': kwargs.get('won_note'),

                })
                if lead:
                    vals = {
                        'stage_id': int(kwargs.get('stage_id')) if kwargs.get('stage_id') else False,
                    }

                    if kwargs.get('followup_description'):
                        vals['description'] = kwargs['followup_description']

                    lead.write(vals)

                    # lead.write({'stage_id': int(kwargs.get('stage_id')) if kwargs.get('stage_id') else False,})



        except ValidationError as e:

                return request.redirect(f'/lead_followups/edit/{followup_id}?error=missing_quotation')
            

        return request.redirect(f'/lead_followups/edit/{followup_id}')
        
        # return request.redirect(f'/lead_followups/edit/{followup_id}')



    

    @http.route('/lead_followups/upload', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def upload_followup_document(self, **post):
        ALLOWED_EXTENSIONS = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'txt': 'text/plain',
    }
        followup_id = int(post.get('followup_id', 0))
        stage_label = post.get('stage_label')
        note = post.get('note', '')
        file = post.get('document')

        if not followup_id or not file:
            return request.redirect('/lead_followups')

        followup = request.env['lead.followup'].sudo().browse(followup_id)
        if not followup.exists():
            return request.redirect('/lead_followups')

        filename = secure_filename(file.filename or '')
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        mimetype = file.content_type

        # Validate file type
        if extension not in ALLOWED_EXTENSIONS or ALLOWED_EXTENSIONS[extension] != mimetype:
            # Optionally you could flash a warning message here
            return request.redirect(f'/lead_followups/edit/{followup_id}')

        attachment_name = f"{followup.lead_id.name}_{stage_label}.{extension}"

        # Save the attachment
        request.env['ir.attachment'].sudo().create({
            'name': attachment_name,
            'datas': base64.b64encode(file.read()),
            'res_model': 'lead.followup', 
            'res_id': followup.id,
            'mimetype': mimetype,
            'description': f"Stage: {stage_label}\n{note}" if (stage_label or note) else False,
        })

        return request.redirect(f'/lead_followups/edit/{followup_id}')
    
    @http.route('/lead_followups/attachment/delete/<int:attachment_id>', type='http', auth='user', website=True, csrf=True)
    def delete_followup_attachment(self, attachment_id, **kwargs):
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        followup_id = attachment.res_id

        # Ensure it's linked to the lead.followup model
        if attachment and attachment.res_model == 'lead.followup':
            attachment.unlink()

        return request.redirect(f'/lead_followups/edit/{followup_id}')