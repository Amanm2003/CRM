{
    'name': 'StagElevator',
    'version': '1.0',
    'category': 'Website',
    'depends': ['base', 'web', 'auth_signup', 'website','crm','sale','sale_management','survey'],
    'author':'Aman Mishra',
    'data': [
        # 'security\security_groups.xml',
        'security/ir.model.access.csv',
        
        'views/login.xml',
        'views/prelogin_layout.xml',
        'views/postlogin_layout.xml',
        'views/dashboard.xml',
        'views/city.xml',
        'views/crm_stage_template.xml',
        'views/user_permission_list_template.xml',
        'views/user_list_template.xml',
        'views/leads.xml',
        'views/quotation.xml',
        'views/lead_followup_template.xml',
        'views/crm_client.xml',
        'views/production_client.xml',
    ],
    'assets': {
    'web.assets_frontend': [
        'stag_elevators/static/src/css/custom_login.css',
        'stag_elevators/static/src/img/stag_logo.png',
        # 'stag_elevators\static\src\js\stage4_upload.js',
        'stag_elevators\\static\\files\\lead_template.xlsx'
    ],
},

    'installable': True,
    'application': False,
}

