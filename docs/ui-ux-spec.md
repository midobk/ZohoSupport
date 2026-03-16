# Support Assistant UI/UX Specification

## 1) Screen Inventory

| Screen | Primary user goal | Primary actions | Trust + source behavior |
|---|---|---|---|
| Ask Mode (default) | Ask a support question and get immediate grounded guidance | Ask question, refine question, copy answer, open sources, escalate to live call | Source rail always visible; **Official Sources** pinned above **Similar Historical Tickets** |
| Live Call Assist Mode | Get real-time suggestions while on a customer call | Start/stop listening, pin suggested responses, mark action items, open references fast | Confidence + recency badges shown on each suggestion; source chips are mandatory |
| Similar Tickets Mode | Find prior incidents and reuse proven resolutions | Search/filter by product, severity, status, date; compare tickets; apply resolution snippet | Ticket similarity score separated from source authority; clear “historical pattern only” messaging |
| Settings / Admin | Configure governance, data scope, roles, and integrations | Manage connectors, source priority, confidence thresholds, audit settings, role permissions | Global trust policy controls; visual indicators for approved connectors and sync health |
| Embedded Widget (Desk/CRM) | Provide quick in-context assist without leaving host tool | Ask, summarize case, fetch similar tickets, insert response into host record | Compact source drawer with two tabs: Official vs Similar Tickets |

---

## 2) Annotated Wireframes (Markdown)

> Notes:
> - Desktop-first layout uses 12-column grid.
> - Mobile collapses right rail to bottom sheet, preserving source visibility.
> - Trust cues are shown in header and per-answer cards.

### 2.1 Ask Mode (Desktop)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ [Logo] Support Assistant                       [Workspace] [User/Admin Menu] │
├──────────────────────────────────────────────────────────────────────────────┤
│ Left Nav (fixed)     │ Main Ask Panel (8 cols)      │ Sources Rail (3 cols)│
│ - Ask (active)       │ ┌──────────────────────────┐  │ ┌───────────────────┐ │
│ - Live Call Assist   │ │ “Ask anything…” input    │  │ │ OFFICIAL SOURCES  │ │
│ - Similar Tickets    │ │ [Attach Context] [Ask]   │  │ │ 1) KB-3421        │ │
│ - Analytics (opt.)   │ └──────────────────────────┘  │ │ 2) API Docs v2    │ │
│ - Settings/Admin     │ ┌──────────────────────────┐  │ ├───────────────────┤ │
│                      │ │ Answer card              │  │ │ SIMILAR TICKETS   │ │
│                      │ │ Confidence: High (92%)   │  │ │ #88321 (82% sim)  │ │
│                      │ │ Trust badges: Verified   │  │ │ #87100 (77% sim)  │ │
│                      │ │ [Copy] [Use Draft]       │  │ └───────────────────┘ │
│                      │ └──────────────────────────┘  │ Always visible        │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Annotations**
1. Keep a single primary CTA: **Ask**.
2. Source rail is sticky and never hidden on desktop.
3. Official sources are listed first, with shield icon + freshness timestamp.
4. Similar tickets include similarity score + outcome label (Resolved/Unresolved).
5. Confidence is numeric + label (High/Medium/Low) with tooltip.

---

### 2.2 Live Call Assist Mode

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Live Call Assist                         Status: ● Listening   [Pause] [End] │
├──────────────────────────────────────────────────────────────────────────────┤
│ Real-time Transcript (left 7 cols)      │ Suggested Responses (right 5 cols)│
│ - Customer: “We see timeout on sync…”   │ ┌ Suggestion A (High 90%) ───────┐ │
│ - Agent: “Checking known fixes…”        │ │ [Pin] [Insert] [View Sources]  │ │
│                                         │ └─────────────────────────────────┘ │
│                                         │ ┌ Suggestion B (Medium 71%) ─────┐ │
│                                         │ │ [Pin] [Insert] [View Sources]  │ │
│                                         │ └─────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────┤
│ Action Bar: [Create Follow-up Task] [Email Summary] [Open Similar Tickets] │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Annotations**
1. Transcript and suggestions shown side-by-side for low cognitive switching.
2. Every suggestion requires source links before Insert is enabled (trust gate).
3. “Listening” indicator and privacy notice are persistent.
4. Pinned suggestions remain available after call ends.

---

### 2.3 Similar Tickets Mode

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Similar Tickets                                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│ Filters: [Product▼] [Severity▼] [Date Range▼] [Status▼] [Apply] [Reset]     │
├──────────────────────────────────────────────────────────────────────────────┤
│ Results List (left 5 cols)               │ Ticket Detail & Reuse (right 7)  │
│ #88321  82% similar  Resolved            │ Root cause summary                │
│ #87100  77% similar  Resolved            │ Steps that worked                 │
│ #86011  68% similar  Partial             │ [Insert internal note]            │
│                                           │ [Use customer-safe response]      │
│                                           │ Source type: Historical ticket    │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Annotations**
1. Similarity score and resolution state are always paired.
2. Clear label: “Historical ticket insight (not official policy).”
3. One-click reuse actions to minimize clicks.

---

### 2.4 Settings / Admin Page

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Settings / Admin                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ Tabs: [Data Sources] [Trust Policy] [Roles] [Audit] [Integrations]           │
├──────────────────────────────────────────────────────────────────────────────┤
│ Data Sources                                                                   │
│ - Official KB Connector    Connected ●   Last sync: 5m ago   [Configure]     │
│ - Product Docs Connector   Warning ▲      Last sync: 2d ago   [Fix]           │
│ - Ticket Archive           Connected ●    [Priority: 2]       [Configure]     │
├──────────────────────────────────────────────────────────────────────────────┤
│ Trust Policy                                                                    │
│ - Minimum confidence to auto-suggest: [75]                                    │
│ - Require official source for customer-facing drafts: [ON]                    │
│ - Show low-confidence warning banner: [ON]                                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Annotations**
1. Emphasize governance and freshness with health states.
2. Source ranking is configurable and transparent.
3. Auditability controls are first-class for enterprise trust.

---

### 2.5 Embedded Widget (Desk/CRM)

```text
┌─────────────────────────────── Host App Case Panel ──────────────────────────┐
│ Customer Case #12903                                                         │
│ ┌──────────────────────── Support Assistant Widget ─────────────────────────┐ │
│ │ Ask about this case…                                      [Ask]          │ │
│ │ Quick actions: [Summarize Case] [Draft Reply] [Find Similar]             │ │
│ │ -----------------------------------------------------------------------  │ │
│ │ Answer snippet... [Insert into Reply] [Copy]                             │ │
│ │ Sources: [Official (2)] [Similar Tickets (3)]                            │ │
│ └───────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
```

**Annotations**
1. Compact, context-aware, and low-click for existing workflows.
2. Source tabs persist inside widget to maintain trust transparency.
3. “Insert into Reply” uses host-native action pattern.

---

## 3) Component List

### Global
- App shell (header, left nav, content area)
- Workspace switcher
- User menu + role badge
- Notification center

### Core Interaction
- Prompt input with context attach
- Primary/secondary action buttons
- Answer card with confidence + badges
- Source rail with grouped sections
- Source item row (title, type, freshness, open action)

### Live Assist
- Call status indicator (Listening/Paused/Ended)
- Real-time transcript stream
- Suggestion card (confidence, source, actions)
- Pinboard for saved suggestions

### Similar Tickets
- Filter bar + chips
- Results list row with similarity + status
- Ticket detail comparison pane
- Reuse action buttons (internal vs customer-safe)

### Admin
- Connector health card
- Policy toggles/sliders
- Role matrix table
- Audit log table + export controls

### Embedded Widget
- Compact prompt bar
- Quick action chips
- Inline answer panel
- Two-tab source switcher (Official / Similar)

---

## 4) Design Tokens

### Color (Enterprise neutral + trust accents)
- `color.bg.canvas`: `#F7F9FC`
- `color.bg.surface`: `#FFFFFF`
- `color.border.default`: `#D9E1EC`
- `color.text.primary`: `#1F2937`
- `color.text.secondary`: `#4B5563`
- `color.brand.primary`: `#0B5FFF`
- `color.brand.primaryHover`: `#084ACF`
- `color.success`: `#0E9F6E`
- `color.warning`: `#B7791F`
- `color.danger`: `#D14343`
- `color.trust.official`: `#0E9F6E`
- `color.trust.historical`: `#6B7280`

### Typography
- `font.family.base`: `Inter, Segoe UI, Roboto, sans-serif`
- `font.size.xs`: `12px`
- `font.size.sm`: `14px`
- `font.size.md`: `16px`
- `font.size.lg`: `20px`
- `font.weight.regular`: `400`
- `font.weight.medium`: `500`
- `font.weight.semibold`: `600`

### Spacing & Layout
- `space.1`: `4px`
- `space.2`: `8px`
- `space.3`: `12px`
- `space.4`: `16px`
- `space.6`: `24px`
- `space.8`: `32px`
- `radius.sm`: `6px`
- `radius.md`: `10px`
- `shadow.card`: `0 1px 2px rgba(16,24,40,0.08)`
- `grid.desktop`: `12 columns`
- `breakpoint.mobile`: `<= 768px`

### Status & Confidence
- `confidence.high`: `>= 85`
- `confidence.medium`: `70–84`
- `confidence.low`: `< 70`
- Badge styles map to success/warning/danger colors.

---

## 5) UI Copy

### Buttons
- Primary: `Ask`
- Secondary: `Attach Context`
- Tertiary: `View Sources`
- Live assist: `Pause Listening`, `Resume Listening`, `End Assist`
- Reuse: `Insert into Reply`, `Use Internal Note`, `Copy Draft`
- Admin: `Configure Connector`, `Run Sync Now`, `Save Policy`

### Empty States
- Ask mode: `Ask a question to get a grounded answer with cited sources.`
- Live assist: `Start Live Call Assist to receive real-time suggestions.`
- Similar tickets: `No similar tickets found. Try broadening filters or date range.`
- Sources rail: `No sources yet. Ask a question to load verified references.`
- Admin connectors: `No data sources connected. Add a connector to begin.`

### Warnings / Guardrails
- Low confidence: `Low confidence response. Verify with an official source before sharing.`
- Missing official source: `Customer-facing draft blocked: official source required.`
- Stale source: `Source may be outdated (last updated over 90 days ago).`
- Call privacy: `Live transcription is active. Ensure customer consent is recorded.`

### Confidence Labels
- `High confidence · Verified alignment with official documentation`
- `Medium confidence · Check source details before sharing externally`
- `Low confidence · Use as internal guidance only`

### Trust Labels
- Official source badge: `Official`
- Historical ticket badge: `Historical`
- Resolution badge: `Resolved`, `Partially Resolved`, `Unresolved`

---

## Responsive Behavior (Desktop-first, mobile-ready)
- On mobile, left nav collapses into bottom navigation.
- Source rail becomes bottom sheet with pinned tabs (`Official`, `Similar`).
- Primary CTA remains fixed at bottom in Ask mode.
- Live assist stacks transcript above suggestions; call controls remain sticky.

