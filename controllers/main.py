# -*- coding: utf-8 -*-
from odoo import http

class FourSureERPBase(http.Controller):

    @http.route('/', auth='public', website=True)
    def index(self, **kwargs):
        """Redirect root to login"""
        return http.request.render('4sureERP_base.login_template')

    @http.route('/dashboard', auth='public', website=True)
    def dashboard(self, **kwargs):
        """Owner Dashboard"""
        return http.request.render('4sureERP_base.dashboard_template')

