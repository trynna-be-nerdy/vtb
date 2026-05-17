-- Board of Supervisors meeting
INSERT INTO meetings (title, board_slug, meeting_date, source_url, meeting_overview, top_decisions, fiscal_total, total_items, fiscal_items, processing_status)
VALUES (
  'Board of Supervisors Regular Meeting - May 2026',
  'board-of-supervisors',
  '2026-05-07',
  'https://loudoun.gov/meetings',
  'The Board approved the FY2027 budget with a 4-cent tax rate reduction, authorized a $42M school construction bond, and adopted new zoning guidelines for Ashburn mixed-use development.',
  ARRAY['FY2027 budget adopted with 4-cent tax rate reduction', 'Approved $42M bond for LCPS school construction', 'Rezoned 18 acres in Ashburn for mixed-use development'],
  '$42,000,000',
  12, 4, 'completed'
);

-- Planning Commission meeting
INSERT INTO meetings (title, board_slug, meeting_date, source_url, meeting_overview, top_decisions, total_items, fiscal_items, processing_status)
VALUES (
  'Planning Commission Regular Meeting - May 2026',
  'planning-commission',
  '2026-05-14',
  'https://loudoun.gov/meetings',
  'The Commission reviewed three rezoning applications and approved modifications to the Loudoun Station Transit-Oriented Development plan.',
  ARRAY['Approved Loudoun Station TOD plan modifications', 'Approved rezoning for 240-unit residential development in Leesburg', 'Deferred decision on industrial park expansion pending traffic study'],
  8, 1, 'completed'
);

-- LCPS meeting
INSERT INTO meetings (title, board_slug, meeting_date, source_url, meeting_overview, top_decisions, fiscal_total, total_items, fiscal_items, processing_status)
VALUES (
  'LCPS School Board Business Meeting - May 2026',
  'lcps-school-board',
  '2026-05-13',
  'https://lcps.org/boarddocs',
  'The School Board approved the FY2027 operating budget of $1.87B, adopted a revised student discipline policy, and approved staffing plans for the new Moorefield Station Elementary School.',
  ARRAY['Adopted $1.87B FY2027 operating budget (3.2% increase)', 'Approved Moorefield Station ES opening with 82 staff positions', 'Revised Code of Student Conduct for 2026-27 school year'],
  '$1,870,000,000',
  15, 6, 'completed'
);

-- Advisory Boards meeting
INSERT INTO meetings (title, board_slug, meeting_date, source_url, meeting_overview, total_items, processing_status)
VALUES (
  'Transportation Safety Commission Meeting - April 2026',
  'advisory-boards',
  '2026-04-22',
  'https://loudoun.gov/meetings',
  'The Commission reviewed pedestrian safety improvements along Route 7 corridor and recommended traffic calming measures for three residential neighborhoods.',
  6, 'completed'
);

-- Agenda items for BOS meeting
INSERT INTO agenda_items (meeting_id, title, summary, decisions, action_items, primary_category, urgency, fiscal_impact, key_figures)
VALUES
  (1, 'FY2027 Budget Adoption',
   'The Board adopted the FY2027 operating budget of $2.1 billion, including a 4-cent reduction in the real property tax rate from $0.945 to $0.905 per $100 of assessed value. The budget increases school funding by $85 million while maintaining public safety staffing levels.',
   ARRAY['Adopted FY2027 budget with 4-cent tax rate reduction', 'Approved $85M increase in school funding'],
   ARRAY['County Administrator to publish final budget documents within 30 days', 'Finance department to issue taxpayer notification letters'],
   'budget-finance', 'significant', true,
   '{"amounts": ["$2,100,000,000", "$85,000,000"], "vote_tallies": ["7-2"], "dates": ["July 1, 2026"]}'::jsonb),

  (1, 'Ashburn Mixed-Use Rezoning - ZMAP-2025-0042',
   'The Board approved a rezoning application for 18 acres at the intersection of Ashburn Village Blvd and Loudoun County Pkwy from PD-H (Planned Development Housing) to PD-TC (Planned Development Town Center). The development will include 320 residential units and 45,000 sq ft of retail.',
   ARRAY['Approved ZMAP-2025-0042 for Ashburn mixed-use development', 'Approved proffers including $1.2M transportation contribution'],
   ARRAY['Applicant to submit site plan within 24 months', 'Transportation improvements to be completed prior to first occupancy'],
   'zoning-land-use', 'notable', false,
   '{"amounts": ["$1,200,000"], "vote_tallies": ["6-3"], "dates": ["Site plan deadline: May 2028"]}'::jsonb),

  (1, 'LCPS School Construction Bond Authorization',
   'The Board authorized a $42 million general obligation bond to fund construction of a new elementary school in the Moorefield Station area of Ashburn to address projected enrollment growth. The school is expected to open for the 2028-29 school year.',
   ARRAY['Authorized $42M GO bond for Moorefield Station Elementary School', 'Approved site acquisition at parcel 083-19-4532'],
   ARRAY['LCPS to begin design procurement by September 2026', 'Construction to commence no later than January 2027'],
   'school-construction', 'significant', true,
   '{"amounts": ["$42,000,000"], "vote_tallies": ["8-1"], "schools": ["Moorefield Station Elementary School"]}'::jsonb),

  (1, 'Public Safety Radio System Upgrade',
   'The Board approved a contract with Motorola Solutions for a $6.8M upgrade to the Countywide public safety communications system. The upgrade will extend coverage to known dead zones and increase encryption capabilities.',
   ARRAY['Awarded $6.8M contract to Motorola Solutions for radio system upgrade'],
   ARRAY['IT department to coordinate with Public Safety for phased rollout starting Q4 2026'],
   'public-safety', 'notable', true,
   '{"amounts": ["$6,800,000"], "vote_tallies": ["9-0"]}'::jsonb);

-- Agenda items for LCPS meeting
INSERT INTO agenda_items (meeting_id, title, summary, decisions, action_items, primary_category, urgency, fiscal_impact, key_figures)
VALUES
  (3, 'FY2027 Operating Budget Adoption',
   'The Board adopted the FY2027 operating budget of $1.87 billion, a 3.2% increase over FY2026. Key investments include 125 new teacher positions, expanded mental health support services, and technology upgrades across all schools.',
   ARRAY['Adopted $1.87B FY2027 operating budget', 'Approved 125 new teacher positions', 'Approved expanded mental health support program'],
   ARRAY['Superintendent to publish staffing plan by June 15', 'Budget office to send parent notification'],
   'schools-education', 'significant', true,
   '{"amounts": ["$1,870,000,000"], "vote_tallies": ["7-2"], "schools": ["All LCPS schools"]}'::jsonb),

  (3, 'Moorefield Station Elementary School Staffing Plan',
   'The Board approved a staffing plan of 82 positions for the new Moorefield Station Elementary School opening in Fall 2028, including one principal, two assistant principals, 54 classroom teachers, and 25 support staff.',
   ARRAY['Approved 82-position staffing plan for Moorefield Station ES'],
   ARRAY['Human Resources to begin recruitment by January 2027', 'Principal hiring to commence by August 2027'],
   'school-construction', 'notable', false,
   '{"amounts": [], "vote_tallies": ["9-0"], "schools": ["Moorefield Station Elementary"]}'::jsonb),

  (3, 'Revised Code of Student Conduct 2026-27',
   'The Board adopted revisions to the Code of Student Conduct for the 2026-27 school year, including updated cell phone policies, revised disciplinary procedures for first-time offenses, and new restorative practices guidelines.',
   ARRAY['Adopted revised Code of Student Conduct effective August 2026', 'Approved new restorative practices framework'],
   ARRAY['Student Services to provide training to all administrators by August 2026', 'Parent communications to be distributed in July 2026'],
   'policy-governance', 'routine', false, '{}'::jsonb);

-- Update total_items counts
UPDATE meetings SET total_items = (SELECT count(*) FROM agenda_items WHERE meeting_id = meetings.id);
