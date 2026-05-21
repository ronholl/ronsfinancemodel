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


OUT = "/Users/ronholl/Documents/Apps/Ron_Finance_Model/Deployed Versions/Version 1.4/rons_retirement_guide.pdf"

GOLD = colors.HexColor("#8a6800")
DARK = colors.HexColor("#1a1208")
CREAM = colors.HexColor("#faf7ef")
LINE = colors.HexColor("#d4a843")
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
    out = []
    for item in items:
        out.append(p("• " + item))
    return out


def section(title):
    return [p(title, "H1x")]


def two_col(rows, widths=(2.1 * inch, 4.8 * inch)):
    data = [[p(f"<b>{a}</b>"), p(b)] for a, b in rows]
    t = Table(data, colWidths=list(widths), hAlign="LEFT")
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#ddd3bd")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2ead8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def override_table(rows):
    data = [[p("Override", "TableHead"), p("Use it for", "TableHead")]]
    data.extend([[p(f"<b>{a}</b>"), p(b)] for a, b in rows])
    t = Table(data, colWidths=[2.15 * inch, 4.75 * inch], hAlign="LEFT", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#ddd3bd")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5efe1")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def info_table(headers, rows, widths=(2.0 * inch, 4.9 * inch)):
    data = [[p(headers[0], "TableHead"), p(headers[1], "TableHead")]]
    data.extend([[p(f"<b>{a}</b>"), p(b)] for a, b in rows])
    t = Table(data, colWidths=list(widths), hAlign="LEFT", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#ddd3bd")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5efe1")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
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
story += [
    Spacer(1, 0.45 * inch),
    p("Ron’s Retirement Finance Model V1", "GuideTitle"),
    p("Plain-English User Guide", "GuideSub"),
    p("This guide explains what the model is doing, which screens matter most, how to protect your data, and how to use Roth conversion, IRMAA, survivor-mode, and override controls without needing to be a tax expert.", "Callout"),
    p("Important: this model is a planning tool. It estimates future balances, taxes, Medicare costs, and income. It is not tax, legal, investment, or Medicare advice. Review major decisions with a qualified professional.", "Smallx"),
    info_table(("Term", "Plain-English Meaning"), [
        ("IRA", "A retirement account where withdrawals are usually taxable."),
        ("Roth IRA", "A retirement account where qualified withdrawals are usually tax-free."),
        ("Roth conversion", "Moving money from IRA to Roth. You pay tax now so the money can grow tax-free later."),
        ("Inherited IRA", "An IRA inherited from someone else. The model separates older pre-2020 inherited IRAs from post-2020 lots because the distribution rules are different."),
        ("RMD", "Required minimum distribution. This is money the tax rules require you to withdraw from certain retirement accounts."),
        ("MAGI", "Income number used by Medicare for IRMAA. For this model, think Medicare income."),
        ("IRMAA", "Extra Medicare premium charged when income is above certain thresholds."),
        ("Headroom", "A cushion. Example: stop $5,000 below a limit instead of exactly at it."),
        ("Override", "A year-range instruction that changes one assumption without changing the global default."),
    ]),
]
story.append(PageBreak())

story += section("1. Data Storage and Backups")
story += [
    p("This is the most important housekeeping rule in the model: keep your own backup file. The app may save data automatically, but automatic browser storage is not the same as a permanent backup.", "Callout"),
    p("By default, the model saves your information in the browser you are using. That is convenient, but it can disappear. Browser data may be cleared by a system cleanup tool, browser settings, privacy settings, an update, a different device, or opening a different copy of the app file."),
    p("If that happens, the app may open later with no data even though everything looked saved last time."),
    p("What to do:", "H2x"),
]
story += bullets([
    "Use the <b>Export</b> tab to download a JSON backup file after meaningful changes.",
    "Keep that JSON backup somewhere safe, such as iCloud Drive, Dropbox, Google Drive, OneDrive, an external drive, or another folder you routinely back up.",
    "Make a new backup after major changes: new balances, new overrides, tax table updates, Social Security changes, survivor-mode changes, or GitHub setup changes.",
    "If the app ever opens with missing data, use <b>Import JSON Backup</b> from the Export tab to restore your saved file.",
])
story += [
    p("GitHub sync is helpful, but it does not remove the need for backups. GitHub gives the model another place to save and load data, especially across devices. Still export JSON backups regularly.", "Callout"),
    p("The backup file includes the model data and GitHub setup information, so it is the safest way to move or recover a complete setup. If browser storage is lost, the GitHub login/token setup may also be lost; the exported JSON is your portable recovery copy."),
    p("Simple habit: after every serious planning session, click <b>Export Backup</b>. Treat the JSON file like the master copy of your work."),
]

story += section("2. What the Model Does")
story += [
    p("The model projects retirement year by year. It estimates money coming in, money going out, taxes, Medicare premiums, account balances, Roth conversions, and net worth."),
    p("Each year follows the same basic order:"),
]
story += bullets([
    "Start with the account balances and assumptions for that year.",
    "Apply the year’s growth model to most investment balances, while tracking taxable dividends and interest separately.",
    "Add income that arrives automatically, such as wages, Social Security, RMDs, dividends, interest, HSA withdrawals, and inherited IRA draws.",
    "Pay spending and taxes using the draw order built into the model.",
    "Apply optional Roth conversion strategies from the Override Tables.",
    "Carry the ending balances into the next year.",
])
story += [
    p("The model is most useful when you compare scenarios: different Roth conversion plans, different Social Security ages, different spending levels, different survivor assumptions, or different tax assumptions.", "Callout"),
]
story.append(PageBreak())

story += [
    KeepTogether([
        p("Main Tabs", "H2x"),
        info_table(("Tab", "What it is for"), [
            ("Dashboard", "Quick view of net worth, three-year action plan, and big-picture results."),
            ("Inputs", "Long-term assumptions: people, dates, rates, Social Security, Medicare, survivor mode, and starting settings."),
            ("Start of Year", "Enter real yearly values as life happens. Entered values replace model-derived values for that year."),
            ("Override Tables", "Temporary or planned changes for certain years, including Roth conversion strategies and new rate overrides."),
            ("Year Detail", "A single-year explanation when a result looks surprising."),
            ("Cash Flow", "Detailed year-by-year money movement."),
            ("Tax Summary", "Federal tax, state tax, Medicare/IRMAA, and marginal tax rates."),
            ("Tax Tables", "The IRS/Medicare tables used by the model. Update yearly when new tables are published."),
            ("Export", "Backup, restore, and GitHub sync setup."),
        ]),
    ])
]

story += section("3. First Setup")
story += [
    p("Begin with the Inputs tab. The goal is not perfection. The goal is to give the model enough information to create a useful first projection."),
]
story += bullets([
    "Enter names, birth years, filing status, state, and plan years.",
    "Enter growth, dividend, interest, dividend reinvestment, spending inflation, Social Security COLA, wage growth, stock-gain, and cash-floor assumptions.",
    "Enter Social Security start age and monthly benefit for each person.",
    "Enter Medicare/IRMAA settings if you want the model to plan around Medicare income tiers.",
    "Enter inherited IRA information if the plan includes inherited retirement accounts. Use the pre-2020 section for older inherited IRAs and the post-2020 lot section for 10-year-rule inherited IRAs.",
    "Enter survivor-mode assumptions if you want to model one spouse surviving the other.",
    "Enter 401(k) contribution and employer match assumptions if still working.",
])
story += [
    p("Then go to Start of Year and enter actual starting balances. These are the balances the projection grows from: cash, securities/brokerage, IRA, Roth, HSA, and inherited IRA if any."),
    p("Tip: update Start of Year once per year with real values. That keeps the long-term projection anchored to reality instead of drifting farther from your actual life.", "Callout"),
]

story += section("4. How Money Is Drawn")
story += [
    p("The model first uses income that arrives whether you need it or not: wages, Social Security, RMDs, dividends, interest, HSA withdrawals, and inherited IRA draws."),
    p("If that income is not enough to cover spending and taxes, the model draws more money from accounts in this order:"),
]
story += bullets([
    "Cash, down to your cash floor.",
    "Securities/brokerage account.",
    "Traditional IRA or 401(k), which is taxable when withdrawn.",
    "The remaining account buckets in the selected funding order: Securities, traditional IRA, and Roth IRA. The default is Securities, then IRA, then Roth.",
])
story += [
    p("Cash stays outside the funding-order setting. If you want the model to preserve more cash, raise the Cash Floor. After cash above the floor is used, the Default Funding Order controls whether Securities, IRA, or Roth is drawn first, second, and third. This can also be overridden by year range.", "Callout"),
    p("Pre-2020 inherited IRA has its own funding setting. It can be set to RMDs only, used before regular IRA, or used after regular IRA. That setting only controls where inherited IRA sits inside the IRA-side funding path."),
]

story += section("5. Account Flow Timing")
story += [
    p("The model is year-based, so it has to decide whether growth happens before or after deposits and withdrawals. These rules are useful when checking the Cash Flow and Year Detail screens."),
    info_table(("Account", "How the Year Is Modeled"), [
        ("Brokerage / Securities", "Starts with the start-of-year balance. Total return is split between price growth and dividends. The dividend reinvest percentage controls how much of the dividend is reinvested versus paid out as taxable cash flow. Securities draws reduce the account; excess funding and cash sweeps can add to it."),
        ("Cash", "Starts with the start-of-year cash balance. Wages, Social Security, dividends not reinvested, interest, RMDs, IRA draws, inherited IRA draws, HSA withdrawals, Roth withdrawals, and securities sales can add cash. Spending, taxes, Medicare costs, and cash sweeps reduce it. The cash floor controls how much cash the model tries to preserve."),
        ("Traditional IRA / 401(k)", "Growth is applied to the starting balance. Then RMDs, extra IRA draws, and Roth conversions reduce the account. Traditional 401(k) employee and employer contributions can add to it when wages are active."),
        ("Roth IRA / Roth 401(k)", "Growth is applied to the starting balance. Roth conversions and Roth 401(k) contributions add to it. Roth withdrawals reduce it."),
        ("HSA", "Growth is applied to the starting balance, then HSA deposits are added and HSA withdrawals are subtracted."),
        ("Pre-2020 inherited IRA", "RMDs are calculated from the start-of-year inherited IRA balance. Required inherited IRA RMDs and optional funding draws are then subtracted, and growth is applied to the remaining balance. Start of Year entries can reset the balance later."),
        ("Post-2020 inherited IRA lots", "Each lot is tracked separately. Required RMD, optional draw strategy, and the final 10-year deadline draw are calculated from the lot balance for that year, then withdrawals are subtracted and growth is applied to the remaining balance."),
    ]),
    p("Because these timing rules differ by account, two balances with the same beginning value and growth rate can end the year differently when one has deposits or withdrawals during the year.", "Callout"),
]
story.append(PageBreak())

story += section("6. Inputs That Can Be Overridden")
story += [
    p("Several Inputs fields are global defaults but can be overridden by year range. The bold note under those fields is meant to make that flexibility visible."),
    override_table([
        ("Portfolio Growth Rate", "Override by year range to model a down-market period, a conservative early-retirement sequence, or a different long-term return assumption."),
        ("Brokerage Dividend Rate, Dividend Reinvest, and Cash Interest Rate", "These share one override row. Enter any combination. Brokerage dividend rate affects taxable brokerage dividends; Dividend Reinvest controls what percentage is reinvested versus paid to cash; Cash Interest Rate affects taxable cash interest."),
        ("Annual Spending Increase", "Can be adjusted with the Spending override percentage-change field for a year range."),
        ("Wage Growth", "Can be overridden by year range for career stages, part-time periods, or salary assumptions."),
        ("Stock Sales Taxable Gain", "Override the percentage of securities sales treated as taxable gain. Useful when basis assumptions change over time."),
        ("Cash Floor", "Override the minimum cash balance to maintain for a year range."),
        ("Default Funding Order", "Choose the global draw order for Securities, IRA, and Roth. Cash remains controlled separately by Cash Floor."),
        ("IRMAA Target Cap", "Can be overridden in Roth Conversion Strategy for years with different Medicare income targets."),
        ("IRMAA Fill Mode", "Controls what happens when income is already above the selected IRMAA target: add no extra fill, fill toward the next tier, or use Roth withdrawals instead of taxable draws."),
        ("IRMAA Max Bracket and Bracket Headroom", "Global defaults can be set in Inputs and overridden by year range in Roth Conversion Strategy."),
    ]),
]

story += section("7. Override Tables and Year Ranges")
story += [
    p("Overrides let you change behavior for selected years without changing global assumptions. Overlapping rows are layered: for each field, the later nonblank value wins. Blank cells inherit from an earlier matching row, and then from the global Inputs default if no override row supplies that field.", "Callout"),
    override_table([
        ("Spending", "Override annual spending amount, percentage change, tax funding dollars, and notes. Spending amount resets the spending base unless 1 Year Only is selected; percentage change adjusts the inflation-based amount."),
        ("Deductions", "Test itemized deductions, charity, or tax changes."),
        ("IRMAA Level Target", "Manage Roth conversions around Medicare income tiers, fill mode, and optional tax bracket caps."),
        ("Income Level Target", "Use a specific dollar MAGI ceiling. It has priority over IRMAA and Tax Bracket Fill."),
        ("Tax Bracket Fill", "Fill the current federal tax bracket."),
        ("Growth / Wage Growth", "Change market return or wage growth for selected years."),
        ("Income Rates", "Combined brokerage dividend rate, dividend reinvest percentage, and cash interest rate override."),
        ("Stock Sales Taxable Gain", "Change the taxable-gain percentage used for securities sales."),
        ("Cash Floor / HSA / State / Funding Order", "Change cash reserve targets, HSA deposits, state tax assumption, or the Securities / IRA / Roth draw order."),
    ]),
]
story.append(PageBreak())

story += section("8. Roth Conversions in Plain English")
story += [
    p("A Roth conversion moves money from a traditional IRA into a Roth IRA. The conversion increases taxable income in the year it happens. The benefit is that the money may grow tax-free afterward and may reduce future required IRA withdrawals."),
    p("A conversion is not automatically good or bad. It depends on tax brackets, Medicare IRMAA, future RMDs, survivor taxes, and how long the money may stay invested."),
    p("The model lets you create conversion rules for specific years in the Override Tables tab. You can use three main approaches:"),
    info_table(("Strategy", "Plain-English Use"), [
        ("IRMAA Level Target", "Convert up to a Medicare income tier, while optionally avoiding a high tax bracket."),
        ("Tax Bracket Fill", "Convert enough to fill the tax bracket your income is already in."),
        ("Income Level Override", "Convert up to a specific dollar income target you choose."),
    ]),
    p("Priority rule: if more than one conversion strategy applies to the same year, Income Level wins first, then IRMAA / Max Bracket, then Tax Bracket Fill.", "Callout"),
    p("Conversions add taxable income now. The model shows the result in Cash Flow and Tax Summary so you can see both the conversion amount and the tax/Medicare effect."),
]

story += section("9. IRMAA and Max Bracket Override")
story += [
    p("IRMAA is an extra Medicare premium charged when Medicare income is above certain thresholds. In the model, the IRMAA Level Target is a way to say: Convert IRA money to Roth, but try not to cross this Medicare income line."),
    p("The Max Bracket option adds a second guardrail. It lets you say: I am willing to go up to this IRMAA level, but do not push me into a higher federal tax bracket than I choose."),
    info_table(("Control", "What It Means"), [
        ("IRMAA Target Cap", "The Medicare income tier ceiling you are willing to target. Off disables IRMAA targeting unless Max Bracket is selected. Level 0 means the base tier, Level 1 means Tier 1, up through Level 4 for Tier 4."),
        ("Fill Mode", "Blank means no extra fill when income is already above the target. Fill mode can use conversions to fill toward the next tier. Roth-withdrawal mode can use Roth withdrawals instead of taxable draws above the target."),
        ("Max Bracket", "Optional tax bracket ceiling. If selected, conversions stop at that bracket target when it is lower than the IRMAA target."),
        ("Bracket HR ($)", "Extra cushion below the Max Bracket target. Example: $5,000 stops $5,000 below the bracket target."),
    ]),
]
story += bullets([
    "If IRMAA Target Cap is Off and Max Bracket is blank, the row is off.",
    "If IRMAA Target Cap is Off and Max Bracket is selected, the row becomes a bracket-only conversion target.",
    "If IRMAA Target Cap is Level 0-4 and Max Bracket is blank, the model targets the selected IRMAA threshold.",
    "If IRMAA Target Cap is Level 0-4 and Max Bracket is selected, the model uses whichever target is lower: the IRMAA threshold or the bracket target.",
])
story += [
    p("The Max Bracket dropdown only shows bracket choices that can actually affect the selected IRMAA level. The No cap choice shows the uncapped IRMAA target and the tax bracket it lands in, so you can compare before choosing.", "Callout"),
]
story.append(PageBreak())

story += section("10. Simple Conversion Examples")
story += [
    p("These examples are simplified, but they show how to think about the controls."),
    info_table(("Goal", "Override Row"), [
        ("Convert up to an IRMAA tier and do not care which tax bracket it reaches.", "Choose an IRMAA Level and leave Max Bracket as No cap."),
        ("Target a high IRMAA level but avoid a painful tax bracket.", "Choose the IRMAA Level, then choose a Max Bracket such as 24% or 32%."),
        ("Do not target IRMAA; just fill a tax bracket.", "Choose IRMAA Target Cap Off and select a Max Bracket. Add Bracket HR if you want cushion."),
        ("Stay slightly below a bracket line.", "Select Max Bracket and enter Bracket HR, such as 5,000."),
        ("Use an exact income number instead of IRMAA/bracket logic.", "Use Income Level Override. It has priority over IRMAA and Tax Bracket Fill."),
    ]),
    p("Example: if IRMAA Level 5 would allow income up to a high Medicare threshold but also push you into a 35% marginal bracket, choose Level 5 plus Max Bracket 24% or 32%. The model will convert only up to the lower bracket target."),
    p("Example: if you choose IRMAA Target Cap Off and Max Bracket 24%, the model is not using IRMAA at all. It is simply trying to convert up to the 24% bracket target, less Bracket HR."),
]

story += section("11. Survivor Mode")
story += [
    p("Survivor mode models one spouse dying while the survivor keeps retirement balances. It can also end the deceased spouse’s Social Security, replace the survivor’s Social Security with the higher benefit, and switch the survivor to Single filing starting the year after death."),
    info_table(("Control", "What It Means"), [
        ("Scenario", "Choose which spouse survives, or leave survivor mode off."),
        ("Death Year", "The death year remains under the base filing setup. Changes begin the following year."),
        ("End deceased spouse Social Security", "Stops that benefit starting the year after death."),
        ("Survivor receives higher benefit", "Uses the higher Social Security benefit for the survivor when selected."),
        ("Switch survivor to Single filing", "Starting the year after death, federal and CA brackets, standard deductions, taxable Social Security, Medicare/IRMAA count, and senior deductions use Single."),
        ("Survivor Spending Adjustment", "Adjusts projected spending starting the year after death. Default is 0%. Use negative values for lower spending and positive values for higher spending. Explicit Spending override rows still take priority."),
    ]),
    p("Review survivor years carefully. Filing status, tax brackets, Social Security, Medicare/IRMAA, and spending can all change after one spouse dies.", "Callout"),
]
story.append(PageBreak())

story += section("12. Inherited IRAs")
story += [
    p("Inherited IRAs are modeled separately because the rules are different depending on when the account was inherited. The model supports both pre-2020 inherited IRA RMDs and post-2020 inherited IRA lots."),
    info_table(("Type", "How to Enter It"), [
        ("Pre-2020 inherited IRA", "Use the Inputs tab section named Pre-2020 Inherited IRA RMD. Enter the initial inherited IRA balance, optional balance start year, deceased owner birth year, and deceased owner death year for the applicable person. Start of Year can update the balance later."),
        ("Post-2020 inherited IRA", "Use the Post-2020 Inherited IRA Lots section. Enter one row per inherited IRA lot with beneficiary, balance, active year, deceased owner birth year, death year, and optional draw strategy."),
        ("Start of Year updates", "Use Start of Year when you have a real annual balance. Pre-2020 inherited IRA balances are person-specific. Post-2020 inherited IRA has a total reset that is allocated across active lots proportionally."),
    ]),
    p("For pre-2020 inherited IRAs, the model uses the deceased owner birth/death years to determine whether inherited IRA RMDs are required, then uses the beneficiary’s life-expectancy schedule for the divisor. In survivor mode, any remaining pre-2020 inherited IRA balance carries to the survivor and the inherited IRA RMDs continue from the inherited IRA settings."),
    p("For post-2020 inherited IRA lots, the death year sets the 10-year deadline. If the deceased owner had reached RMD age, the model calculates required inherited IRA RMDs before the deadline. Optional draw strategies can take more than the required amount, and the final deadline year drains the remaining lot balance.", "Callout"),
]

story += section("13. Reading the Results")
story += bullets([
    "<b>Dashboard:</b> check the three-year action plan and overall net worth path.",
    "<b>Year Detail:</b> use this when a year looks strange and you want to see what drove it.",
    "<b>Cash Flow:</b> look for Roth conversion amount, IRA draws, inherited IRA draws, Roth withdrawals, spending, taxes, cash sweeps, and securities investments.",
    "<b>Tax Summary:</b> check AGI, taxable income, marginal rate, Medicare Part B, and IRMAA surcharge.",
    "<b>Report:</b> print the readable plan with summary, assumptions, active overrides, action plan, discussion questions, and year-by-year cash-flow tables.",
])
story += [
    p("A larger Roth conversion can look bad in one year because tax rises, but still help long-term if it reduces later RMDs or survivor taxes. Always compare scenarios, not just one year.", "Callout"),
]

story += section("14. Printed Report")
story += bullets([
    "Use the browser’s normal print command to print or save as PDF.",
    "The report includes active override rows and notes so assumptions can be reviewed later.",
    "The year-by-year section is split into larger tables for practical review.",
    "For Safari, the app uses a direct print-ready page flow to avoid blank PDF behavior seen with generated blob PDFs.",
    "Page numbers are included in the printed report.",
])

story += section("15. Updating Tax Tables")
story += [
    p("The Tax Tables tab stores federal brackets, standard deductions, state tax values, Medicare IRMAA thresholds, and Medicare premium amounts. The model can inflate values into future years, but actual IRS and Medicare numbers change over time."),
]
story += bullets([
    "Each year, add the newest tax year when official numbers are available.",
    "Use IRS sources for federal brackets and CMS/Medicare sources for IRMAA and Part B premiums.",
    "Keep old years because they are useful for historical calculations and comparisons.",
])
story += [
    p("If you are not sure whether a table is current, treat the results as a planning estimate and avoid making precise tax decisions from it.", "Callout"),
]

story += section("16. Good Habits")
story += bullets([
    "Export a JSON backup after major changes, and keep it somewhere outside the browser.",
    "Use notes in override rows so Future You knows why a change was made.",
    "Compare one change at a time when testing strategies.",
    "Watch marginal tax rate and IRMAA surcharge together. A year can look fine for income tax but expensive after Medicare costs.",
    "Review survivor years carefully.",
    "Print or save the report after meaningful scenario changes.",
])
story += [
    p("Best practical workflow: make a baseline, export it, add one strategy, compare, then keep or undo it. Small careful tests beat one giant mystery scenario.", "Callout"),
    Spacer(1, 0.15 * inch),
    p("© 2026 Ronald Hollander · Licensed CC BY-NC 4.0 · This guide is informational and is not financial, tax, legal, or investment advice.", "Smallx"),
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
