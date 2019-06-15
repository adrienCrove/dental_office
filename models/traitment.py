# -*- coding: utf-8 -*-
##############################################################################
#
#    Multi Canal Services Ltd.
#    Copyright (C) 2017-TODAY Multi Canal Services(<https://www.MultiCanalServices.com>).
#    Maintainer: Multi Canal Services (<https://www.MultiCanalServices.com>)
#
##############################################################################

import datetime
from odoo.exceptions import UserError
from odoo import fields, models, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class traitmentRecord(models.Model):
    _name = 'devis.record'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "name"

    name = fields.Many2one('patient.record', string='Nom patient', required=True)
    id_devis = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    devi_date = fields.Date(string="Date de confirmation", required=True, default=lambda s: fields.Datetime.now())
    line_soins = fields.One2many('soins.lines', 'devis_line_soin', required=1, ondelete='cascade')
    state = fields.Selection([
        ('draft', 'brouillon'),
        ('confirm', 'Confirmé'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft',
    )
    inv_count = fields.Integer(compute="_compute_state_inv", string='# of Invoices', copy=False, default=0)
    # currency_id = fields.Many2one("res.currency", string="Currency")
    total_amount = fields.Float(compute='get_total', string='Montant Total')
    total_amount_pat = fields.Float(compute='get_total_p', string='Montant Assureur')
    total_amount_ass = fields.Float(compute='get_total_a', string='Montant Patient')
    devis_lines = fields.One2many('soins.lines', 'devis_line_soin')
    is_assureur = fields.Many2one('res.partner', domain="[('is_assureur','=',True)]",string='Assuré par')
    numero = fields.Char(string='N° contribuable')
    pourcentage = fields.Integer(string='Pourcentage Assuré')

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('devis.record'))
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
                                          readonly=True)


    # constraint pourcentage
    @api.constrains('pourcentage')
    @api.one
    def _check_number(self):
        pourcentage = self.pourcentage
        if pourcentage > 100:
            raise ValidationError(_('Pourcentage est compris entre 0 et 100'))

    @api.onchange('name')
    def assur_update(self):
        if self.name:
            self.is_assureur = self.name.is_assureur
            self.numero = self.name.assurance_number
            self.pourcentage = self.name.pourcentage

    @api.multi
    @api.depends('line_soins')
    def get_total(self):
        total = 0
        for obj in self:
            for each in obj.line_soins:
                total += each.amount
            obj.total_amount = total

    @api.depends('total_amount', 'pourcentage')
    def get_total_p(self):
        for record in self:
            if record.total_amount > 0 and record.pourcentage > 0:
                record.total_amount_pat = (record.total_amount * record.pourcentage) / 100.0
            else:
                record.total_amount_pat = 0

    # IMPOSSIBILITE DE SUPPRIMER UN DEVIS CONFIRMER
    @api.multi
    def unlink(self):
        for d in self:
            if d.state not in 'draft':
                raise UserError(
                    ('Vous ne pouvez pas supprimer un devis qui est confirmé'))
        return super(traitmentRecord, self).unlink()

    # FIN IMPOSSIBILITE DE SUPPRIMER UN DEVIS CONFIRMER

    @api.depends('total_amount_pat', 'total_amount')
    def get_total_a(self):
        for record in self:
            if record.total_amount > 0 and record.total_amount_pat > 0:
                record.total_amount_ass = record.total_amount - record.total_amount_pat
            else:
                record.total_amount_ass = record.total_amount

    @api.model
    def create(self, vals):
        if vals:
            vals['id_devis'] = self.env['ir.sequence'].next_by_code('devis.record') or _('New')
            result = super(traitmentRecord, self).create(vals)
            return result

    @api.multi
    def _compute_state_inv(self):
        for obj in self:
            obj.inv_count = self.env['account.invoice'].search_count([('test_devis', '=', obj.id)])

    @api.multi
    def create_invoice(self):
        invoice_obj = self.env["account.invoice"]
        invoice_line_obj = self.env["account.invoice.line"]
        for dent in self:
            dent.write({'state': 'confirm'})
            if dent.id_devis:
                curr_invoice = {
                    'partner_id': dent.name.id_name.id,
                    'patient_name': dent.name.id_name.id,
                    'account_id': dent.name.id_name.property_account_receivable_id.id,
                    'state': 'draft',
                    'type': 'out_invoice',
                    'date_invoice': datetime.datetime.now(),
                    'origin': "Devis # : " + dent.id_devis,
                    'target': 'new',
                    'test_devis': dent.id,
                    'montant_assur': dent.total_amount_pat,
                    'montant_patient': dent.total_amount_ass,
                    'pourcentage_assureur': dent.pourcentage,
                    'is_dent_invoice': True
                }

                inv_ids = invoice_obj.create(curr_invoice)
                inv_id = inv_ids.id

                if inv_ids:
                    journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
                    prd_account_id = journal.default_credit_account_id.id
                    if dent.devis_lines:
                        for line in dent.devis_lines:
                            curr_invoice_line = {
                                'name': line.nomsoin.nomsoin,
                                'price_unit': line.prix or 0,
                                'dent': line.dent.dents,
                                'code': line.codsoin,
                                'account_id': prd_account_id,
                                'invoice_id': inv_id,
                            }

                            invoice_line_obj.create(curr_invoice_line)

                # self.write({'state': 'facture'})
                form_view_ref = self.env.ref('account.invoice_form', False)
                tree_view_ref = self.env.ref('account.invoice_tree', False)

                return {
                    'domain': "[('id', '=',  " + str(inv_id) + ")]",
                    'name': 'Facture Patient',
                    'view_mode': 'form',
                    'res_model': 'account.invoice',
                    'type': 'ir.actions.act_window',
                    'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
                }

        message_body = "Cher(e)" + self.name.name.name + "," + "<br>Votre devis a ete confirme" \
                                                               '<br><br>Merci'

        template_obj = self.env['mail.mail']
        template_data = {
            'subject': 'Devis confirmation',
            'body_html': message_body,
            'email_from': self.env.user.company_id.email,
            'email_to': self.name.patient_email
        }
        template_id = template_obj.create(template_data)
        template_obj.send(template_id)
        self.write({'state': 'confirm'})

    class SoinsLines(models.Model):
        _name = 'soins.lines'

        nomsoin = fields.Many2one('soins.record', string="Nom", required=1)
        codsoin = fields.Char(string='Code')
        prix = fields.Float(string="Prix")
        dent = fields.Many2one('record.dents', string="Dent")
        requesting_date = fields.Date(string="Date")
        amount = fields.Float(compute='compute_amount', string='Montant', readonly=True, store=True)
        devis_line_soin = fields.Many2one('devis.record', string="Devis")

        @api.onchange('nomsoin')
        def prix_update(self):
            if self.nomsoin:
                self.prix = self.nomsoin.prixsoin
                self.codsoin = self.nomsoin.codesoin


        @api.depends('prix')
        def compute_amount(self):
            for record in self:
                record.amount = record.amount+record.prix


    class DentPatientInherit(models.Model):
        _inherit = 'patient.record'

        app_count_devis = fields.Integer(compute="_compute_state_devis", string='# de Devis', copy=False, default=0)

        @api.multi
        def _compute_state_devis(self):
            for obj in self:
                obj.app_count_devis = self.env['devis.record'].search_count([('name', '=', obj.id)])
