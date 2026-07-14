# Location selection — tailored per role (verified live 2026-07-14)

Locations are job-board DISTRIBUTION fuel: portals syndicate by city, and the candidate-facing picker cannot be turned off, so a job takes CITIES, not regions. Do NOT dump the full region set (79+ cities = buried among 200 competing posts in the big hubs). The strategy (Tania's, 2026-07-09): **~12-15 strategic cities = a few main hubs + a rotating cast of overlooked smaller cities, spread across countries.** Big cities keep reach; small cities (Rosario, Tegucigalpa, Antofagasta) make the post a standout for overlooked talent. **Seed the draw by JOB ID** so each role gets a DIFFERENT balanced set and roles don't stack on the same cities.

## Pool
- Read the full library: `GET locations?page[size]=300` (internal API; plain `per_page` caps at 50 — use the JSON:API `page[size]` param; ~232 cities).
- Filter by region for the role's geography: Latam region_id **1422** (~142 cities), US **2600**, Canada **1423**, EMEA **2630**, APAC **4947**. Geography comes from the brief: LATAM → Latam · USA → US · Americas → Latam+US+Canada · worldwide → all · specific countries → filter pool by `country`.

## Algorithm (deterministic, no Math.random — seeded by job id)
```js
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}}
// 1. rnd = mulberry32(jobId)
// 2. hubs = seededShuffle(pool ∩ HUB_NAMES, rnd).slice(0,4)
// 3. rest grouped by country, each country's list seeded-shuffled, country order seeded-shuffled
// 4. round-robin one city per country per pass until total = 14
```
HUB_NAMES (match on `(l.city||l.name).trim()`, case-insensitive): Mexico City/Ciudad de México, Guadalajara, Monterrey, Buenos Aires, Bogotá, Medellín, São Paulo, Rio de Janeiro, Lima, Santiago, Montevideo, Quito, San José, Asunción, Guatemala City, Santo Domingo, Panama City.

Result shape (live example): UX Designer 661641 → São Paulo, Lima, Rio, Guadalajara + Salto, Rosario, Ciudad del Este, Maracaibo, Antofagasta, Tegucigalpa, Callao, Guarulhos, Bucaramanga, San Salvador. Product Specialist 661644 got a different 14 (overlap 2). Round-robin across countries gives ~11-12 countries per set.

## Writing location_ids — the safe PUT
`location_ids` lives on the JOB, but a bare `PUT jobs/{id} {job:{location_ids}}` → **422 "Client can't be blank"** (verified; the 422 changes nothing). The safe write echoes the live state back:
1. `GET job_details/{id}` → current body, pitch, picked_custom_fields, picked_questions, picked_interview_kits.
2. `PUT jobs/{id}` with `{job:{location_ids, job_detail:{ body, pitch, picked_custom_fields_attributes:[client row WITH its id], picked_questions_attributes:[all rows WITH ids], picked_interview_kits_attributes:[rows WITH ids] }}}`.
3. GET-verify: location count = 14, body/pitch lengths unchanged, q count unchanged, kit + client present.

## Rotation (built: the `tt-location-rotation` skill)
Scheduled ~10 days: changing `location_ids` re-syndicates on boards. The rotation skill reads each open job's CURRENT `location_ids` live (state lives in TT — no memory needed), keeps the hubs, and resamples the rest with seed = `mulberry32(jobId + windowIndex)`, `windowIndex = floor(days_since_2026_01_01 / 10)` — deterministic inside a window (idempotent re-runs), fresh across windows. It shares THIS file's algorithm, HUB_NAMES, and safe-PUT recipe; maintain them here, not duplicated there.
