from odoo import api, fields, models, _


class medicamentRecord(models.Model):
    _name = 'medicament.record'
    _rec_name = 'nom_medicament'

    ref = fields.Char(string='Reference', size=16, readonly=True, required=True, help="ID Medicament",
                      default=lambda *a: '#')

    nom_medicament = fields.Char(string='Nom medicament', required=True)
    prise_medicament = fields.Text(string='Prise par defaut')
    gramme = fields.Char(string='Grammage')


    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('medicament.record')
        vals['ref'] = sequence or '/'
        return super(medicamentRecord, self).create(vals)



