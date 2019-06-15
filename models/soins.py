# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Maintainer: Cybrosys Technologies (<https://www.cybrosys.com>)
#
##############################################################################

from odoo import models, fields, api


class Categorie(models.Model):
    _name = 'soins.record'
    _rec_name = 'nomsoin'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    nomsoin = fields.Char(string="Nom", required=True)
    codesoin = fields.Char(string="code", required=True)
    prixsoin = fields.Integer(string="Prix", required=True)
    Nomcat = fields.Many2one('soin.categorie', string='Catégorie')


