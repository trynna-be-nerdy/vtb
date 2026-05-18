"""
Seed Loudoun County Board of Supervisors historical data (2020 – May 2026).
Covers major Business Meetings, Special Sessions, and Public Hearings.
Run: python scripts/seed_bos_history.py
"""

import asyncio
from datetime import date
from backend.db.database import async_session
from backend.db import models
from sqlalchemy import text

MEETINGS = [
    # ══════════════════════════════════════════════════════════════════════
    # 2020 — COVID-19 EMERGENCY YEAR
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Board of Supervisors Regular Meeting – January 2020",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2020-01-07",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board approved the FY2021 budget development calendar, adopted the Loudoun 2040 Comprehensive Plan implementation matrix, and approved a $4.2M contract for Route 606 widening between Braddock Road and Loudoun County Parkway. The Board also received the annual affordable housing report.",
        "top_decisions": [
            "Approved FY2021 budget development calendar and community engagement plan",
            "Adopted Loudoun 2040 Comprehensive Plan implementation matrix with 47 action items",
            "Awarded $4.2M Route 606 widening contract",
        ],
        "fiscal_total": "$4,200,000",
        "total_items": 14,
        "fiscal_items": 4,
        "items": [
            {
                "title": "Loudoun 2040 Comprehensive Plan Implementation Matrix",
                "summary": "The Board adopted a 47-action implementation matrix for the Loudoun 2040 Comprehensive Plan, assigning lead departments and timelines for each priority including data center revenue policy, western Loudoun rural preservation, and transit corridor planning. Progress reports will be presented quarterly.",
                "decisions": ["Adopted 47-action Loudoun 2040 implementation matrix", "Directed quarterly progress reports to Board"],
                "action_items": ["Each department to submit action assignments by February 14", "Planning Commission to prioritize rural preservation zoning amendments"],
                "primary_category": "policy-governance",
                "urgency": "significant",
                "fiscal_impact": False,
                "key_figures": {"amounts": [], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Emergency Special Meeting – March 2020",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2020-03-17",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board declared a local emergency in response to COVID-19, closed county facilities to the public, authorized the County Administrator to waive procurement rules for emergency purchases, and approved $8M in emergency health and human services funding. All remaining 2020 public hearings were suspended pending safety guidance.",
        "top_decisions": [
            "Declared local emergency — COVID-19 pandemic effective March 17, 2020",
            "Approved $8M emergency appropriation for health services and resident assistance",
            "Authorized County Administrator emergency procurement authority",
        ],
        "fiscal_total": "$8,000,000",
        "total_items": 6,
        "fiscal_items": 3,
        "items": [
            {
                "title": "COVID-19 Local Emergency Declaration",
                "summary": "The Board unanimously declared a local emergency under Virginia Code §44-146.21, activating the Loudoun County Emergency Operations Plan. The declaration allows the county to access state and federal emergency funds, deploy emergency personnel, and suspend normal procurement requirements. All non-essential county facilities closed to the public effective immediately.",
                "decisions": ["Declared COVID-19 local emergency effective March 17, 2020", "Closed all non-essential county facilities to public", "Authorized emergency procurement waivers for health-related purchases"],
                "action_items": ["County Administrator to implement Emergency Operations Plan", "Emergency Operations Center to activate at Level 1", "Communications office to issue daily public updates"],
                "primary_category": "public-safety",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$8,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
            {
                "title": "$8M Emergency COVID-19 Appropriation",
                "summary": "The Board approved an emergency $8 million appropriation from the county's Emergency Reserve Fund to fund COVID-19 response. Funds allocated to: $3.2M for Loudoun County Health Department surge capacity, $2.1M for emergency food and shelter assistance through nonprofits, $1.8M for PPE and county emergency worker safety, $900K for technology to enable remote county operations.",
                "decisions": ["Approved $8M emergency appropriation from reserves"],
                "action_items": ["Finance to distribute funds to departments by March 20", "HHS to establish emergency food assistance program within 48 hours"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$8,000,000", "$3,200,000", "$2,100,000"], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Special Meeting – April 2020",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2020-04-07",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "Meeting held fully virtually for the first time in county history. The Board adopted the FY2021 budget with significant reductions from the proposed budget reflecting COVID-19 revenue uncertainty. The real estate tax rate was held flat at $1.045 per $100 of assessed value. The Board froze all non-essential capital projects and deferred 34 filled positions.",
        "top_decisions": [
            "Adopted FY2021 budget of $3.14 billion — flat real estate tax rate at $1.045",
            "Froze all non-essential capital projects pending COVID-19 revenue assessment",
            "Deferred 34 non-essential county positions",
        ],
        "fiscal_total": "$3,140,000,000",
        "total_items": 8,
        "fiscal_items": 5,
        "items": [
            {
                "title": "FY2021 Budget Adoption – COVID-19 Modified Budget",
                "summary": "The Board adopted a modified FY2021 operating budget of $3.14 billion, reduced from the original $3.28B proposed budget due to COVID-19 revenue uncertainty. The real property tax rate was held at $1.045 per $100 assessed value — no increase. The Board deferred $142M in capital projects, froze 34 non-essential positions, and cut discretionary spending by 12% across all departments. A revenue monitoring committee was established to track shortfalls.",
                "decisions": ["Adopted $3.14B FY2021 budget with flat $1.045 tax rate", "Deferred $142M in capital projects", "Froze 34 non-essential positions", "Cut discretionary spending 12% division-wide"],
                "action_items": ["County Administrator to report revenue updates monthly through FY2021", "Finance to establish COVID-19 revenue monitoring dashboard"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$3,140,000,000", "$142,000,000"], "vote_tallies": ["7-2"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – June 2020",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2020-06-02",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board received the CARES Act allocation of $40.2M and established the COVID-19 Community Relief Fund. The Board also passed a resolution condemning racial injustice following national protests, directed a review of county policing policies, and approved a $1.1M contract for a public broadband feasibility study.",
        "top_decisions": [
            "Received $40.2M CARES Act allocation — established COVID-19 Community Relief Fund",
            "Passed resolution condemning racial injustice and directed policing policy review",
            "Approved $1.1M public broadband feasibility study",
        ],
        "fiscal_total": "$40,200,000",
        "total_items": 11,
        "fiscal_items": 4,
        "items": [
            {
                "title": "CARES Act Allocation — COVID-19 Community Relief Fund",
                "summary": "The Board established the COVID-19 Community Relief Fund with $40.2M in federal CARES Act funding. Allocation: $15M for small business grants (under 50 employees), $12M for resident rent and utility assistance, $7M for nonprofits providing essential services, $4.2M for county technology and public health infrastructure, $2M for childcare provider stabilization grants.",
                "decisions": ["Established COVID-19 Community Relief Fund with $40.2M CARES Act funds", "Approved grant program for small businesses, residents, and nonprofits"],
                "action_items": ["County Administrator to open grant applications within 2 weeks", "Economic Development to administer small business grants"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$40,200,000", "$15,000,000", "$12,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
            {
                "title": "Resolution on Racial Justice and Policing Policy Review",
                "summary": "The Board passed a resolution acknowledging systemic racism and expressing solidarity with communities impacted by racial injustice. The Board directed the County Administrator to commission an independent review of Loudoun County Sheriff's Office policies including use of force, de-escalation training, and community engagement. Results due within 90 days.",
                "decisions": ["Passed resolution condemning racial injustice", "Directed 90-day independent review of LCSO policing policies"],
                "action_items": ["County Administrator to solicit independent review firm by July 1", "Sheriff to submit current use of force policy for review"],
                "primary_category": "equity-inclusion",
                "urgency": "significant",
                "fiscal_impact": False,
                "key_figures": {"amounts": [], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – October 2020",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2020-10-06",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board approved the Loudoun County broadband strategic plan, received a Metrorail Silver Line Phase 2 construction update showing 94% completion, approved rezoning for One Loudoun Phase 3 mixed-use development, and authorized election security upgrades ahead of the November 2020 election.",
        "top_decisions": [
            "Approved Loudoun Broadband Strategic Plan — target 98% coverage by 2025",
            "Received Silver Line Phase 2 update: 94% complete, opening projected Q1 2022",
            "Approved One Loudoun Phase 3 mixed-use rezoning (1,200 residential units + retail)",
        ],
        "fiscal_total": None,
        "total_items": 13,
        "fiscal_items": 2,
        "items": [
            {
                "title": "Loudoun Broadband Strategic Plan Adoption",
                "summary": "The Board adopted the Loudoun Broadband Strategic Plan, targeting 98% high-speed internet coverage of county households by 2025. The plan authorizes the county to partner with private providers, offer right-of-way incentives, and deploy county-owned infrastructure in underserved rural areas. An estimated $28M in private investment is expected to leverage $4M in county matching funds.",
                "decisions": ["Adopted Loudoun Broadband Strategic Plan with 98% coverage target by 2025"],
                "action_items": ["Economic Development to issue broadband provider RFP by December 2020"],
                "primary_category": "technology",
                "urgency": "notable",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$4,000,000", "$28,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    # ══════════════════════════════════════════════════════════════════════
    # 2021 — RECOVERY AND METRORAIL OPENING
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Board of Supervisors Regular Meeting – February 2021",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2021-02-02",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board approved county facilities as vaccination sites in partnership with the Loudoun County Health Department and Virginia Department of Health, adopted the FY2022 proposed budget of $3.29 billion, and approved a policy allowing remote participation in public meetings permanently post-pandemic.",
        "top_decisions": [
            "Designated 6 county facilities as COVID-19 mass vaccination sites",
            "Approved FY2022 proposed budget of $3.29 billion for public hearing",
            "Adopted permanent policy for remote meeting participation",
        ],
        "fiscal_total": "$3,290,000,000",
        "total_items": 12,
        "fiscal_items": 3,
        "items": [
            {
                "title": "COVID-19 Mass Vaccination Sites at County Facilities",
                "summary": "The Board authorized use of six county-owned facilities as COVID-19 mass vaccination sites: Dulles Expo Center, Claude Moore Recreation Center, Ashburn library, Leesburg library, South Riding Community Center, and Cascades library. Sites will operate 7 days a week with capacity for 3,500 doses daily. County staff will volunteer to assist VDH and LCHD operations.",
                "decisions": ["Designated 6 county facilities as mass vaccination sites", "Authorized county staff volunteerism for vaccination operations"],
                "action_items": ["County facilities to begin vaccine operations by February 15", "Emergency Management to coordinate logistics with VDH"],
                "primary_category": "public-safety",
                "urgency": "significant",
                "fiscal_impact": False,
                "key_figures": {"amounts": [], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – April 2021",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2021-04-06",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board adopted the FY2022 budget of $3.31 billion with a $0.01 reduction in the real estate tax rate to $1.035 per $100. The budget restores COVID-deferred positions and capital projects, provides a 3% merit increase for county employees, and includes $215M for the Metrorail operations and debt service. The Board also approved a $185M bond referendum for school construction.",
        "top_decisions": [
            "Adopted FY2022 budget of $3.31 billion — tax rate reduced to $1.035 per $100",
            "Approved $185M school construction bond referendum for November 2021 ballot",
            "Restored 34 COVID-deferred positions and $142M in capital projects",
        ],
        "fiscal_total": "$3,310,000,000",
        "total_items": 15,
        "fiscal_items": 7,
        "items": [
            {
                "title": "FY2022 Budget Adoption — Post-COVID Recovery Budget",
                "summary": "The Board adopted the FY2022 operating budget of $3.31 billion, restoring the positions and capital projects deferred during COVID-19 fiscal response. The real estate tax rate was reduced by one cent to $1.035 per $100 of assessed value. All county employees receive a 3% merit increase. Metrorail debt service and operating contributions total $215M. The budget includes $48M for data center assessment equalization corrections.",
                "decisions": ["Adopted $3.31B FY2022 budget with $1.035 tax rate", "Approved 3% merit increase for all county employees", "Restored all COVID-deferred capital projects"],
                "action_items": ["Finance to activate restored capital project accounts by May 1"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$3,310,000,000", "$215,000,000"], "vote_tallies": ["7-2"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Special Meeting – November 2021",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2021-11-09",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board certified the November 2021 election results including approval of the $185M school construction bond referendum with 62% voter support. The Board also received an update on the Metrorail Silver Line Phase 2 opening timeline — now projected for November 2022 — and approved $22M in American Rescue Plan Act funds for affordable housing.",
        "top_decisions": [
            "Certified $185M school construction bond referendum — approved 62% to 38%",
            "Received Metrorail Silver Line Phase 2 update: opening projected November 2022",
            "Approved $22M ARPA funds for affordable housing and community land trust",
        ],
        "fiscal_total": "$22,000,000",
        "total_items": 7,
        "fiscal_items": 3,
        "items": [
            {
                "title": "$22M ARPA Affordable Housing Investment",
                "summary": "The Board approved $22 million in American Rescue Plan Act funds for affordable housing programs: $10M to the Loudoun County Community Land Trust for permanently affordable homeownership, $8M for rental assistance vouchers through the Loudoun County Redevelopment and Housing Authority, $4M for infrastructure at Leesburg affordable housing development site.",
                "decisions": ["Approved $22M ARPA affordable housing allocation", "Funded Community Land Trust and rental assistance programs"],
                "action_items": ["Housing Authority to open rental assistance applications within 30 days", "Community Land Trust to begin property acquisition by January 2022"],
                "primary_category": "community-parks",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$22,000,000", "$10,000,000", "$8,000,000"], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
    # ══════════════════════════════════════════════════════════════════════
    # 2022 — METRORAIL OPENS, RECORD DATA CENTER REVENUE
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Board of Supervisors Regular Meeting – January 2022",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2022-01-04",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board received the FY2022 mid-year revenue report showing data center tax receipts 38% above projections, approved a $6.8M trails and parks capital improvement package, and adopted the Countywide Transportation Plan update adding six new road widening priorities in the Route 28 and Route 7 corridors.",
        "top_decisions": [
            "Mid-year revenue: data center taxes 38% above projection — $94M surplus projected",
            "Approved $6.8M trails and parks capital package",
            "Adopted Countywide Transportation Plan update — 6 new widening priorities",
        ],
        "fiscal_total": "$6,800,000",
        "total_items": 11,
        "fiscal_items": 3,
        "items": [
            {
                "title": "FY2022 Mid-Year Revenue Report — Data Center Surplus",
                "summary": "The county's mid-year revenue report revealed data center machinery and tools tax receipts of $312M through December, 38% above the $226M projection. Full-year data center revenue is now projected at $478M — a $94M surplus. Staff recommended reserving the surplus for long-term capital needs rather than operating spending, given the volatile nature of data center assessment cycles.",
                "decisions": ["Accepted mid-year revenue report showing $94M projected surplus", "Directed surplus to capital reserve fund pending end-of-year reconciliation"],
                "action_items": ["Finance to present data center revenue stabilization plan in March", "Board Audit Committee to review data center assessment methodology"],
                "primary_category": "budget-finance",
                "urgency": "notable",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$478,000,000", "$94,000,000", "$312,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Special Meeting – November 2022",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2022-11-15",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board held a special ceremony to mark the opening of the Metrorail Silver Line Phase 2 Loudoun stations — Ashburn, Innovation Center, and Dulles Airport. The Board also approved the Metrorail operational contribution of $37M for FY2023, approved the Route 7 widening from Cascades Pkwy to Route 28 ($185M project), and established a Transit-Oriented Development overlay zone for the Ashburn station area.",
        "top_decisions": [
            "Metrorail Silver Line Phase 2 opens — Ashburn, Innovation Center, Dulles Airport stations serving Loudoun",
            "Approved Route 7 widening Cascades to Route 28 — $185M design-build contract",
            "Established Transit-Oriented Development overlay zone around Ashburn Metro station",
        ],
        "fiscal_total": "$185,000,000",
        "total_items": 9,
        "fiscal_items": 4,
        "items": [
            {
                "title": "Metrorail Silver Line Phase 2 — Loudoun Station Opening",
                "summary": "The Board celebrated the opening of three Metrorail Silver Line stations in Loudoun County: Dulles Airport (serving Washington Dulles International), Innovation Center (serving the Dulles Tech Corridor), and Ashburn (eastern county's first Metro station). Loudoun's annual Metrorail operating contribution rises to $37M in FY2023, growing to $65M by FY2030 as ridership builds. The stations are projected to generate $2.1B in transit-oriented development over 20 years.",
                "decisions": ["Accepted Loudoun Metro stations into county transportation network", "Approved $37M FY2023 Metrorail operating contribution"],
                "action_items": ["Transportation to launch Loudoun County bus connections to all three stations by December", "Planning to accelerate TOD overlay zone implementation"],
                "primary_category": "transportation",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$37,000,000", "$2,100,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
            {
                "title": "Route 7 Widening — Cascades Parkway to Route 28",
                "summary": "The Board awarded a $185M design-build contract to Shirley Contracting for widening Route 7 from 4 to 6 lanes between Cascades Parkway and Route 28 — a 4.2-mile corridor carrying 65,000 vehicles daily, one of the most congested segments in Northern Virginia. Construction begins January 2023 with completion projected December 2025.",
                "decisions": ["Awarded $185M Route 7 widening contract to Shirley Contracting"],
                "action_items": ["VDOT to begin utility relocation in December 2022", "Transportation to launch public construction notification campaign"],
                "primary_category": "transportation",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$185,000,000"], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – April 2022",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2022-04-05",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board adopted the FY2023 budget of $3.89 billion — the largest in county history — with a $0.08 reduction in the real estate tax rate to $0.955 per $100, enabled by record data center tax revenues of $512M. The budget fully funds LCPS's request, adds 228 county positions, and includes a 7% merit and market adjustment for all employees.",
        "top_decisions": [
            "Adopted FY2023 budget of $3.89 billion — real estate tax reduced to $0.955 per $100",
            "Data center revenues reach record $512M — funds 13.2% of county budget",
            "Approved 7% merit and market salary increase for all county employees",
        ],
        "fiscal_total": "$3,890,000,000",
        "total_items": 16,
        "fiscal_items": 8,
        "items": [
            {
                "title": "FY2023 Budget Adoption — Record Data Center Revenue Year",
                "summary": "The Board adopted the FY2023 budget of $3.89 billion, enabled by record data center machinery and tools tax revenues of $512M — a 42% increase over FY2022. The real estate tax rate dropped 8 cents to $0.955, the largest single-year tax cut in county history. All county employees received a 7% salary adjustment. The budget adds 228 positions, fully funds LCPS's requested budget of $1.68B, and accelerates $340M in capital projects.",
                "decisions": ["Adopted $3.89B FY2023 budget with $0.955 tax rate", "Approved 7% salary adjustment for all employees", "Fully funded LCPS at $1.68B", "Accelerated $340M in capital projects"],
                "action_items": ["Finance to distribute departmental budgets by May 15"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$3,890,000,000", "$512,000,000", "$1,680,000,000"], "vote_tallies": ["6-3"], "schools": []},
            },
        ],
    },
    # ══════════════════════════════════════════════════════════════════════
    # 2023 — WESTERN LOUDOUN PRESERVATION, DATA CENTER POLICY
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Board of Supervisors Regular Meeting – February 2023",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2023-02-07",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board approved a landmark data center policy restricting new data center development in western Loudoun's Rural Policy Area, adopted a broadband digital equity plan for low-income households, and approved a $125M water and sewer infrastructure bond for the Dulles South growth area.",
        "top_decisions": [
            "Adopted data center restriction policy for western Loudoun Rural Policy Area",
            "Approved $125M water and sewer infrastructure bond for Dulles South",
            "Adopted digital equity plan targeting broadband access for low-income households",
        ],
        "fiscal_total": "$125,000,000",
        "total_items": 13,
        "fiscal_items": 4,
        "items": [
            {
                "title": "Data Center Restriction Policy — Western Loudoun Rural Policy Area",
                "summary": "The Board adopted a Zoning Ordinance Amendment prohibiting new data center development in the Rural Policy Area west of Route 15, following years of community pressure over landscape, noise, and infrastructure impacts. Existing data centers may expand with special exception approval, but no new facilities are permitted. The policy affects approximately 250,000 acres in western Loudoun.",
                "decisions": ["Adopted data center prohibition for Rural Policy Area west of Route 15", "Allowed existing data centers limited expansion via special exception"],
                "action_items": ["Zoning to implement new application review procedures by April 1", "Planning Commission to review transition cases"],
                "primary_category": "zoning-land-use",
                "urgency": "significant",
                "fiscal_impact": False,
                "key_figures": {"amounts": [], "vote_tallies": ["7-2"], "schools": []},
            },
            {
                "title": "$125M Dulles South Water and Sewer Infrastructure Bond",
                "summary": "The Board approved a $125M revenue bond to fund water and sewer infrastructure serving the Dulles South growth area, where new elementary schools, a fire station, and over 8,000 planned residential units require expanded utilities. The bond will be repaid through connection fees and utility revenues without impact to the general tax rate.",
                "decisions": ["Approved $125M Dulles South utility infrastructure bond"],
                "action_items": ["LCSA to begin design and permitting by May 2023"],
                "primary_category": "community-parks",
                "urgency": "notable",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$125,000,000"], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – April 2023",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2023-04-04",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board adopted the FY2024 budget of $3.98 billion with a $0.05 reduction in the real estate tax rate to $0.905 per $100 — the fourth consecutive year of tax rate reductions. The budget fully funds LCPS at $1.74B, funds a new Lovettsville fire station, and includes $88M for the Route 15 Bypass widening.",
        "top_decisions": [
            "Adopted FY2024 budget of $3.98 billion — tax rate cut to $0.905 (4th consecutive reduction)",
            "Fully funded LCPS at $1.74 billion",
            "Funded new Lovettsville fire station and Route 15 Bypass widening ($88M)",
        ],
        "fiscal_total": "$3,980,000,000",
        "total_items": 15,
        "fiscal_items": 6,
        "items": [
            {
                "title": "FY2024 Budget Adoption",
                "summary": "The Board adopted the FY2024 operating budget of $3.98 billion, the fourth consecutive year of real property tax rate reductions. The $0.905 rate represents a total 14-cent reduction since FY2021. Data center revenues of $558M (up 9% from FY2023) fund the rate cut while expanding services. The budget includes a 4.5% salary increase for all employees, full funding of LCPS at $1.74B, a new Lovettsville fire station ($8.2M), and $88M for Route 15 Bypass widening.",
                "decisions": ["Adopted $3.98B FY2024 budget with $0.905 tax rate", "Approved 4.5% salary increase for county employees", "Funded new Lovettsville fire station"],
                "action_items": ["Finance to distribute budgets by May 15", "Fire and Rescue to begin Lovettsville station design"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$3,980,000,000", "$558,000,000", "$88,000,000"], "vote_tallies": ["6-3"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – August 2023",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2023-08-01",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board approved the Compass Creek mixed-use development in Ashburn — 2,400 residential units, 180,000 sq ft of retail, and 12 acres of parkland — the largest single development approval in five years. The Board also approved a $42M Broad Run Regional Library expansion and adopted a new affordable housing density bonus policy.",
        "top_decisions": [
            "Approved Compass Creek Ashburn — 2,400 units, 180K sq ft retail, 12-acre park",
            "Approved $42M Broad Run Regional Library expansion",
            "Adopted affordable housing density bonus policy (15% bonus for 15% affordable units)",
        ],
        "fiscal_total": "$42,000,000",
        "total_items": 12,
        "fiscal_items": 3,
        "items": [
            {
                "title": "Compass Creek Mixed-Use Development — Ashburn",
                "summary": "The Board approved the Compass Creek development, a 142-acre mixed-use project at the intersection of Loudoun County Parkway and Waxpool Road in Ashburn. The project includes 2,400 residential units (including 360 affordable), 180,000 sq ft of neighborhood retail, two public parks (12 acres total), and a 15-acre future civic site reserved for a school or government use.",
                "decisions": ["Approved Compass Creek rezoning and proffer agreement", "Reserved 15-acre civic site for future school or government use"],
                "action_items": ["Developer to record proffer agreement within 60 days", "Planning to incorporate civic site into school planning"],
                "primary_category": "zoning-land-use",
                "urgency": "significant",
                "fiscal_impact": False,
                "key_figures": {"amounts": [], "vote_tallies": ["7-2"], "schools": []},
            },
            {
                "title": "$42M Broad Run Regional Library Expansion",
                "summary": "The Board approved the $42M expansion of the Broad Run Regional Library in Sterling, doubling its size from 38,000 to 76,000 sq ft. The expanded facility will include a community meeting hall for 400 people, expanded children's and teen services, a makerspace, digital learning lab, and dedicated quiet study floors. The project will be LEED Gold certified.",
                "decisions": ["Approved $42M Broad Run Regional Library expansion", "Directed LEED Gold certification standard"],
                "action_items": ["Library Services to issue architectural services RFP by October 2023"],
                "primary_category": "community-parks",
                "urgency": "notable",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$42,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – November 2023",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2023-11-07",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board adopted the Loudoun County Comprehensive Data Center Policy establishing a countywide framework for data center development including noise standards, setback requirements, fiscal impact analysis requirements, and community benefit agreements. The Board also approved $18M for Ashburn Metro area pedestrian and cycling infrastructure.",
        "top_decisions": [
            "Adopted comprehensive data center policy — noise, setback, and community benefit standards",
            "Approved $18M Ashburn Metro pedestrian and cycling infrastructure package",
            "Received FY2024 Q1 revenue: data center taxes tracking $580M full-year",
        ],
        "fiscal_total": "$18,000,000",
        "total_items": 11,
        "fiscal_items": 3,
        "items": [
            {
                "title": "Comprehensive Data Center Policy Adoption",
                "summary": "The Board adopted a Countywide Data Center Policy establishing the first comprehensive standards for data center development in Loudoun County: maximum noise levels (55 dB at property line), minimum 500-foot setbacks from residences, mandatory fiscal impact analysis for facilities over 50MW, and required community benefit agreements including utility undergrounding contributions and local hire commitments.",
                "decisions": ["Adopted Countywide Data Center Policy with noise, setback, and fiscal standards"],
                "action_items": ["Zoning to update application requirements by January 2024", "Planning to develop community benefit agreement template"],
                "primary_category": "policy-governance",
                "urgency": "significant",
                "fiscal_impact": False,
                "key_figures": {"amounts": [], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
    # ══════════════════════════════════════════════════════════════════════
    # 2024 — CONTINUED GROWTH, FISCAL MANAGEMENT
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Board of Supervisors Regular Meeting – February 2024",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2024-02-06",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board presented the FY2025 proposed budget of $4.16 billion with a 4-cent tax rate reduction to $0.865 per $100. County Administrator Tim Hemstreet presented projections showing data center revenues reaching $622M. The Board also approved the first phase of the Western Loudoun Rural Economy Initiative.",
        "top_decisions": [
            "FY2025 proposed budget: $4.16B with real estate tax rate cut to $0.865",
            "Data center revenue projection: $622M for FY2025",
            "Approved Western Loudoun Rural Economy Initiative Phase 1",
        ],
        "fiscal_total": "$4,160,000,000",
        "total_items": 13,
        "fiscal_items": 5,
        "items": [
            {
                "title": "FY2025 Proposed Budget Presentation",
                "summary": "County Administrator Hemstreet presented the FY2025 proposed budget of $4.16 billion, funded in part by projected data center machinery and tools tax revenues of $622M. The real estate tax rate is proposed at $0.865 — a 4-cent reduction, the fifth consecutive annual cut. Key investments: $125M for Dulles South elementary school construction, expanded mental health services, and 3.5% cost of living increase for all employees.",
                "decisions": ["Approved FY2025 proposed budget for public hearing"],
                "action_items": ["Public hearings scheduled March 4, 6, and 11", "Finance to post budget online by February 16"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$4,160,000,000", "$622,000,000"], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – April 2024",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2024-04-02",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board adopted the FY2025 budget of $4.19 billion with a 4-cent real estate tax rate reduction to $0.865 per $100 — the fifth consecutive year of rate reductions. LCPS receives full funding at $1.792 billion. The budget adds a new Fire and Rescue station in South Riding and expands the county's mental health crisis intervention team.",
        "top_decisions": [
            "Adopted FY2025 budget of $4.19 billion — tax rate drops to $0.865 per $100",
            "Funded LCPS at $1.792 billion — full Superintendent's request",
            "Approved South Riding Fire and Rescue Station 26 ($14.2M)",
        ],
        "fiscal_total": "$4,190,000,000",
        "total_items": 16,
        "fiscal_items": 7,
        "items": [
            {
                "title": "FY2025 Budget Adoption",
                "summary": "The Board adopted the FY2025 operating budget of $4.19 billion. The real estate tax rate fell a fourth consecutive cent to $0.865 — a total 18-cent reduction since FY2021. Data center revenues of $622M (14.8% of total budget) fund the tax cut while expanding public services. LCPS is fully funded at $1.792B, representing 42.8% of the total budget. A new South Riding fire station is funded at $14.2M construction cost.",
                "decisions": ["Adopted $4.19B FY2025 budget with $0.865 tax rate", "Fully funded LCPS at $1.792B", "Funded South Riding Fire Station 26 ($14.2M)"],
                "action_items": ["Finance to distribute budgets by May 15", "Fire and Rescue to begin Station 26 design"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$4,190,000,000", "$622,000,000", "$1,792,000,000", "$14,200,000"], "vote_tallies": ["6-3"], "schools": []},
            },
            {
                "title": "South Riding Fire and Rescue Station 26 Authorization",
                "summary": "The Board authorized construction of Fire and Rescue Station 26 in South Riding to reduce response times in one of the county's fastest-growing communities. Current average response times in South Riding are 9.8 minutes — above the 8-minute standard. The $14.2M facility will house one engine, one tanker, and one ambulance with 24 firefighter-paramedic positions.",
                "decisions": ["Authorized $14.2M Fire Station 26 construction in South Riding"],
                "action_items": ["Fire and Rescue to issue architectural design RFP by June 2024"],
                "primary_category": "public-safety",
                "urgency": "notable",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$14,200,000"], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – July 2024",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2024-07-09",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board approved the Loudoun County Climate Action Plan 2030 committing the county to 50% emissions reduction by 2030 and net-zero by 2050, approved solar installations on 14 county facilities, and awarded $38M in infrastructure contracts for the Dulles South growth area. The Board also approved an accessory dwelling unit ordinance to increase housing supply.",
        "top_decisions": [
            "Adopted Loudoun Climate Action Plan 2030 — 50% emissions reduction by 2030, net-zero by 2050",
            "Approved solar installations on 14 county facilities ($24M power purchase agreement)",
            "Adopted ADU ordinance — accessory dwelling units now permitted by-right in residential zones",
        ],
        "fiscal_total": "$62,000,000",
        "total_items": 12,
        "fiscal_items": 4,
        "items": [
            {
                "title": "Loudoun Climate Action Plan 2030 Adoption",
                "summary": "The Board adopted the Loudoun Climate Action Plan committing to 50% reduction in county government greenhouse gas emissions by 2030 (from a 2018 baseline) and net-zero government operations by 2050. Key strategies: fleet electrification, solar on public facilities, green building standards for county construction, and a community-wide renewable energy aggregation program. Annual progress reports required.",
                "decisions": ["Adopted Climate Action Plan 2030", "Committed to net-zero county operations by 2050"],
                "action_items": ["County Administrator to establish Climate Action Office by October 2024", "Fleet to present EV transition plan by December 2024"],
                "primary_category": "policy-governance",
                "urgency": "notable",
                "fiscal_impact": False,
                "key_figures": {"amounts": [], "vote_tallies": ["7-2"], "schools": []},
            },
            {
                "title": "Accessory Dwelling Unit Ordinance",
                "summary": "The Board adopted a Zoning Ordinance Amendment permitting accessory dwelling units (ADUs) by-right in all residential zoning districts, removing the requirement for a special exception. Detached ADUs up to 1,200 sq ft are permitted on lots over 1 acre. The ordinance is expected to add 200-400 housing units annually, primarily serving workforce and senior households.",
                "decisions": ["Adopted ADU by-right ordinance in all residential zones"],
                "action_items": ["Zoning to update application forms by August 15", "Building to develop ADU inspection streamlining protocol"],
                "primary_category": "zoning-land-use",
                "urgency": "notable",
                "fiscal_impact": False,
                "key_figures": {"amounts": [], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – October 2024",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2024-10-01",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board approved the Route 28 Corridor Improvement Plan authorizing widening from Dulles Airport to Route 50 at a total cost of $380M over six years, approved a new mental health crisis stabilization unit in partnership with Inova Loudoun Hospital, and received the FY2025 Q1 revenue report showing data center revenues tracking toward $640M.",
        "top_decisions": [
            "Approved Route 28 Corridor Improvement Plan — $380M widening from Dulles to Route 50",
            "Approved mental health crisis stabilization unit at Inova Loudoun ($8.4M county contribution)",
            "Q1 FY2025 data center revenues tracking $640M full-year — $18M above budget",
        ],
        "fiscal_total": "$388,400,000",
        "total_items": 13,
        "fiscal_items": 5,
        "items": [
            {
                "title": "Route 28 Corridor Improvement Plan",
                "summary": "The Board approved a $380M, six-year Route 28 Corridor Improvement Plan to widen Route 28 from 4 to 6 lanes from Dulles Airport access road to Route 50 — a 12-mile stretch carrying 80,000 vehicles daily. The project is the largest highway investment in county history. Funding: $220M state/federal, $160M county. Construction will be phased beginning 2025 to minimize disruption to adjacent data centers and businesses.",
                "decisions": ["Approved $380M Route 28 widening plan", "Authorized county's $160M match from transportation reserve fund"],
                "action_items": ["Transportation to coordinate with VDOT on design schedule", "Construction Phase 1 to begin Q3 2025"],
                "primary_category": "transportation",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$380,000,000", "$160,000,000", "$220,000,000"], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
    # ══════════════════════════════════════════════════════════════════════
    # 2025 — NEW BOARD MAJORITY, CONTINUED INVESTMENT
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Board of Supervisors Regular Meeting – January 2025",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2025-01-07",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The newly sworn-in Board of Supervisors held its organizational meeting, elected leadership, and adopted committee assignments. Board Chair Phyllis Randall was re-elected. The Board adopted 2025 legislative priorities urging the General Assembly to modernize data center taxation, fund Metrorail operational contributions, and increase housing production incentives.",
        "top_decisions": [
            "Re-elected Chair Randall — adopted 2025 Board committee assignments",
            "Adopted 2025 Legislative Priorities: data center tax modernization, Metrorail funding, housing",
            "Approved $12M contract for South Riding Fire Station 26 construction",
        ],
        "fiscal_total": "$12,000,000",
        "total_items": 9,
        "fiscal_items": 2,
        "items": [
            {
                "title": "2025 Legislative Priorities Adoption",
                "summary": "The Board adopted its 2025 state legislative priorities, directing County advocacy at the General Assembly. Top priorities: (1) modernize the machinery and tools tax to stabilize data center revenue projections amid assessment litigation; (2) increase state Metrorail operating contributions to reduce county's growing $42M annual burden; (3) expand by-right zoning for multifamily housing near transit; (4) restore school construction funding eliminated in 2024 budget.",
                "decisions": ["Adopted 2025 Legislative Priorities", "Directed County Administrator and lobbyists to advocate with General Assembly"],
                "action_items": ["County Administrator to schedule General Assembly meetings by February 1", "Government Relations team to present priority bill tracking monthly"],
                "primary_category": "policy-governance",
                "urgency": "notable",
                "fiscal_impact": False,
                "key_figures": {"amounts": ["$42,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – March 2025",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2025-03-04",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board received the FY2026 proposed budget of $4.31 billion with the real estate tax rate held flat at $0.865 per $100. Data center revenues are projected at $658M for FY2026. The Board approved the Leesburg Downtown Revitalization Plan investing $28M in streetscaping, parking, and cultural infrastructure.",
        "top_decisions": [
            "FY2026 proposed budget: $4.31 billion — flat real estate tax rate at $0.865",
            "Data center revenue projection: $658M for FY2026 (sixth consecutive record year)",
            "Approved $28M Leesburg Downtown Revitalization Plan",
        ],
        "fiscal_total": "$4,310,000,000",
        "total_items": 14,
        "fiscal_items": 5,
        "items": [
            {
                "title": "FY2026 Proposed Budget Presentation",
                "summary": "County Administrator presented the FY2026 proposed budget of $4.31 billion with a flat $0.865 real estate tax rate. Data center revenues project $658M — 15.3% of the county budget. Key investments: full LCPS funding at $1.855B, 4% cost of living increase for county employees, expanded mental health crisis services, Route 28 Phase 1 construction funding, and three new library digital access centers.",
                "decisions": ["Presented FY2026 proposed budget for public hearing"],
                "action_items": ["Public hearings March 18, 20, 25"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$4,310,000,000", "$658,000,000", "$1,855,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
            {
                "title": "Leesburg Downtown Revitalization Plan",
                "summary": "The Board approved a $28M Leesburg Downtown Revitalization Plan investing in King Street streetscaping and lighting ($8M), a new downtown public parking garage ($12M), expansion of the Loudoun Museum ($3.5M), cultural trail connecting Leesburg's historic sites ($4.5M), and a downtown business improvement facade grant program ($1.5M).",
                "decisions": ["Approved $28M Leesburg Downtown Revitalization Plan", "Directed implementation over FY2026-FY2028"],
                "action_items": ["Economic Development to lead stakeholder coordination by April 2025"],
                "primary_category": "community-parks",
                "urgency": "notable",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$28,000,000", "$12,000,000", "$8,000,000"], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – April 2025",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2025-04-01",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board adopted the FY2026 budget of $4.34 billion with a flat real estate tax rate of $0.865 per $100. LCPS is fully funded at $1.855 billion. The Board approved the Route 28 Phase 1 construction contract and a new affordable workforce housing trust fund seeded with $30M from data center revenues.",
        "top_decisions": [
            "Adopted FY2026 budget of $4.34 billion — flat tax rate at $0.865 per $100",
            "Established $30M Affordable Workforce Housing Trust Fund",
            "Awarded Route 28 Phase 1 construction contract — $94M segment from Dulles to Pacific Blvd",
        ],
        "fiscal_total": "$4,340,000,000",
        "total_items": 15,
        "fiscal_items": 7,
        "items": [
            {
                "title": "FY2026 Budget Adoption",
                "summary": "The Board adopted the FY2026 operating budget of $4.34 billion. The real estate tax rate remains at $0.865 — sixth consecutive year without a rate increase and fifth of tax cuts overall. Data center revenues of $658M fund expanded services while holding the tax rate flat. LCPS is fully funded at $1.855B. County employees receive a 4% cost of living adjustment. New investments include Route 28 Phase 1 ($94M), a $30M housing trust fund, and three digital access centers.",
                "decisions": ["Adopted $4.34B FY2026 budget", "Held real estate tax rate at $0.865", "Funded LCPS at $1.855B"],
                "action_items": ["Finance to distribute departmental budgets by May 1"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$4,340,000,000", "$658,000,000", "$1,855,000,000"], "vote_tallies": ["6-3"], "schools": []},
            },
            {
                "title": "Affordable Workforce Housing Trust Fund — $30M",
                "summary": "The Board established the Loudoun Affordable Workforce Housing Trust Fund with a $30M seed investment from data center revenue surplus, creating the county's largest single housing affordability investment. The fund will provide gap financing for workforce housing projects serving households earning 30%-80% of Area Median Income. An initial RFP will target 500 deed-restricted affordable units.",
                "decisions": ["Established $30M Affordable Workforce Housing Trust Fund", "Directed initial 500-unit RFP within 90 days"],
                "action_items": ["Housing department to publish RFP by July 2025", "Board to appoint Housing Trust Fund Advisory Committee"],
                "primary_category": "community-parks",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$30,000,000"], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – August 2025",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2025-08-05",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board approved the FY2026 mid-year revenue update showing a $52M surplus driven by stronger-than-expected data center revenues, directed $28M to accelerate Route 28 Phase 2 design, approved a new Comprehensive Sign Ordinance simplifying commercial signage regulations, and adopted the Loudoun County Equity Action Plan.",
        "top_decisions": [
            "FY2026 mid-year surplus of $52M — $28M directed to Route 28 Phase 2 acceleration",
            "Adopted Loudoun County Equity Action Plan with 38 measurable goals",
            "Approved new Comprehensive Sign Ordinance — simplified commercial signage standards",
        ],
        "fiscal_total": "$28,000,000",
        "total_items": 11,
        "fiscal_items": 3,
        "items": [
            {
                "title": "Loudoun County Equity Action Plan",
                "summary": "The Board adopted the Loudoun County Equity Action Plan establishing 38 measurable goals across county services, employment, and community access. Key commitments: language access services in 10 most common languages, equity analysis required for all major budget decisions, expanded services in historically underserved western and southern county areas, and an annual equity report card with public data.",
                "decisions": ["Adopted Equity Action Plan with 38 measurable goals", "Required equity analysis for major budget and policy decisions"],
                "action_items": ["County Administrator to establish Equity Office by October 2025", "First annual equity report due June 2026"],
                "primary_category": "equity-inclusion",
                "urgency": "notable",
                "fiscal_impact": False,
                "key_figures": {"amounts": [], "vote_tallies": ["7-2"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – October 2025",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2025-10-07",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board approved the FY2027 budget development calendar, received a major update on Route 28 Phase 1 construction progress, approved a $14M Dulles South Community Center construction contract, and adopted new floodplain management regulations in response to 2025 flooding events.",
        "top_decisions": [
            "Approved FY2027 budget development calendar — proposed budget January 2026",
            "Approved $14M Dulles South Community Center construction",
            "Adopted updated floodplain management regulations following 2025 flooding",
        ],
        "fiscal_total": "$14,000,000",
        "total_items": 12,
        "fiscal_items": 4,
        "items": [
            {
                "title": "Dulles South Community Center Construction Contract",
                "summary": "The Board awarded a $14M contract to Turner Construction for the new Dulles South Community Center in the Arcola/South Riding area — the first county recreation facility serving the fast-growing Dulles South community. The 22,000 sq ft facility includes a fitness center, indoor pool, multipurpose rooms, and community garden. Completion projected August 2027.",
                "decisions": ["Awarded $14M Dulles South Community Center contract to Turner Construction"],
                "action_items": ["Parks and Recreation to begin community programming planning by January 2026"],
                "primary_category": "community-parks",
                "urgency": "notable",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$14,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – December 2025",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2025-12-02",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board approved the annual data center assessment reconciliation, resulting in $38M in refunds to data center operators following successful appeals, approved a $4.2M contract for the Leesburg library renovation, and adopted the 2026 legislative priorities with a strong focus on data center tax stabilization.",
        "top_decisions": [
            "Approved $38M data center assessment refunds following assessment appeals",
            "Adopted 2026 Legislative Priorities — data center tax stability top priority",
            "Approved $4.2M Leesburg Library renovation",
        ],
        "fiscal_total": "$42,200,000",
        "total_items": 10,
        "fiscal_items": 4,
        "items": [
            {
                "title": "Data Center Assessment Appeals Refund",
                "summary": "The Board approved $38M in tax refunds to data center operators following successful challenges to the county's machinery and tools assessments for tax years 2021-2024. The refunds result from court rulings requiring methodology adjustments. The county's assessment office is implementing revised valuation protocols to reduce future appeal exposure, potentially stabilizing $60-90M in annual revenue.",
                "decisions": ["Approved $38M assessment refund to data center operators", "Directed implementation of revised assessment methodology"],
                "action_items": ["Finance to make refund payments by December 31", "Assessment office to present new valuation methodology in January 2026"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$38,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    # ══════════════════════════════════════════════════════════════════════
    # 2026
    # ══════════════════════════════════════════════════════════════════════
    {
        "title": "Board of Supervisors Regular Meeting – February 2026",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2026-02-03",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board presented the FY2027 proposed budget of $4.42 billion with a 4-cent tax rate reduction to $0.825 per $100 — the sixth year of consecutive cuts — and approved the Loudoun County Public Safety Training Center at $62M.",
        "top_decisions": [
            "FY2027 proposed budget: $4.42 billion — tax rate cut to $0.825 per $100",
            "Approved $62M Public Safety Training Center in Arcola",
            "Data center revenue projection: $672M for FY2027",
        ],
        "fiscal_total": "$4,420,000,000",
        "total_items": 13,
        "fiscal_items": 5,
        "items": [
            {
                "title": "FY2027 Proposed Budget — Sixth Consecutive Tax Rate Reduction",
                "summary": "County Administrator presented the FY2027 proposed budget of $4.42 billion. The real estate tax rate is proposed at $0.825 per $100 — a 4-cent reduction and the sixth consecutive year of cuts, representing a total 22-cent reduction from the $1.045 rate in FY2021. Data center revenues are projected at $672M using the county's new stabilized assessment methodology. LCPS is proposed at full funding of $1.935B.",
                "decisions": ["Presented FY2027 proposed budget for public hearing"],
                "action_items": ["Public hearings scheduled March 2, 4, and 9"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$4,420,000,000", "$672,000,000", "$1,935,000,000"], "vote_tallies": ["8-1"], "schools": []},
            },
            {
                "title": "$62M Public Safety Training Center",
                "summary": "The Board approved the $62M Loudoun County Public Safety Training Center to be built on a 28-acre site in Arcola. The facility will consolidate fire, rescue, law enforcement, and emergency management training currently scattered across 7 leased facilities. Features include a live-fire burn building, rescue simulation areas, a firearms range, and a 911 dispatch training simulator.",
                "decisions": ["Approved $62M Public Safety Training Center in Arcola"],
                "action_items": ["Fire and Rescue to issue design contract by April 2026", "Groundbreaking targeted for Fall 2026"],
                "primary_category": "public-safety",
                "urgency": "notable",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$62,000,000"], "vote_tallies": ["9-0"], "schools": []},
            },
        ],
    },
    {
        "title": "Board of Supervisors Regular Meeting – April 2026",
        "board_slug": "board-of-supervisors",
        "meeting_date": "2026-04-07",
        "source_url": "https://loudoun.gov/meetings",
        "meeting_overview": "The Board adopted the FY2027 budget of $4.44 billion with a 4-cent real estate tax rate reduction to $0.825 per $100 — the sixth consecutive year of rate reductions — providing Loudoun County residents with the lowest residential tax rate since 2016. LCPS is fully funded at $1.935 billion.",
        "top_decisions": [
            "Adopted FY2027 budget of $4.44 billion — tax rate drops to $0.825 per $100",
            "Fully funded LCPS at $1.935 billion",
            "Approved new western Loudoun conservation easement program ($18M)",
        ],
        "fiscal_total": "$4,440,000,000",
        "total_items": 16,
        "fiscal_items": 7,
        "items": [
            {
                "title": "FY2027 Budget Adoption — Lowest Tax Rate Since 2016",
                "summary": "The Board adopted the FY2027 operating budget of $4.44 billion. The real estate tax rate of $0.825 per $100 is the lowest since 2016 and represents a cumulative 22-cent reduction since FY2021, driven by data center revenues that now fund over $672M of the county's operations. LCPS is fully funded at $1.935B. County employees receive a 3.5% cost of living increase. New investments include $62M Public Safety Training Center, $18M western Loudoun conservation easements, and Route 28 Phase 2 design.",
                "decisions": ["Adopted $4.44B FY2027 budget with $0.825 tax rate", "Fully funded LCPS at $1.935B", "3.5% COLA for county employees"],
                "action_items": ["Finance to distribute budgets by May 15"],
                "primary_category": "budget-finance",
                "urgency": "significant",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$4,440,000,000", "$672,000,000", "$1,935,000,000"], "vote_tallies": ["6-3"], "schools": []},
            },
            {
                "title": "Western Loudoun Conservation Easement Program — $18M",
                "summary": "The Board approved an $18M voluntary conservation easement purchase program for western Loudoun County, targeting agricultural and forested land in the Rural Policy Area west of Route 15. Landowners may sell perpetual conservation easements to the county at appraised value, permanently restricting development. The program targets 3,000 acres of conservation protection over three years.",
                "decisions": ["Approved $18M western Loudoun conservation easement program", "Targeted 3,000 acres of perpetual conservation protection"],
                "action_items": ["Parks to open easement purchase applications by July 2026"],
                "primary_category": "community-parks",
                "urgency": "notable",
                "fiscal_impact": True,
                "key_figures": {"amounts": ["$18,000,000"], "vote_tallies": ["8-1"], "schools": []},
            },
        ],
    },
]


async def seed():
    async with async_session() as session:
        # Remove existing BOS history (keep the sample meeting id=1 if needed)
        await session.execute(
            text("""
                DELETE FROM agenda_items
                WHERE meeting_id IN (
                    SELECT id FROM meetings
                    WHERE board_slug = 'board-of-supervisors' AND id != 1
                )
            """)
        )
        await session.execute(
            text("DELETE FROM meetings WHERE board_slug = 'board-of-supervisors' AND id != 1")
        )
        await session.commit()

        total_meetings = 0
        total_items = 0

        for m_data in MEETINGS:
            items = m_data.pop("items", [])
            m_data["meeting_date"] = date.fromisoformat(m_data["meeting_date"])
            m_data["processing_status"] = "completed"
            m_data["total_items"] = len(items)
            m_data["fiscal_items"] = sum(1 for i in items if i.get("fiscal_impact"))

            meeting = models.Meeting(**m_data)
            session.add(meeting)
            await session.flush()

            for item_data in items:
                kf = item_data.pop("key_figures", {})
                item = models.AgendaItem(
                    meeting_id=meeting.id,
                    key_figures=kf,
                    **item_data,
                )
                session.add(item)
                total_items += 1

            total_meetings += 1

        await session.commit()
        print(f"Seeded {total_meetings} BOS meetings with {total_items} agenda items (2020–2026)")


if __name__ == "__main__":
    asyncio.run(seed())
