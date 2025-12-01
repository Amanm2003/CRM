
import json
import logging
from odoo import http
from odoo.http import request
from datetime import date, timedelta
import base64

class ProductionController(http.Controller):

    @http.route('/production/list', type='http', auth='user', website=True)
    def production_client_list(self, **kw):
        my_group = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'production.client'),
                ('group_id', '=', my_group.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        my_groups = request.env['res.groups'].sudo().search([('ismy', '=', True)])
        users_in_my_groups = request.env['res.users'].sudo().search([
            ('active', '=', True),
            ('groups_id', 'in', my_groups.ids)
        ])
        final_users = []
        for user in users_in_my_groups:
            access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'production.client'),
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
        if my_group.is_admin:
            productions = request.env['production.client'].sudo().search([])
        else:
            productions = request.env['production.client'].sudo().search([('assign_to','=',request.env.user.id)])
        return request.render('stag_elevators.production_client_list_template', {
            'productions': productions,
            'users': users
        })
    
    @http.route('/prod/list', type='http', auth='user', website=True)
    def prod_list(self, stage=None, **kwargs):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'production.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to Productions.'
            })
        if my_groups.is_admin:
            users_in_my_groups = request.env['res.users'].sudo().search([
                ('active', '=', True),
                ('groups_id', 'in', my_groups.ids)
            ])
            final_users = []
            for user in users_in_my_groups:
                access_rule = request.env['ir.model.access'].sudo().search([
                    ('model_id.model', '=', 'production.client'),
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
            domain = []
            if stage:
                domain.append(('stage_id.name', '=', stage))   # Adjust field as per your model

            records = request.env['production.client'].sudo().search(domain)

            return request.render('stag_elevators.production_client_list_template', {
                'productions': records,
                'stage': stage,
                'users':users,
            })
        else:
            domain = []
            if stage:
                domain.append(('stage_id.name', '=', stage))
                domain.append(('assign_to','=',request.env.user.id))   # Adjust field as per your model

            records = request.env['production.client'].sudo().search(domain)

            return request.render('stag_elevators.production_client_list_template', {
                'productions': records,
                'stage': stage,
            })

    
    @http.route('/production/client/edit/<int:client_id>', type='http', auth='user', website=True)
    def edit_client(self, client_id, **kw):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'production.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client = request.env['production.client'].sudo().browse(client_id)
        lead_id = request.env['crm.lead'].sudo().search([('id', '=', client.lead_id.id)])
        crm = request.env['crm.client'].search([('lead_id','=',lead_id.id)])
        # crm = request.env['crm.client'].sudo().browse(client_id)
        stages = request.env['crm.stage'].sudo().search([('stage', '=', 'production')])
        return request.render('stag_elevators.edit_production_client_template', {'client': client,'stages': stages,'crm':crm,})

    @http.route('/production/client/update', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def update_prod_client(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'production.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        client_id = int(post.get('client_id'))
        client = request.env['production.client'].sudo().browse(client_id)

        if client:  
            stage1 = post.get('stage1_hidden') == '1'
            stage2 = post.get('stage2_hidden') == '1'
            stage3 = post.get('stage3_hidden') == '1'
            stage4 = post.get('stage4_hidden') == '1'
            stage5 = post.get('stage5_hidden') == '1'
            stage6 = post.get('stage6_hidden') == '1'
            stage7 = post.get('stage7_hidden') == '1'
            stage8 = post.get('stage8_hidden') == '1'
            stage9 = post.get('stage9_hidden') == '1'
            site_visit_person = post.get('visitPerson_hidden')
            model_no = post.get('modelNo_hidden')
            shaft_type = post.get('shaftType_hidden')
            start_installation = post.get('startInstallation_hidden')
            material_dispatch = post.get('material_dispatch_hidden') == '1'
            material_delivery = post.get('material_delivery_hidden') == '1'
            material_delivery_date = post.get('material_delivery_date_hidden')
            material_dispatch_date = post.get('material_dispatch_date_hidden')
            ongoing = post.get('ongoing_hidden') == '1'
            handover = post.get('handover_hidden') == '1'
            completed = post.get('completed_hidden') == '1'
            handover_date = post.get('handover_date_hidden')
            installation_schedule = post.get('installation_schedule_hidden') == '1'
            installation_schedule_date = post.get('installation_schedule_date_hidden')
            installation_schedule_remark = post.get('installation_schedule_remark_hidden')
            glass_schedule = post.get('glass_schedule_hidden') == '1'
            glass_schedule_date = post.get('glass_schedule_date_hidden')
            glass_schedule_remark = post.get('glass_schedule_remark_hidden')

            

            client.write({
                'lead_model': post.get('lead_model'),
                'floor': post.get('floor'),
                'shaft': post.get('shaft'),
                'followup_date': post.get('followup_date') or False,
                'followup_description': post.get('followup_description'),
                'contact_address': post.get('contact_address'),
                
                'stage1':stage1,
                'stage2':stage2,
                'stage3':stage3,
                'stage4':stage4,
                'stage5':stage5,
                'stage6':stage6,
                'stage7':stage7,
                'stage8':stage8,
                'stage9':stage9,
                'site_visit_person':site_visit_person,
                'model_no':model_no,
                'shaft_type':shaft_type,
                'start_installation':start_installation,
                'material_dispatch':material_dispatch,
                'material_delivery':material_delivery,
                'material_delivery_date':material_delivery_date,
                'material_dispatch_date':material_dispatch_date,
                'ongoing':ongoing,
                'completed':completed,
                'handover':handover,
                'handover_date':handover_date,
                'installation_schedule':installation_schedule,
                'installation_schedule_date':installation_schedule_date,
                'installation_schedule_remark':installation_schedule_remark,
                'glass_schedule':glass_schedule,
                'glass_schedule_date':glass_schedule_date,
                'glass_schedule_remark':glass_schedule_remark,   
            })
            stage_id = post.get('stage_id')
            if stage_id:
                client.stage_id = int(stage_id)

            # Update related lead
            lead = client.lead_id
            if lead:
                lead.write({
                    'city': post.get('client.lead_id.city'),
                    'email_from': post.get('email'),
                })
        

        return request.redirect(f'/production/client/edit/{client_id}')
    

    


    @http.route('/production/stage1/upload', type='http', auth='user', csrf=False, methods=['POST'])
    def production_stage1_upload(self, **post):
        client_id = post.get("client_id")
        files = request.httprequest.files.getlist("siteVisitImages[]")
        attachments = []
        for file in files:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(file.read()),
                'res_model': 'production.client',
                'res_id': int(client_id),
                'mimetype': file.content_type,
            })
            attachments.append(attachment.id)

        client = request.env['production.client'].sudo().browse(int(client_id))
        if client.exists():
            client.sudo().write({
                'site_visit_images': [(6, 0, attachments)]
            })
            return http.Response(
                '{"success": true, "message": "Uploaded successfully"}',
                content_type="application/json"
            )

        return http.Response(
            '{"success": false, "message": "Client not found"}',
            content_type="application/json"
        )
    
    @http.route('/production/stage6/upload', type='http', auth='user', csrf=False, methods=['POST'])
    def production_stage6_upload(self, **post):
        client_id = post.get("client_id")
        files = request.httprequest.files.getlist("stage6_attachment")
        attachments = []
        for file in files:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(file.read()),
                'res_model': 'production.client',
                'res_id': int(client_id),
                'mimetype': file.content_type,
            })
            attachments.append(attachment.id)

        client = request.env['production.client'].sudo().browse(int(client_id))
        if client.exists():
            client.material_dispatch_attachment=attachments[0]
            return http.Response(
                '{"success": true, "message": "Uploaded successfully"}',
                content_type="application/json"
            )

        return http.Response(
            '{"success": false, "message": "Client not found"}',
            content_type="application/json"
        )
    
    @http.route('/production/stage7/upload', type='http', auth='user', csrf=False, methods=['POST'])
    def production_stage7_upload(self, **post):
        client_id = post.get("client_id")
        files = request.httprequest.files.getlist("stage7_attachment")
        attachments = []
        for file in files:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(file.read()),
                'res_model': 'production.client',
                'res_id': int(client_id),
                'mimetype': file.content_type,
            })
            attachments.append(attachment.id)

        client = request.env['production.client'].sudo().browse(int(client_id))
        if client.exists():
            client.stage_7_attachment=attachments[0]
            return http.Response(
                '{"success": true, "message": "Uploaded successfully"}',
                content_type="application/json"
            )

        return http.Response(
            '{"success": false, "message": "Client not found"}',
            content_type="application/json"
        )
    
    @http.route('/production/stage8/upload', type='http', auth='user', csrf=False, methods=['POST'])
    def production_stage8_upload(self, **post):
        client_id = post.get("client_id")
        files = request.httprequest.files.getlist("stage8_attachment")
        attachments = []
        for file in files:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(file.read()),
                'res_model': 'production.client',
                'res_id': int(client_id),
                'mimetype': file.content_type,
            })
            attachments.append(attachment.id)

        client = request.env['production.client'].sudo().browse(int(client_id))
        if client.exists():
            client.attachment_handover=attachments[0]
            return http.Response(
                '{"success": true, "message": "Uploaded successfully"}',
                content_type="application/json"
            )

        return http.Response(
            '{"success": false, "message": "Client not found"}',
            content_type="application/json"
        )
    
    @http.route('/production/stage81/upload', type='http', auth='user', csrf=False, methods=['POST'])
    def production_stage81_upload(self, **post):
        client_id = post.get("client_id")
        files = request.httprequest.files.getlist("stage81_attachment")
        attachments = []
        for file in files:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(file.read()),
                'res_model': 'production.client',
                'res_id': int(client_id),
                'mimetype': file.content_type,
            })
            attachments.append(attachment.id)

        client = request.env['production.client'].sudo().browse(int(client_id))
        if client.exists():
            client.installation_schedule_attachment=attachments[0]
            return http.Response(
                '{"success": true, "message": "Uploaded successfully"}',
                content_type="application/json"
            )

        return http.Response(
            '{"success": false, "message": "Client not found"}',
            content_type="application/json"
        )
    
    @http.route('/production/stage82/upload', type='http', auth='user', csrf=False, methods=['POST'])
    def production_stage82_upload(self, **post):
        client_id = post.get("client_id")
        files = request.httprequest.files.getlist("stage82_attachment")
        attachments = []
        for file in files:
            attachment = request.env['ir.attachment'].sudo().create({
                'name': file.filename,
                'datas': base64.b64encode(file.read()),
                'res_model': 'production.client',
                'res_id': int(client_id),
                'mimetype': file.content_type,
            })
            attachments.append(attachment.id)

        client = request.env['production.client'].sudo().browse(int(client_id))
        if client.exists():
            client.glass_schedule_attachment=attachments[0]
            return http.Response(
                '{"success": true, "message": "Uploaded successfully"}',
                content_type="application/json"
            )

        return http.Response(
            '{"success": false, "message": "Client not found"}',
            content_type="application/json"
        )
    
    @http.route('/production/upload/stage2', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_stage2(self, **post):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'production.client'),
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
        client = request.env['production.client'].sudo().browse(int(client_id))

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
                client = request.env['production.client'].sudo().browse(int(client_id))

            

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
                    'res_model': 'production.client',
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
        
    @http.route('/Pupdate/stage1/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage1(self, **post):
        client_id = int(post.get("client_id"))
        stage1 = post.get("stage1") == "true"

        client = request.env['production.client'].browse(client_id)
        if client.exists() and stage1:
            client.write({"stage1": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/Pupdate/stage2/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage2(self, **post):
        client_id = int(post.get("client_id"))
        stage2 = post.get("stage2") == "true"

        client = request.env['production.client'].browse(client_id)
        if client.exists() and stage2:
            client.write({"stage2": True,"stage3":True,"stage4":True,"stage5":True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/Pupdate/stage6/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage6(self, **post):
        client_id = int(post.get("client_id"))
        stage6 = post.get("stage6") == "true"

        client = request.env['production.client'].browse(client_id)
        if client.exists() and stage6:
            client.write({"stage6": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/Pupdate/stage7/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage7(self, **post):
        client_id = int(post.get("client_id"))
        stage7 = post.get("stage7") == "true"

        client = request.env['production.client'].browse(client_id)
        if client.exists() and stage7:
            client.write({"stage7": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/Pupdate/stage8/proceed', type='http', auth='user', methods=['POST'], csrf=False)
    def update_stage8(self, **post):
        client_id = int(post.get("client_id"))
        stage8 = post.get("stage8") == "true"

        client = request.env['production.client'].browse(client_id)
        if client.exists() and stage8:
            client.write({"stage8": True})
            return json.dumps({"success": True})
        return json.dumps({"success": False, "error": "Invalid request"})
    
    @http.route('/prod/assign/bulk', type='http', auth='user', methods=['POST'], csrf=False)
    def assign_bulk(self, **kw):
        my_groups = request.env.user.groups_id.filtered(lambda g: g.ismy)
        access_rule = request.env['ir.model.access'].sudo().search([
                ('model_id.model', '=', 'production.client'),
                ('group_id', '=', my_groups.id),
                ('perm_read', '=', True)
            ], limit=1)
        if not access_rule:
            return request.render('stag_elevators.access_denied_template', {
                'message': 'You do not have permission to view.'
            })
        
        if my_groups.is_admin:
            data = json.loads(request.httprequest.data)
            assignments = data.get('assignments', [])
            for item in assignments:
                lead_id = item.get('client_id')
                user_id = item.get('user_id')
                if lead_id and user_id:
                    lead = request.env['production.client'].sudo().browse(int(lead_id))
                    lead.assign_to = int(user_id)
                    
            return json.dumps({'success': True})
        else:
            return json.dumps({'success': False})
        
    @http.route('/attachment/delete/<int:attachment_id>', type='http', auth='user', methods=['POST'], csrf=True)
    def delete_attachment(self, attachment_id, **kwargs):
        attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
        if attachment.exists():
            attachment.unlink()
        return request.redirect(request.httprequest.referrer or '/')