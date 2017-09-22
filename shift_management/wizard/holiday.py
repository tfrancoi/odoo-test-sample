# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Subscribe(models.TransientModel):
    _name = 'shift.holiday'
    _inherit = 'shift.action_mixin'

    holiday_start_day = fields.Date(string="Start date for the holiday", default=fields.Date.today)
    holiday_end_day = fields.Date(string="End date for the holiday (included)")

    @api.multi
    def holidays(self):
        self = self._check() #maybe a different group
        status_id = self.env['cooperative.status'].search([('cooperator_id', '=', self.cooperator_id.id)])
        status_id.sudo().write({'holiday_start_time': self.holiday_start_day, 'holiday_end_time': self.holiday_end_day})
