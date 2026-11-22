# Drive (2011) "Getaway": beat sheet and cutting breakdown

Source: `drive2011_getaway.mp4` (1280x720 @ 23.976 fps, 134.34 s). The picture is letterboxed at about **2.39:1**: the active area is roughly 1280x540 at y≈88.
- 0–8.842 s: black title card ("FilmDistrict / Drive / Clip #1 – Get away"). Excluded.
- 133.050–134.34 s: black tail. The clip cuts to black in the middle of the film's scene. Excluded.
- **Usable scene: 8.842–133.050 s = 124.21 s, 45 shots.** Per-shot fields are in `shots.json`. Its `t0`/`t1` are clip time; `frames` gives the first frame of the shot and the first frame of the next shot.

What the clip shows: the opening heist pickup. The Driver waits outside a warehouse with one masked robber already in the back seat. The second robber runs out and dives in. They drive off, kill the lights and hide behind a parked truck while a police cruiser passes. They slip out, calmly tail a cruiser until it turns off, then cross a long lamp-lit bridge toward downtown. **There are no aerial or helicopter shots and no exterior views of the hero car in this clip.**

Cut-detection note: the auto list had 46 entries, including the title card and the black tail. One cut was **missed at 63.939 s** (old shot #21 is really two shots: the OTS of the stationary car, then the robbers hiding). All other auto cuts are real and frame-accurate (each is a strong per-frame peak). I checked these candidates frame by frame and they are **not** cuts:
- 48.59 s: oncoming headlight flare during the swerve
- 124.1 / 124.8 s: lamp bloom on the bridge
- 126.0 s: a shadow band wiping the Driver's face
- 130.2 s: lamp flare

The long takes #1 (8.55 s), #23 (6.84 s), #28 (5.59 s) and #30 (5.67 s) contain no hidden cut.

## Stats

| metric | value |
|---|---|
| shots | 45 |
| scene length | 124.21 s (2:04) |
| mean / median shot | 2.76 s / 2.34 s |
| p25 / p75 | 1.79 s / 3.29 s |
| min / max | 1.04 s (#41) / 8.55 s (#1) |
| shots > 5 s | 4 (#1 8.55, #23 6.84, #28 5.59, #30 5.67) |
| shots < 1.5 s | 5 (#13, #16, #41, #42, #43) |

**Shot sizes** (counted by primary size): MCU 20 · WS 10 · MS 7 (5 of them OTS) · CU 6 · MWS 2. There are no ECU shots, except the eyes-in-mirror at the end of #30, and no EWS.

**In-car:** 42/45 shots (93%) have the camera inside the car. The other 3 (#17, #19, #44) are low front-bumper views from the car. In total, 100% of the scene is seen from the car.

**Screen time:**

| who | shots | seconds | share |
|---|---|---|---|
| Driver's face | 20 | 55.2 | 44% |
| Robbers | 10 | 20.0 | 16% |
| Road, POV and exterior | 15 | 49.0 | 39% |

**Transitions:** all straight cuts. There are 0 dissolves and 0 slow-motion shots. One cut is on action: 8→9, the Driver's head turn into the robber's dive. One is a motivated cut: 23→24, the head lift into the pull-out.

**Camera setups.** Only about 11 camera positions are used, which makes the scene very reusable for generation:

| setup | shots | n |
|---|---|---|
| A. Passenger-seat side profile of the Driver, facing screen-right | 1 (push-in), 10, 12, 16, 18, 23, 42 | 7 |
| B. Low console CU, 3/4 up at the Driver (teal bokeh) | 3, 6, 8, 20 | 4 |
| C. Front seats looking back at the rear seat (robbers) | 2, 5, 9, 11, 13, 22, 29, 31, 36, 43 | 10 |
| D. Rear OTS: gloved hand on the wheel, road through the windshield, mirror top-centre | 15, 21, 24, 26, 32 | 5 |
| E. Passenger-dash front 3/4 MCU of the Driver | 14, 25, 27 | 3 |
| F. Dash-level windshield POV with a blurred mirror (following the cruiser) | 28, 30 | 2 |
| G. Rear-seat-centre POV through the windshield (bridge) | 34, 38, 40 | 3 |
| H. Frontal cyan MCU/CU of the Driver (bridge) | 33, 37, 39, 41 | 4 |
| I. Interior wide from the passenger dash: Driver right, robbers behind | 35, 45 | 2 |
| J. Exterior, bumper height (2 moving, 1 locked) | 17, 19, 44 | 3 |
| K. POV out the passenger window to the warehouse gate | 4, 7 | 2 |

**Car layout:** left-hand drive. The Driver sits front-left and the front passenger seat is empty (that is where the camera lives). Robber A sits rear-left behind the Driver; Robber B sits rear-right. In every side-on shot the car's forward direction is screen-right (Driver and robber profiles), and the camera always stays on the passenger side of the car's long axis.

## Sound shape (RMS envelope only; no ASR was available, so no lines were verified)

- 8.8–124 s: a **steady pulse at about 100 BPM (0.597 s period)** under everything. This is music or a ticking clock. The cuts are not beat-locked: 19 of 44 cuts fall within ±0.15 beat, against about 13 expected by chance.
- Levels by section:

| time | level | section |
|---|---|---|
| 8.8–29 s | about −28 to −35 dB | wait |
| 29–50 s | about −22 to −27 dB | pickup and drive |
| 50–73 s | quietest, about −30 to −40 dB | hiding |
| 74–124 s | about −22 to −30 dB | — |
| **124–133 s** | swell of +8–10 dB, to −12 dB | bridge climax; the loudest part of the clip |

- Visible speech: Robber A shouts toward the front at about 32.2 s (#9), A talks at the Driver in #13, and B whispers to A in #29. **The Driver never speaks.**

## Script by beat

| # | time | shots | what happens | purpose | cutting rhythm |
|---|---|---|---|---|---|
| B1 The wait | 8.84–29.45 | 1–8 | 8.5 s push-in on the Driver in profile, who turns his head toward the back seat. Cut to masked, goggled Robber A in the rear seat, peering out. Low CU of the Driver watching. POV through the passenger window: fence, gate, empty lot, lit warehouse door. Robber A fidgets. Driver CU. POV: Robber B bursts out of the door and sprints toward the car. Driver CU turns to face front. | Patience against nerves. The clock runs on an empty doorway. | One long breath (8.55 s), then a tight eyeline loop D–R–D–P–R–D–P–D at 1.5–2.1 s per shot. |
| B2 Pickup and pull-away | 29.45–40.42 | 9–13 | Handheld: Robber B dives through the rear door with bag and bolt cutters, and A shouts "go" at the front. Locked side MS: the Driver pulls away smoothly, palming the wheel. Handheld: B rips off his balaclava. Driver profile, still. Both robbers, unmasked, lean forward, A talking at him. | Chaos in the back, total calm at the wheel. | 2.9 / 2.9 / 2.0 / 1.75 / 1.46 s, quickening. Handheld for the robbers, locked for the Driver. |
| B3 Evade and hide | 40.42–56.85 | 14–19 | Driver checks his mirror (front 3/4). OTS through quiet streets. Profile. Bumper cam: the car swerves past a box truck, **kills its headlights**, and creeps into the shadow behind a flatbed truck. Profile, waiting. Locked low WS from the hiding place: a black-and-white cruiser crawls right-to-left across the far street. | Technique over speed: vanish rather than run. | 3.0 / 2.25 / 1.33 / 3.8 / 2.75 / 3.3 s. Longer takes start to appear. |
| B4 Hold still | 56.85–73.24 | 20–23 | Low CU of the Driver watching, motionless for 3.7 s. OTS: the car is stationary and the cruiser lingers far left. Robbers hunched low, hiding. **6.84 s profile hold**: the Driver dips his head, listening, then lifts it. Decision. | Suspense through stillness; the Driver owns time. | Slowest section: 3.7 / 3.4 / 2.5 / 6.8 s (mean 4.1 s). |
| B5 Slip out and tail the cop | 73.24–93.43 | 24–29 | OTS: the car eases out and the headlights come on. Front 3/4: shoulder checks. OTS turn, eyes in the mirror. Driver spots something. Windshield POV: **following a police cruiser** at a steady distance for 5.6 s, with the Driver's eyes blurred in the mirror. Robbers whisper and stare at the cruiser. | Hiding in plain sight. | 4.3 / 3.25 / 2.1 / 2.3 / 5.6 / 2.6 s. |
| B6 The cop turns off | 93.43–104.94 | 30–32 | The cruiser peels off left at an intersection while the car bears right. **Rack focus to the Driver's eyes in the rear-view mirror**, then oncoming headlights. Robbers twist to watch it go. OTS: the car swings onto a wide avenue toward the downtown skyline. | Release. The camera moves from the threat to the Driver's eyes. | 5.7 / 1.9 / 3.9 s. |
| B7 The bridge | 104.94–133.05 | 33–45 | The palette flips to cyan. A frontal Driver MCU emerges from darkness, then alternates with a rear-centre windshield POV of the lamp-lined bridge: 33/34, 37/38, 39/40. Inserted: a wide of all three (35), robbers in cold-rim profile (36), and passing lamp shadows sweeping the Driver's face. The run accelerates to 1.0–1.2 s: frontal (41), profile against a teal blur (42), B lurching and A grabbing the roof handle (43). Release: the first exterior since #19, a bumper cam under the steel truss arch (44). End on the interior wide, Driver in control (45). Hard cut to black. | Escalation to the climax: speed without a chase. | 2.6 / 2.8 / 2.4 / 1.8 / 1.9 / 3.8 / 3.4 / 2.1 / **1.0 / 1.2 / 1.1** / 2.3 / 1.7 s. The audio swells from #40 on. |

## Editing grammar (must replicate)

1. **The car is the world.** 93% of shots are inside the cabin and 100% are seen from the car. There are no exterior shots of the hero car, no aerials and no street-level coverage. The outside is seen only through glass (windshield, side window, mirror) or from bumper height.
2. **Calm against chaos is shown with the camera.** Every Driver shot is locked-off (or a slow push-in, #1). The robbers get handheld at the peaks: dive (#9), unmasking (#11), brace (#43). The robbers lean, talk and twist. The Driver only moves his eyes, with small head turns and one head dip.
3. **The profile metronome.** Setup A, the passenger-seat side profile with a toothpick and a blurred satin sleeve in the foreground, returns between action beats (#10, 12, 16, 18, 23, 42). Hold on the Driver's calm face while the danger happens elsewhere. The longest hold of the scene (6.84 s) comes right after the cop passes.
4. **Eyeline loops.** B1 cycles Driver CU → Robber A or POV of the gate → Driver CU. B5 runs Driver looks (#27) → cruiser through the windshield (#28) → robbers stare (#29).
5. **The threat appears only at a distance, through glass.** The cruiser is never closer than ~25 m and never in its own close-up (#19, 21, 28, 30). The hiding beat is a locked WS where the threat crosses deep in the background.
6. **Mirror and eyes motif.** The rear-view mirror sits top-centre in every windshield/OTS frame. The Driver's eyes show in it in #26, 28, 30, 32, and #30 racks focus onto them at the moment of release.
7. **Shot length is used for suspense.** Fast loops (1.5–2 s) while waiting for action, long holds (3.3–6.8 s) while hiding or tailing, then strict A/B alternation on the bridge (frontal face ↔ windshield) that shrinks to ~1 s before the exterior release.
8. **Light marks the acts.**

   | shots | light |
   |---|---|
   | B1–B2 | warm amber sodium with teal accents |
   | B3–B6 | dark teal-green; the headlight-kill (#17) and headlights-on (#24) are story beats |
   | B7 | hard cyan, with passing lamp shadows sweeping the face rhythmically (#33, 37, 39, 41) |

9. **Screen direction is never broken.** The car's forward direction is screen-right in every side view. The Driver faces the lens in dash shots, and the road always recedes into depth. The cruiser crosses right-to-left (#19) and exits left (#30).

## Silent-demo notes (where the original leans on sound)

| original sound | shots | how the picture carries it in the demo |
|---|---|---|
| Steady pulse (whole scene) | 1–44 | The cut rhythm itself; keep the exact durations. |
| Probably a shouted "go", door slam, engine | 9–10 | A's open-mouth shout to the front; the car visibly pulls away (lamps sliding through the window). |
| Probably radio or scanner telling him when to hide and when to go (unverified) | 17–23 | Make the **headlight switch-off** read as deliberate (#17). Make the **cruiser legible** (white doors, roof bar) in #19 and #21. In #23 the head-dip-and-lift has to read as "listening… now". |
| Back-seat whispers | 13, 29 | Lean-ins, mouths moving, fixed stares at the cruiser. |
| Loud swell 124–133 s | 40–45 | Rely on the 1.0–1.2 s cuts, the light sweeps and the bumper-cam speed; do not slow the ending down. |

## Recast (new, original identities; costumes kept close to the roles)

- **Driver ("Cal")**
  - Face: mid-30s, lean and long-limbed. Dark-brown hair cropped at the sides with a slightly messy top. Thick straight dark brows, narrow hazel-grey eyes, a long straight nose, light olive skin, close-trimmed dark stubble, a small pale scar on his chin. Expressionless the whole time.
  - Costume: pale silver/ivory quilted satin bomber with a black ribbed knit collar and cuffs (plain, no embroidery), dark navy shirt, tan perforated leather driving gloves, a steel watch worn over the left glove cuff, a wooden toothpick.
- **Robber A ("Goggles"), rear-left**
  - Face: late 20s, slim and wiry. Dense copper-red curly hair to the ears, pale freckled skin, a thin ginger moustache, wide restless blue eyes.
  - Masked: grey knit balaclava with round smoked-lens welding/moto goggles strapped over it.
  - Costume: dark olive hooded parka over a rust-orange tee, black gloves.
- **Robber B ("Cutters"), rear-right**
  - Face: late 40s, heavy-set with a thick neck. Shaved head, short salt-and-pepper boxed beard, broad flattened nose, heavy brow, deep-brown skin.
  - Masked: black knit balaclava, which he pulls off in #11.
  - Costume: black canvas work jacket over a charcoal hoodie, black gloves.
  - Props: black duffel and red-handled bolt cutters, plus a black plastic loot bag.
- **Police cruiser:** generic black-and-white patrol sedan with a roof light bar. No officers are visible.
- **Hero car (interior only):**
  - 2000s full-size sedan, left-hand drive.
  - Charcoal cloth seats with grey headrests.
  - Teal-backlit gauges and a rear-view mirror.
  - Its exterior is never shown, so it needs no exterior design.
- **Vehicles in frame:** a white/yellow rental-style box truck (#17) and a dark flatbed/stake truck (#17, 19, 21).

## target_cut

- The usable scene is **124.21 s (2:04)** over 45 shots, which **meets the 2–3 min target** as a 1:1 re-creation. There is no need to pad with the title card (8.84 s black) or the black tail.
- The margin above 2:00 is only 4.2 s, so **no shot can be dropped or shortened** without compensating elsewhere.
- Generation lengths: 41 shots are ≤ 5 s. Four need more than 5 s of usable footage: #1 8.55 s, #23 6.84 s, #28 5.59 s, #30 5.67 s. Generate those at the model's 8–10 s length and trim.

## Hard shots (for current text/image-to-video) and the closest simplification

| shot | why it is hard | simplification (keeps framing and cut length) |
|---|---|---|
| #1 (8.55 s) | Longer than most generation windows. The slow push-in plus a continuous head turn from away-from-lens to 3/4 must hold one identity. | Generate 10 s from a start frame of the profile, prompting the slow push-in and the head turn, and trim to 8.55. Fallback: a static camera and a 1.4x digital push in post. |
| #9 | A handheld whip while a body dives through a car door with a bag and bolt cutters, landing in a two-shot. | Static rear-facing camera with the door already open. B slides in from frame-left and the bolt cutters land across his lap; add light shake in post. End frame is the two-shot of the masks. |
| #11 | Unmasking (a balaclava pulled over the head) in near-dark handheld, with B's face needing to match later shots. | Start from an image with the mask already half-raised and do one upward pull. Or B is already unmasked and wipes his face with the mask in hand: same framing, same 2.0 s. |
| #17 | One take holds a swerve past a truck, a headlight switch-off and a creep behind a second truck in the dark. | Generate the swerve past the box truck, then ramp exposure to near-black at 49.1 s in post (an exposure ramp, not a cut). The hiding view is carried by #19 anyway. |
| #19 | Nearly black frame; the small cruiser crossing the background tends to vanish or the model brightens the scene. | Generate brighter, with the cruiser a bit larger and clearly crossing right-to-left in the gap left of the truck, then grade down. |
| #28, #30 | A defocused rear-view mirror with the Driver's eyes, a cruiser ahead, and in #30 the cruiser turning off plus a **rack focus** to the mirror. | #28: keep the mirror soft (an orange blur is enough). #30: generate two takes on the same framing (A: road sharp, cruiser exits left; B: mirror sharp with eyes) and join them with a ~0.5 s cross-dissolve to fake the rack. It still reads as one shot of 5.67 s. |
| #33, 37, 39, 41 | Rhythmic passing-lamp shadows sweeping the face; models flicker randomly or keep the light static. | Prompt "bands of streetlight passing across his face every ~1 s, cyan". Fallback: a steady cyan key plus a brightness pulse added in post. |
| #42 | An ambiguous huge defocused teal shape in the window. | Replace it with "blurred steel bridge girders streaming past the window". |
| #44 | Bumper cam under a steel truss arch; the truss geometry warps, and the lane-change roll adds instability. | A straight lane with no roll, the arch approaching and passing overhead, an SUV ahead. |
| #10, 15, 21, 24, 26, 32 | Gloved hands on the wheel (glove and finger artefacts); hand-over-hand steering in #10. | Hands stay put at 10 and 2 or 10–11 o'clock, with only small wheel motion. Let the world through the glass carry the movement. |
| Global | Very low-key night exposure, plus continuity of the car interior, costume, masks and toothpick across 45 shots. | Build reference stills first: the Driver, A masked and unmasked, B masked and unmasked, the cabin from setups A, C, D and H. Reuse the 11 setups and grade every shot down afterwards. |
