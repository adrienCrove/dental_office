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
import re
from odoo.exceptions import ValidationError
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class PatientRecord(models.Model):
    _name = 'patient.record'
    _description = "patient du cabinet medical"
    _order = 'name'

    # by convention, many2one fields end with '_id'
    active = fields.Boolean(default=True)
    id_name = fields.Many2one('res.partner', string='Nom', ondelete="cascade",
                              required=True, delegate=True)
    patient_name = fields.Char('Nom', related='id_name.name',
                               store=True, readonly=True)

    refp = fields.Char(string='Reference', size=16, readonly=True, required=True,
                       default=lambda *a: '#')
    patient_surname = fields.Char(string='Prenom')
    patient_photo = fields.Binary(string='Photo', filters='*.png,*.jpg')

    patient_gender = fields.Selection([('M', 'M'), ('F', 'F')], string='Genre', required=True)
    patient_civ = fields.Selection([('mr', 'Monsieur'), ('mme', 'Madame'), ('mlle', 'Mademoiselle'), ('enf', 'Enfant')],
                                   string='Civilité')
    patient_statut = fields.Selection([('c', 'Célibataire'), ('m', 'Marié(e)'), ('v', 'Veuf (ve)')],
                                      string='Statut matrimonial', required=True, default='c')
    patient_dental_scheme = fields.Selection([('a', 'Adulte'), ('e', 'Enfant')], string='Schema dentaire')
    # by convention, many2many fields end with '_ids'
    nationality_id = fields.Many2one('res.country', string='Pays', default=48)
    patient_telephone = fields.Char(string='Téléphone 1')
    patient_telephone_bis = fields.Char(string='Téléphone 2')
    patient_profession = fields.Char(string='Profession')
    patient_adress = fields.Char(string='Adresse')
    patient_street = fields.Char(string='Rue')
    patient_bp = fields.Char(string='Boite Postale')
    patient_region = fields.Selection(
        [('1', 'Adamaoua'), ('2', 'Centre'), ('3', 'Est'), ('4', 'Extreme-Nord'), ('5', 'Littoral'), ('6', 'Nord'),
         ('7', 'Nord-Ouest'), ('8', 'Ouest'), ('9', 'Sud'), ('10', 'Sud-Ouest')], string='Region', default='5')
    patient_town = fields.Char(string='Ville')
    patient_quartier = fields.Char(string='Quartier')
    patient_height = fields.Char(string='Poids')
    patient_email = fields.Char(string='Email')
    patient_comment = fields.Text(string='commmentaire')
    patient_tutor_name1 = fields.Char(string='Nom tuteur 1')
    patient_tutor_name2 = fields.Char(string='Nom tuteur 2')
    patient_tutor_number1 = fields.Char(string='Numero tuteur 1')
    patient_tutor_number2 = fields.Char(string='Numero tuteur 2')
    assurance_date = fields.Date(string='Date de validité')
    assurance_compagny = fields.Char(string="Compagnie d'assurance")
    assurance_number = fields.Char(string='N° Dossier assurance')
    invoice_idd = fields.One2many('account.invoice', 'test_devis', string='Vente', readonly=True)
    is_assureur = fields.Many2one('res.partner', string='Nom de l\'assurance', select=True)
    # assuranc = fields.Char(string="Compagnie d'assurance")
    pourcentage = fields.Integer(string='Pourcentage Assuré')
    rdv_ids = fields.One2many('rdv.record', 'name', readonly=True)
    ord_ids = fields.One2many('ord.medical', 'name', readonly=True)
    con_ids = fields.One2many('consultation.record', 'name', readonly=True)
    expertise_ligne = fields.One2many('expertise.record', 'patient_expertise', string='Demande expertise',
                                      readonly=True)
    certificat_ligne = fields.One2many('cert.medical', 'patient_id', string='Certificat medical', readonly=True)
    fact_ids = fields.One2many('account.invoice', 'name', readonly=True)
    date_patient_arrived = fields.Datetime(string='Date arrivée', default=lambda s: fields.Datetime.now(),
                                           invisible=True)
    date_inscription = fields.Datetime(string='Date d\'inscription', default=lambda s: fields.Datetime.now(),
                                       invisible=True)
    employee_patient = fields.Char(string='Nom de la société', index=True)
    """request = fields.Integer(compute="do_operation", string='# of appointment', copy=False, default=0)"""

    age = fields.Integer(string='Age', compute='compute_age', readonly=True)
    patient_dob = fields.Date(string="Date de naissance", required=True)
    date = fields.Datetime(string='Date Requested', default=lambda s: fields.Datetime.now(), invisible=True)

    # nom prenom
    firstname = fields.Char(
        "Prenom",
        index=True,
    )

    lastname = fields.Char(
        "Nom",
        index=True,
        required=True,
    )

    nameupdate = fields.Char(
        compute="_compute_name",
        required=False,
        store=True)

    @api.onchange('employee_patient')
    def set_u_upper(self):
        for record in self:
            if record.employee_patient != False:
                record.employee_patient = record.employee_patient.upper().encode('utf-8')
        return

    @api.onchange('lastname')
    def set_upper(self):
        for record in self:
            if record.lastname != False:
                record.lastname = record.lastname.upper().encode('utf-8')
        return

    @api.onchange('firstname')
    def set_title(self):
        for record in self:
            if record.firstname != False:
                record.firstname = record.firstname.title().encode('latin1')
        return

    @api.model
    def _names_order_default(self):
        return 'last_first'

    @api.model
    def _get_names_order(self):
        """Get names order configuration from system parameters.
        You can override this method to read configuration from language,
        country, company or other"""
        return self.env['ir.config_parameter'].get_param(
            'partner_names_order', self._names_order_default())

    @api.model
    def _get_computed_name(self, lastname, firstname):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        order = self._get_names_order()
        if order == 'last_first_comma':
            return u", ".join((p for p in (lastname, firstname) if p))
        elif order == 'first_last':
            return u" ".join((p for p in (firstname, lastname) if p))
        else:
            return u" ".join((p for p in (lastname, firstname) if p))

    @api.multi
    @api.depends("firstname", "lastname")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for record in self:
            record.name = record._get_computed_name(
                record.lastname, record.firstname,
            )

    @api.multi
    def _inverse_name(self):
        """Try to revert the effect of :meth:`._compute_name`."""
        for record in self:
            parts = record._get_inverse_name(record.name, record.is_company)
            record.lastname = parts['lastname']
            record.firstname = parts['firstname']

    # nom prenom

    # constraint pourcentage
    @api.constrains('pourcentage')
    @api.one
    def _check_number(self):
        pourcentage = self.pourcentage
        if pourcentage > 100:
            raise ValidationError(_('Pourcentage est compris entre 0 et 100'))

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('patient.record')
        vals['refp'] = sequence or '/'
        return super(PatientRecord, self).create(vals)

    # fonction qui valide l'email
    @api.constrains('patient_email')
    @api.onchange('patient_email')
    def validate_mail(self):
        if self.patient_email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                             self.patient_email)
            if match == None:
                raise ValidationError('Identifiant de courrier électronique non valide')

    # fonction qui valide le telephone
    @api.constrains('patient_telephone')
    def validate_phone(self):
        if self.patient_telephone:
            test_match = re.match('^[2|3|6]+([0-9]{8})$', self.patient_telephone)
            if test_match == None:
                raise ValidationError('Telephone 1  invalide')
                self.patient_telephone = None


    # fonction qui calcule l'age 2
    @api.multi
    @api.depends('patient_dob')
    def compute_age(self):
        '''Method to calculate student age'''
        current_dt = datetime.today()
        for rec in self:
            if rec.patient_dob:
                start = datetime.strptime(rec.patient_dob,
                                          DEFAULT_SERVER_DATE_FORMAT)
                age_calc = ((current_dt - start).days / 365)
                # Age should be greater than 0
                if age_calc > 0.0:
                    rec.age = age_calc

        # fonction qui calcule l'age à laquelle un patient doit etre en registré dans le système enregistré dans les systèmes

    # Fonction quio fait en sorte que l'age ne doit pas etre supérieur à 2
    @api.constrains('patient_dob')
    def check_age(self):
        '''Method to check age should be greater than 2'''
        current_dt = datetime.today()
        if self.patient_dob:
            start = datetime.strptime(self.patient_dob, DEFAULT_SERVER_DATE_FORMAT)
            age_calc = ((current_dt - start).days / 365)
            # Check if age less than 2 years
            if age_calc < 0:
                raise ValidationError(
                    _('''Date de naissance impossible à valider'''))
            elif age_calc < 2:
                raise ValidationError(_('''Age du patient doit être supérieur à 2 ans!'''))

    # @api.constrains('patient_dob')
    # def check_age(self):
    #     '''Method to check age should be greater than 5'''
    #     current_dt = datetime.today()
    #     if self.patient_dob:
    #         start = datetime.strptime(self.patient_dob,
    #                                   DEFAULT_SERVER_DATE_FORMAT)
    #         age_calc = ((current_dt - start).days / 365)
    #         # Check if age less than 5 years
    #         if age_calc <= 1:
    #             raise ValidationError(_('''L'âge du patient devrait être supérieur ou égal à 2 ans!'''))

    # # constraint
    # @api.constrains('number')
    # @api.one
    # def _check_number(self):
    #     number = self.number
    #     if number and len(str(abs(number))) > 4:
    #         raise ValidationError(_('Number of digits must on exceed 4'))

    # @api.onchange('visited', 'patient_name')
    # def add_check(self):
    #     if self.visited != 0:
    #         return {
    #             'warning': {
    #                 'title': "Message d'accueil",
    #                 'message': "Bienvenue au patient" + " " + self.patient_name.patient_name,
    #             },
    #         }

    """@api.multi
    def do_operation(self):
        for obj in self:
            obj.request = self.env['rdv.record'].search([('name', '=', obj.id)])"""


# classe qui envoie un message whatsapp qui calcule l'age
class PatientWhatsapp(models.Model):
    _inherit = 'res.partner'

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


class MedicalQuestionnaire(models.Model):
    _inherit = 'patient.record'

    ask01 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask02 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask03 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask04 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask04_1 = fields.Char()
    ask05 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask05_1 = fields.Char()
    ask06 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask07 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask07_1 = fields.Char()
    ask08 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask09 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask09_1 = fields.Char()
    ask10 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask11 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask12 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask13 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask14 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask14_1 = fields.Char()
    ask15 = fields.Selection([('O', 'oui'), ('N', 'non')])
    ask15_1 = fields.Char()
    ask15_2 = fields.Char()
    ask16 = fields.Selection([('O', 'oui'), ('N', 'non')])

    ord_ids = fields.One2many('ord.medical', 'name', readonly=True)
    traitment_ids = fields.One2many('devis.record', 'name', readonly=True)
    fact_ids = fields.One2many('account.invoice', 'test_devis', readonly=True)
