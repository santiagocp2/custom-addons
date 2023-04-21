# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InsuranceDetails(models.Model):
    _name = 'insurance.details'

    name = fields.Char(
        string='Name', required=True, copy=False, readonly=True, index=True,
        default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer',
                                 required=True)
    start_date = fields.Date(
        string='Date Started', default=fields.Date.context_today, required=True)
    close_date = fields.Date(string='Date Closed', readonly=True)
    invoice_ids = fields.One2many('account.move', 'insurance_id',
                                  string='Invoices', readonly=True)
    employee_id = fields.Many2one(
        'employee.details', string='Agent', required=True)
    commission_rate = fields.Float(string='Commission Percentage')
    policy_id = fields.Many2one(
        'policy.details', string='Policy', required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    amount = fields.Monetary(related='policy_id.amount', string='Amount')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('closed', 'Closed')],
        required=True, default='draft')
    hide_inv_button = fields.Boolean(copy=False)
    note_field = fields.Html(string='Comment')
    contribute = fields.Boolean(string='Contributiva', default=False)

    def action_confirm_insurance(self):
        if self.amount > 0:
            self.state = 'confirmed'
            self.hide_inv_button = True
        else:
            raise UserError(_("Amount should be greater than zero"))

    def action_create_invoice(self):
        created_invoice = self.env['account.move'].sudo().create({
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.context_today(self),
            'partner_id': self.partner_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'name': 'Invoice For Insurance',
                'quantity': 1,
                'price_unit': self.amount,
                'account_id': 549,
            })],
        })
        self.invoice_ids = created_invoice
        if self.policy_id.payment_type == 'fixed':
            self.hide_inv_button = False

    def action_close_insurance(self):
        for records in self.invoice_ids:
            if records.state == 'paid':
                raise UserError(_("All invoices must be paid"))
        self.state = 'closed'
        self.close_date = fields.Date.context_today(self)
        self.hide_inv_button = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'insurance.details') or 'New'
        return super(InsuranceDetails, self).create(vals)
