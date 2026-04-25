-- =============================================================================
--  Centific Pricing Intelligence â€” Seed Data (DML)
--  Target:  PostgreSQL 14+
--  Seeds the curated Centific Pricing Intelligence dashboard data.
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
--  clients
-- -----------------------------------------------------------------------------
INSERT INTO clients (name) VALUES
  ('City of Tucker, GA'),
  ('Bexar County CHCS'),
  ('Illinois Dept of IT'),
  ('UN System Staff College'),
  ('New Castle County, DE'),
  ('Pfizer Inc.'),
  ('Kansas Dept of Transportation'),
  ('Bank of America'),
  ('UK National Health Service'),
  ('Tokyo Metro Transit'),
  ('Walmart Inc.'),
  ('Siemens Healthineers'),
  ('Aetna Healthcare'),
  ('Deutsche Bank AG'),
  ('Delta Air Lines'),
  ('UNICEF Regional Office'),
  ('Govt. of Telangana'),
  ('Samsung Electronics'),
  ('Microsoft Corp.');

-- -----------------------------------------------------------------------------
--  rfps
-- -----------------------------------------------------------------------------
INSERT INTO rfps
  (rfp_code, name, short_label, client_id, category, description,
   tcv_base, pricing_model, scenario_used, renewal_date, submitted_date,
   duration, locale, win_probability, risk_level, hil_stage,
   status, pipeline_stage, current_hil_level,
   scenario_assumptions, benchmark_scope, benchmark_note,
   tcv_display, active_in_pipeline, active_pipeline_rank, is_current)
VALUES
  ('RFP 2025-007', 'Tucker GA Call Center Services', 'Call Center',
    (SELECT id FROM clients WHERE name = 'City of Tucker, GA'),
    'Call Center', 'Inbound call center for citizen services',
    1684620, 'Annual Retainer', 'Base', '2027-04-15', '2025-03-12',
    '2 years', 'en-US', 72, 'Low', 'L2',
    'Active', 'Pricing', 2,
    NULL, NULL, NULL,
    'â‚¹16,84,620', TRUE, 1, FALSE),

  ('RFP-2024-017', 'Bexar County Interpretation', 'Interpretation',
    (SELECT id FROM clients WHERE name = 'Bexar County CHCS'),
    'Interpretation', 'Medical interpretation services for 11 locales',
    2850000, 'Per Min + Per Hr', 'Conservative', '2026-11-30', '2024-09-05',
    '2 years', 'en-US, es-MX', 85, 'Medium', 'L4',
    'Priced', 'HIL Review', 4,
    NULL, NULL, NULL,
    'â‚¹28,50,000', TRUE, 2, FALSE),

  ('SAPSI20251', 'Illinois DoT SAP Migration', 'SAP Migration',
    (SELECT id FROM clients WHERE name = 'Illinois Dept of IT'),
    'IT Services', 'Full SAP S/4HANA migration and support',
    45000000, 'Hybrid Fixed+T&M', 'Base', '2028-06-01', '2024-11-18',
    '3 years', 'en-US', 94, 'High', 'L5',
    'Awarded', 'Approved', 5,
    NULL, NULL, NULL,
    'â‚¹4,50,00,000', TRUE, 3, FALSE),

  ('RFP 8/2021', 'UN System Translation', 'Translation',
    (SELECT id FROM clients WHERE name = 'UN System Staff College'),
    'Translation', 'Multilingual training material translation',
    920000, 'Per 1,000 Words', 'Base', 'â€”', '2025-02-20',
    '1 year', 'en-US, fr-FR', 68, 'Low', 'L1',
    'Active', 'Extracting', 1,
    NULL, NULL, NULL,
    'â‚¹9,20,000', TRUE, 4, FALSE),

  ('25PPA-003', 'New Castle County TPA Claims', 'TPA Claims',
    (SELECT id FROM clients WHERE name = 'New Castle County, DE'),
    'BPO', 'Third-party admin claims processing',
    380000, 'Per Claim', 'Base', '2026-01-15', '2025-04-08',
    '3 years', 'en-US', 61, 'Medium', 'L1',
    'Active', 'Ingesting', 1,
    'Base: 3,200 claims/yr Â· Buy Rate â‚¹95/claim Â· Overhead 15% Â· Margin 20%',
    'Call center / OPI â€” Similar scope, last 12 months',
    'ðŸ’¡ Your base rate is 11.6% above market avg â€” consider conservative scenario for competitive bids',
    'â‚¹3,80,000', TRUE, 5, TRUE),

  ('RFP-2024-009', 'Pfizer Clinical Translation', NULL,
    (SELECT id FROM clients WHERE name = 'Pfizer Inc.'),
    'Translation', 'Clinical trial document translation Â· regulated',
    4200000, 'Per Word', 'Aggressive', '2026-08-30', '2024-06-12',
    '2 years', 'en-US, ja-JP', 88, 'Medium', 'L4',
    'Won', NULL, 4, NULL, NULL, NULL, 'â‚¹42,00,000', FALSE, NULL, FALSE),

  ('RFP-2023-101', 'Kansas DOT IT Services', NULL,
    (SELECT id FROM clients WHERE name = 'Kansas Dept of Transportation'),
    'IT Services', 'Roadside IoT and traffic management platform',
    18000000, 'Hybrid', 'Base', '2027-10-01', '2023-08-14',
    '5 years', 'en-US', 79, 'Medium', 'L5',
    'Won', NULL, 5, NULL, NULL, NULL, 'â‚¹1,80,00,000', FALSE, NULL, FALSE),

  ('RFP-2024-088', 'Bank of America BPO', NULL,
    (SELECT id FROM clients WHERE name = 'Bank of America'),
    'BPO', 'Credit card processing back-office support',
    7500000, 'PMPM', 'Aggressive', 'â€”', '2024-10-22',
    '3 years', 'en-US', 42, 'High', 'L5',
    'Lost', NULL, 5, NULL, NULL, NULL, 'â‚¹75,00,000', FALSE, NULL, FALSE),

  ('RFP-2025-003', 'UK NHS Translation', NULL,
    (SELECT id FROM clients WHERE name = 'UK National Health Service'),
    'Translation', 'Patient-facing document translation for 24 locales',
    5200000, 'Per Word', 'Base', '2027-03-15', '2025-01-10',
    '2 years', 'en-GB, hi-IN', 81, 'Low', 'L4',
    'Awarded', NULL, 4, NULL, NULL, NULL, 'â‚¹52,00,000', FALSE, NULL, FALSE),

  ('RFP-2025-004', 'Tokyo Metro Translation', NULL,
    (SELECT id FROM clients WHERE name = 'Tokyo Metro Transit'),
    'Translation', 'Signage and announcement translation',
    1800000, 'Fixed Fee', 'Conservative', 'â€”', '2024-07-08',
    '1 year', 'ja-JP, en-US', 55, 'Low', 'L3',
    'Archived', NULL, 3, NULL, NULL, NULL, 'â‚¹18,00,000', FALSE, NULL, FALSE),

  ('RFP-2024-045', 'Walmart Call Center', NULL,
    (SELECT id FROM clients WHERE name = 'Walmart Inc.'),
    'Call Center', '24x7 omnichannel customer support',
    9500000, 'Per Hour', 'Base', '2026-12-01', '2024-05-30',
    '3 years', 'en-US, es-MX', 70, 'Medium', 'L3',
    'Priced', NULL, 3, NULL, NULL, NULL, 'â‚¹95,00,000', FALSE, NULL, FALSE),

  ('RFP-2024-120', 'Siemens IT Managed Services', NULL,
    (SELECT id FROM clients WHERE name = 'Siemens Healthineers'),
    'IT Services', 'Global IT helpdesk and infrastructure ops',
    22000000, 'Hybrid', 'Base', '2028-02-28', '2024-12-05',
    '4 years', 'en-US, de-DE', 83, 'Medium', 'L5',
    'Won', NULL, 5, NULL, NULL, NULL, 'â‚¹2,20,00,000', FALSE, NULL, FALSE),

  ('RFP-2025-012', 'Aetna Claims Processing', NULL,
    (SELECT id FROM clients WHERE name = 'Aetna Healthcare'),
    'BPO', 'Medical claims adjudication and processing',
    6800000, 'Per Claim', 'Conservative', '2027-09-20', '2025-03-28',
    '3 years', 'en-US', 64, 'High', 'L2',
    'Active', NULL, 2, NULL, NULL, NULL, 'â‚¹68,00,000', FALSE, NULL, FALSE),

  ('RFP-2024-066', 'Deutsche Bank Translation', NULL,
    (SELECT id FROM clients WHERE name = 'Deutsche Bank AG'),
    'Translation', 'Financial document localization',
    2100000, 'Per Word', 'Aggressive', 'â€”', '2024-08-18',
    '2 years', 'de-DE, en-GB', 38, 'Medium', 'L3',
    'Lost', NULL, 3, NULL, NULL, NULL, 'â‚¹21,00,000', FALSE, NULL, FALSE),

  ('RFP-2025-008', 'Delta Airlines Helpdesk', NULL,
    (SELECT id FROM clients WHERE name = 'Delta Air Lines'),
    'Call Center', 'Loyalty program and reservations support',
    3400000, 'Per Hour', 'Base', '2026-07-12', '2025-03-01',
    '2 years', 'en-US', 75, 'Low', 'L2',
    'Active', NULL, 2, NULL, NULL, NULL, 'â‚¹34,00,000', FALSE, NULL, FALSE),

  ('RFP-2023-078', 'UNICEF Interpretation', NULL,
    (SELECT id FROM clients WHERE name = 'UNICEF Regional Office'),
    'Interpretation', 'Field interpretation during humanitarian ops',
    650000, 'Per Hour', 'Conservative', 'â€”', '2023-11-22',
    '1 year', 'en-US, ar-EG', 72, 'Medium', 'L3',
    'Archived', NULL, 3, NULL, NULL, NULL, 'â‚¹6,50,000', FALSE, NULL, FALSE),

  ('RFP-2025-015', 'Government of Telangana IT', NULL,
    (SELECT id FROM clients WHERE name = 'Govt. of Telangana'),
    'IT Services', 'Citizen services portal and digital e-governance',
    12000000, 'Hybrid', 'Base', '2028-03-31', '2025-02-14',
    '3 years', 'en-IN, hi-IN, te-IN', 77, 'Medium', 'L4',
    'Priced', NULL, 4, NULL, NULL, NULL, 'â‚¹1,20,00,000', FALSE, NULL, FALSE),

  ('RFP-2024-099', 'Samsung Call Center BPO', NULL,
    (SELECT id FROM clients WHERE name = 'Samsung Electronics'),
    'BPO', 'Consumer electronics product support',
    8900000, 'PMPM', 'Aggressive', '2027-05-15', '2024-09-28',
    '3 years', 'en-US, ko-KR', 86, 'Low', 'L5',
    'Won', NULL, 5, NULL, NULL, NULL, 'â‚¹89,00,000', FALSE, NULL, FALSE),

  ('RFP-2025-020', 'Microsoft Azure Translation', NULL,
    (SELECT id FROM clients WHERE name = 'Microsoft Corp.'),
    'Translation', 'Cloud documentation localization (60 languages)',
    15000000, 'Per Word', 'Base', '2027-08-01', '2025-04-02',
    '3 years', 'en-US, + 59', 69, 'High', 'L3',
    'Active', NULL, 3, NULL, NULL, NULL, 'â‚¹1,50,00,000', FALSE, NULL, FALSE);

-- -----------------------------------------------------------------------------
--  hil_checkpoints (master)
-- -----------------------------------------------------------------------------
INSERT INTO hil_checkpoints (level, title, description, owner_role) VALUES
  (1, 'Data Extraction Validation',
      'Validate RFP inputs, fix missing fields, confirm locale codes',
      'ðŸ‘¤ Pricing Analyst'),
  (2, 'Pricing Computation Review',
      'Review margin, overhead settings and scenario assumptions',
      'ðŸ‘¤ Analyst / Manager'),
  (3, 'Benchmarking Validation',
      'Validate market positioning vs historical comparables',
      'ðŸ‘¤ Analyst / Manager'),
  (4, 'Final Pricing Approval',
      'Manager approves before template population & client delivery',
      'ðŸ‘¤ Pricing Manager'),
  (5, 'High-Risk / High-Value Review',
      'Leadership approval for risk score > threshold or deal > â‚¹1Cr',
      'ðŸ‘¤ Leadership');

-- -----------------------------------------------------------------------------
--  rfp_hil_progress (for 25PPA-003 â€” the "current" RFP on the dashboard)
-- -----------------------------------------------------------------------------
INSERT INTO rfp_hil_progress (rfp_id, level, status) VALUES
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 1, 'done'),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 2, 'pending'),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 3, 'waiting'),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 4, 'waiting'),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 5, 'waiting');

-- -----------------------------------------------------------------------------
--  pricing_scenarios (for 25PPA-003)
-- -----------------------------------------------------------------------------
INSERT INTO pricing_scenarios
  (rfp_id, scenario_type, annual_value_display, period_sub,
   volume_display, volume_factor, margin_pct, sell_rate_display, is_recommended)
VALUES
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'Conservative',
   'â‚¹3.42L', 'Annual Â· Year 1', '2,880 claims', 'Ã—0.90', '22%', 'â‚¹130.90', FALSE),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'Base',
   'â‚¹3.80L', 'Annual Â· Year 1', '3,200 claims', 'Ã—1.00', '20%', 'â‚¹128.25', TRUE),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'Aggressive',
   'â‚¹4.30L', 'Annual Â· Year 1', '3,840 claims', 'Ã—1.20', '18%', 'â‚¹125.66', FALSE);

-- -----------------------------------------------------------------------------
--  benchmarks (for 25PPA-003)
-- -----------------------------------------------------------------------------
INSERT INTO benchmarks (rfp_id, label, rate_display, bar_width_pct, color_css, sort_order) VALUES
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'Your Base',     'â‚¹27.00', 78, 'var(--gradient-banner)', 1),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'LA City Award', 'â‚¹23.50', 68, 'var(--success)',         2),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'Market High',   'â‚¹33.00', 95, '#F87171',                3),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'Market Low',    'â‚¹16.50', 48, '#94A3B8',                4),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'Market Avg',    'â‚¹24.20', 70, '#A855F7',                5);

-- -----------------------------------------------------------------------------
--  contract_risks (for 25PPA-003)
-- -----------------------------------------------------------------------------
INSERT INTO contract_risks (rfp_id, severity, description, sort_order) VALUES
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'low',
    '3-year annual renewal with 90-day exit clause â€” standard structure', 1),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'med',
    'No volume tolerance band defined â€” actual calls may exceed Â±30%',    2),
  ((SELECT id FROM rfps WHERE rfp_code = '25PPA-003'), 'low',
    'Optional webchat add-on carries no SLA penalty exposure',            3);

-- -----------------------------------------------------------------------------
--  approvals
-- -----------------------------------------------------------------------------
INSERT INTO approvals (rfp_id, level, title, meta, status) VALUES
  ((SELECT id FROM rfps WHERE rfp_code = 'RFP 2025-007'), 2,
    'Tucker GA Â· Pricing Computation Review',
    'Review margin (20%) and overhead (15%) settings Â· â‚¹16.85L Base TCV',
    'pending'),
  ((SELECT id FROM rfps WHERE rfp_code = 'RFP-2024-017'), 4,
    'Bexar County Â· Final Approval',
    'Manager sign-off before client delivery Â· â‚¹28.5L TCV',
    'pending'),
  ((SELECT id FROM rfps WHERE rfp_code = 'SAPSI20251'), 5,
    'Illinois SAP Â· Leadership Escalation',
    'High-value deal > â‚¹4Cr requires leadership approval',
    'pending');

-- -----------------------------------------------------------------------------
--  pricing_settings
-- -----------------------------------------------------------------------------
INSERT INTO pricing_settings (key, value, label, description, kind, sort_order) VALUES
  ('overhead',           '15%',             'Default Overhead %',
    'Applied to Buy Rate before margin calculation',                    'input',      1),
  ('margin',             '20%',             'Default Margin %',
    'Standard margin on top of cost',                                   'input',      2),
  ('conservativeVol',    '0.90',            'Conservative Volume Factor',
    'Multiplier for conservative scenario volume',                      'input',      3),
  ('aggressiveVol',      '1.20',            'Aggressive Volume Factor',
    'Multiplier for aggressive scenario volume',                        'input',      4),
  ('riskBuffer',         'true',            'Auto-flag Risk Buffer',
    'Add 10-15% buffer when no historical comparables',                 'toggle',     5),
  ('blockOnMissingBuy',  'true',            'Block on Missing Buy Rate >30%',
    'Halt workflow if buy rate is missing for >30% of scope',           'toggle',     6),
  ('l5Threshold',        'â‚¹1,00,00,000',    'HIL L5 Escalation Threshold (â‚¹)',
    'Auto-escalate deals above this value to leadership',               'input_wide', 7);

-- -----------------------------------------------------------------------------
--  win_rate_points
-- -----------------------------------------------------------------------------
INSERT INTO win_rate_points (range_type, period_label, win_rate_pct, seq) VALUES
  ('week', 'W1', 61, 1), ('week', 'W2', 64, 2), ('week', 'W3', 60, 3),
  ('week', 'W4', 67, 4), ('week', 'W5', 65, 5), ('week', 'W6', 70, 6),
  ('week', 'W7', 72, 7),

  ('month', 'Nov', 55, 1), ('month', 'Dec', 59, 2), ('month', 'Jan', 62, 3),
  ('month', 'Feb', 64, 4), ('month', 'Mar', 67, 5), ('month', 'Apr', 68, 6),

  ('quarter', 'Q1', 52, 1), ('quarter', 'Q2', 58, 2),
  ('quarter', 'Q3', 65, 3), ('quarter', 'Q4', 68, 4);

-- -----------------------------------------------------------------------------
--  win_rate_insights
-- -----------------------------------------------------------------------------
INSERT INTO win_rate_insights (range_type, slot, label, value, color_css, header_label, sub_label) VALUES
  ('week',    1, 'Best Week',     'W7 Â· 72%', 'var(--pink)',    'Last 7 Weeks',     'Pricing win-rate â€” weekly breakdown'),
  ('week',    2, 'Growth WoW',    '+2 pts',   'var(--success)', 'Last 7 Weeks',     'Pricing win-rate â€” weekly breakdown'),
  ('week',    3, 'Forecast W8',   '~74%',     NULL,             'Last 7 Weeks',     'Pricing win-rate â€” weekly breakdown'),

  ('month',   1, 'Best Month',    'Apr Â· 68%','var(--pink)',    'Last 6 Months',    'Pricing win-rate â€” monthly trend'),
  ('month',   2, 'Growth MoM',    '+1 pt',    'var(--success)', 'Last 6 Months',    'Pricing win-rate â€” monthly trend'),
  ('month',   3, 'Forecast May',  '~70%',     NULL,             'Last 6 Months',    'Pricing win-rate â€” monthly trend'),

  ('quarter', 1, 'Best Quarter',  'Q4 Â· 68%', 'var(--pink)',    'Last 4 Quarters',  'Pricing win-rate trajectory â€” last 4 quarters'),
  ('quarter', 2, 'Growth YoY',    '+16 pts',  'var(--success)', 'Last 4 Quarters',  'Pricing win-rate trajectory â€” last 4 quarters'),
  ('quarter', 3, 'Forecast Q1',   '~72%',     NULL,             'Last 4 Quarters',  'Pricing win-rate trajectory â€” last 4 quarters');

-- -----------------------------------------------------------------------------
--  activity_snapshot
-- -----------------------------------------------------------------------------
INSERT INTO activity_snapshot (variant, icon, value, label, trend_dir, trend_text, sort_order) VALUES
  ('upload',    'ðŸ“¥', '3',   'RFPs Uploaded',   'up',   'â†‘ 2 vs yesterday', 1),
  ('tools',     'âš¡', '42',  'Tool Executions', 'up',   'â†‘ 18% vs avg',     2),
  ('approvals', 'âœ…', '5',   'HIL Approvals',   'flat', 'â€” 1 pending',      3),
  ('time',      'â±ï¸', '2.3h','Avg Turnaround',  'up',   'â†“ 0.4h faster',    4);

-- -----------------------------------------------------------------------------
--  top_deal_today
-- -----------------------------------------------------------------------------
INSERT INTO top_deal_today (id, summary) VALUES
  (1, 'Bexar County Â· â‚¹28.5L priced in 1.8h');

-- -----------------------------------------------------------------------------
--  accuracy_buckets
-- -----------------------------------------------------------------------------
INSERT INTO accuracy_buckets (bucket_label, deal_count, in_sweet_spot, seq) VALUES
  ('-10%',   1, FALSE, 1),
  ('-7.5%',  3, FALSE, 2),
  ('-5%',    7, TRUE,  3),
  ('-2.5%', 12, TRUE,  4),
  ('0%',    14, TRUE,  5),
  ('+2.5%', 11, TRUE,  6),
  ('+5%',    5, FALSE, 7),
  ('+7.5%',  2, FALSE, 8),
  ('+10%',   0, FALSE, 9);

COMMIT;
