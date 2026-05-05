# Jobber accounting codes

Source: live authenticated Jobber expense modal DOM in the attached `user` browser lane.

Field name:
- `expense[accounting_code_id]`

Columns:
- `accountingCodeId` = decoded numeric value
- `EncodedId` = raw DOM option value seen in Jobber

## Core operational codes

| Label | accountingCodeId | EncodedId |
|---|---:|---|
| commissions/marketing costs | 124659 | `MTI0NjU5` |
| equipment rental | 37069 | `MzcwNjk=` |
| fuel expense | 37024 | `MzcwMjQ=` |
| lodging | 37070 | `MzcwNzA=` |
| permits/licenses | 37071 | `MzcwNzE=` |
| subcontractors | 111162 | `MTExMTYy` |
| supplies and materials | 37021 | `MzcwMjE=` |
| W2 LABOR | 584283 | `NTg0Mjgz` |

## Supply-specific codes

| Label | accountingCodeId | EncodedId |
|---|---:|---|
| Supplies: 1K Urethane/ 1part High Enhance/ Medium Sheen - $47.29/gal | 596751 | `NTk2NzUx` |
| Supplies: Acid HF $10/gal | 365957 | `MzY1OTU3` |
| Supplies: Bare Brick, Stone & Masonry Graffiti Remover $22.95/quart or $65/gal | 365958 | `MzY1OTU4` |
| Supplies: Blast Media (Max Strip) $1.02/lb | 579350 | `NTc5MzUw` |
| Supplies: Bleach/Chlorine $9/gal | 365955 | `MzY1OTU1` |
| Supplies: C3 Tunnel Cleaner $75/gal | 365989 | `MzY1OTg5` |
| Supplies: Chlorine $34/Gal | 579338 | `NTc5MzM4` |
| Supplies: Concrete/Paver Color Enhancing Sealer (Sealthane Paver 1 part) $27/gal | 365962 | `MzY1OTYy` |
| Supplies: Dawn dish soap $2.69/ bottle | 384338 | `Mzg0MzM4` |
| Supplies: EC-11 - $156.36/1.5gal | 596754 | `NTk2NzU0` |
| Supplies: EC84 - $152.09/1.5gal | 596756 | `NTk2NzU2` |
| Supplies: Enzone Powder $1/oz | 477858 | `NDc3ODU4` |
| Supplies: F9 BARC Efflorescence 58.85/ GAL. | 388132 | `Mzg4MTMy` |
| Supplies: Glass Cleaner $3.27/can | 482418 | `NDgyNDE4` |
| Supplies: Graffiti Remover $22/bottle | 482416 | `NDgyNDE2` |
| Supplies: Joint Sand $15/bag | 365964 | `MzY1OTY0` |
| Supplies: NUwall - $197.84/pail | 596758 | `NTk2NzU4` |
| Supplies: NuWall Tunnel Cleaner $50/gal | 365990 | `MzY1OTkw` |
| Supplies: Paver Seal Rx/ Enhancer & Sealer (1part Low Enhance/ Low Sheen) $40.53/gal | 600178 | `NjAwMTc4` |
| Supplies: Penetrating Natural (microseal) $1.50/oz Concentrate 6oz per gal | 365960 | `MzY1OTYw` |
| Supplies: Plastic roll 6x10 $54/roll | 482415 | `NDgyNDE1` |
| Supplies: Powdered Degreaser $10/ziplock bag | 365959 | `MzY1OTU5` |
| Supplies: PSR/ Paver Sealer Remover $51.79/gal | 365961 | `MzY1OTYx` |
| Supplies: Rust Remover Acid $15/gal | 365956 | `MzY1OTU2` |
| Supplies: SC10 - $62.19/gal | 596755 | `NTk2NzU1` |
| Supplies: SC-35 - $64.66/gal | 596757 | `NTk2NzU3` |
| Supplies: SC42 - $24/gal | 596752 | `NTk2NzUy` |
| Supplies: SC65 - $134.96/gal | 596753 | `NTk2NzUz` |
| Supplies: Specialty Media (Pool Tile Glass Bead, Walnut Shell) $50/50lb bag or $1/lb | 365966 | `MzY1OTY2` |
| Supplies: Standard Blast Media (Crushed Glass) - $37/100lb bag or .37c/lb | 600202 | `NjAwMjAy` |
| Supplies: Standard Blast Media (Green Diamond) - $23/50lb bag or .23c/lb | 600207 | `NjAwMjA3` |
| Supplies: Standard Blast Media (Kleen Blast,Sand) - $23/100lb bag or .23c/lb | 365965 | `MzY1OTY1` |
| Supplies: Tarbuster $75/gal | 365988 | `MzY1OTg4` |
| Supplies: Topical Concrete/Paver Color Enhancing Sealer (Sealthane WET 2 part) $27/gal | 584577 | `NTg0NTc3` |
| Supplies: Topical Concrete/Paver Matte Sealer/ Natural Paver Sealer (Sealthane Matte 2 part) $26.25/gal | 584576 | `NTg0NTc2` |
| Supplies: Topical Concrete Semi Gloss Sealer (SC42) $25/gal | 365963 | `MzY1OTYz` |
| Supplies: White Tape $4.79/ roll / Blue Tape $4.87 | 482412 | `NDgyNDEy` |
| Supplies: Zep Purple Cleaner $50/bottle | 482417 | `NDgyNDE3` |

## Notes

- This mapping was read from the real Jobber UI DOM, not guessed from schema.
- The public GraphQL schema exposed `accountingCodeId` on write inputs, but did not enumerate these values directly.
- For future expense creation, use the matching `EncodedId` value in the Jobber API mutation path that expects `EncodedId`.
