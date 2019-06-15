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


class ordMedical(models.Model):
    _name = 'ord.medical'
    _rec_name = 'name'
    _description = "Ordonnance"

    ref = fields.Char(string='Reference', size=16, readonly=True, required=True, help="ID traitement",
                      default=lambda *a: '#')
    name = fields.Many2one('patient.record', string="Nom du patient" , required=True)
    Observation = fields.Html(string="Observation")
    date_ord = fields.Datetime(string='Date du jour', default=lambda s: fields.Datetime.now(), required=True)
    nom_medec = fields.Integer(compute='_get_current')
    nom_medecin = fields.Char(compute='_get_current_ord', string="Nom du médecin", readonly=True)
    nom_med = fields.One2many('medicament.lines', 'med_id', string="Nom du medicament", required=1, ondelete='cascade')
    duree = fields.Date(string="Echeance", required=True)


    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ord.medical')
        vals['ref'] = sequence or '/'
        return super(ordMedical, self).create(vals)

    @api.depends()
    def _get_current(self):
        self.nom_medec = self.create_uid

    @api.depends()
    def _get_current_ord(self):
        obj_user = self.env['res.users'].search([('id', '=', self.nom_medec)])
        self.nom_medecin = obj_user.name

    @api.depends('Observation')
    def parseHtml(self):
        h = HTMLParser()

        for obj in self:
            return h.unescape(obj.Observation)

    class SoinsLines(models.Model):
        _name = 'medicament.lines'

        nom = fields.Many2one('medicament.record', string="Nom Medicament", required=1)
        prise = fields.Text(string='Prise par defaut')
        gramme = fields.Char(string='Grammage')
        med_id = fields.Many2one('ord.medical', string='Code Medicament')

        @api.onchange('nom')
        def prise_update(self):
            if self.nom:
                self.prise = self.nom.prise_medicament
                self.gramme = self.nom.gramme

    class OrdPatientInherit(models.Model):
        _inherit = 'patient.record'

        ord_count = fields.Integer(compute="_compute_state2", string='# of ordonnances', copy=False, default=0)

        @api.multi
        def _compute_state2(self):
            for obj in self:
                obj.ord_count = self.env['ord.medical'].search_count([('name', '=', obj.id)])
