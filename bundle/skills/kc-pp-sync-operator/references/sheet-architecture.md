# KC PP Sync — Sheet Architecture

## Primary spreadsheet

Spreadsheet ID:
- `1p4lxIUjWFYNDp6ptqSMwyRcdle5Hcv5UMC6TdpZE99Q`

## Tab families

Main tab groups:
- **One-off (new)**, for newer month tabs like `March` and `April`
- **One-off (legacy)**, for older month tabs like `February`
- **Recurring**, for tabs like `April - R`
- **GTP $**, for payout/output tabs like `April - GTP $`
- **Dashboard**, for payment and profitability summary
- **⚡ Command** and `Log`, for sync visibility and operational evidence

Do not assume exact business meaning from the tab name alone when the tab can be read directly.

## Layout differences that matter

### New one-off layout

Used for newer month tabs.

Key traits:
- has `Margin %`
- has `# of Invoices`, `Total Invoiced`, and `All Paid?`
- has a 5-slot invoice tracker block (`Inv #1` through `Inv #5` with amount and paid flags)
- includes manual finance columns and `Auto Notes`

### Legacy one-off layout

Used for older tabs like `February`.

Key traits:
- has `Margin %`
- uses older single-invoice style columns like `Invoice Number`, `Jobber Invoice Total Amount`, `Invoice Issued Date`, and `Jobber Invoice Status`
- still includes HeyPros invoice, sub invoice, release amount, payment, and notes fields
- does not use the newer 5-slot invoice tracker block

### Recurring layout

Used for tabs like `March - R` and `April - R`.

Critical warning:
- recurring tabs do **not** have `Margin %` in column C
- recurring columns are offset relative to one-off tabs
- recurring tabs require their own mental model; do not treat them like normal month tabs

Repo-doc callouts:
- recurring tabs are handled differently in code
- manual fields include columns like A, F, and L in operations

### GTP $ tabs

Use as Good To Pay outputs.

Key traits:
- generated output tab per month
- merges one-off and recurring data
- reporting/output surface, not the main operational edit surface

### Dashboard

Use for reporting summary.

Key traits:
- payment-status aggregates
- profitability metrics from February onward
- weighted average margin is surfaced here and reused elsewhere

### ⚡ Command / Log

Use for sync evidence.

Key traits:
- sync results appended every run
- useful for tracing what mode ran and whether a sync succeeded

## Margin behavior

Per-row margin is computed as:
- `(Total Invoiced − all Sub Invoice Amounts for the same Job #) / Total Invoiced`

Important rules:
- multi-contractor jobs show the same combined margin across rows for the same Job #
- margin is gated by payment status
- unpaid / uninvoiced / hybrid states may leave margin blank
- recurring tabs do not carry the margin column

## Safe reading posture

When working with the sheet:
- read headers before claims
- inspect example rows before assuming column meaning
- do not compare recurring and one-off tabs column-for-column without adjusting for layout differences
- when a value looks wrong, consider whether it is generated output before proposing a manual sheet fix
