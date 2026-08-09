# Project Design / Architecture Spec — Evaluation Rubric

Use this rubric to score an existing design or architecture specification. It is derived
from four converging peer-established sources: the ISO/IEC/IEEE 42010:2022 standard for
architecture description, the arc42 template (Starke & Hruschka), Architecture Decision
Records (Nygard; adopted by ThoughtWorks), and ISO/IEC 25010 quality-attribute practice
(SMART non-functional requirements and quality-attribute scenarios).

## How to score

- Score each criterion: **2** = fully met, **1** = partially met, **0** = absent or inadequate.
- Mark a criterion **N/A** only when the tier rule below permits it.
- Compute the tier score as `(sum of applicable points) / (2 × count of applicable criteria)`.
- Treat any Tier-1 criterion scoring 0 as a blocking defect regardless of total score.

## Tiers

- Apply **Tier 1 (Core)** to every spec. Do not mark Tier-1 criteria N/A.
- Apply **Tier 2 (Standard)** to any spec with more than one component, more than one team,
  or an external dependency.
- Apply **Tier 3 (Extended)** to safety-critical, regulated, distributed, or
  long-lived systems, or when a reviewer requests it.

---

## Tier 1 — Core (always required)

### C1. Purpose and scope
- State the problem the system solves in one or two sentences.
- Define what is in scope and what is explicitly out of scope.
- State the document's intended audience.

### C2. Stakeholders and concerns
- List each stakeholder role (e.g. developers, operators, business owner, end users).
- State each stakeholder's primary concern.
- Associate every stated concern with at least one stakeholder.

### C3. Constraints
- List technical constraints (fixed platforms, languages, existing systems).
- List organizational and business constraints (budget, timeline, compliance, team skills).
- State each constraint as a fixed condition, not a design choice.

### C4. System context and boundary
- Identify every external actor, system, and service the system interacts with.
- Define each external interface crossing the system boundary (data in, data out).
- Distinguish the system under design from the external entities.

### C5. High-level solution and structure
- Describe the overall structural approach (major components/modules and their responsibilities).
- State how the major components interact.
- Include at least one diagram showing components and their relationships.

### C6. Key design decisions with rationale
- Record each architecturally significant decision (one affecting structure, dependencies,
  interfaces, or quality attributes).
- For each decision, state: context/forces, the decision, alternatives considered, and consequences (positive and negative).
- State the current status of each decision (proposed, accepted, superseded).

### C7. Quality attributes (non-functional requirements)
- Identify the quality attributes that matter (e.g. performance, availability, security,
  scalability, maintainability), drawn from a recognized taxonomy such as ISO/IEC 25010.
- Express each as a measurable, testable target, not a vague adjective
  (e.g. "p95 latency < 200 ms at 1,000 req/s", not "fast").
- Prioritize the attributes and name any known trade-offs between them.

---

## Tier 2 — Standard (required for multi-component / multi-team / externally-dependent specs)

### C8. Data design
- Describe the primary data entities and their relationships.
- State how data is stored, and its lifecycle (creation, update, retention, deletion).
- Identify sensitive data and any handling requirements.

### C9. Interface and API design
- Define each internal interface between components (contract, inputs, outputs).
- Define each external API or integration point.
- State error and failure behavior for each interface.

### C10. Runtime behavior
- Describe at least the critical runtime scenarios (e.g. main success path, key failure path).
- Show how components collaborate over time for those scenarios (e.g. sequence of interactions).
- Cover error handling and recovery for the critical paths.

### C11. Deployment and infrastructure
- Describe the target runtime environment (hardware, cloud, containers, network).
- Map components to their deployment locations.
- State scaling, configuration, and environment differences (dev/staging/prod).

### C12. Dependencies and assumptions
- List external dependencies (libraries, services, teams) and their versions or SLAs.
- State each assumption the design relies on.
- Identify the impact if an assumption proves false.

### C13. Risks and technical debt
- Identify known risks to delivery or operation.
- State the likelihood/impact and any mitigation for each risk.
- Record known technical debt and any deferred decisions.

---

## Tier 3 — Extended (required for safety-critical, regulated, distributed, or long-lived systems)

### C14. Cross-cutting concepts
- Document recurring approaches applied system-wide (e.g. logging, error handling,
  authentication, i18n, persistence strategy).
- State each concept once and reference it where it applies, avoiding contradiction.

### C15. Security and compliance
- State the threat model or trust boundaries.
- Define authentication, authorization, and data-protection approaches.
- Map requirements to any applicable regulation or standard (e.g. GDPR, PCI DSS, HIPAA, ISO 27001).

### C16. Observability and operations
- Define how the system is monitored (metrics, logs, traces, alerts).
- State health checks, SLOs, and incident-response expectations.
- Describe backup, disaster recovery, and rollback approach.

### C17. Multiple architectural views
- Provide separate views addressing distinct stakeholder concerns
  (e.g. logical, deployment, runtime, data), per ISO/IEC/IEEE 42010.
- Ensure each identified concern is framed by at least one view.
- State correspondences and check consistency across views.

### C18. Evolution and maintainability
- Describe how the architecture is expected to change over time.
- Identify extension points and areas designed for change.
- State versioning and backward-compatibility approach for interfaces.

---

## Cross-cutting quality checks (apply to the whole document, any tier)

### Q1. Consistency
- Ensure terminology is used consistently; define terms in a glossary when non-obvious.
- Ensure diagrams and text agree.
- Ensure no two sections contradict each other.

### Q2. Traceability
- Trace every major design decision back to a driving requirement, constraint, or concern.
- Trace every quality attribute to the component(s) responsible for meeting it.

### Q3. Verifiability
- State every requirement and quality target so that it can be tested or measured.
- Remove or rewrite any unmeasurable adjective ("fast", "secure", "scalable", "user-friendly").

### Q4. Diagrams and visual support
- Include diagrams for structure, and for runtime and deployment where Tier 2+ applies.
- Label diagram elements and keep them consistent with the naming used in text.
- Avoid diagrams that exhaustively list trivial detail; keep them at an appropriate abstraction level.

### Q5. Currency and ownership
- State the document version, date, and owner.
- Note the status of the document (draft, reviewed, approved).
- Keep decisions dated so that superseded ones remain traceable.

---

## Scoring summary template

| Tier | Applicable criteria | Points earned | Max points | % |
|------|--------------------|---------------|-----------|---|
| Tier 1 (Core) | | | | |
| Tier 2 (Standard) | | | | |
| Tier 3 (Extended) | | | | |
| Cross-cutting (Q1–Q5) | | | | |

Blocking defects (any Tier-1 criterion at 0): _list here_
