# -*- coding: utf-8 -*-
##############################################################################
#
#    Multi Canal Services Ltd.
#    Copyright (C) 2017-TODAY Multi Canal Services(<https://www.MultiCanalServices.com>).
#    Maintainer: Multi Canal Services (<https://www.MultiCanalServices.com>)
#
##############################################################################

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _


class PatientDocument(models.Model):
    _name = 'patient.document'
    _rec_name = 'id_doc'
    _description = 'Patient Documents'

    name = fields.Char(string='Nom du document', copy=False)
    id_doc = fields.Char(string='Réference', size=16, readonly=True, required=True, help="ID consultation",
                       default=lambda *a: '#')
    description = fields.Text(string='Description', copy=False)
    patient_ref = fields.Many2one('patient.record', invisible=1, copy=False)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Attachement",
                                         help='You can attach the copy of your document', copy=False, required=True)
    issue_date = fields.Date(string='Date', default=fields.datetime.now(), copy=False)
    type_doc = fields.Many2one('type_document.record', string='Type document')

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('patient.document')
        vals['id_doc'] = sequence or '/'
        return super(PatientDocument, self).create(vals)


class PatientDoc(models.Model):
    _inherit = 'patient.record'

    @api.multi
    def _document_count(self):
        for each in self:
            document_ids = self.env['patient.document'].search([('patient_ref', '=', each.id)])
            each.document_count = len(document_ids)

    @api.multi
    def document_view(self):
        self.ensure_one()
        domain = [
            ('patient_ref', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'patient.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Cliquez pour créer pour de nouveaux documents
                        </p>'''),
            'limit': 80,
            'context': "{'default_patient_ref': '%s'}" % self.id
        }

    document_count = fields.Integer(compute='_document_count', string='# Documents')


class PatientAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('patient.document', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Attachment", invisible=1)
