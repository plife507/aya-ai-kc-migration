# PP Recurring Jobs

This tracker keeps the repeat details for PP recurring jobs so each service date can be posted and expensed consistently.

## Posting Pattern

Use the same field order as one-off PP Slack posts:

```text
Job: <client link|Client> - <job link|Job #0000>
Location: Service address
Sub: Sub name
Type of Service: Service scope (Recurring)
Date of Service: M/D/YYYY
Sale: $X.XX
Sub Pay: $Y.YY
Margin: $Z.ZZ / NN.NN%
Notes: CC checklist: <checklist name>.
```

## Jobs

### Craft Coast Beer & Tacos - Job #19372

- Jobber job: https://secure.getjobber.com/work_orders/134456556
- Jobber client: https://secure.getjobber.com/clients/128225366
- Client: Craft Coast Beer & Tacos
- Scope: MRR/2x-Weekly Power Washing Maintenance & 2x/Month Exterior Trailer Cleaning - RECLAIM REQUIRED
- Location: 1325 Grand Avenue, San Marcos, CA 92078
- Job type: Recurring
- Default sub: Jason
- CompanyCam user: PP - Jason Ednoff / user ID 3470389
- Sale price: $140.00 per visit
- Sub pay: $85.00 per visit
- Margin: $55.00 / 39.29%
- CompanyCam checklist: Ops: PW Comm> General/Misc Jobs / template ID 52548
- CompanyCam project: https://app.companycam.com/projects/97853136
- Expense note pattern: Jason - Recurring <M/D>

#### Known Service Posts

| Service Date | Sub | Sale | Sub Pay | Margin | Jobber Expense | CompanyCam | Slack |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 2026-04-27 | Jason | $140.00 | $85.00 | $55.00 / 39.29% | Expense `18078183` | Existing project `97853136`, fresh checklist `9442431`, assigned `3470389` | `1777307475.746869` |

### Jeved Management - Job #1484

- Jobber job: https://secure.getjobber.com/work_orders/8817983
- Jobber client: https://secure.getjobber.com/clients/13290650
- Client: Jeved Management
- Scope: Weekly Power Wash 7:30am (Trash Area) - Recurring - hard time
- Location: 532 West 1st Street, Claremont, CA 91711
- Job type: Recurring
- Default sub: Efrain / Efrain Jose Worker
- CompanyCam users: PP - Efrain (Jose) / user ID 3941861, plus PP - Efrain Garcia / user ID 3653981 whenever Efrain worker is assigned
- Sale price: $225.00 per visit
- Sub pay: $100.00 per visit
- Margin: $125.00 / 55.56%
- CompanyCam checklist: Ops: PW Comm> General/Misc Jobs / template ID 52548
- CompanyCam project: https://app.companycam.com/projects/21891666
- CompanyCam caution: use the long-running recurring album `21891666`; duplicate album `103991569` was created on 2026-04-27 and has 13 photos, so it needs CompanyCam web merge into `21891666` before archive.
- Expense note pattern: Efrain - Recurring <M/D>

#### Known Service Posts

| Service Date | Sub | Sale | Sub Pay | Margin | Jobber Expense | CompanyCam | Slack |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| 2026-04-27 | Efrain / Efrain Jose Worker | $225.00 | $100.00 | $125.00 / 55.56% | Expense `18073674` | Duplicate project `103991569`, checklist `9435643`, assigned `3941861` and `3653981`; merge into canonical project `21891666` | `1777297508.430449` |
