# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Maintainer: Cybrosys Technologies (<https://www.cybrosys.com>)
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ConsultationPatient(models.Model):
    _name = 'consultation.record'
    _rec_name = 'id_consult'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Consultation"

    name = fields.Many2one('patient.record', string='Nom patient', required=True)
    id_consult = fields.Char(string='Réference', size=16, readonly=True, required=True, help="ID consultation",
                             default=lambda *a: '#')
    dents = fields.Many2many('record.dents', string='Dents')
    diagnotic = fields.Text(string="Diagnostic", required=True)
    traitpre = fields.Text(string="Traitement préconisé")
    date_consult = fields.Datetime(string='Date du jour', default=lambda s: fields.Datetime.now())
    amount = fields.Float(string='Montant', required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('confirmed', 'Confirmé')],
                             string='Status', readonly=True, copy=False, index=True, track_visibility='onchange',
                             default='draft', )
    invoice_ids = fields.One2many('account.invoice', 'consultation_id', string='Invoices', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'consultation.record'))

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('consultation.record')
        vals['id_consult'] = sequence or '/'
        return super(ConsultationPatient, self).create(vals)

    @api.multi
    def create_invoice(self):
        self.write({'state': 'confirmed'})
        self.env['account.invoice'].create({
            'type': 'out_invoice',
            'partner_id': self.name.id_name.id,
            'user_id': self.env.user.id,
            'consultation_id': self.id,
            'state': 'draft',
            'origin': self.id_consult,
            'invoice_line_ids': [(0, 0, {
                'name': 'Consultation',
                'quantity': 1,
                'price_unit': self.amount,
                'account_id': self.name.id_name.property_account_receivable_id.id,
            })],
        })

    class ConAccountInvoiceRelate(models.Model):
        _inherit = 'account.invoice'

        consultation_id = fields.Many2one('consultation.record', string='Consultation')

    class DentPatientInherit(models.Model):
        _inherit = 'patient.record'

        consult_count = fields.Integer(compute="_compute_state_consult", string='# de consultation', copy=False,
                                       default=0)

        @api.multi
        def _compute_state_consult(self):
            for obj in self:
                obj.consult_count = self.env['consultation.record'].search_count([('name', '=', obj.id)])

    class DentPatient(models.Model):
        _name = 'record.dents'
        _rec_name = 'dents'

        dents = fields.Char(string="Dents")
