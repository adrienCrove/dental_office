from odoo import api, fields, models, _
from HTMLParser import HTMLParser


class expertiseRecord(models.Model):
    _name = 'expertise.record'
    _rec_name = 'patient_expertise'

    ref = fields.Char(string='Reference', size=16, readonly=True, required=True, help="ID Expertise",
                      default=lambda *a: '#')
    patient_expertise = fields.Many2one('patient.record', string='Nom patient', required=True)
    motif_expertise = fields.Text(string='Motif de l expertise', required=True)
    date_expertise = fields.Date(string='Date de  demande d expertise', default=fields.Date.today, required=True)
    user_medecin = fields.Integer(compute='_get_current_exper')
    nom_medecin = fields.Char(compute='_get_current_expert', string="Nom du medecin", readonly=True)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('expertise.record')
        vals['ref'] = sequence or '/'
        return super(expertiseRecord, self).create(vals)

    @api.depends()
    def _get_current_exper(self):
        self.user_medecin = self.create_uid

    @api.depends()
    def _get_current_expert(self):
        obj_user = self.env['res.users'].search([('id', '=', self.user_medecin)])
        self.nom_medecin = obj_user.name


class ExaPatientInherit(models.Model):
    _inherit = 'patient.record'

    exp_count = fields.Integer(compute="_compute_state_exp", string='# of examens', copy=False, default=0)

    @api.multi
    def _compute_state_exp(self):
        for obj in self:
            obj.exp_count = self.env['expertise.record'].search_count([('patient_expertise', '=', obj.id)])
