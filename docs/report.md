# Task: Eurobot 2026 Rules — Goals & Focus Report

## Description

Read the official Eurobot 2026 rules ("Winter is Coming") and turn them into a concrete set of team goals: what the game rewards, what's mandatory vs. optional, and what we should focus engineering time on first. This report is the reference the team uses to scope the main robot and SIMA(s) before any CAD or code starts.

## Owner

Mouhib Arfaoui

## Desired Output

- A single `report.md` (this file) summarizing the 2026 game, scored so the team can prioritize.
- A points table for all 5 actions, with a read on which ones have the best effort-to-point ratio.
- A constraints checklist (robot + SIMA dimensions, safety, mandatory hardware) usable during homologation.
- A short, ordered list of what "setting goals" means in practice — what to build first.
- An open-questions list for anything the rules text didn't fully resolve.

## Input

- Official Eurobot and Eurobot Junior 2026 Rules v1.0 (game-specific rules) — eurobot.org
- Eurobot General Rules v1.0 (contest-wide rules: registration, robot dimensions, safety, matches, penalties) — eurobot.org

---

## 1. The Theme (in one paragraph)

Squirrels need to survive winter. Humans crated up hazelnuts and are about to leave with them — we have 100 seconds to grab crates and stash them, raid the humans' granary with a small ninja squirrel (SIMA), tune a thermometer cursor, get our main robot home to the nest, and have our squirrels (SIMAs) "eat" in the pantries. All five actions are independent — **nothing is mandatory, no sequence is imposed.** That single sentence is the most important design constraint in the whole document: it means we choose our own subset of actions rather than trying to do everything.

---

## 2. The Five Actions & Their Points

| # | Action | What it needs | Points |
|---|--------|----------------|--------|
| E.1 | **Let's keep the hazelnuts warm!** (main action) | Robot collects hazelnut crates → nest or pantries | 2 pts/crate in nest (max 6 = 12 pts) · 3 pts/crate valid in a pantry (no limit) · 5 pts bonus per pantry with color majority |
| E.2 | **To find is to keep!** | One SIMA ("ninja squirrel") empties the granary's fridges, refills them with empty crates | 2 pts/fridge emptied of hazelnut crates (×4 fridges) · 5 pts/fridge filled with empty crates — **scored for both teams**, not just whoever does it |
| E.3 | **Not too warm, not too cold** | Move a cursor along a thermometer strip toward the center (zone 0 → higher-value zones) | X pts depending on the zone reached (11 zones) — exact table not given in text, must check the appendix/diagram |
| E.4 | **Nest, sweet nest** | Main robot parks in its own nest by end of match | 5 pts partially in zone + 5 more pts fully in zone (10 max) |
| E.5 | **Munch time!** | Up to 6 SIMAs (+ the ninja SIMA) reach pantries and visibly "eat" (moving actuator) | 5 pts per pantry occupied · 10 pts bonus if **all** SIMAs eat |

**Match length: 100 seconds.** Everything above has to fit in that window, including any SIMA deployment.

### Read this as a priority signal, not just a rulebook
- The **hazelnut/pantry action (E.1)** has no cap on pantry crates and stacks with a 5‑pt majority bonus — this is the highest-ceiling, most replayable action and should be the main robot's primary job.
- **E.2 (granary/SIMA)** rewards *both* teams for the same fridge state, which changes the incentive: it's cooperative-ish, so it's a lower-risk, decent-value action if we build a capable SIMA — but it requires a second, fully autonomous mechanism (the "ninja" SIMA) that must survive in an area only it can enter.
- **E.3 (thermometer/cursor)** looks simple (no color/team management, no game-piece manipulation) but its point value is unknown from the text alone — worth checking the appendix table before deciding how much engineering time it deserves. There is also a **defensive trap**: if the opposing robot/SIMA disturbs our cursor significantly, we *automatically* win max points — so this could matter more as a "protect it" consideration than an "optimize it" one.
- **E.4 (return to nest)** is cheap points (10 max) for something we need to do anyway at match end if we want our robot safe from being touched/damaged — treat as close to "free" if pathing already brings the robot home.
- **E.5 (SIMAs eating)** rewards deploying *multiple* SIMAs and getting all of them to visibly "eat" — the 10-pt all-or-nothing bonus means partial SIMA fleets are punished proportionally more; decide up front whether we're building 1 SIMA (granary only) or several (granary + pantry swarm).

---

## 3. Hard Constraints We Must Design Around

### Main robot
- Perimeter ≤ **1200 mm** not deployed / ≤ **1400 mm** deployed.
- Height ≤ **350 mm** (emergency stop button may reach 375 mm).
- Must fit in the **450 × 600 mm** starting/nest zone at end of setup.
- Needs an **emergency stop button** (≥20 mm, visible, top or accessible side).
- Needs a **starting cord** system (≥500 mm cord, pulled by a teammate) — no remote/manual-switch starts allowed.
- Needs a **collision-avoidance system** for opposing robots (checked at homologation).
- Needs a **100 × 70 mm free rectangular space** on a side face for the organizer's team sticker.
- On-board beacon support height convention (430 mm) if we want to support opponent beacon placement — optional but avoids a possible forfeit risk if the opponent needs it and we can't provide it.
- Power: max 48 V DC / 48 V AC p-p, only approved energy sources (batteries, springs/elastics, compressed air ≤4 bar, gravity). No liquids, pyrotechnics, radioactive material.

### SIMA(s) — the "little squirrels"
- Must fit the **granary SIMA starting area: 20 × 20 cm** (for the ninja SIMA) or the **150 × 450 mm** SIMA starting strip (for pantry SIMAs).
- Height ≤ **150 mm**, min size a 60 mm cube, deployable perimeter growth ≤ +100 mm, max height when deployed 350 mm.
- Weight ≤ **1.5 kg** each.
- Same safety rules as the main robot (e-stop, avoidance, LiPo fire bags, etc.) and must be independently autonomous (can be touched/communicated with by our own robot, but must move under its own power).
- Up to **6 SIMAs** on the table (excluding the granary one) + **1 in the granary**.

### Team & event
- Team of **≥2 people**, age ≤30 for European final eligibility.
- **Technical poster** (A1 min, PDF ≤25 MB, English version for the international final) is mandatory — separate deliverable from the robot itself.
- Score-estimation display device is required on the robot/beacon/remote unit.
- Robots must be able to play **3 matches in a row** — battery planning matters.

---

## 4. What "Setting Goals" Should Actually Look Like

Given the rules are explicitly modular ("no single action is mandatory"), the team's job is to pick a **realistic subset** and build it reliably rather than attempting all five actions at low quality. Concretely:

1. **Decide robot scope first, before any CAD or code.** Pick which of the 5 actions the main robot will attempt (recommend: E.1 as the core, E.4 as a near-free add-on, E.3 if cheap to add) and which the SIMA(s) will attempt (E.2 and/or E.5).
2. **Build the single main robot to be reliable, not clever.** The rules literally warn beginners: *"one well-functioning robot is better than several that don't move."* Prioritize a robust chassis + one manipulation mechanism (crate pickup/placement) over multiple gadgets.
3. **Treat the SIMA as its own mini-project with its own timeline**, not an afterthought bolted on late — it has its own dimensional limits, its own starting procedure, and its own reliability risk (it's unsupervised once released).
4. **Get the exact thermometer point table** from the rules appendix/diagram before committing engineering time to E.3 — right now we only know "X points depending on zone," not the actual values.
5. **Map every mandatory constraint (Section 3) into homologation checklist items early** — dimensional/safety failures are forfeit-level penalties, not just point losses, so they should be verified continuously during build, not just before competition.
6. **Plan the technical poster and score-display device as parallel workstreams**, since they're required deliverables independent of robot performance.
7. **Practice the 3-in-a-row match cadence** (setup + 100s match + battery swap) well before the event — it's an explicit stated risk in the rules, not just a nice-to-have.

---

## 5. Open Questions to Resolve Before Locking the Design

- What are the actual point values per thermometer zone (E.3)? Need the appendix figure.
- Do we build 1 SIMA (granary only) or a full swarm (granary + pantry eaters)? This is the single biggest scope decision and should be made first, since it drives whether we need one or several independent autonomous subsystems.
- Will we use an on-board beacon support, given it's optional but can cause an opponent forfeit request if absent?
- What's our crate-manipulation mechanism (gripper vs. push/scoop) — this decision drives most of the main robot's mechanical design and should be prototyped early since it's shared across E.1 and E.4 pathing.

---

## Docs Needed

- Thermometer point-value table (appendix diagram, E.3) — not extractable as text, needs a direct look at the PDF figure.
- Beacon/granary layout diagrams (Appendix G.1) if we go for a full beacon-tracking system.
- National Organizing Committee (NOC) page for our country, in case local meeting rules add constraints on top of these.

## References

- Official Eurobot and Eurobot Junior 2026 Rules v1.0 (game-specific): `https://www.eurobot.org/wp-content/uploads/2025/10/Eurobot2026_Rules_1.0_EN.pdf`
- Eurobot General Rules v1.0 (contest-wide): `https://www.eurobot.org/wp-content/uploads/2024/10/Eurobot_General_Rules_EN.pdf`

**Last updated:** 2026-07-25
