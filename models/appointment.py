# -*- coding: utf-8 -*-
##############################################################################
#
#    Multi Canal Services Ltd.
#    Copyright (C) 2017-TODAY Multi Canal Services(<https://www.MultiCanalServices.com>).
#    Maintainer: Multi Canal Services (<https://www.MultiCanalServices.com>)
#
##############################################################################


from odoo.exceptions import UserError
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from odoo import fields, models, api, _


class RdvRecord(models.Model):
    _name = 'rdv.record'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'name'
    _description = "rendez-vous"
    _order = 'patient_date_rdv'

    name = fields.Many2one('patient.record', string='Nom patient', required=True)
    patient_date_rdv = fields.Datetime(string="Date", default=lambda self: fields.Datetime.now(),
                                       help="date du rendez-vous", required=True)
    id_rdv = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    motif_rdv = fields.Text(string="Motif",  required=True)
    doctor_rdv = fields.Many2one('hr.employee', string="Médecin",  domain="[('doctor_rdv','=',True)]", required=True)
    #app_id = fields.Many2one('patient.record', string='patients')
    state = fields.Selection([
        ('draft', 'brouillon'),
        ('confirm', 'Confirmé'),
        ('cancel', 'Annulé'),
        ('done', 'effectué'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft',
    )

    @api.model
    def create(self, vals):
        if vals:
            vals['id_rdv'] = self.env['ir.sequence'].next_by_code('rdv.record') or _('New')
            result = super(RdvRecord, self).create(vals)
            return result

    @api.multi
    def confirm_appointment(self):

        self.write({'state': 'confirm'})

    @api.multi
    def cancel_appointment(self):
        return self.write({'state': 'cancel'})

        # les differentes fonctions qui permettent d'envoyer un template mail


    @api.multi
    def appointment_done(self):
        return self.write({'state': 'done'})

    @api.multi
    def action_sent(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('dental_office', 'email_template_edi_rdv')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'rdv.record',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.one
    @api.constrains('patient_date_rdv')
    #DEFAULT_SERVER_DATE_FORMAT= %Y-%m-%d
    def _check_date_pubd(self):
        if self.patient_date_rdv:
            if datetime.strptime(self.patient_date_rdv,DEFAULT_SERVER_DATE_FORMAT+' %H:%M:%S') < datetime.now():
                raise ValidationError(('Imposible de prendre à une date et une heure antérieure'))


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'rdv.record' and self._context.get('default_res_id'):
            order = self.env['rdv.record'].browse([self._context['default_res_id']])
            if order.state == 'draft':
                order.state = 'confirm'
            order.sent = True
            self = self.with_context(mail_post_autofollow=True)
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)


class PatientInherit(models.Model):
    _inherit = 'patient.record'

    app_count = fields.Integer(compute="_compute_state_rdv", string='# of Appointments', copy=False, default=0)

    @api.multi
    def _compute_state_rdv(self):
        for obj in self:
            obj.app_count = self.env['rdv.record'].search_count([('name', '=', obj.id)])


class PatientWhatsapp(models.Model):
    _inherit = 'patient.record'

    mobile_whatsapp_link = fields.Html(compute='compute_mobile_whatsapp_link')

    def compute_mobile_whatsapp_link(self):
        for record in self:
            body = ''

            if record.mobile:
                body = """
                <a target="_blank" href="https://api.whatsapp.com/send?phone=%s">
                    <i class="fa fa-whatsapp"/> <span class="hidden-lg hidden-xl">Send via Whatsapp</span>
                </a>                
                """ % record.mobile
            record.mobile_whatsapp_link = body
