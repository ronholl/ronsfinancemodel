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
    fontSize=10,
    leading=13,
    textColor=INK2,
    alignment=TA_CENTER,
    spaceAfter=18,
))
styles.add(ParagraphStyle(
    name="H1x",
    parent=styles["Heading1"],
    fontName="Times-Bold",
    fontSize=17,
    leading=20,
    textColor=GOLD,
    spaceBefore=8,
    spaceAfter=8,
))
styles.add(ParagraphStyle(
    name="H2x",
    parent=styles["Heading2"],
    fontName="Times-Bold",
    fontSize=12,
    leading=14,
    textColor=DARK,
    spaceBefore=8,
    spaceAfter=5,
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
    name="Smallx",
    parent=styles["BodyText"],
    fontName="Times-Italic",
    fontSize=8.5,
    leading=11,
    textColor=INK2,
    spaceAfter=4,
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
    fontSize=10,
    leading=12,
    textColor=colors.white,
))


def p(txt, style="Bodyx"):
    return Paragraph(txt, styles[style])


def bullets(items):
    return [p("- " + item) for item in items]


def section(title):
    return [p(title, "H1x")]


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
    return info_table(("Step", "What to do"), rows, widths=(1.8 * inch, 5.1 * inch))


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
story += [
    Spacer(1, 0.45 * inch),
    p("Ron's Retirement Finance Model V1", "GuideTitle"),
    p("Plain-English Guide to Setup, Check-Ins, Strategies, and Reports", "GuideSub"),
    p("Start with the Setup Guide. It is the front door to the model. It asks for information in a safer order, explains what each answer means, checks what is missing, and keeps most people away from the raw tables.", "Callout"),
    Spacer(1, 0.10 * inch),
    p("Quick translation: you do not need to understand every finance term before using the app. Answer the setup questions you know, leave truly unused items blank or zero, use Readiness to find missing pieces, and then generate a report.", "GoodCallout"),
    Spacer(1, 0.10 * inch),
    p("Important: this is a planning tool, not tax, legal, investment, or Medicare advice. Use it to ask better questions and review major decisions with a qualified professional.", "Smallx"),
]
story.append(PageBreak())


story += section("1. The Simple Way to Use the App")
story += [
    p("Think of the app like a guided interview. You tell it who is in the household, what accounts exist, what income exists, and what future changes you want to test. The app turns that into a year-by-year plan."),
    simple_steps([
        ("1. Setup Guide", "Answer the setup screens in order. This is where most users should do setup. The app explains each field and uses your names in later screens."),
        ("2. Readiness", "Check what is complete, what is missing, and what may need review. Use the buttons there to jump to the right setup screen."),
        ("3. Annual Check-In", "Once each year, enter real balances and real first-year information. This keeps the plan tied to reality."),
        ("4. Strategy Builder", "Add future changes in plain language, such as changing spending, testing a Roth conversion target, changing growth assumptions, or setting a cash floor."),
        ("5. Report", "Generate the readable report. Use the report to review the plan, the active strategies, and the three-year action plan."),
    ]),
    p("Most users should not need the raw Inputs, Start of Year, or Override Tables tabs. They are still there in Advanced Mode for inspection and expert editing.", "Callout"),
]


story += section("2. What the Main Buttons Mean")
story += [
    info_table(("Button or Area", "Plain-English Meaning"), [
        ("Guide", "Opens this guide."),
        ("Report", "Builds the readable planning report from the current data."),
        ("Advanced", "Shows the raw tabs: Inputs, Start of Year, Override Tables, Year Detail, Cash Flow, Tax Summary, Tax Tables, and Export. Leave Advanced off unless you need those tools."),
        ("Interview", "The guided setup screens. This is the normal setup path."),
        ("Readiness", "A checklist. It tells you what the app thinks is missing or worth reviewing."),
        ("Annual Check-In", "A yearly update area. Use it when a new year starts or when balances change and you want the model anchored to actual numbers."),
        ("Strategy Builder", "A plain-language way to create the same override rows that advanced users can edit in the raw Override Tables."),
    ]),
]
story.append(PageBreak())


story += section("3. Setup Guide Overview")
story += [
    p("The Setup Guide is broken into small screens. You can move through them in order, or use Readiness to jump back to a screen that needs attention."),
    info_table(("Setup Screen", "What It Asks"), [
        ("Household", "Who is in the plan, where taxes are estimated, when the plan starts, and how many years it should run."),
        ("Survivor Plan", "For two-person plans only. The normal default is both people live through the plan end. Use survivor planning only when you want to test one person dying during the plan."),
        ("Assumptions", "The model's normal defaults: growth, dividends, cash interest, spending increase, Social Security COLA, wage growth, cash floor, and draw order."),
        ("Opening Year", "The first-year spending amount and starting account balances: cash, brokerage, IRA/401k, Roth, HSA, and inherited accounts if any."),
        ("Inherited IRAs", "Only for inherited retirement accounts. It asks for rule details, not just balances, so required withdrawals can be calculated."),
        ("Income", "Work income and Social Security. These are separated so retired users can skip work income and focus on Social Security."),
        ("401k Defaults", "Global contribution and employer match defaults for people still working."),
        ("Medicare & IRMAA", "Medicare income lookback and Roth-conversion target settings related to Medicare premium surcharges."),
        ("Review", "A final checklist before using the dashboard or report."),
    ]),
]


story += section("4. Household")
story += [
    p("This screen tells the model who the plan is about. The names you enter become labels across the setup and report, so the app can say Primary Person or Spouse/Partner by name."),
    info_table(("Field", "What It Means"), [
        ("Plan Includes", "Choose One person or Two people. If you choose One person, spouse and survivor setup are hidden. If you choose Two people, the app keeps spouse and survivor planning available."),
        ("Primary Person Name", "The main person in the plan. This is used for labels and report headings."),
        ("Spouse / Partner Name", "The second person in a two-person plan. Leave this hidden by choosing One person if there is no second person."),
        ("Birth Year", "Used to calculate age. Age affects Social Security, Medicare, required IRA withdrawals, and some tax rules."),
        ("Tax Filing Status", "Usually Single for one person and Married Filing Jointly for two people. The app should default that way, but you can review it here."),
        ("State Tax Setting", "California turns on California tax estimates. Federal Only skips state income tax estimates."),
        ("Plan Start Year", "The first year shown in the plan and report. This is usually the current tax year or the first year you want to model."),
        ("Plan Length", "How long the projection runs. Pick enough years to cover retirement, Medicare, RMDs, inherited IRA deadlines, and survivor planning."),
    ]),
    p("The ages shown on the screen are not decoration. They help people notice simple mistakes, like typing the wrong birth year or making the plan too short.", "GoodCallout"),
]
story.append(PageBreak())


story += section("5. Survivor Plan")
story += [
    p("For most couples, the default is simple: both people live through the plan end. That is the easiest and least scary starting point."),
    p("Use Survivor Plan only when you want to test what changes if one spouse dies during the plan. This can change taxes, Social Security, Medicare count, spending, and required withdrawals."),
    info_table(("Question", "Why It Matters"), [
        ("Who survives?", "Tells the model whose age, Social Security, and Medicare situation continues after the death year."),
        ("Death year", "The year one spouse dies in the test. Most changes start the next year."),
        ("Social Security", "A survivor may keep the higher of the two Social Security benefits, while the other benefit stops."),
        ("Filing status", "A survivor usually files as Single after the transition period. That can raise taxes because the single brackets are smaller."),
        ("Spending adjustment", "Spending may go down after one person dies, but not always by half. Housing and many bills may stay similar."),
    ]),
    p("If this topic is uncomfortable or not needed, leave the default. The model does not require survivor mode for a normal two-person plan.", "WarnCallout"),
]


story += section("6. Assumptions")
story += [
    p("Assumptions are the model's default guesses. They are not promises. They simply tell the model what to use unless a later strategy changes the rule for certain years."),
    info_table(("Field", "Plain-English Meaning"), [
        ("Portfolio Growth Rate", "How much investment accounts are assumed to grow each year before specific year overrides. This is a general planning guess, not a forecast."),
        ("Brokerage Dividend Rate", "How much taxable dividend income the brokerage account is expected to produce."),
        ("Cash Interest Rate", "How much interest cash or near-cash may earn."),
        ("Dividend Reinvest", "How much of brokerage dividends stay invested instead of showing up as spendable cash."),
        ("Dividend Tax Treatment", "How the model taxes dividends. Ordinary income is simpler and more conservative for many plans; qualified dividends may be taxed differently."),
        ("Annual Spending Increase", "How spending grows each year from inflation or lifestyle changes."),
        ("SS COLA", "The annual Social Security cost-of-living increase assumption."),
        ("Wage Growth", "How wages increase while work income is still active."),
        ("Stock Sales Taxable Gain", "When brokerage investments are sold, this is the percent treated as taxable gain."),
        ("Cash Floor", "The cash cushion the model tries not to spend below. Cash here means non-IRA cash or near-cash, not retirement accounts."),
    ]),
    p("The Draw 1, Draw 2, Draw 3 settings tell the model where to pull extra money from after regular income and cash above the cash floor are used. Example: Securities first, then IRA, then Roth.", "Callout"),
    p("If a future year should behave differently, do not change the global assumption just for that year. Use Strategy Builder so the change is clear and attached to a year range.", "GoodCallout"),
]
story.append(PageBreak())


story += section("7. Opening Year")
story += [
    p("Opening Year is the starting line. It tells the model what you have at the beginning of the first plan year. Blank or zero is fine when an account truly does not exist."),
    info_table(("Field", "Plain-English Meaning"), [
        ("Annual Spending", "The amount you expect to spend in the first plan year, before income taxes. Later years inflate from here unless a strategy changes spending."),
        ("Cash Balance", "Money outside retirement accounts that is available or nearly available: bank accounts, money market, CDs, short-term Treasury funds, and similar cash-like reserves."),
        ("Securities / Brokerage", "Taxable investment account money outside IRAs and Roth accounts."),
        ("IRA / 401k", "Traditional retirement money. This includes traditional IRA, rollover IRA, and traditional 401k money. Withdrawals are usually taxable."),
        ("Roth", "Roth IRA or Roth 401k money. Qualified withdrawals are usually tax-free."),
        ("HSA", "Health Savings Account. If you do not have one, leave it blank or zero. The model includes it because some retirees use HSAs for medical spending."),
        ("Pre-2020 Inherited IRA(s)", "Only for older inherited IRAs that use beneficiary life-expectancy RMD rules. The Inherited IRAs screen now supports separate lots when accounts have different owners, death years, or beneficiaries."),
        ("Post-2020 Inherited IRA Active-Lot Reset", "Optional yearly balance reset for post-2020 inherited IRA lots that are active in that check-in year. Use the Inherited IRAs screen to enter the actual lots and rules."),
    ]),
    p("If someone has a 401k and an IRA, this model treats traditional IRA and traditional 401k as one traditional retirement bucket for planning. Same idea for Roth IRA and Roth 401k.", "Callout"),
]


story += section("8. Inherited IRAs")
story += [
    p("Use this screen only when the plan includes inherited retirement accounts. Regular IRAs, 401ks, and Roth accounts belong on Opening Year, not here."),
    p("Inherited IRAs need rule details. A balance alone is not enough because the required withdrawal depends on when the person died, who inherited the account, and sometimes the age of the original owner."),
    p("For pre-2020 inherited IRAs, use one row per old life-expectancy RMD schedule. If two accounts have the same beneficiary and same original-owner birth/death years, you may combine them. If they came from different owners, different death years, or different beneficiaries, add separate lots so the model can calculate each RMD separately.", "Callout"),
    info_table(("Field", "Plain-English Meaning"), [
        ("Beneficiary", "Whose inherited IRA rules and age apply."),
        ("Starting Balance", "The balance at the beginning of the first year this lot is active in the projection. If the owner died in 2020 and the lot starts in 2026, use the 2026/current balance, not the original inherited amount."),
        ("First Modeled Draw Year", "The first year this lot appears for projection draws. It is not automatically the year after death. If the account already exists when the plan starts, this is often the plan start year. Use a later year only when you intentionally want draws to begin later."),
        ("Deceased Owner Birth Year", "Used to tell whether annual required withdrawals apply before the 10-year deadline."),
        ("Death Year", "For post-2020 lots, this sets the 10-year deadline. For pre-2020 lots, this helps calculate the life-expectancy RMD schedule."),
        ("Draw Strategy", "How much extra to take before the deadline, beyond anything required."),
        ("Draw Percent", "Used only when the draw strategy is Percent of balance."),
        ("Notes", "A place to write whose account it was or why the strategy was chosen."),
    ]),
    p("For post-2020 inherited IRAs, the account usually must be emptied by the end of year 10 after death. The First Modeled Draw Year is a modeling choice: it controls when this lot starts appearing for projection draws. If required annual RMDs should be modeled before that year, choose the earlier year.", "WarnCallout"),
    p("For pre-2020 inherited IRAs, the model uses beneficiary life-expectancy RMD rules for each lot. Annual Check-In can still stay simple: enter the total current pre-2020 inherited IRA balance for a person, and the app allocates that reset across that person's active lots.", "Callout"),
]
story.append(PageBreak())


story += section("9. Income")
story += [
    p("Income is split into Work / Earned Income and Social Security so the screen is less noisy. If there is no work income, skip the work section and focus on Social Security."),
    info_table(("Field", "Plain-English Meaning"), [
        ("W-2 Gross Wages", "Annual salary before taxes, 401k contributions, and payroll deductions."),
        ("Income-Tax Withholding %", "Optional override for federal/state income tax withheld from wages. Most users can leave it blank and let the model calculate taxes separately."),
        ("Pre-Tax Payroll Deductions", "Optional items taken out before income tax, such as health premiums, FSA, or cafeteria-plan deductions."),
        ("Last W-2 Wage Year", "The last year wages continue. Use 9999 if ongoing."),
        ("Self-Employment / 1099", "Annual consulting or self-employment income."),
        ("Last Self-Employment Year", "The last year self-employment income continues. Use 9999 if ongoing."),
        ("SS Start Age", "The age Social Security starts if the person has not started yet."),
        ("Monthly SS at Start", "The expected monthly Social Security benefit at the start age."),
        ("Current Monthly SS", "Use this only if the person is already receiving Social Security in the plan start year."),
    ]),
    p("Withholding can be confusing because people often know their paycheck amount, not their withholding percent. That is okay. Leave the withholding percent blank unless you are deliberately modeling tax paid during the year.", "GoodCallout"),
]


story += section("10. 401k Defaults")
story += [
    p("This screen is for people still working. It sets global 401k contribution defaults so you do not have to enter them every year."),
    info_table(("Field", "Plain-English Meaning"), [
        ("% Net Pay to Traditional 401k", "Employee contribution to traditional 401k. Traditional contributions usually reduce taxable wages now."),
        ("% Net Pay to Roth 401k", "Employee contribution to Roth 401k. Roth contributions usually do not reduce taxable wages now, but qualified withdrawals can be tax-free later."),
        ("% Employer to Traditional 401k", "Employer match or employer contribution."),
        ("Year Wages End", "When W-2 wages stop. Use 9999 if ongoing."),
        ("Year Self-Employment Ends", "When consulting or 1099 income stops. Use 9999 if ongoing."),
    ]),
    p("If work ends or contributions change in a future year, use Strategy Builder or the advanced Start of Year tools to override the default when needed.", "Callout"),
]


story += section("11. Medicare & IRMAA")
story += [
    p("Medicare has an extra premium charge called IRMAA when income is above certain levels. Medicare usually looks back two years. That means this year's income can affect a future Medicare premium."),
    info_table(("Field", "Plain-English Meaning"), [
        ("IRMAA Target Cap", "A Medicare income level the model can use as a Roth conversion target. In plain words: convert up to this line, but try not to cross it."),
        ("IRMAA Fill Mode", "What to do when income is already near or above the target. Fill to next tier means the model may continue up to another useful line."),
        ("IRMAA Headroom", "A cushion below the line. Example: 4,000 means stop about $4,000 below the target."),
        ("IRMAA Max Bracket", "Optional tax bracket guardrail for Roth conversions. It can stop conversions before they reach a tax bracket you do not want."),
        ("Bracket Headroom", "A cushion below the tax bracket line."),
        ("Medicare MAGI - 2 Years Before Start", "Your Medicare income from two years before the plan starts. This helps estimate first-year Medicare premiums."),
        ("Medicare MAGI - 1 Year Before Start", "Your Medicare income from one year before the plan starts. This helps estimate second-year Medicare premiums."),
    ]),
    p("This section is complicated because it helps with Roth conversion planning. If you are not using Medicare or Roth conversions yet, use reasonable prior MAGI numbers if known and move on. Readiness will remind you if something important is missing.", "WarnCallout"),
]
story.append(PageBreak())


story += section("12. Review and Readiness")
story += [
    p("Review is not another data-entry screen. It is the model checking its homework."),
]
story += bullets([
    "Green means the item looks complete.",
    "Brown or warning-style items mean the app thinks you should review it.",
    "Missing means the model needs that item for a better plan.",
    "Each button should open the most useful screen, such as Open Medicare Interview, Open Income Interview, or Open Inherited Setup.",
])
story += [
    p("When Review looks good enough, go to Dashboard or generate the report. The goal is not perfection. The goal is a plan that is clear enough to discuss and improve.", "GoodCallout"),
]


story += section("13. Annual Check-In")
story += [
    p("The Annual Check-In is how the model stays useful after the first setup. Once a new year starts, enter real information from statements, pay records, or tax documents."),
    simple_steps([
        ("Pick the year", "Choose the year you are updating."),
        ("Update balances", "Enter actual cash, brokerage, IRA/401k, Roth, HSA, and inherited IRA balances if known."),
        ("Update income", "Enter actual wages, self-employment, Social Security, HSA withdrawals, or other year-specific values if they differ from the model's defaults."),
        ("Rerun report", "Generate a fresh report so the action plan reflects reality."),
    ]),
    p("Annual Check-In is like correcting the map after you find out where you actually are. It does not mean the old plan was wrong. It means life moved and the plan should move with it.", "Callout"),
]


story += section("14. Strategy Builder")
story += [
    p("Strategy Builder is for future changes. It writes the same override rows that advanced users can edit directly, but it lets normal users create them without touching tables."),
    info_table(("Strategy Type", "Use It For"), [
        ("Spending Change", "A future spending change, such as a big trip, home project, lower spending after retirement, or a one-year expense."),
        ("Tax Funding / Deferred Tax", "A year-specific tax funding change, such as paying less estimated tax this year and catching up next year."),
        ("Roth Conversion / IRMAA Target", "Testing conversions up to Medicare income targets or tax bracket limits."),
        ("Income Target", "Testing a specific dollar income ceiling."),
        ("Portfolio Return Scenario", "Testing a different investment growth rate for certain years. This is a return scenario, not a prediction."),
        ("Dividend / Interest Rates", "Changing brokerage dividends, dividend reinvestment, or cash interest assumptions for selected years."),
        ("Cash Floor", "Keeping more or less cash available for selected years."),
        ("Funding Order", "Changing whether extra money comes from Securities, IRA, or Roth first for selected years."),
    ]),
    p("Active Strategies shows the current strategy rows in plain language. If you need the raw table, use the link from Active Strategies or turn on Advanced Mode.", "GoodCallout"),
]
story.append(PageBreak())


story += section("15. Advanced Mode")
story += [
    p("Advanced Mode is like opening the machine room. It is useful, but most people should not need it for normal setup."),
    info_table(("Advanced Tab", "What It Is For"), [
        ("Inputs", "Raw global settings. Most of these are now handled by Setup Guide."),
        ("Start of Year", "Raw yearly actuals. Annual Check-In is the simpler path for most updates."),
        ("Override Tables", "Raw strategy rows. Strategy Builder is the simpler path for most future changes."),
        ("Year Detail", "A deep explanation of one year when a result seems surprising."),
        ("Cash Flow", "Detailed year-by-year money movement."),
        ("Tax Summary", "Detailed tax, Medicare, and marginal-rate estimates."),
        ("Tax Tables", "The IRS, state, and Medicare tables used by the model."),
        ("Export", "Backup, restore, and GitHub sync tools."),
    ]),
    p("If Advanced Mode feels intimidating, leave it off. That is exactly why the Setup Guide exists.", "Callout"),
]


story += section("16. A Few Finance Words")
story += [
    info_table(("Term", "Near-Plain Meaning"), [
        ("IRA", "A retirement account where withdrawals are usually taxed."),
        ("Roth IRA", "A retirement account where qualified withdrawals are usually not taxed."),
        ("Roth Conversion", "Moving money from IRA to Roth. You usually pay tax now so that money can grow tax-free later."),
        ("RMD", "Required minimum distribution. Money the rules force you to take from some retirement accounts."),
        ("MAGI", "A special income number. Medicare uses it to decide IRMAA."),
        ("IRMAA", "Extra Medicare premium for higher income."),
        ("Cash Floor", "The cash cushion the model tries to protect."),
        ("Funding Order", "Where the model pulls extra money from when income is not enough."),
        ("Override", "A rule for certain years that replaces the normal default."),
        ("Headroom", "A safety cushion below a limit."),
    ]),
]


story += section("17. Reading the Report")
story += [
    p("The report is meant to be read by humans. It gathers the plan, active strategies, three-year action plan, assumptions, and year-by-year tables."),
]
story += bullets([
    "Start with the summary and three-year action plan.",
    "Check Active Strategies so you remember what future changes are turned on.",
    "Look at funding sources to see where money is coming from.",
    "Look at taxable income, marginal rate, and Medicare/IRMAA together.",
    "If a year looks odd, use Year Detail or Cash Flow in Advanced Mode.",
])
story += [
    p("One strange year is not always a problem. A Roth conversion, inherited IRA deadline, home project, or survivor transition can make one year look unusual on purpose.", "Callout"),
]


story += section("18. Backups")
story += [
    p("Keep backups. Browser storage is convenient, but it is not a permanent filing cabinet."),
]
story += bullets([
    "Export a JSON backup after important changes.",
    "Keep the backup somewhere outside the browser, like iCloud Drive, Dropbox, OneDrive, Google Drive, or an external drive.",
    "Make a new backup after setup, annual check-ins, major strategy changes, tax table updates, and GitHub sync changes.",
    "If the app opens with missing data, import the JSON backup.",
])
story += [
    p("GitHub sync can be helpful later, especially across devices, but JSON backup is still the simple safety net.", "WarnCallout"),
]


story += section("19. Good Habits")
story += bullets([
    "Use Setup Guide first.",
    "Use Readiness when you are not sure what is missing.",
    "Use Annual Check-In once a year.",
    "Use Strategy Builder for future changes.",
    "Use Advanced Mode only when you want to inspect or edit raw details.",
    "Add notes to strategies so Future You remembers why they exist.",
    "Change one big thing at a time when testing scenarios.",
    "Save a backup before and after serious planning sessions.",
])
story += [
    p("Best practical workflow: build a simple baseline, export a backup, add one strategy, generate a report, compare, then keep or remove the strategy. Small clear tests beat one giant mystery scenario.", "GoodCallout"),
    Spacer(1, 0.15 * inch),
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
