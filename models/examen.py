from odoo import api, fields, models, _
from HTMLParser import HTMLParser


class examenRecord(models.Model):

    _name = 'examen.record'
    _rec_name = 'name'

    ref = fields.Char(string='Reference', size=16, readonly=True, required=True, help="ID Examen",
                      default=lambda *a: '#')
    name = fields.Many2one('patient.record', string='Nom patient', required=True)
    date_ordonnance = fields.Date(string='Date de delivrance', default=fields.Date.today, required=True)
    nom_examen = fields.Char(string='Nom examen', required=True)
    user_medecin = fields.Integer(compute='_get_current_exa')
    nom_medecin = fields.Char(compute='_get_current_exam', string="Nom du medecin", readonly=True)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('examen.record')
        vals['ref'] = sequence or '/'
        return super(examenRecord, self).create(vals)

    @api.depends()
    def _get_current_exa(self):
        self.user_medecin = self.create_uid

    @api.depends()
    def _get_current_exam(self):
        obj_user = self.env['res.users'].search([('id', '=', self.user_medecin)])
        self.nom_medecin = obj_user.name

    class ExaPatientInherit(models.Model):
        _inherit = 'patient.record'

        exa_count = fields.Integer(compute="_compute_stat", string='# of examens', copy=False, default=0)

        @api.multi
        def _compute_stat(self):
            for obj in self:
                obj.exa_count = self.env['examen.record'].search_count([('name', '=', obj.id)])





