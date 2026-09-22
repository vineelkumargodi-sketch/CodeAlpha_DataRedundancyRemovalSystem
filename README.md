# Cloud Data Redundancy Removal System

A Flask-based web application developed for **CodeAlpha Cloud Computing Internship — Task 1**.

The system validates incoming records, normalizes data, detects exact duplicates using SHA-256 fingerprints, identifies possible duplicates using similarity analysis, prevents redundant records from being stored, and provides a web dashboard for monitoring records and validation events.

---

## 1. Project Objective

The objective of this project is to build a system that:

- Identifies redundant data and possible duplicate records.
- Validates new data against existing records.
- Prevents duplicate data from being added to the database.
- Stores only unique and verified records.
- Maintains validation and duplicate-attempt logs.
- Provides a dashboard for monitoring the system.

These are aligned with the CodeAlpha Task 1 requirements. :contentReference[oaicite:0]{index=0}
## 2. Key Features

### Data Validation

Incoming records are checked for:

- Required name
- Required email
- Valid email format
- Valid phone number format

Invalid records are rejected and logged.

### Data Normalization

Before duplicate checking:

- Names are converted to lowercase.
- Extra spaces are removed.
- Email addresses are normalized.
- Phone numbers are normalized to digits.

Example:

```text
"  John   Smith  "