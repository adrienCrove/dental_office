# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Maintainer: Cybrosys Technologies (<https://www.cybrosys.com>)
#
##############################################################################
from odoo import models, fields, api


class DentRequestInvoices(models.Model):
    _inherit = 'account.invoice'

    is_dent_invoice = fields.Boolean(string="Is Invoice")
    test_devis = fields.Many2one('devis.record', string="ID Devis", help="Source Document")
    montant_assur = fields.Float(string="Montant Assurance", readonly=True)
    montant_patient = fields.Float(string="Montant Patient", readonly=True)
    pourcentage_assureur = fields.Integer(string='Pourcentage Assuré', readonly=True)
    consultation_id = fields.Many2one('consultation.record', string='Consultation')
    patient_name = fields.Many2one('res.partner', string='Nom Patient', ondelete="cascade", required=True, delegate=True)
    user_medecin = fields.Integer(compute='_get_current_exa')
    nom_medecin = fields.Char(compute='_get_current_exam', string="Nom du medecin", readonly=True)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('account.invoice')
        vals['ref'] = sequence or '/'
        return super(DentRequestInvoices, self).create(vals)

    @api.depends()
    def _get_current_exa(self):
        self.user_medecin = self.create_uid

    @api.depends()
    def _get_current_exam(self):
        obj_user = self.env['res.users'].search([('id', '=', self.user_medecin)])
        self.nom_medecin = obj_user.name


class DentRequestInvoices(models.Model):
    _inherit = 'account.invoice.line'

    dent = fields.Char(string='N° Dent')
    code = fields.Char(string="Code")


