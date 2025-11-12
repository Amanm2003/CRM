from multiprocessing import get_context
from odoo import api, models, fields
from odoo.exceptions import AccessDenied, ValidationError

# class UserRole(models.Model):
#     _name = 'user.role'
#     _description = 'User Permission Role'

#     name = fields.Char(string="User Role", required=True)

    # group_id = fields.Many2one(
    #     'res.groups',
    #     string="Linked Odoo Group",
    #     domain="[('id', 'in', [ref('stag_elevators.group_custom_admin'), ref('stag_elevators.group_custom_crm'), ref('stag_elevators.group_custom_sales')])]",
    #     readonly=True
    # )

    # @api.model
    # def create(self, vals):
    #     role_name = vals.get("name", "").strip().lower()

    #     if role_name not in ["admin", "crm", "sales"]:
    #         raise ValidationError("Role name must be one of: Admin, CRM, Sales")

    #     if role_name == "admin":
    #         vals["group_id"] = self.env.ref("stag_elevators.group_custom_admin").id
    #     elif role_name == "crm":
    #         vals["group_id"] = self.env.ref("stag_elevators.group_custom_crm").id
    #     elif role_name == "sales":
    #         vals["group_id"] = self.env.ref("stag_elevators.group_custom_sales").id

    #     return super(UserRole, self).create(vals)

    # def write(self, vals):
    #     if "name" in vals:
    #         role_name = vals.get("name", "").strip().lower()
    #         if role_name not in ["admin", "crm", "sales"]:
    #             raise ValidationError("Role name must be one of: Admin, CRM, Sales")

    #         if role_name == "admin":
    #             vals["group_id"] = self.env.ref("stag_elevators.group_custom_admin").id
    #         elif role_name == "crm":
    #             vals["group_id"] = self.env.ref("stag_elevators.group_custom_crm").id
    #         elif role_name == "sales":
    #             vals["group_id"] = self.env.ref("stag_elevators.group_custom_sales").id

    #     return super(UserRole, self).write(vals)

class ResGroups(models.Model):
    _inherit='res.groups'

    ismy = fields.Boolean()
    is_admin = fields.Boolean()

    _sql_constraints = [
        ('unique_group_name', 'unique(name)', 'Group name must be unique!')
    ]



from werkzeug.security import check_password_hash

class Users(models.Model):
    _inherit='res.users'

    lead_count = fields.Integer(String="lead count")


    role_id = fields.Many2one(
        'res.groups',
        string="User Role",
        help="Select a role (Admin, CRM, Sales). The corresponding group will be assigned automatically."
    )
    location = fields.Many2one('res.city')


