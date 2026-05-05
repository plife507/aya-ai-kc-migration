# KC PP Job Costing Rules

## Purpose

This reference defines how Aya should reason about KC Preferred Partner job costing and how to present it cleanly.

## Canonical fields

- `Sub`: subcontractor / crew display name
- `Job`: client or job title plus visible job number
- `Scope`: short scope label
- `Location`: customer/job address in display form
- `Sale`: the sale basis used for profitability
- `Sub Pay`: confirmed subcontractor payout total
- `Margin`: both percent and dollars

## Multiple subcontractor rule

Some jobs have more than one subcontractor cost line or more than one subcontractor name.

When that happens:
- for the first version, prefer the Jobber line/vendor identity as the subcontractor source of truth
- total all confirmed subcontractor pay into one `Sub Pay`
- do not fake a single subcontractor name
- if only one Jobber line/subcontractor is confirmed, show that name
- if multiple subcontractors are confirmed, prefer:
  - `Sub: Multiple`
  - or a joined label like `Sub: Andres M + WashPros` if the lane allows it

The important thing is that the displayed `Sub` label matches reality and the `Sub Pay` reflects the combined total.

## Sale basis rule

When Nathan asks about margin or profitability, inspect quote-side economics first.

That means:
- start from the quote-side sale amount when available
- include discounts
- do not treat downstream job totals as the only truth if quote economics say otherwise

If the answer instead uses invoiced totals or sheet-derived totals, say that explicitly.

## Margin formula

- `margin_dollars = sale - sub_pay`
- `margin_percent = (margin_dollars / sale) * 100`

Round display values to 2 decimals.

## Display format

Use this exact block shape when Nathan wants the Slack-style costing post:

```text
Sub: Andres M
Job: Shawn Dillion - Job #19198
Scope: Wood Blasting
Location: 4301 Manson Avenue / Los Angeles, California 91364
Sale: $2,375.00
Sub Pay: $850.00
Margin: 64.21% = $1,525.00
```

## Validation posture

When facts are missing or conflicting, call it out directly:

- missing discount information
- no confirmed subcontractor pay
- sheet margin differs from recomputed margin
- quote-side sale differs from invoice-side total

Do not fake a complete costing block from partial evidence.
