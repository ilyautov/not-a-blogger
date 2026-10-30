---
id: agent-unambiguous-csv-columns
title: Name data columns for the agent so they can't be read two ways
section: agent
lang: any
status: proven
evidence: measurement
tools: [Claude Code, CSV]
learn: ../../learn/en/10-working-with-agent.md
added: 2026-10-23
updated: 2026-10-23
contributors: [not-a-blogger]
---

## When
The agent computes from a CSV and writes its own code. A column like `sold_qty` reads as both "ordered" and "bought out". The agent picks the wrong one, subtracts returns twice, and a wrong number goes on screen in large type.

## Do
1. One column name = exactly one quantity: `bought_out_qty`, `revenue_bought_out_rub`, `returns_qty`.
2. Units and period in the name: `_rub`, `_qty`, `_30d`.
3. Next to the CSV, `COLUMNS.md`: one line per column, what it holds and what was subtracted from what.
4. Compute a control number yourself beforehand and compare with the agent's answer before building.

```text
sku,bought_out_qty,revenue_bought_out_rub,unit_cost_rub,returns_qty,commission_rub
```

```bash
python3 -c "import pandas as p; d=p.read_csv('data.csv'); print((d['revenue_bought_out_rub']-d['bought_out_qty']*d['unit_cost_rub']-d['commission_rub']).groupby(d['sku']).sum())"
```

## Verify
Your control number equals the agent's to the unit.

## Don't
- Don't skip the control number after renaming: renaming doesn't fix a wrong formula the agent chose.

## Evidence
With `sold_qty / revenue_rub` columns the agent subtracted returns twice: −51,457 RUB instead of the correct −40,625 RUB for one product per month. Caught before release; the correct value went into the video.

## Related
- [Review the final contact sheet yourself](../qa/qa-contact-sheet-final.md)
