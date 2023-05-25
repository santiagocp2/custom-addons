# -*- coding: utf-8 -*-
# Copyright 2022-Today TechKhedut.
# Part of TechKhedut. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class InsuranceInformation(models.Model):
    """Insurance Information"""
    _name = 'insurance.information'
    _description = __doc__
    _rec_name = 'insurance_number'

    insurance_number = fields.Char(string='Insurance', required=True, readonly=True, default=lambda self: _('New'),
                                   copy=False)
    insured_id = fields.Many2one('res.partner', string='Insured', domain=[('is_customer', '=', True)], required=True)
    insurance_nominee_id = fields.Many2one('insurance.nominee', string="Nominee")
    your_nominee_is_your = fields.Selection(related='insurance_nominee_id.your_nominee_is_your',
                                            string="Your Nominee is Your")
    nominee_dob = fields.Date(related='insurance_nominee_id.nominee_dob')
    dob = fields.Date(string="Date Of Birth", required=True)
    age = fields.Char(string="Age", compute="get_insured_age_count")
    gender = fields.Selection([('male', "Male"), ('female', "Female"), ('others', "Others")], string="Gender",
                              required=True)
    issue_date = fields.Date(string="Issue Date", required=True)
    expiry_date = fields.Date(string="Expiry Date", readonly=True, compute="_compute_time_period_date")
    agent_id = fields.Many2one('res.partner', string='Agent', required=True, domain=[('is_agent', '=', True)])
    agent_phone = fields.Char(related='agent_id.phone', string="Phone")

    premium_type = fields.Selection([('fixed', "Fixed"), ('installment', "Installment")], default='fixed',
                                    string="Premium Type")
    insurance_category_id = fields.Many2one('insurance.category', string="Policy Category", required=True)
    category = fields.Selection(related="insurance_category_id.category")
    insurance_sub_category_id = fields.Many2one('insurance.sub.category', string="Sub Category",
                                                domain="[('insurance_category_id', '=', insurance_category_id)]",
                                                required=True)
    insurance_policy_id = fields.Many2one('insurance.policy', string='Insurance Policy',
                                          domain="[('insurance_sub_category_id', '=', insurance_sub_category_id)]",
                                          required=True)

    insurance_buying_for_id = fields.Many2one('insurance.buying.for', string="Buying For",
                                              domain="[('insurance_category_id', '=', insurance_category_id)]")
    insurance_time_period = fields.Char(related="insurance_policy_id.insurance_time_period_id.t_period")
    duration = fields.Integer(related="insurance_policy_id.insurance_time_period_id.duration",
                              string="Duration (Months)")
    policy_terms_and_conditions = fields.Text(string="Terms & Conditions")
    commission_type = fields.Selection([('fixed', "Fixed Commission"), ('monthly', "Monthly Commission")],
                                       string="Commission Type")
    commission = fields.Float(string='Commission (%)', required=True)
    policy_amount = fields.Monetary(string="Policy Amount")
    total_commission = fields.Monetary(string="Total Commission")
    total_policy_amount = fields.Monetary(string="Total Policy Amount")

    duration = fields.Integer(related="insurance_policy_id.duration", string="Duration (Months)")
    monthly_installment = fields.Monetary(string="Monthly Installment", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, string="Company")
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")

    invoice_id = fields.Many2one('account.move')
    payment_state = fields.Selection(related="invoice_id.payment_state", string="Invoice Status")

    insurance_emi_ids = fields.One2many('insurance.emi', 'insurance_information_id')
    state = fields.Selection([('draft', "Draft"), ('running', "Running"), ('expired', "Expired")], default='draft')
    instalment_complete = fields.Boolean()

    insured_document_id = fields.Many2one("insured.documents", string="Document")
    document_count = fields.Integer(compute='_compute_document_count')
    claim_count = fields.Integer(compute='_compute_claim_count')

    # Life Insurance:
    life_insured_age = fields.Selection(
        [('five_to_twenty', "Between 5 to 20 Years"), ('twenty_to_fifty', "Between 20 to 50 Years"),
         ('fifty_to_seventy', "Between 50 to 70 Years"), ('above_seventy', "Above 70 Years")], string="Insured Age")
    desired_death_amount = fields.Monetary(string="Death Amount")
    life_deductible_amount = fields.Monetary(string="Deductible Amount")
    is_smoking_status = fields.Selection([('yes', "Yes"), ('no', "No")], string="Smoking Status")
    length_of_coverage_term = fields.Text(string="Length of Coverage Terms")
    life_health_history = fields.Text(string="Insured Health History")
    occupation_and_hobbies = fields.Text(string="Occupation and Hobbies Insured")
    family_medical_history = fields.Text(string="Family Medical History")

    # Health Insurance:
    health_insured_age = fields.Selection(
        [('five_to_twenty', "Between 5 to 20 Years"), ('twenty_to_fifty', "Between 20 to 50 Years"),
         ('fifty_to_seventy', "Between 50 to 70 Years"), ('above_seventy', "Above 70 Years")], string="Insured Age")
    desired_coverage_type = fields.Selection([('individual', "Individual"), ('family', "Family"), ('group', "Group")],
                                             string="Coverage Type")
    health_deductible_amount = fields.Monetary(string="Deductible Amount")
    copay_amount = fields.Monetary(string="Co-pay Amount")
    out_of_pocket_maximum = fields.Text(string="Out-of-Pocket Maximum")
    health_history_of_insured = fields.Text(string="Health History")
    drug_coverage = fields.Text(string="Prescription Drug Coverage")
    healthcare_provider_network = fields.Text(string="Preferred Healthcare Provider Network")

    # Property Insurance:
    construct_year = fields.Char(string="Construct Year")
    street = fields.Char(string="Street", translate=True)
    street2 = fields.Char(string="Street 2", translate=True)
    city = fields.Char(string="City", translate=True)
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="Country")
    zip = fields.Char(string="Zip", size=6)
    property_value = fields.Monetary(string="Estimated Value")
    property_damage_coverage = fields.Monetary(string="Damage Coverage")
    property_deductible_amount = fields.Monetary(string="Deductible Amount")
    desired_coverage_types = fields.Selection(
        [('dwelling', "Dwelling"), ('personal_property', "Personal Property"), ('liability', "Liability"),
         ('additional_living_expenses', "Additional Living Expenses")], string="Coverage Type")
    property_coverage_limits = fields.Text(string="Property Coverage Limits")
    construction_type_and_materials = fields.Text(string="Construction Type and Materials")
    special_features_of_the_property = fields.Text(string="Special Features of the Property")
    personal_property_inventory = fields.Text(string="Personal Property Inventory")

    # Liability Insurance:
    type_of_liability_risk = fields.Selection(
        [('auto', "Auto"), ('homeowner', "HomeOwner's"), ('business', "Business")], string="Liability Risk")
    liability_coverage_type = fields.Selection(
        [('general_liability', "General Liability"), ('professional_liability', "Professional Liability")],
        string="Coverage Type")
    desired_coverage_limits = fields.Text(string="Desired Coverage Limits")
    business_type_and_operations = fields.Text(string="Business Type and Operations")

    # Disability Insurance:
    occupation = fields.Char(string="Occupation")
    income = fields.Monetary(string="Income")
    disability_desired_benefit_amount = fields.Monetary(string="Desired Amount")
    insured_is_smoking = fields.Boolean(string="Insured is Smoking")
    length_coverage_disability_period = fields.Text(string="Length of Coverage Period")
    disability_health_history = fields.Text(string="Health History")
    occupation_and_hobbies = fields.Text(string="Occupation and Hobbies")

    # Travel Insurance:
    types_of_coverage = fields.Selection(
        [('trip_cancellation', "Trip Cancellation"), ('medical_emergency', "Medical Emergency"),
         ('lost_luggage', "Lost Luggage")], string="Type of Coverage")
    trip_length = fields.Integer(string="Trip Length")
    trip_coverage_amount = fields.Monetary(string="Coverage Amount")
    odometer_unit = fields.Selection([('km', 'Kilometers'), ('mi', 'Miles')], 'Odometer Unit', default='km')
    traveler_health_history = fields.Text(string="Traveler Health History")

    # Pet Insurance:
    age_of_breed_of_the_pet = fields.Integer(string="Age of Breed")
    pet_desired_coverage_type = fields.Selection(
        [('accident', "Accident"), ('illness', "Illness"), ('comprehensive', "Comprehensive")], string="Coverage Type")
    exclusions = fields.Selection(
        [('pre_existing_conditions', "Pre-Existing Conditions"), ('certain_breeds', "Certain Breeds")],
        string="Exclusions")

    accident_coverage = fields.Monetary(string="Accident Amount")
    illness_coverage = fields.Monetary(string="Illness Amount")
    pet_deductible_amount = fields.Monetary(string="Deductible Amount")
    pet_coverage_limits = fields.Text(string="Coverage Limits")

    # Business Insurance:
    business_desired_coverage_type = fields.Selection(
        [('property_damage', "Property Damage"), ('liability', "Liability"), ('workers', "Workers Compensation")],
        string="Coverage Type")
    number_of_employees = fields.Integer(string="No. of Employees")
    business_property_value = fields.Monetary(string="Property Value")
    business_deductible_amount = fields.Monetary(string="Deductible Amount")
    business_type_operation = fields.Text(string="Business Type and Operations")
    business_coverage_limits = fields.Text(string="Business Coverage Limits")
    industry_specific_risks = fields.Text(string=" Industry-Specific Risks")

    # Vehicle Insurance:
    vehicle_name = fields.Char(string="Vehicle")
    model = fields.Char(string="Model")
    year = fields.Char(string="Year of MFG")
    vin_no = fields.Char(string="VIN No")
    reg_no = fields.Char(string="Registration No")
    place_of_reg = fields.Char(string="Place of Registration")
    cubic_capacity = fields.Integer(string="Cubic Capacity")
    setting_capacity = fields.Integer(string="Setting Capacity")
    usage_of_vehicle = fields.Selection([('personal', "Personal"), ('commercial', "Commercial")],
                                        string="Usage of Vehicle")
    coverage_type = fields.Selection(
        [('liability', "Liability"), ('collision', "Collision"), ('comprehensive', "Comprehensive")],
        string="Coverage Type")

    # Policy Details
    policy_certificate_no = fields.Char(string="Policy/Certificate No")
    previous_policy_no = fields.Char(string="Previous Policy No")

    # Vehicle IDV
    for_the_vehicle = fields.Monetary(string="For the Vehicle")
    for_trailer = fields.Monetary(string="For Trailer")
    non_electric_accessories = fields.Monetary(string="Non Electric Accessories")
    electric_accessories = fields.Monetary(string="Electric Accessories")
    value_of_cng_lpg_kit = fields.Monetary(string="Value of CNG/LPG Kit")
    total_idv = fields.Monetary(string="Total IDV Value")

    # Own Damage
    basic_od = fields.Monetary(string="Basic OD")
    od_package_premium = fields.Monetary(string="Package Premium")
    service_tax = fields.Monetary(string="Service Tax")
    special_discount = fields.Monetary(string="Special Discount (-)")
    final_premium = fields.Monetary(string="Final Premium")

    # Liability
    basic_tp_liability = fields.Monetary(string="Basic TP Liability")
    pa_cover_for_owner_driver = fields.Monetary(string="PA Cover for Owner-Driver")
    package_premium = fields.Monetary(string="Package Premium")
    liability_service_tax = fields.Monetary(string=" Service Tax")
    total_premium = fields.Monetary(string="Total Premium")

    limitation_as_to_use = fields.Text(string="Limitations as to Use")
    limits_of_liability = fields.Text(string="Limits of Liability")
    deductibles_under_section = fields.Text(string="Deductibles Under Section")
    special_conditions = fields.Text(string="Special Conditions")
    driving_history = fields.Text(string="Driving History of the Insured")
    vehicle_insurance_image_ids = fields.One2many('vehicle.insurance.image', 'insurance_information_id',
                                                  string="Images")

    @api.onchange('insurance_policy_id')
    def policy_terms_and_condition(self):
        for rec in self:
            if rec.insurance_policy_id:
                rec.policy_terms_and_conditions = rec.insurance_policy_id.policy_terms_and_conditions

    @api.onchange('insurance_category_id')
    def get_insurance_cetogary(self):
        for rec in self:
            if rec.insurance_category_id:
                # Life Insurance:
                rec.length_of_coverage_term = rec.insurance_category_id.length_of_coverage_term
                rec.life_health_history = rec.insurance_category_id.life_health_history
                rec.occupation_and_hobbies = rec.insurance_category_id.occupation_and_hobbies
                rec.family_medical_history = rec.insurance_category_id.family_medical_history
                # Health Insurance:
                rec.out_of_pocket_maximum = rec.insurance_category_id.out_of_pocket_maximum
                rec.health_history_of_insured = rec.insurance_category_id.health_history_of_insured
                rec.drug_coverage = rec.insurance_category_id.drug_coverage
                rec.healthcare_provider_network = rec.insurance_category_id.healthcare_provider_network
                # Property Insurance:
                rec.property_coverage_limits = rec.insurance_category_id.property_coverage_limits
                rec.construction_type_and_materials = rec.insurance_category_id.construction_type_and_materials
                rec.special_features_of_the_property = rec.insurance_category_id.special_features_of_the_property
                rec.personal_property_inventory = rec.insurance_category_id.personal_property_inventory
                # Liability Insurance:
                rec.desired_coverage_limits = rec.insurance_category_id.desired_coverage_limits
                rec.business_type_and_operations = rec.insurance_category_id.business_type_and_operations
                # Disability Insurance:
                rec.length_coverage_disability_period = rec.insurance_category_id.length_coverage_disability_period
                rec.disability_health_history = rec.insurance_category_id.disability_health_history
                rec.occupation_and_hobbies = rec.insurance_category_id.occupation_and_hobbies
                # Travel Insurance:
                rec.traveler_health_history = rec.insurance_category_id.traveler_health_history
                # Pet Insurance:
                rec.pet_coverage_limits = rec.insurance_category_id.pet_coverage_limits
                # Business Insurance:
                rec.business_type_operation = rec.insurance_category_id.business_type_operation
                rec.business_coverage_limits = rec.insurance_category_id.business_coverage_limits
                rec.industry_specific_risks = rec.insurance_category_id.industry_specific_risks
                # Vehicle Insurance:
                rec.driving_history = rec.insurance_category_id.driving_history
                rec.limitation_as_to_use = rec.insurance_category_id.limitation_as_to_use
                rec.limits_of_liability = rec.insurance_category_id.limits_of_liability
                rec.deductibles_under_section = rec.insurance_category_id.deductibles_under_section
                rec.special_conditions = rec.insurance_category_id.special_conditions

    @api.onchange('for_the_vehicle', 'for_trailer', 'non_electric_accessories', 'electric_accessories',
                  'value_of_cng_lpg_kit')
    def _vehicle_idv_value(self):
        for rec in self:
            rec.total_idv = rec.for_the_vehicle + rec.for_trailer + rec.non_electric_accessories + rec.electric_accessories + rec.value_of_cng_lpg_kit

    @api.onchange('basic_od', 'od_package_premium', 'service_tax', 'special_discount')
    def _own_damage_value(self):
        for record in self:
            record.final_premium = record.basic_od + record.od_package_premium + record.service_tax - record.special_discount

    @api.onchange('basic_tp_liability', 'pa_cover_for_owner_driver', 'package_premium', 'liability_service_tax')
    def _liability_value(self):
        for value in self:
            value.total_premium = value.basic_tp_liability + value.pa_cover_for_owner_driver + value.package_premium + value.liability_service_tax

    @api.depends('dob')
    def get_insured_age_count(self):
        today = fields.Date.today()
        for rec in self:
            if rec.dob:
                age = today.year - rec.dob.year - ((today.month, today.day) < (rec.dob.month, rec.dob.day))
                if not age < 0:
                    rec.age = str(age) + ' Years'
                else:
                    rec.age = str(0) + ' Years'
            else:
                rec.age = str(0) + ' Years'

    def draft_to_running(self):
        self.state = 'running'

    def running_to_expired(self):
        self.state = 'expired'

    @api.model
    def create(self, vals):
        if vals.get('insurance_number', 'New') == 'New':
            vals['insurance_number'] = self.env['ir.sequence'].next_by_code(
                'insurance.information') or 'New'
        return super(InsuranceInformation, self).create(vals)

    def _compute_document_count(self):
        for rec in self:
            document_count = self.env['insured.documents'].search_count([('insured_info_id', '=', rec.id)])
            rec.document_count = document_count
        return True

    def action_insured_document(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Documents',
            'res_model': 'insured.documents',
            'domain': [('insured_info_id', '=', self.id)],
            'context': {'default_insured_info_id': self.id},
            'view_mode': 'tree',
            'target': 'current',
        }

    def _compute_claim_count(self):
        for rec in self:
            claim_count = self.env['claim.information'].search_count([('insurance_id', '=', rec.id)])
            rec.claim_count = claim_count
        return True

    def action_insured_claim(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Claims',
            'res_model': 'claim.information',
            'domain': [('insurance_id', '=', self.id)],
            'context': {'default_insurance_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current',
        }

    @api.depends('issue_date', 'expiry_date')
    def _compute_time_period_date(self):
        for rec in self:
            expiry_date = fields.date.today()
            if rec.issue_date:
                expiry_date = rec.issue_date + relativedelta(months=rec.duration)
                rec.expiry_date = expiry_date
            else:
                rec.expiry_date = expiry_date

    @api.onchange('insurance_policy_id')
    def get_insurance_policy_amount(self):
        for rec in self:
            if rec.insurance_policy_id:
                rec.policy_amount = rec.insurance_policy_id.policy_amount

    @api.constrains('commission')
    def _check_agent_commission(self):
        for record in self:
            if record.commission == 0:
                raise ValidationError("Please Agent Commisiion can not be zero")

    @api.onchange('commission', 'policy_amount')
    def _total_commission(self):
        for rec in self:
            rec.total_commission = (rec.commission * rec.policy_amount) / 100

    @api.onchange('total_commission', 'policy_amount')
    def _total_amount(self):
        for rec in self:
            rec.total_policy_amount = rec.total_commission + rec.policy_amount

    @api.onchange('total_policy_amount', 'duration')
    def _total_monthly_installment_amount(self):
        for rec in self:
            if rec.duration > 0:
                rec.monthly_installment = rec.total_policy_amount / rec.duration

    # Seduler
    def action_create_emi_installment(self):
        self.instalment_complete = True
        date = fields.date.today()
        for rec in self:
            if rec.issue_date:
                for i in range(rec.insurance_policy_id.duration):
                    date = rec.issue_date + relativedelta(months=i)
                    data = {
                        'insurance_information_id': self.id,
                        'name': 'Installment ' + str(i + 1),
                        'installment_date': date,
                        'installment_amount': self.monthly_installment
                    }
                    self.env['insurance.emi'].create(data)
                self.state = 'running'

    def action_insurance_invoice(self):
        self.instalment_complete = True
        insurance_invoice = {
            'product_id': self.env.ref('tk_insurance_management.insurance_invoice').id,
            'name': self.insurance_policy_id.policy_name,
            'quantity': 1,
            'price_unit': self.total_policy_amount,
        }
        invoice_lines = [(0, 0, insurance_invoice)]
        data = {
            'partner_id': self.insured_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines
        }

        invoice_id = self.env['account.move'].sudo().create(data)
        invoice_id.action_post()
        self.invoice_id = invoice_id.id
        self.state = 'running'


class InsuranceEMI(models.Model):
    """Insurance EMI"""
    _name = 'insurance.emi'
    _description = __doc__
    _rec_name = 'name'

    name = fields.Char(string="Name", required=True)
    installment_date = fields.Date(string="Installment Date")
    installment_amount = fields.Monetary(string="Installment Amount")
    premium_type = fields.Selection(related="insurance_information_id.premium_type", string="Premium Type")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', related="company_id.currency_id")
    insurance_information_id = fields.Many2one('insurance.information')
    invoice_id = fields.Many2one('account.move')
    payment_state = fields.Selection(related="invoice_id.payment_state", string="Invoice Status")

    def action_insurance_invoice(self):
        insurance_invoice = {
            'product_id': self.env.ref('tk_insurance_management.insurance_invoice').id,
            'name': self.name,
            'quantity': 1,
            'price_unit': self.installment_amount,
        }
        invoice_lines = [(0, 0, insurance_invoice)]
        data = {
            'partner_id': self.insurance_information_id.insured_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines
        }

        invoice_id = self.env['account.move'].sudo().create(data)
        invoice_id.action_post()
        self.invoice_id = invoice_id.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice_id.id,
            'view_mode': 'form',
            'target': 'current'
        }
