# Scheduling System (Clients + Shifts) — effective 07/01/2026

This is a second, independent pipeline added alongside the existing HR
pipeline (employee hire/fire/appraisals). It was kept separate on purpose:

- The HR pipeline owns `Datasets/Dataset1.csv` and is driven by
  `main.py` / `Scripts/simulate_day.py` / `.github/workflows/main.yml`.
- The scheduling pipeline owns `Datasets/Clients.csv` and
  `Datasets/Shifts.csv`, and is driven by `main_shifts.py` /
  `Scripts/simulate_day_shifts.py` / `.github/workflows/main_shifts.yml`.

Neither pipeline writes to the other's files. The only connection between
them is a read-only one: shift generation reads `employee_id` and `status`
("Active") from the employee dataset to know who is eligible to be
scheduled. If the HR system's schema changes in a way that breaks that
contract, only the scheduling pipeline needs fixing — the HR pipeline is
unaffected either way.

## Why a separate system

Three reasons:
1. **Different cadence/ownership.** Hiring/firing and day-to-day scheduling
   are different business processes in a real home care agency, run by
   different teams (HR vs. Scheduling/Staffing coordinators).
2. **Blast radius.** A bug in shift generation should never be able to
   corrupt employee records, and vice versa.
3. **Independent re-runs.** You can regenerate shift history without
   touching employee history, or re-seed employees without wiping out
   accumulated shift history.

## Schema

### Clients.csv

| Column | Description |
|---|---|
| client_id | Primary key |
| first_name, last_name | Client name |
| address, city, state, zip | Service address |
| primary_phone | Contact number |
| payer_type | Private Pay, Medicaid, Medicare, LTC Insurance, VA Benefits |
| care_type | Personal Care, Companion Care, Skilled Nursing, Respite Care, Homemaker Services |
| required_position | The employee position needed for this client's care (CNA, CHHA, LPN, RN, CG) |
| status | Active, Active - On Hold, Discharged - * |
| start_of_care_date | Date client was onboarded |
| end_of_care_date | Date client was discharged (null while active) |
| weekly_authorized_hours | Hours/week this client is authorized for (payer-driven) |
| emergency_contact, emergency_contact_phone | Client emergency contact |

### Shifts.csv

| Column | Description |
|---|---|
| shift_id | Primary key |
| employee_id | Foreign key -> Dataset1.csv `employee_id` |
| client_id | Foreign key -> Clients.csv `client_id` |
| shift_date | Calendar date the shift was scheduled for |
| scheduled_start, scheduled_end | Planned shift window |
| scheduled_hours | Planned shift length |
| clock_in, clock_out | Actual times worked (null unless status = Completed) |
| actual_hours | Hours actually worked (0 for cancellations/no-shows, null while still Scheduled) |
| status | Completed, Cancelled - Client, Cancelled - Employee, No-Show, Scheduled |
| created_at | Date this row was generated (audit trail) |

## Running it

```bash
# One-time: seed history from 07/01/2026 up to today
python backfill_shifts.py --end-date 2026-07-15

# Going forward: run once per day (this is what the GH Action calls)
python main_shifts.py
```

`main_shifts.py` refuses to generate shifts for any date before
2026-07-01, so it's safe to enable the GitHub Action ahead of the
go-live date without producing premature data.
