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


class AssuranceRecord(models.Model):
    _name = 'assurance.record'


class ResPartnerPatient(models.Model):
    _inherit = 'res.partner'

    is_pat = fields.Boolean(string='Patient')
    is_assureur = fields.Boolean(string='Assureur', readonly=1)
    code = fields.Char(string="Code")







