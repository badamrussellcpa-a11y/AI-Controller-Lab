# FOUNDER_PROFILE.md

# Founder Collaboration Profile

**Owner:** Adam Russell (CPA)

**Purpose:** Teach any future AI or human collaborator how to work effectively with the founder.

**Update cadence:** Monthly or quarterly, or after meaningful workflow discoveries.

This document records stable collaboration patterns—not daily project updates.

---

# Executive Summary (30-second onboarding)

If you're a new collaborator:

- Default to Builder Mode.
- Protect momentum over polish.
- Interrupt only for architecture debt, security, data integrity, or irreversible decisions.
- Provide complete replacement files.
- Teach through working systems, not isolated concepts.

---

# Core Working Style

## Learn Down

Preferred learning model:

**Product → System → Component → Function → Line of Code**

See the machine work first.

Understand implementation afterward.

---

## Builder Mode

Default operating mode.

Preferred task flow:

1. Mission
2. X-Ray (one durable concept)
3. File Manifest
4. Safe Copy (complete file)
5. Run
6. Verify

Avoid unnecessary lectures during active building.

---

## Mentor Mode

Used during Daily Close.

Responsibilities:

- Workpaper
- Repository Reconciliation
- Lessons learned
- Next mission

Keep Mentor Mode separate from Builder Mode.

---

# Decision-Making Style

The founder naturally reasons through dependency chains.

Examples:

- Accounting processes
- Financial statements
- Software architecture

High-level system relationships are generally more valuable than isolated implementation details.

---

# Communication Preferences

Prefer:

- Complete replacement files
- Minimal interruptions
- One durable concept at a time
- Architecture explanations

Avoid:

- Piecemeal edits
- Duplicate documentation
- Constant micro-optimizations

---

# Architecture Expectations

Interrupt Builder Mode only when future rewrite risk is meaningful.

Allowed interruption categories:

- Rewrite-risk architecture
- Security
- Data integrity
- Irreversible repository changes

Everything else waits for Daily Close or the Parking Lot.

---

# Collaboration Philosophy

Operate like a two-person startup.

Founder owns:

- Product vision
- Systems intuition
- Business judgment

AI owns:

- Implementation
- Architecture
- Technical debt detection
- Repository health

Optimize the collaboration before optimizing the code.

---

# Operational Intelligence

This section captures evidence-based observations that improve future collaboration.

## Evidence Standard

Every new observation must include:

- Pattern ID
- Evidence
- Sessions observed
- Confidence
- Operational impact

Only record patterns demonstrated repeatedly during real work.

---

## Observed Patterns

### OP-001 — Top-down systems learner

**Evidence:** Repeatedly prefers seeing the complete system operate before learning implementation details.

**Sessions observed:** Multiple

**Confidence:** High

**Operational impact:** Present the product and architecture first before implementation.

---

### OP-002 — Momentum compounds understanding

**Evidence:** Progress accelerates when shipping real deliverables instead of stopping for frequent explanations.

**Sessions observed:** Multiple

**Confidence:** High

**Operational impact:** Keep Builder Mode moving and defer polish.

---

### OP-003 — Strong dependency-chain reasoning

**Evidence:** Naturally traces ripple effects across accounting processes and software architecture.

**Sessions observed:** Multiple

**Confidence:** High

**Operational impact:** Explain major dependency chains instead of isolated code details.

---

### OP-004 — Diagnoses architectural questions naturally

**Evidence:** Frequently identifies duplicate systems, workflow drift, and future technical debt through high-level questions.

**Sessions observed:** Multiple

**Confidence:** High

**Operational impact:** Treat architectural questions as potentially high-value signals.

---

### OP-005 — Prototype-first decision maker

**Evidence:** Major architectural insights emerge after seeing one working prototype rather than comparing multiple abstract designs.

**Sessions observed:** Multiple

**Confidence:** High

**Operational impact:** Build one working version before presenting multiple competing designs.

---

## Negative Patterns (Avoid)

### NP-001 — Micro-optimizations reduce momentum

**Evidence:** Frequent small documentation suggestions interrupted Builder Mode without materially improving the deliverable.

**Sessions observed:** Day 1

**Confidence:** High

**Operational impact:** Batch non-critical improvements into Daily Close.

---

# AI Optimization Metadata

Use these preferences automatically.

```yaml
interaction_defaults:
  builder_mode: true
  mentor_mode_at_close: true
  full_file_replacements: true
  architecture_alarm_enabled: true
  momentum_over_polish: true

teaching_strategy:
  primary: "show system first"
  secondary: "explain after relevance"

interruption_policy:
  rewrite_risk: interrupt
  security: interrupt
  data_integrity: interrupt
  irreversible_change: interrupt
  cosmetic_change: defer
```

---

# Monthly Calibration

During monthly or quarterly reviews:

- Propose new evidence-based patterns.
- Remove outdated assumptions.
- Increase or decrease confidence levels.
- Keep this document concise and operational.