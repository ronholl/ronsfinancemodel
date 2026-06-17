from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


OUT = "/Users/ronholl/Documents/Apps/Ron_Finance_Model/Deployed Versions/Version 1.5/rons_retirement_guide.pdf"

GOLD = colors.HexColor("#8a6800")
DARK = colors.HexColor("#1a1208")
CREAM = colors.HexColor("#faf7ef")
PALE = colors.HexColor("#f5efe1")
LINE = colors.HexColor("#d4a843")
GREEN = colors.HexColor("#1f6b2a")
BROWN = colors.HexColor("#7b4b00")
INK2 = colors.HexColor("#3d2e10")
MUTED = colors.HexColor("#6f623f")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="GuideTitle",
    parent=styles["Title"],
    fontName="Times-Bold",
    fontSize=25,
    leading=29,
    textColor=GOLD,
    alignment=TA_CENTER,
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="GuideSub",
    parent=styles["Normal"],
    fontName="Times-Italic",
    fontSize=10.5,
    leading=13,
    textColor=INK2,
    alignment=TA_CENTER,
    spaceAfter=16,
))
styles.add(ParagraphStyle(
    name="H1x",
    parent=styles["Heading1"],
    fontName="Times-Bold",
    fontSize=17,
    leading=20,
    textColor=GOLD,
    spaceBefore=8,
    spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="H2x",
    parent=styles["Heading2"],
    fontName="Times-Bold",
    fontSize=12,
    leading=14,
    textColor=DARK,
    spaceBefore=7,
    spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="Bodyx",
    parent=styles["BodyText"],
    fontName="Times-Roman",
    fontSize=10,
    leading=13,
    textColor=DARK,
    spaceAfter=5,
))
styles.add(ParagraphStyle(
    name="BodyBold",
    parent=styles["Bodyx"],
    fontName="Times-Bold",
))
styles.add(ParagraphStyle(
    name="Smallx",
    parent=styles["BodyText"],
    fontName="Times-Italic",
    fontSize=8.5,
    leading=11,
    textColor=INK2,
    spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="Mini",
    parent=styles["BodyText"],
    fontName="Times-Roman",
    fontSize=8.2,
    leading=10.2,
    textColor=INK2,
    spaceAfter=3,
))
styles.add(ParagraphStyle(
    name="Callout",
    parent=styles["BodyText"],
    fontName="Times-Bold",
    fontSize=10,
    leading=13,
    textColor=DARK,
    backColor=CREAM,
    borderColor=LINE,
    borderWidth=0.6,
    borderPadding=7,
    spaceBefore=4,
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="GoodCallout",
    parent=styles["Callout"],
    borderColor=GREEN,
))
styles.add(ParagraphStyle(
    name="WarnCallout",
    parent=styles["Callout"],
    borderColor=BROWN,
))
styles.add(ParagraphStyle(
    name="TableHead",
    parent=styles["BodyText"],
    fontName="Times-Bold",
    fontSize=9.5,
    leading=11,
    textColor=colors.white,
))
styles.add(ParagraphStyle(
    name="CardHead",
    parent=styles["BodyText"],
    fontName="Times-Bold",
    fontSize=8.2,
    leading=9.4,
    textColor=GOLD,
    spaceAfter=2,
))


def p(txt, style="Bodyx"):
    return Paragraph(txt, styles[style])


def bullets(items):
    return [p("- " + item) for item in items]


def section(title):
    return [p(title, "H1x")]


def subhead(title):
    return [p(title, "H2x")]


def info_table(headers, rows, widths=(2.0 * inch, 4.9 * inch)):
    data = [[p(headers[0], "TableHead"), p(headers[1], "TableHead")]]
    data.extend([[p(f"<b>{a}</b>"), p(b)] for a, b in rows])
    t = Table(data, colWidths=list(widths), hAlign="LEFT", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#ddd3bd")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def simple_steps(rows):
    return info_table(("Step", "What to do"), rows, widths=(1.55 * inch, 5.35 * inch))


def cards(rows, cols=2):
    widths = [6.9 * inch / cols] * cols
    grid = []
    for i in range(0, len(rows), cols):
        cells = []
        for head, body in rows[i:i + cols]:
            cells.append([p(head.upper(), "CardHead"), p(body, "Bodyx")])
        while len(cells) < cols:
            cells.append("")
        grid.append(cells)
    t = Table(grid, colWidths=widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2d6be")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2d6be")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, letter[0], letter[1], stroke=0, fill=1)
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.8)
    canvas.line(doc.leftMargin, letter[1] - 0.55 * inch, letter[0] - doc.rightMargin, letter[1] - 0.55 * inch)
    canvas.setFont("Times-Bold", 8)
    canvas.setFillColor(GOLD)
    canvas.drawString(doc.leftMargin, letter[1] - 0.42 * inch, "RON'S RETIREMENT FINANCE MODEL V1")
    canvas.setFont("Times-Roman", 8)
    canvas.setFillColor(INK2)
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.38 * inch, f"Page {doc.page}")
    canvas.restoreState()


story = []

# Title / orientation
story += [
    Spacer(1, 0.36 * inch),
    p("Ron's Retirement Finance Model V1", "GuideTitle"),
    p("A plain-English onboarding guide for setup, Roth Lab, check-ins, and advisor conversations", "GuideSub"),
    p("Start with the Setup Guide. It is the front door to the model. It asks for information in a safer order, explains what each answer means, checks what is missing, and keeps most people away from the raw tables.", "Callout"),
    p("Quick translation: you do not need to understand every finance term before using the app. Build a reasonable baseline, use Readiness to find missing pieces, then use Roth Lab or Strategy Builder only when you are ready to test choices.", "GoodCallout"),
    Spacer(1, 0.08 * inch),
    cards([
        ("Use this guide first", "Read the first sections to understand why the app exists and how to get a useful first report."),
        ("Use reference later", "The field details are near the back. Do not start there unless a screen or field is confusing."),
        ("Advisor use", "The Roth Lab Advisor Report is designed to create better questions, not to replace professional advice."),
        ("Not advice", "This is a planning tool. It is not tax, legal, investment, Medicare, or financial advice."),
    ], cols=2),
]
story.append(PageBreak())

# Why / what the app does
story += section("1. What This App Does")
story += [
    p("Most retirement calculators ask one question: will the money last? This app tries to answer a more useful question: where should money come from each year, what tax and Medicare effects does that create, and when should taxable income be created on purpose for Roth conversions?"),
    p("The model still tracks balances year by year, but the real value is that it turns retirement cash flow into choices you can discuss.", "GoodCallout"),
    info_table(("Job", "Plain-English Meaning"), [
        ("1. Projection engine", "Moves the household through time using starting balances, growth, inflation, wages, Social Security, RMDs, inherited IRA rules, taxes, Medicare/IRMAA, and spending."),
        ("2. Funding engine", "Figures out how spending, income taxes, and cash needs are funded. It uses automatic income first, then follows the funding order for discretionary account draws."),
        ("3. Strategy engine", "Lets you test future decisions: Roth conversion targets, Roth conversion sources, IRMAA targets, tax bracket caps, spending changes, survivor planning, cash floors, growth scenarios, and funding order changes."),
    ]),
]
story += subhead("Two Active Planning Functions")
story += [
    p("Beyond tracking portfolio movement, the app actively models two decision systems."),
    cards([
        ("Funding buckets", "The app decides which buckets fund life: wages, Social Security, RMDs, inherited IRA draws, dividends, cash, taxable brokerage, IRA/401k, and Roth."),
        ("Roth conversion income", "The app can intentionally create taxable income by converting IRA money to Roth, using rules such as IRMAA tiers or federal tax bracket caps."),
    ], cols=2),
]
story += subhead("Who Benefits Most")
story += [
    info_table(("User", "Why They Might Use It"), [
        ("Retired or near retired", "To plan Roth conversions, RMD pressure, Medicare IRMAA exposure, survivor outcomes, cash flow, and account draw order."),
        ("Still working", "To understand future retirement timing, 401k savings, tax bracket room, and whether Roth conversions before Medicare might help."),
        ("Advisor discussion", "To bring a concise comparison of possible income targets instead of asking an advisor to react to a giant spreadsheet."),
    ]),
]
story.append(PageBreak())

# First run
story += section("2. First Useful Run")
story += [
    p("Do not try to optimize everything on day one. The first goal is a simple baseline that is close enough to review."),
    simple_steps([
        ("1. Open Setup Guide", "Enter the household, plan years, starting balances, income, and Medicare/IRMAA lookback if relevant."),
        ("2. Use Readiness", "Let the app tell you what looks complete, what is missing, and what deserves review."),
        ("3. Generate Report", "Read the summary, active strategies, and first few action years. Do not worry about every detailed table yet."),
        ("4. Save Backup", "Export a JSON backup after the baseline makes sense."),
        ("5. Open Roth Lab", "If Roth conversions matter, save the Current Plan as a User Scenario, then compare a few Roth income targets."),
        ("6. Print Advisor Report", "Use the concise Roth Lab report for discussion with a tax or financial advisor."),
    ]),
    p("A good baseline beats a perfect-looking plan that nobody understands. Get the model roughly right, then improve one thing at a time.", "GoodCallout"),
]
story += subhead("What Not To Do First")
story += bullets([
    "Do not start in raw Inputs, Start of Year, or Override Tables unless you already know why you need them.",
    "Do not compare Roth strategies before the household, balances, income, and Medicare lookback are reasonable.",
    "Do not change five assumptions at once. Change one major thing, rerun, and see what moved.",
])
story.append(PageBreak())

# Money flow
story += section("3. How The Model Thinks About Money")
story += [
    p("The app works year by year. In each year, money comes in, needs are calculated, and account draws fill the gap."),
    info_table(("Layer", "What Happens"), [
        ("Automatic income", "Wages, self-employment, Social Security, RMDs, inherited IRA required draws, brokerage dividends/interest, and cash interest appear according to setup and strategies."),
        ("Required needs", "The model funds annual spending, income taxes, and any cash gap needed to rebuild cash toward the target."),
        ("Funding order", "If automatic income is not enough, the model follows the selected draw order, such as IRA/401k, then taxable brokerage, then Roth."),
        ("Roth conversions", "A Roth conversion is not spending. It moves money from IRA to Roth and creates taxable income now, usually to reduce future taxable IRA/RMD pressure."),
        ("Roth conversion source", "The source setting controls which person's IRA supplies the conversion dollars. The Cash Flow tab shows the split by person so the taxable conversion can be audited."),
        ("Taxable account buckets", "Taxable brokerage income is estimated from entered balances. Regular taxable investments, U.S. Treasuries, CA municipal bonds, and other-state municipal bonds receive different tax treatment."),
    ]),
    p("Important cash-flow convention: annual spending is the household spending budget and is assumed to include normal Medicare premiums. Income taxes are modeled separately. IRMAA is shown separately for planning comparison, but it is not added as a second separate spending withdrawal unless you include it in spending.", "Callout"),
]
story += subhead("Why This Matters")
story += bullets([
    "A Roth conversion can improve future account location but raise current tax or IRMAA.",
    "An IRA draw used to fund spending is taxable income, so funding choices can change tax results.",
    "A survivor case can change filing status, tax brackets, Social Security, Medicare count, and account pressure.",
])
story.append(PageBreak())

# User paths
story += section("4. Pick The Right Path")
story += [
    p("Different users should pay attention to different parts of the app. This keeps the tool from feeling bigger than the decision in front of you."),
    cards([
        ("Retired or near retired", "Start with Setup Guide, Medicare lookback, Social Security, RMDs, inherited IRAs if any, and Roth Lab IRMAA scenarios."),
        ("Still working", "Start with wages, 401k defaults, retirement timing, savings assumptions, and tax bracket scenarios. IRMAA may matter later, but it may not be the first question."),
        ("Widow/widower planning", "Use Survivor Plan to understand single-filing tax brackets, Social Security changes, Medicare count, spending changes, and future RMD pressure."),
        ("Advisor meeting", "Use the Advisor Report, not the raw tables. Bring a few scenarios and questions rather than every possible detail."),
    ], cols=2),
]
story += subhead("Retired or Near-Retired Workflow")
story += [simple_steps([
    ("1. Baseline", "Complete Setup Guide and Readiness."),
    ("2. Medicare", "Enter prior MAGI and review IRMAA assumptions."),
    ("3. Roth Lab", "Use IRMAA Base through Tier 4 to see how different income targets change taxes, IRMAA, IRA depletion, Roth balance, and net worth."),
    ("4. Advisor Report", "Select up to five useful scenarios and print the report."),
])]
story += subhead("Working User Workflow")
story += [simple_steps([
    ("1. Baseline", "Enter wages, 401k defaults, self-employment or 1099 income if any, and retirement timing."),
    ("2. Tax focus", "Use No Extra Roth, Tax Bracket Fill, or a Federal Bracket Cap if you want to test using tax bracket space."),
    ("3. Medicare later", "As Medicare approaches, add IRMAA-aware scenarios because Medicare premiums can jump based on income from two years earlier."),
])]
story.append(PageBreak())

# Setup overview
story += section("5. Setup Guide In Human Order")
story += [
    p("The Setup Guide is the normal data-entry path. It asks for information in the order most people can answer it."),
    info_table(("Setup Screen", "Why It Exists"), [
        ("Household", "Names, one-person or two-person plan, tax filing, state, plan start year, and plan length."),
        ("Survivor Plan", "Only needed for two-person plans when testing one spouse dying during the plan."),
        ("Assumptions", "Global defaults for growth, inflation, dividends, cash interest, spending growth, Social Security COLA, cash floor, and draw order."),
        ("Opening Year", "First-year spending and balances. Taxable brokerage is split into regular taxable investments, U.S. Treasuries, CA municipal bonds, and other-state municipal bonds before IRA/401k, Roth, HSA, and inherited accounts."),
        ("Inherited IRAs", "Rule details for inherited retirement accounts. Use this only if inherited accounts exist."),
        ("Income", "Work income and Social Security. Retired users can skip work income if it does not apply."),
        ("401k Defaults", "Global contribution defaults for people still working."),
        ("Medicare & IRMAA", "Prior MAGI, Medicare surcharge assumptions, and default Roth conversion targets."),
        ("Review", "A checklist that sends you back to the right screen when something needs attention."),
    ]),
    p("Leave truly unused items blank or zero. The app should explain when a blank means 'not applicable' and when a field is actually needed.", "GoodCallout"),
]
story += subhead("Taxable Brokerage And Bond Balances")
story += [
    p("Opening Year and Annual Check-In ask for taxable-account balances, not annual interest. Put ordinary taxable brokerage holdings in Taxable Stocks/Funds. Use the U.S. Treasury bucket for Treasury or federal-obligation balances, CA Municipal Bond for California municipal bonds, and Other-State Municipal Bond for municipal bonds taxable by California.", "Callout"),
    p("The model applies the Brokerage Dividend / Interest Rate to those balances to estimate annual income, while the full taxable account still shares the overall Investment Growth Rate.", "GoodCallout"),
    info_table(("Bucket", "Tax Treatment"), [
        ("Taxable Stocks/Funds", "Federally taxable and generally taxable by California."),
        ("U.S. Treasury / Federal Obligation", "Federally taxable, but exempt from California/state tax."),
        ("CA Municipal Bond", "Exempt from regular federal and California tax, but included for Social Security provisional income and Medicare MAGI."),
        ("Other-State Municipal Bond", "Federally tax-exempt municipal interest that is taxable by California."),
    ]),
]
story.append(PageBreak())

# Roth Lab
story += section("6. Roth Lab")
story += [
    p("Roth Lab is the comparison tool for Roth conversion planning. It is for asking: how much income should we intentionally create now by converting IRA money to Roth?"),
    p("A Roth conversion can reduce future IRA balances, future RMD pressure, and future taxable income. But it can also increase current income tax, state tax, Medicare IRMAA, or cash-flow pressure. Roth Lab puts those tradeoffs side by side.", "Callout"),
]
story += subhead("What Roth Lab Is Not")
story += bullets([
    "It is not a recommendation engine.",
    "It does not know your risk tolerance, estate goals, tax preparer preferences, or exact future tax law.",
    "It is a discussion tool so you and an advisor can see the tradeoffs more clearly.",
])
story += subhead("The Main Scenario Families")
story += [
    info_table(("Scenario", "Plain-English Meaning"), [
        ("Current Plan", "The plan exactly as currently saved, including existing Roth target rows and strategies."),
        ("User Scenario", "A saved snapshot of one plan so you can experiment and later restore or compare against it."),
        ("No Extra Roth", "Turns off intentional Roth conversion targets in the Roth Lab window. Useful as a baseline."),
        ("IRMAA Base / Tiers", "Medicare-aware targets. These compare converting up to selected Medicare income tiers, less a cushion."),
        ("Tax Bracket Fill", "Tax-focused target. It fills available federal tax bracket space and ignores Medicare IRMAA tiers."),
        ("Federal Bracket Cap", "A selected federal bracket ceiling. Useful for working users or users who care more about tax bracket space than IRMAA."),
    ]),
]
story.append(PageBreak())

story += section("7. How To Use Roth Lab")
story += [
    simple_steps([
        ("1. Save Current Plan", "Before experimenting, use Save / Replace User Scenario. This gives you a named plan to restore or compare."),
        ("2. Pick a window", "Choose the Roth Lab years. Many retirees focus on years before RMDs, before a survivor change, or before inherited IRA deadlines."),
        ("3. Start with a preset", "Retiree preset compares IRMAA tiers. Working / Tax preset compares tax-bracket choices."),
        ("4. Compare scorecards", "Look at lifetime Roth conversions, income tax, IRMAA, tax + Medicare impact, final IRA, final Roth, final other assets, final net worth, and weighted effective tax rate."),
        ("5. Inspect year-by-year", "Use this when a scenario looks surprising. It shows AGI, Roth conversions, IRMAA created, IRMAA paid, taxes, and ending balances."),
        ("6. Print Advisor Report", "Select up to five scenarios that tell the clearest story and print the concise report."),
        ("7. Use a strategy only after deciding", "If a scenario becomes the plan, use the strategy button to write the Roth target rows into the plan."),
    ]),
]
story += subhead("Important Roth Lab Controls")
story += [
    info_table(("Control", "Meaning"), [
        ("IRMAA target", "The Medicare income ceiling to aim for, less the cushion."),
        ("IRMAA cushion", "How far below the IRMAA line to stop, such as $4,000 below the tier threshold."),
        ("No extra fill", "Do not intentionally convert above the selected target. Funding still follows the normal draw order."),
        ("Fill to next tier", "If income is already over the selected target, the model may convert toward the next useful tier."),
        ("Use Roth above target", "If spending or tax funding would require taxable IRA draws above the target, use Roth withdrawals above the target instead."),
        ("Federal bracket cap", "Optional tax-bracket ceiling. For working users, this may be more relevant than IRMAA."),
        ("Roth conversion source", "Choose where conversion dollars come from: higher IRA, lower IRA, first person, second person, or a percent split such as 50/50. If one IRA does not have enough available, the model uses the other IRA to finish the target."),
    ]),
    p("Retired users often start with IRMAA Base through Tier 4. Working users often start with No Extra Roth, Tax Bracket Fill, and a conservative federal bracket cap if one has been chosen.", "GoodCallout"),
]
story.append(PageBreak())

# Advisor report
story += section("8. Advisor Report")
story += [
    p("The Advisor Report is the clean conversation piece. It is meant to be short enough to discuss and detailed enough to avoid vague guesses."),
    info_table(("Report Area", "Why It Is There"), [
        ("Key assumptions", "Shows the assumptions that could change the answer, such as growth, inflation, survivor plan, Medicare lookback, tax filing, and Roth Lab window."),
        ("Scenario comparison", "Compares the selected Roth strategies side by side."),
        ("Year-by-year detail", "Shows the first few years or the selected detail range for each scenario."),
        ("Advisor questions", "Prompts the discussion: which income target is reasonable, whether IRMAA is worth paying, whether survivor planning changes the answer, and whether the strategy should stop at a tier or bracket."),
    ]),
]
story += subhead("Good Advisor Questions")
story += bullets([
    "Is the selected IRMAA tier worth paying to reduce future IRA and RMD pressure?",
    "Should conversions stop at an IRMAA tier, a federal bracket, or a custom MAGI amount?",
    "Does the answer change if growth is lower, growth is higher, or one spouse dies earlier?",
    "Should taxes be paid from cash, taxable brokerage, IRA, or Roth in specific years?",
    "Are estate goals more important than lowest lifetime tax in this plan?",
])
story += [
    p("The Advisor Report is not trying to win the argument. It is trying to make the right argument visible.", "Callout"),
]
story.append(PageBreak())

# Check-ins / strategies
story += section("9. Annual Check-In And Strategy Builder")
story += [
    p("The first setup is only the starting map. Annual Check-In and Strategy Builder keep the map useful."),
    cards([
        ("Annual Check-In", "Use once a year to enter real balances, taxable-account bond buckets, real income, and other actual details. This keeps the model anchored to reality."),
        ("Strategy Builder", "Use for future decisions: spending changes, Roth targets, cash floors, growth scenarios, tax timing, and funding order changes."),
    ], cols=2),
]
story += subhead("Annual Check-In")
story += [simple_steps([
    ("Pick year", "Choose the year being updated."),
    ("Enter actuals", "Update spending, income, HSA, inherited IRA values, and balances. For taxable accounts, enter the balance split between taxable investments, Treasuries, CA munis, and other-state munis."),
    ("Rerun report", "Generate a fresh report so the action plan reflects reality."),
])]
story += subhead("Strategy Builder")
story += [
    info_table(("Strategy", "Use It For"), [
        ("Spending change", "A future lifestyle change, one-time cost, or spending reduction."),
        ("Tax funding / deferred tax", "A year-specific tax funding choice, such as paying less estimated tax this year and catching up later."),
        ("Roth conversion / IRMAA target", "A rule for intentional Roth conversion income."),
        ("Roth conversion source", "A year-range rule for which IRA supplies conversion dollars: higher IRA, lower IRA, either named person first, or a percent split."),
        ("Income target", "A custom taxable income ceiling."),
        ("Portfolio return scenario", "A selected year range with a different assumed growth rate."),
        ("Cash floor", "A future change to the cash reserve target."),
        ("Funding order", "A future change to which accounts are tapped first."),
    ]),
    p("Add notes to strategies. A note that seems obvious today may save Future You from wondering why a rule exists.", "GoodCallout"),
]
story.append(PageBreak())

# Reference setup
story += section("10. Setup Reference")
story += [
    p("Use this section when a field is confusing. You do not need to memorize it before using the app."),
    info_table(("Area", "Key Plain-English Notes"), [
        ("Household", "Names are used in labels. One-person plans hide spouse and survivor setup. Two-person plans usually default to Married Filing Jointly."),
        ("Birth years", "Used for age, Social Security, Medicare, RMDs, and senior deduction timing."),
        ("Plan start and length", "The first and last years shown in reports. Pick enough years to cover retirement, Medicare, RMDs, inherited IRA deadlines, and survivor planning."),
        ("Cash", "Non-IRA cash or near-cash only: bank accounts, money markets, CDs, short-term Treasuries, or similar reserves."),
        ("Securities / brokerage", "Taxable investment money outside IRA and Roth accounts. Enter it by tax bucket when possible: taxable stocks/funds, U.S. Treasuries, CA municipal bonds, and other-state municipal bonds."),
        ("IRA / 401k", "Traditional retirement money. Withdrawals and conversions are usually taxable."),
        ("Roth conversion source", "For two-person plans, this controls whose traditional IRA is converted first or how conversions are split. It changes the source account, not the conversion target amount."),
        ("Roth", "Roth IRA or Roth 401k money. Qualified withdrawals are usually tax-free."),
        ("HSA", "Health Savings Account. Leave blank or zero if none exists."),
        ("Social Security", "Enter current monthly benefit if already receiving. Otherwise enter start age and estimated monthly benefit at that age."),
        ("W-2 withholding", "Optional. Most users can leave blank so the model calculates income tax separately."),
    ]),
]
story.append(PageBreak())

# Inherited IRA reference
story += section("11. Inherited IRA Reference")
story += [
    p("Use inherited IRA setup only for inherited retirement accounts. Regular IRA, 401k, Roth, and HSA balances belong in Opening Year."),
    info_table(("Field", "Meaning"), [
        ("Beneficiary", "Whose inherited IRA rules and age apply."),
        ("Starting balance", "The balance at the beginning of the first modeled year for that lot. If setting up in 2026, use the 2026/current balance, not the original inheritance amount."),
        ("Distributions begin year", "The first year this inherited IRA lot is active for projection draws. It is a modeling choice, not automatically the year after death."),
        ("Death year", "For post-2020 lots, this sets the 10-year deadline. For pre-2020 lots, it helps calculate life-expectancy RMDs."),
        ("Deceased owner birth year", "Used to determine whether annual RMDs apply before a final deadline."),
        ("Draw strategy", "How optional draws are spread before the deadline."),
        ("Pre-2020 lots", "Add separate lots when accounts came from different owners, different death years, or different beneficiaries. Combine only when they use the same RMD schedule."),
    ]),
    p("Inherited IRA rules can be unforgiving. When in doubt, use the app to model cash flow, but confirm required distribution rules with a tax professional or custodian.", "WarnCallout"),
]

# Advanced / backups / glossary
story += section("12. Advanced Mode, Backups, And Glossary")
story += [
    p("Advanced Mode shows the raw machine room: Inputs, Start of Year, Override Tables, Year Detail, Cash Flow, Tax Summary, Tax Tables, and Export/Import. Most users can leave it off."),
    p("Use Export/Import for JSON backups. Make a backup after setup, after annual check-ins, before major strategy testing, and after changes you would not want to recreate.", "Callout"),
    info_table(("Term", "Plain-English Meaning"), [
        ("AGI / MAGI", "Income measures used for tax and Medicare planning. Medicare IRMAA uses a MAGI-style lookback."),
        ("IRMAA", "Extra Medicare premium for higher income."),
        ("RMD", "Required minimum distribution from some retirement accounts."),
        ("Roth conversion", "Moving IRA money to Roth and paying tax now so future qualified Roth withdrawals may be tax-free."),
        ("Roth conversion source", "The IRA account used for conversion dollars. This can be higher IRA, lower IRA, a named person first, or a percent split."),
        ("Tax-free bond buckets", "Taxable-account balance entries for U.S. Treasuries and municipal bonds so federal and California tax treatment can differ."),
        ("Funding order", "The order used when the model needs extra money from accounts."),
        ("Cash floor", "The cash reserve target the model tries to protect."),
        ("Cushion / headroom", "A safety amount below a target, such as staying $4,000 below an IRMAA tier."),
        ("Strategy / override", "A rule for selected years that changes the default plan."),
        ("Weighted effective tax rate", "A blended tax-rate measure weighted by taxable income, so very small or zero-income years do not distort the comparison."),
    ]),
    p("Best habit: build a simple baseline, export a backup, test one strategy, compare, then either keep it or remove it. Clear experiments beat giant mystery scenarios.", "GoodCallout"),
    Spacer(1, 0.12 * inch),
    p("(c) 2026 Ronald Hollander - Licensed CC BY-NC 4.0 - This guide is informational and is not financial, tax, legal, Medicare, or investment advice.", "Smallx"),
]


doc = BaseDocTemplate(
    OUT,
    pagesize=letter,
    leftMargin=0.7 * inch,
    rightMargin=0.7 * inch,
    topMargin=0.72 * inch,
    bottomMargin=0.58 * inch,
    title="Ron's Retirement Finance Model V1 Guide",
    author="Ronald Hollander",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
doc.addPageTemplates([PageTemplate(id="guide", frames=[frame], onPage=header_footer)])
doc.build(story)
print(OUT)
