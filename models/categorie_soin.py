# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Maintainer: Cybrosys Technologies (<https://www.cybrosys.com>)
#
##############################################################################

from odoo import models, fields


class Categorie(models.Model):
    _name = 'soin.categorie'
    _rec_name = 'Nomcat'

    Nomcat = fields.Char(string="Nom", required=True)
    code = fields.Char(string="Code", required=True)
