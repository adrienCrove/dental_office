from odoo import api,fields, models


class TypedocumentRecord(models.Model):

    _name = 'type_document.record'
    _rec_name = 'nom'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    nom = fields.Char(string="Nom Document", required=True)
    code = fields.Char(string="Code document", required=True)
