import base64
from datetime import date, datetime, timedelta
import json
import logging

from requests import Response
import werkzeug
from odoo import http
from odoo.exceptions import AccessDenied, ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)

class CRMClientController(http.Controller):

    @http.route('/crm_client/list', type='http', auth='user', website=True)
    def crm_client_list(self, **kw):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        
        if my_groups.is_admin:
        # if not request.env.user.has_group('admin'):
        #     return request.redirect('/Dashboard')
            today = date.today()
            start_of_month = today.replace(day=1)
            end_of_month = today.replace(
                day=28) + timedelta(days=4)  # go to next month
            end_of_month = end_of_month.replace(day=1) - timedelta(days=1)  # last day of current month

            clients = request.env['crm.client'].sudo().search([
                
            ])
            # users = request.env['res.users'].sudo().search([('active', '=', True)])
            # Groups that have 'ismy' = True
            my_groups = request.env['res.groups'].sudo().search([('ismy', '=', True)])
            users_in_my_groups = request.env['res.users'].sudo().search([
                ('active', '=', True),
                ('groups_id', 'in', my_groups.ids)
            ])
            final_users = []
            for user in users_in_my_groups:
                access_rule = request.env['ir.model.access'].sudo().search([
                    ('model_id.model', '=', 'crm.client'),
                    ('group_id', 'in', user.groups_id.ids),
                    ('perm_read', '=', True)
                ], limit=1)
                access_rule_admin = request.env['ir.model.access'].sudo().search([
                    ('model_id.model', '=', 'ir.model.access'),
                    ('group_id', 'in', user.groups_id.ids),
                    ('perm_read', '=', True)
                ], limit=1)
                
                if access_rule:
                    if not access_rule_admin:
                        final_users.append(user)
            users = request.env['res.users'].browse([u.id for u in final_users])




            return request.render('stag_elevators.crm_client_list_template', {
                'clients': clients,
                'users':users
            })
        else:
            today = date.today()
            start_of_month = today.replace(day=1)
            end_of_month = today.replace(
                day=28) + timedelta(days=4)  # go to next month
            end_of_month = end_of_month.replace(day=1) - timedelta(days=1)  # last day of current month

            # clients = request.env['crm.client'].sudo().search([
            #     ('create_date', '>=', start_of_month),
            #     ('create_date', '<=', end_of_month)
            # ])
            request.env.cr.rollback()  # resets the transaction
            user = request.env.user
            clients = request.env['crm.client'].sudo().search([
                ('assign_to','=',user.id)
            ])
            # users = request.env['res.users'].sudo().search([('active', '=', True)])
            my_groups = request.env['res.groups'].sudo().search([('ismy', '=', True)])
            users_in_my_groups = request.env['res.users'].sudo().search([
                ('active', '=', True),
                ('groups_id', 'in', my_groups.ids)
            ])
            final_users = []
            for user in users_in_my_groups:
                access_rule = request.env['ir.model.access'].sudo().search([
                    ('model_id.model', '=', 'crm.client'),
                    ('group_id', 'in', user.groups_id.ids),
                    ('perm_read', '=', True)
                ], limit=1)
                access_rule_admin = request.env['ir.model.access'].sudo().search([
                    ('model_id.model', '=', 'ir.model.access'),
                    ('group_id', 'in', user.groups_id.ids),
                    ('perm_read', '=', True)
                ], limit=1)
                
                if access_rule:
                    if not access_rule_admin:
                        final_users.append(user)
            users = request.env['res.users'].browse([u.id for u in final_users])
            return request.render('stag_elevators.crm_client_list_template', {
                'clients': clients,
                'users':users
            })
        
    @http.route('/crm/client/list', type='http', auth='user', website=True)
    def crm_client_list1(self, **kw):
        stage_name = kw.get('stage')   # <-- read ?stage= param
        domain = []
        # domain.append(('stage','=','crm'))

        if stage_name:
            # Match stage by name (case-insensitive)
            stage = request.env['crm.stage'].sudo().search([('name', 'ilike', stage_name),('stage','=','crm')], limit=1)
            if stage:
                domain.append(('stage_id', '=', stage.id))

        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
            ('model_id.model', '=', 'crm.client'),
            ('group_id', '=', my_groups.id),
            ('perm_read', '=', True)
        ], limit=1)

        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })

        today = date.today()
        start_of_month = today.replace(day=1)
        end_of_month = today.replace(day=28) + timedelta(days=4)
        end_of_month = end_of_month.replace(day=1) - timedelta(days=1)

        # If admin → show all
        if my_groups.is_admin:
            clients = request.env['crm.client'].sudo().search(domain)
        else:
            user = request.env.user
            domain.append(('assign_to', '=', user.id))
            clients = request.env['crm.client'].sudo().search(domain)

        # Users for filter
        my_groups = request.env['res.groups'].sudo().search([('ismy', '=', True)])
        users_in_my_groups = request.env['res.users'].sudo().search([
            ('active', '=', True),
            ('groups_id', 'in', my_groups.ids)
        ])
        final_users = []
        for user in users_in_my_groups:
            access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', 'in', user.groups_id.ids),
                ('perm_read', '=', True)
            ], limit=1)
            access_rule_admin = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'ir.model.access'),
                ('group_id', 'in', user.groups_id.ids),
                ('perm_read', '=', True)
            ], limit=1)
            if access_rule:
                if not access_rule_admin:
                    final_users.append(user)
        users = request.env['res.users'].browse([u.id for u in final_users])

        return request.render('stag_elevators.crm_client_list_template', {
            'clients': clients,
            'users': users,
            'stage_name': stage_name or ''
        })


    @http.route('/crm_client/form', type='http', auth='user', website=True)
    def crm_client_form(self, **kw):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        leads = request.env['crm.lead'].sudo().search([], limit=50)
        return request.render('stag_elevators.crm_client_template', {
            'leads': leads
        })

    @http.route('/crm_client/get_lead_info', type='json', auth='user')
    def get_lead_info(self, lead_id):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        lead = request.env['crm.lead'].sudo().browse(int(lead_id))
        return {
            'contact_no': lead.phone or '',
            'email': lead.email_from or ''
        }

    @http.route('/crm_client/submit', type='http', auth='user', website=True, csrf=True, methods=['POST'])
    def crm_client_submit(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
            
        request.env['crm.client'].sudo().create({
            'lead_id': post.get('lead_id'),
            'contact_no': post.get('contact_no'),
            'email': post.get('email'),
            'location': post.get('location'),
            'contact_address': post.get('contact_address'),
            'order_taken_by': post.get('order_taken_by'),
            'lead_model': post.get('lead_model'),
            'floor': post.get('floor'),
            'shaft': post.get('shaft'),
            'followup_description': post.get('followup_description'),
            'date': post.get('date'),
        })
        return request.redirect('/crm_client/form')
    
    @http.route('/crm/client/edit/<int:client_id>', type='http', auth='user', website=True)
    def edit_client(self, client_id, **kw):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })

        client = request.env['crm.client'].sudo().browse(client_id)
        lead_id = request.env['crm.lead'].search([('id','=',client.lead_id.id)])
        followup = request.env['lead.followup'].sudo().browse(lead_id.followup_ids).id
        prod = request.env['production.client'].sudo().search([('lead_id','=',lead_id.id)])
        stages = request.env['crm.stage'].sudo().search([('stage', '=', 'crm')])
        return request.render('stag_elevators.edit_crm_client_template', {'client': client,'stages': stages,'prod':prod,'followup':followup,})
    
    @http.route('/crm/client/update', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def update_client(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get('client_id'))
        client = request.env['crm.client'].sudo().browse(client_id)

        if client:
            # Checkbox values
            # new_date = post.get('date')
            # if new_date and client.date:
            #     if new_date < str(client.date):
            #         return request.redirect(f'/crm/client/edit/{client_id}?error=date_v')
            
            site_visit_done = post.get("site_visit_done") == "1"
            drawing_sent = post.get('drawing_sentt') == '1'
            rev1 = post.get('rev1') == '1'
            rev2 = post.get('rev2') == '1'
            rev3 = post.get('rev3') == '1'
            rev4 = post.get('rev4') == '1'
            rev5 = post.get('rev5') == '1'
            lead_model = post.get('lead_model')
            stage_id = post.get('stage_id')

            # Date fields

            rev_1_date = post.get("rev_1_date_hidden")
            rev_2_date = post.get("rev_2_date_hidden")
            rev_3_date = post.get("rev_3_date_hidden")
            rev_4_date = post.get("rev_4_date_hidden")
            rev_5_date = post.get("rev_5_date_hidden")
            site_visit = post.get("site_visit_hidden") == '1'
            finishes_form = post.get("finishes_form") == '1'

            redinessform = post.get("redinessform_hidden") == '1'
            stage1 = post.get('stage1_hidden') == '1'
            stage2 = post.get('stage2_hidden') == '1'
            stage3 = post.get('stage3_hidden') == '1'
            stage4 = post.get('stage4_hidden') == '1'
            stage5 = post.get('stage5_hidden') == '1'
            stage6 = post.get('stage6_hidden') == '1'
            stage7 = post.get('stage7_hidden') == '1'
            stage8 = post.get('stage8_hidden') == '1'
            stage9 = post.get('stage9_hidden') == '1'
            

            material_dispatch = post.get("material_dispatch_hidden") == '1'
            material_delivery = post.get("material_delivery_hidden") == '1'
            material_dispatch_date = post.get("material_dispatch_date_hidden")
            material_delivery_date = post.get("material_delivery_date_hidden")

            readiness_notification = post.get("readiness_notification_hidden") == '1'
            advance_paid_percentage = post.get("advance_paid_percentage_hidden")
            advance_paid_checkbox = post.get("advance_paid_checkbox_hidden") == '1'
            advance_paid_amount = post.get("advance_paid_amount_hidden")

            readiness_collected_checkbox = post.get("readiness_collected_checkbox_hidden") == '1'
            handover_checkbox = post.get("handover_checkbox_hidden") == '1'
            balance_checkbox = post.get("balance_checkbox_hidden") == '1'

            readiness_collected_percentage = post.get("readiness_collected_percentage_hidden")
            handover_percentage = post.get("handover_percentage_hidden")
            balance_percentage = post.get("balance_percentage_hidden")

            readiness_collected_amount = post.get("readiness_collected_amount_hidden")
            handover_amount = post.get("handover_amount_hidden")
            balance_amount = post.get("balance_amount_hidden")
            preinstallation_amount = post.get("preinstallation_amount_hidden")
            
            ongoing = post.get("ongoing_hidden") == '1'
            completed = post.get("completed_hidden") == '1'
            handover = post.get("handover_hidden") == '1'
            amc = post.get("amc_hidden") == '1'
            service = post.get("service_hidden") == '1'
            handover_date = post.get("handover_date_hidden")
            amc_start_date = post.get("amc_start_date_hidden")
            amc_end_date = post.get("amc_end_date_hidden")
            renew = post.get('renew_hidden') == '1'
            not_renew = post.get('not_renew_hidden') == '1'
            renew_date = post.get("renew_date_hidden")
            # type = post.get("type_hidden")

            

            # Validation checks for revisions
            # if rev1 and (not drawing_sent or not client.drawing_sent_attachment):
            #     raise ValidationError("You must mark 'Drawing Sent' as done before marking 'Rev 1' as done.")
                #     return {
                #     'success': False,
                #     'error': "You must mark 'Drawing Sent' as done before marking 'Rev 1' as done."
                # }
                # return request.make_json_response({
                #     'success': False,
                #     'error': "You must mark 'Drawing Sent' as done before marking 'Rev 1' as done."
                # }, status=400)
            try:
                # if drawing_sent and not client.drawing_sent_attachment :
                #     raise ValidationError("You must mark 'Drawing Sent' as done and upload attachment")
                # if (rev1 )  and (not drawing_sent or not client.drawing_sent_attachment or not client.rev_1_attachment or not rev_1_date):
                #     raise ValidationError("You must mark 'Drawing Sent' as done and upload attachment before marking 'Rev 1'")
                # if (rev2 ) and (not rev1 or not rev_1_date or not client.rev_1_attachment or not client.rev_2_attachment or not rev_2_date):
                #     raise ValidationError("You must complete 'Rev 1' with date and attachment before marking 'Rev 2'")
                # if (rev3 ) and (not rev2 or not rev_2_date or not client.rev_2_attachment or not client.rev_3_attachment or not rev_3_date):
                #     raise ValidationError("You must complete 'Rev 2' with date and attachment before marking 'Rev 3'")
                # if (rev4 ) and (not rev3 or not rev_3_date or not client.rev_3_attachment or not client.rev_4_attachment or not rev_4_date):
                #     raise ValidationError("You must complete 'Rev 3' with date and attachment before marking 'Rev 4'")
                # if (rev5 ) and (not rev4 or not rev_4_date or not client.rev_4_attachment or not client.rev5_attachment or not rev_5_date):
                #     raise ValidationError("You must complete 'Rev 4' with date and attachment before marking 'Rev 5'")
                # if (rev_1_date)  and (not drawing_sent or not client.drawing_sent_attachment or not client.rev_1_attachment or not rev1):
                #     raise ValidationError("You must mark 'Drawing Sent' as done and upload attachment before marking 'Rev 1'")
                # if (rev_2_date) and (not rev1 or not rev_1_date or not client.rev_1_attachment or not client.rev_2_attachment or not rev2):
                #     raise ValidationError("You must complete 'Rev 1' with date and attachment before marking 'Rev 2'")
                # if (rev_3_date) and (not rev2 or not rev_2_date or not client.rev_2_attachment or not client.rev_3_attachment or not rev3):
                #     raise ValidationError("You must complete 'Rev 2' with date and attachment before marking 'Rev 3'")
                # if (rev_4_date) and (not rev3 or not rev_3_date or not client.rev_3_attachment or not client.rev_4_attachment or not rev4):
                #     raise ValidationError("You must complete 'Rev 3' with date and attachment before marking 'Rev 4'")
                # if (rev_5_date) and (not rev4 or not rev_4_date or not client.rev_4_attachment or not client.rev5_attachment or not rev5):
                #     raise ValidationError("You must complete 'Rev 4' with date and attachment before marking 'Rev 5'")
                # if amc and service:
                #     raise ValidationError("You cannot select both AMC and Service")
                if not site_visit and stage1:
                    raise ValidationError("Stage 1 Cannot be Completed ")

                
            except ValidationError as e:
                request.session['error_message'] = str(e)
                return werkzeug.utils.redirect(f'/crm/client/edit/{client_id}')


            # Update crm.client record
            client.write({
                'site_visit':site_visit,
                'site_visit_done': site_visit_done,
                'drawing_sent': drawing_sent,
                'rev_1': rev1,
                'rev_2': rev2,
                'rev_3': rev3,
                'rev_4': rev4,
                'rev_5': rev5,
                'rev_1_date': rev_1_date,
                'rev_2_date': rev_2_date,
                'rev_3_date': rev_3_date,
                'rev_4_date': rev_4_date,
                'rev_5_date': rev_5_date,
                'location': post.get('location'),
                'lead_model': post.get('lead_model'),
                'floor': post.get('floor'),
                'shaft': post.get('shaft'),
                'date': post.get('date') or False,
                'followup_description': post.get('followup_description'),
                'contact_address': post.get('contact_address'),
                'redinessform':redinessform,
                'finishes_form':finishes_form,
                'stage1':stage1,
                'stage2':stage2,
                'stage3':stage3,
                'stage4':stage4,
                'stage5':stage5,
                'stage6':stage6,
                'stage7':stage7,
                'stage8':stage8,
                'stage9':stage9,
                'material_dispatch':material_dispatch,
                'material_delivery':material_delivery,
                'material_dispatch_date':material_dispatch_date,
                'material_delivery_date':material_delivery_date,
                'readiness_notification':readiness_notification,
                'advance_paid_percentage':advance_paid_percentage,
                'advance_paid_checkbox':advance_paid_checkbox,
                'advance_paid_amount':advance_paid_amount,
                'readiness_collected_checkbox':readiness_collected_checkbox,
                'handover_checkbox':handover_checkbox,
                'balance_checkbox':balance_checkbox,
                'readiness_collected_percentage':readiness_collected_percentage,
                'handover_percentage':handover_percentage,
                'balance_percentage':balance_percentage,
                'readiness_collected_amount':readiness_collected_amount,
                'handover_amount':handover_amount,
                'balance_amount':balance_amount,
                # "preinstallation_amount":preinstallation_amount,
                "ongoing":ongoing,
                "completed":completed,
                "handover":handover,
                "amc":amc,
                "service":service,
                "handover_date":handover_date,
                "amc_end_date":amc_end_date,
                "amc_start_date":amc_start_date,
                'renew':renew,
                'not_renew':not_renew,
                'renew_date':renew_date,
                'lead_model':lead_model,
                'stage_id':stage_id,
                
                
                
            })
            client.stage_id = int(stage_id)

            # Update related lead
            lead = client.lead_id
            if lead:
                lead.write({
                    'city': post.get('client.lead_id.city'),
                    'email_from': post.get('email'),
                })
        

        return request.redirect(f'/crm/client/edit/{client_id}')

    @http.route('/upload/stage3', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage3(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        file = request.httprequest.files.get('file')
        client_id = post.get('client_id')

        if not file or not client_id:
            return request.make_json_response({'success': False, 'error': 'Missing data'}, status=400)

        try:
            file_content = base64.b64encode(file.read())
            file_name = file.filename

            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': file_content,
                'res_model': 'crm.client',
                'res_id': int(client_id),
                'type': 'binary',
                'mimetype': file.content_type,
            })

            # Save the attachment to the client record
            client = request.env['crm.client'].sudo().browse(int(client_id))
            client.redinessform_attachment = attachment.id

            return request.make_json_response({'success': True})
        except Exception as e:
            return request.make_json_response({'success': False, 'error': str(e)}, status=500)
        
    @http.route('/download/readiness/<int:attachment_id>', type='http', auth='user')
    def download_readiness(self, attachment_id):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        if not attachment.exists():
            return request.not_found()

        file_content = base64.b64decode(attachment.datas or b'')
        return request.make_response(
            file_content,
            headers=[
                ('Content-Type', attachment.mimetype or 'application/octet-stream'),
                ('Content-Disposition', f'attachment; filename="{attachment.name}"'),
            ]
        )
    
    @http.route('/delete/stage3', type='http', auth='user', methods=['POST'], csrf=False)
    def delete_stage3(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = post.get('client_id')
        if not client_id:
            return request.make_json_response({'success': False, 'error': 'Missing client_id'}, status=400)
        try:
            client = request.env['crm.client'].sudo().browse(int(client_id))
            if client.redinessform_attachment:
                client.redinessform_attachment.unlink()
                client.redinessform_attachment = False
            return request.make_json_response({'success': True})
        except Exception as e:
            return request.make_json_response({'success': False, 'error': str(e)}, status=500)
        
    @http.route('/upload/stage1', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage1(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        file = request.httprequest.files.get('file')
        client_id = post.get('client_id')

        if not file or not client_id:
            return request.make_json_response({'success': False, 'error': 'Missing data'}, status=400)

        try:
            file_content = base64.b64encode(file.read())
            file_name = file.filename

            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': file_content,
                'res_model': 'crm.client',
                'res_id': int(client_id),
                'type': 'binary',
                'mimetype': file.content_type,
            })

            # Save the attachment to the client record
            client = request.env['crm.client'].sudo().browse(int(client_id))
            client.stage11_attachment = attachment.id

            return request.make_json_response({'success': True})
        except Exception as e:
            return request.make_json_response({'success': False, 'error': str(e)}, status=500)

    @http.route('/upload/stage2', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage2(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        file = request.httprequest.files.get('file')
        client_id = post.get('client_id')
        tag = post.get('tag')  # e.g., 'rev_1', 'drawing_sent', etc.
        dateInput = post.get('dateInput')
        stage2 = post.get('stage2') =='true'
        client = request.env['crm.client'].sudo().browse(int(client_id))

        if (not file or not client_id or not tag) and not stage2:
            return request.make_json_response({'success': False, 'error': 'Missing required data'}, status=400)

        try:
            # Mapping of tags to field names and their requirements
            workflow = {
                'drawing_sent': {
                    'field': 'drawing_sent_attachment',
                    'requires': None,  # First step has no requirements
                    'boolean_field': 'drawing_sent',
                    'date_field': 'drawing_sent_date'
                },
                'rev_1': { 
                    'field': 'rev_1_attachment',
                    'requires': ('drawing_sent', 'drawing_sent_attachment'),
                    'boolean_field': 'rev_1',
                    'date_field': 'rev_1_date'
                },
                'rev_2': {
                    'field': 'rev_2_attachment',
                    'requires': ('rev_1', 'rev_1_attachment'),
                    'boolean_field': 'rev_2',
                    'date_field': 'rev_2_date'
                },
                'rev_3': {
                    'field': 'rev_3_attachment',
                    'requires': ('rev_2', 'rev_2_attachment'),
                    'boolean_field': 'rev_3',
                    'date_field': 'rev_3_date'
                },
                'rev_4': {
                    'field': 'rev_4_attachment',
                    'requires': ('rev_3', 'rev_3_attachment'),
                    'boolean_field': 'rev_4',
                    'date_field': 'rev_4_date'
                },
                'rev_5': {
                    'field': 'rev_5_attachment',
                    'requires': ('rev_4', 'rev_4_attachment'),
                    'boolean_field': 'rev_5',
                    'date_field': 'rev_5_date'
                }
            }

            # Validate tag exists
            if tag not in workflow and not stage2:
                return request.make_json_response({
                    'success': False,
                    'error': f"Invalid tag '{tag}' - must be one of {list(workflow.keys())}"
                }, status=400)
            if tag in workflow:

                config = workflow[tag]
                client = request.env['crm.client'].sudo().browse(int(client_id))

            

            # 1. Check if previous step was completed (boolean field)
                if config['requires']:
                    prev_bool_field, prev_attachment_field = config['requires']
                    if not getattr(client, prev_bool_field):
                        return request.make_json_response({
                            'success': False,
                            'error': f"Cannot upload This Rev,  {prev_bool_field.replace('_', ' ').title()} must be Completed First"
                        }, status=400)

                    if not getattr(client, prev_attachment_field):
                        return request.make_json_response({
                            'success': False,
                            'error': f"Cannot upload  {prev_attachment_field.replace('_attachment', '').replace('_', ' ').title()} file must be uploaded first"
                        }, status=400)

            if file:
                file_content = base64.b64encode(file.read())
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': file.filename,
                    'datas': file_content,
                    'res_model': 'crm.client',
                    'res_id': client.id,
                    'type': 'binary',
                    'mimetype': file.content_type,
                    'description': tag,
                })

            # Update client record
                vals = {
                    config['field']: attachment.id,
                    # Only mark the boolean field True when the final file is uploaded
                    config['boolean_field']: True  
                }
                if config.get('date_field') and dateInput:
                    vals[config['date_field']] = dateInput
                
                client.write(vals)
            if stage2:
                client.write({
                    'stage2': True,  
                })
            

            

            return request.make_json_response({
                'success': True,
                'message': f"File uploaded successfully for {tag}",
                'attachment_id': attachment.id
            })

        except Exception as e:
            logging.error(f"Error uploading file for tag {tag}: {str(e)}")
            return request.make_json_response({
                'success': False,
                'error': f"An error occurred: {str(e)}"
            }, status=500)






from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class StageAttachmentsController(http.Controller):

    @http.route('/web/save_stage_attachments', type='http', auth="user", methods=['POST'], csrf=False)
    def save_stage_attachments(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        try:
            client_id = post.get('client_id')
            remarks = post.get('remarks', '')
            finishes_form = post.get('finishes_form') == 'true'
            stage3 = post.get('stage3') =='true'
            
            client = request.env['crm.client'].browse(int(client_id))
            if not client.exists():
                return request.make_json_response({
                    'success': False,
                    'error': 'Client not found'
                }, status=404)
            
            # Map file input names to Many2one fields
            file_fields = {
                'cop_accent': 'cop_accent',
                'cabin_interiors': 'cabin_interiors',
                'doors': 'doors',
                'ceiling': 'ceiling',
                'cabin_rel_color': 'cabin_rel_color',
                'flooring': 'flooring',
                'glass_wall_1': 'glass_wall_1',
                'glass_wall_2': 'glass_wall_2',
                'outer_shaft_color': 'outer_shaft_color',
                'others': 'others'
            }
            
            for field_name, client_field in file_fields.items():
                file_data = request.httprequest.files.get(field_name)
                if file_data:
                    # Read and encode file in base64 (keep it as bytes)
                    file_content = base64.b64encode(file_data.read())
                    
                    # Create the attachment
                    attachment = request.env['ir.attachment'].sudo().create({
                        'name': file_data.filename,
                        'datas': file_content,
                        'res_model': 'crm.client',
                        'res_id': client.id,
                        'type': 'binary',
                        'mimetype': file_data.content_type,
                    })
                    
                    # Link the attachment ID to the Many2one field
                    client.sudo().write({client_field: attachment.id})
            
            # Update remarks & finishes form status
            client.sudo().write({
                'finishes_remarks': remarks,
                'finishes_form': finishes_form,
                'stage3':stage3
            })
            
            return request.make_json_response({
                'success': True,
                'message': 'Attachments saved successfully'
            })
        
        except Exception as e:
            _logger.error(f"Error saving attachments: {str(e)}", exc_info=True)
            return request.make_json_response({
                'success': False,
                'error': str(e)
            }, status=500)



# =======================================stage 5=================================================

    @http.route('/upload/stage51', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage51(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        file = request.httprequest.files.get('file')
        client_id = post.get('client_id')

        if not file or not client_id:
            return request.make_json_response({'success': False, 'error': 'Missing data'}, status=400)

        try:
            file_content = base64.b64encode(file.read())
            file_name = file.filename

            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': file_content,
                'res_model': 'crm.client',
                'res_id': int(client_id),
                'type': 'binary',
                'mimetype': file.content_type,
            })

            # Save the attachment to the client record
            client = request.env['crm.client'].sudo().browse(int(client_id))
            client.advance_paid_attachment = attachment.id

            return request.make_json_response({'success': True})
        except Exception as e:
            return request.make_json_response({'success': False, 'error': str(e)}, status=500)
        
    @http.route('/upload/stage52', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage52(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        file = request.httprequest.files.get('file')
        client_id = post.get('client_id')

        if not file or not client_id:
            return request.make_json_response({'success': False, 'error': 'Missing data'}, status=400)

        try:
            file_content = base64.b64encode(file.read())
            file_name = file.filename

            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': file_content,
                'res_model': 'crm.client',
                'res_id': int(client_id),
                'type': 'binary',
                'mimetype': file.content_type,
            })

            # Save the attachment to the client record
            client = request.env['crm.client'].sudo().browse(int(client_id))
            client.readiness_collected_attachment = attachment.id

            return request.make_json_response({'success': True})
        except Exception as e:
            return request.make_json_response({'success': False, 'error': str(e)}, status=500)
        
    
    @http.route('/upload/stage53', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage53(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        file = request.httprequest.files.get('file')
        client_id = post.get('client_id')

        if not file or not client_id:
            return request.make_json_response({'success': False, 'error': 'Missing data'}, status=400)

        try:
            file_content = base64.b64encode(file.read())
            file_name = file.filename

            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': file_content,
                'res_model': 'crm.client',
                'res_id': int(client_id),
                'type': 'binary',
                'mimetype': file.content_type,
            })

            # Save the attachment to the client record
            client = request.env['crm.client'].sudo().browse(int(client_id))
            client.handover_attachment = attachment.id

            return request.make_json_response({'success': True})
        except Exception as e:
            return request.make_json_response({'success': False, 'error': str(e)}, status=500)
        
    @http.route('/upload/stage54', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage54(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        file = request.httprequest.files.get('file')
        client_id = post.get('client_id')

        if not file or not client_id:
            return request.make_json_response({'success': False, 'error': 'Missing data'}, status=400)

        try:
            file_content = base64.b64encode(file.read())
            file_name = file.filename

            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': file_content,
                'res_model': 'crm.client',
                'res_id': int(client_id),
                'type': 'binary',
                'mimetype': file.content_type,
            })

            # Save the attachment to the client record
            client = request.env['crm.client'].sudo().browse(int(client_id))
            client.balance_attachment = attachment.id

            return request.make_json_response({'success': True})
        except Exception as e:
            return request.make_json_response({'success': False, 'error': str(e)}, status=500)



# =========================== Stage 6 =================================

    @http.route('/upload/stage6', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage6(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        file = request.httprequest.files.get('file')
        client_id = post.get('client_id')

        if not file or not client_id:
            return request.make_json_response({'success': False, 'error': 'Missing data'}, status=400)

        try:
            file_content = base64.b64encode(file.read())
            file_name = file.filename

            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': file_content,
                'res_model': 'crm.client',
                'res_id': int(client_id),
                'type': 'binary',
                'mimetype': file.content_type,
            })

            # Save the attachment to the client record
            client = request.env['crm.client'].sudo().browse(int(client_id))
            client.material_dispatch_attachment = attachment.id

            return request.make_json_response({'success': True})
        except Exception as e:
            return request.make_json_response({'success': False, 'error': str(e)}, status=500)
        
        
# =========================== Stage 7 =================================

    @http.route('/upload/stage7', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage7(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        file = request.httprequest.files.get('file')
        client_id = post.get('client_id')

        if not file or not client_id:
            return request.make_json_response({'success': False, 'error': 'Missing data'}, status=400)

        try:
            file_content = base64.b64encode(file.read())
            file_name = file.filename

            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': file_content,
                'res_model': 'crm.client',
                'res_id': int(client_id),
                'type': 'binary',
                'mimetype': file.content_type,
            })

            # Save the attachment to the client record
            client = request.env['crm.client'].sudo().browse(int(client_id))
            client.preinstallation_attachment = attachment.id
            client.start_installation = post.get('start_installation').lower()

            return request.make_json_response({'success': True})
        except Exception as e:
            return request.make_json_response({'success': False, 'error': str(e)}, status=500)
        
        
        # ===================== stage 8 ==========================

    @http.route('/upload/stage8', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage8(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        file = request.httprequest.files.get('file')
        client_id = post.get('client_id')

        if not file or not client_id:
            return request.make_json_response({'success': False, 'error': 'Missing data'}, status=400)

        try:
            file_content = base64.b64encode(file.read())
            file_name = file.filename

            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': file_content,
                'res_model': 'crm.client',
                'res_id': int(client_id),
                'type': 'binary',
                'mimetype': file.content_type,
            })

            # Save the attachment to the client record
            client = request.env['crm.client'].sudo().browse(int(client_id))
            client.attachment_handover = attachment.id

            return request.make_json_response({'success': True})
        except Exception as e:
            return request.make_json_response({'success': False, 'error': str(e)}, status=500)
        

# =========== auto switch type in crm client ================================

    @http.route('/crm/client/toggle_type', type='http', auth='user',website=True,csrf=False, methods=['POST'])
    def toggle_client_type(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get("id"))
        client = request.env['crm.client'].sudo().browse(client_id)
        result={}
        if client and client.exists():
            if client.amc:  # AMC → Service
                client.write({'amc': False, 'service': True,})
                client.write({
                    'amc_start_date': False,
                    'amc_end_date': False,
                    'renew': False,
                    'not_renew':  False,
                    'renew_date': False,
                })

            result = {"success": True}
        result= {"success": False}
        
        return request.make_json_response(result)



    # Activate AMC (Service → AMC)
    @http.route('/crm/client/activate_amc', type='http', auth='user',website=True,csrf=False, methods=['POST'])
    def activate_amc(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get("client_id"))
        client = request.env['crm.client'].sudo().browse(client_id)

        if not client or not client.exists():
            return {"success": False}

        # Get values
        amc_start_date = post.get("amc_start_date")
        amc_end_date = post.get("amc_end_date")
        renewal = post.get("renewed")
        renew_date = post.get("renew_date") or False

        # Write to DB
        client.write({
            'amc': True,
            'service': False,
            'amc_start_date': amc_start_date,
            'amc_end_date': amc_end_date,
            'renew': True if renewal == 'true' else False,
            'not_renew': True if renewal == 'false' else False,
            'renew_date': renew_date,
        })

        result= {"success": True}
        return request.make_json_response(result)
    

    # @http.route('/opportunity/assign/single', type='http', auth='user', methods=['POST'], csrf=False)
    # def assign_single(self, **kw):
    #     data = json.loads(request.httprequest.data)
    #     lead_id = data.get('lead_id')
    #     user_id = data.get('user_id')
    #     if lead_id and user_id:
    #         lead = request.env['crm.lead'].sudo().browse(int(id))
    #         lead.user_id = int(user_id)
    #         return json.dumps({'success': True})
    #     return json.dumps({'success': False})

    @http.route('/crm/assign/bulk', type='http', auth='user', methods=['POST'], csrf=False)
    def assign_bulk(self, **kw):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        crm_new_stage = request.env['crm.stage'].search([
                            ('name', '=', 'New'),
                            ('stage','=','crm')
                        ], limit=1)
        crm_won_stage = request.env['crm.stage'].search([
                            ('name', '=', 'Won'),
                            ('stage','=','crm')
                        ], limit=1)
        if my_groups.is_admin:
            data = json.loads(request.httprequest.data)
            assignments = data.get('assignments', [])
            for item in assignments:
                lead_id = item.get('client_id')
                user_id = item.get('user_id')
                if lead_id and user_id:
                    lead = request.env['crm.client'].sudo().browse(int(lead_id))
                    lead.assign_to = int(user_id)
                    if lead.stage_id == (crm_won_stage):
                        lead.stage_id = int(crm_new_stage)
            return json.dumps({'success': True})
        else:
            return json.dumps({'success': False})
    


    # ================== stage 5 edit button =============
from bs4 import BeautifulSoup
class CrmClientController(http.Controller):


    @http.route('/crm/client/check_admin_password', type='http', auth='user', methods=['POST'], csrf=False)
    def check_admin_password(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        password = post.get("password")
        if not password:
            return {'valid': False}

        admin_user = request.env['res.users'].sudo().search([('id', '=', 2)], limit=1)
        if not admin_user:
            return json.dumps({'valid': False})

        try:
            raw_html = admin_user.signature or ""
            text = BeautifulSoup(raw_html, "html.parser").get_text().strip()
            if password == text:
                return json.dumps({'valid': True})
            else:
                return json.dumps({'valid': False})
            #     admin_user.sudo()._check_credentials({'type': 'password', 'password': password},
            #                                     user_agent_env={'interactive': True})
            #     return json.dumps({'valid': True})
        except AccessDenied:
            return json.dumps({'valid': False})
        

# ============ proceed stages===============

    @http.route('/update/stage9/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage9(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get("client_id"))
        stage9 = post.get("stage9") == "true"

        client = request.env['crm.client'].browse(client_id)
        if client.exists() and stage9:
            client.write({"stage9": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/update/stage8/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage8(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get("client_id"))
        stage8 = post.get("stage8") == "true"

        client = request.env['crm.client'].browse(client_id)
        if client.exists() and stage8:
            client.write({"stage8": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/update/stage7/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage7(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get("client_id"))
        stage7 = post.get("stage7") == "true"

        client = request.env['crm.client'].browse(client_id)
        if client.exists() and stage7:
            client.write({"stage7": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/update/stage6/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage6(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get("client_id"))
        stage6 = post.get("stage6") == "true"

        client = request.env['crm.client'].browse(client_id)
        if client.exists() and stage6:
            client.write({"stage6": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/update/stage5/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage5(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get("client_id"))
        stage5 = post.get("stage5") == "true"

        client = request.env['crm.client'].browse(client_id)
        if client.exists() and stage5:
            client.write({"stage5": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/update/stage4/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage4(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get("client_id"))
        stage4 = post.get("stage4") == "true"

        client = request.env['crm.client'].browse(client_id)
        if client.exists() and stage4:
            client.write({"stage4": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/update/stage1/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage1(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get("client_id"))
        stage1 = post.get("stage1") == "true"

        client = request.env['crm.client'].browse(client_id)
        if client.exists() and stage1:
            client.write({"stage1": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/update/stage2/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage2(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'crm.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get("client_id"))
        stage2 = post.get("stage2") == "true"

        client = request.env['crm.client'].browse(client_id)
        if client.exists() and stage2:
            client.write({"stage2": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})


   
