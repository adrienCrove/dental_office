# -*- coding: utf-8 -*-
##############################################################################
#
#    Multi Canal Services Ltd.
#    Copyright (C) 2017-TODAY Multi Canal Services(<https://www.MultiCanalServices.com>).
#    Maintainer: Multi Canal Services (<https://www.MultiCanalServices.com>)
#
##############################################################################

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from HTMLParser import HTMLParser


class certificatMedical(models.Model):
    _name = 'cert.medical'
    _rec_name = 'patient_id'
    _description = "Certificat du patient du cabinet medical"
    _order = 'patient_id'

    ref = fields.Char(string='Reference', size=16, readonly=True, required=True, help="ID Certificat",
                             default=lambda *a: '#')
    patient_id = fields.Many2one('patient.record', string="Patient", required=True)
    # activity = fields.Char(string="Occupation")
    period = fields.Integer(string="Duree", required=True)
    create_date = fields.Datetime(string='Date du jour', default=lambda s: fields.Datetime.now(), required=True)
    motif = fields.Selection([('ap', 'attestation presence'), ('at', 'arret de travail'), ], string='Motif', required=True)
    user_medecin = fields.Integer(compute='_get_current_cer')
    nom_medecin_cer = fields.Char(compute='_get_current_cert', string="Nom du médecin", readonly=True)

    @api.depends()
    def _get_current_cer(self):
        self.user_medecin = self.create_uid

    @api.depends()
    def _get_current_cert(self):
        obj_user = self.env['res.users'].search([('id', '=', self.user_medecin)])
        self.nom_medecin_cer = obj_user.name

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('cert.medical')
        vals['ref'] = sequence or _('New')
        return super(certificatMedical, self).create(vals)

    class CertPatientInherit(models.Model):
        _inherit = 'patient.record'

        cert_count = fields.Integer(compute="_compute_state_certificat", string='# of certificats', copy=False, default=0)

        @api.multi
        def _compute_state_certificat(self):
            for obj in self:
                obj.cert_count = self.env['cert.medical'].search_count([('patient_id', '=', obj.id)])
