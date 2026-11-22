# Creed (2015) "The Final Round": beat script and cutting breakdown

Source: `creed2015_final_round.mp4` (1280x720, 23.976 fps, picture letterboxed to about 2.39:1).
Usable scene: **0.00–146.52 s** (frames 0–3512). The end card runs 146.52–156.57 and is excluded.
Per-shot detail is in `shots.json`. Its `frames` field gives exact `[f0, f1)` frame indices; t = f / 23.976.

## Stats

| metric | value |
|---|---|
| total shots | **71** |
| median / mean shot length | **1.42 s / 2.06 s** (min 0.54, max 8.09) |
| median during the fight (shots 1–43, 0–74.9 s) | 1.21 s |
| median in the aftermath (shots 44–71, 74.9–146.5 s) | 1.94 s |
| shot sizes | MS 32 (45%) · MCU 21 (30%) · CU 10 (14%) · WS 5 (7%) · EWS 2 (3%) · MWS 1 (1%) · ECU 0 |
| handheld | **55 / 71 = 77%** |
| slow-motion shots | **1** (#41, the knockdown fall, about 2–3x, the whole shot; no speed ramps found) |
| reaction inserts | 21 (Trainer 7, Girlfriend 4, Mother 4, B's trainer 3, fans/stands 3), median 1.00 s |
| long holds (≥ 3.5 s) | #3 crane 7.0 s, #17 combo 4.4 s, #44 count 8.1 s, #52 ref check 4.9 s, #57 hug orbit 5.9 s, #58 EWS 3.7 s, #68 3.5 s, #69 belt/respect 7.3 s |

Boundary corrections relative to the PySceneDetect list:
- **Added 10 missed cuts:** 22.23, 26.32, 30.03, 56.01, 59.52, 60.23, 60.77, 61.69, 72.20 (hidden inside a whip-pan blur), 100.98.
- **Removed 1 false cut:** 69.945, a flashbulb flicker.
- **Dropped the end card.**
- **Checked as single continuous takes:** the crane in #3, 56.0–59.5, 61.7–62.8 (a whip-tilt), 63.8–64.9, 84.6–85.6, 95.6–98.9, 101–103 (a foreground wipe), the hug at 106.6–112.4, and 137.1–144.4. Each was verified at 1-frame steps.

## Cast key (roles only; recast freely)

- **Boxer A (challenger, hero).** Lean, muscular young Black man with close-cropped hair and a thin mustache. His left eye (screen-right in frontal shots) is swollen nearly shut, with a cut brow and blood smeared over the cheek. Stars-and-stripes trunks: red/white vertical stripes and a blue star-print waistband with name lettering. White gloves with red/blue trim and white wrist tape.
- **Boxer B (champion).** Stocky, heavily built white man with short dark hair and a goatee. He bleeds from a cut under his left eye. Tattoos on chest, arms and back. Black trunks with silver trim and a name waistband; black gloves with blue cuffs. After the fight he wears a green title belt.
- **Referee.** Stocky, ruddy, buzz cut, light-blue shirt, dark trousers.
- **Trainer (A's corner).** Older man in a black knit beanie, white corner jacket with blue trim, and a blue towel around his neck.
- **B's trainer.** Bald with a full grey beard, dressed in black.
- **B's cornerman.** Bald, glasses, black "TEAM <champ>" t-shirt.
- **A's corner men.** An older bald Black man and a younger Black man, both in white jackets with blue collars, plus an older white cutman with glasses and a grey mustache.
- **Girlfriend.** Young Black woman with long box braids, dressed in black, sitting ringside among men in tuxedos.
- **Mother.** Older woman with short dark curls, a red cardigan over a cream top, sitting on a cream sofa at home and watching on TV.
- **Others.** A ring announcer (white hair, tuxedo, hanging mic), a post-fight interviewer (black suit, branded mic), fans (one holding a replica belt), ringside photographers, and TV camera operators.

## Look

- **Arena:** hard white top light from the overhead ring truss, so skin has specular highlights. The crowd falls off into deep navy, the truss carries blue LEDs, and the canvas is bright blue with red sponsor logos. Ropes are white with red logos, and A's corner pads are red. The grade is low-key teal/navy with red blood accents.
- **Home cutaways:** warm tungsten and amber. A practical lamp sits in the background right and a soft key comes from the TV side. This warm look is the deliberate counter-colour to the arena.
- **Broadcast layer:** a TV score bug ("<NETWORK> BOXING", then a clock "2:57 | 12 OF 12") on the opening crane. During the rally a countdown clock (0:11 → 0:00) is overlaid on ring shots.

## Beats

| # | beat | time | shots | n | median | what it achieves | cutting rhythm |
|---|---|---|---|---|---|---|---|
| 1 | Face-off | 0.00–9.30 | #1–2 | 2 | 4.65 s | A rises off his stool into a ruined-eye CU, answered by B's CU stare. Sets up two equal wills. | Two long matched handheld tele CUs. No crowd and no fight; the sound is almost quiet. |
| 2 | Bell / round 12 opens | 9.30–16.31 | #3 | 1 | 7.01 s | Broadcast crane through the lighting rig to the glove touch, then a high wide. Establishes geography and the "final round" stakes. | One 7 s crane move with the score bug. The only crane shot. |
| 3 | Opening exchanges | 16.31–37.12 | #4–16 | 13 | 1.21 s | An even trade at close range. Both corners react, and the crowd is introduced. | OTS reverse pairs (#5/#6, #10/#11) cut on punches. After about 3 fight shots come 2 corner inserts (#8 Trainer, #9 B's trainer). A low wide-lens "geography reset" (#14). Trainer insert closes the beat. |
| 4 | A's surge | 37.12–56.01 | #17–28 | 12 | 1.10 s | A takes over with a 4.4 s combination (#17), and the outside world reacts: Girlfriend, then the Mother turning away, then fans. Ends with the Trainer praying. | Opens on the longest action shot, then speeds up. Second low wide reset (#18). Introduces the Mother cross-cut (#22). A slow push-in (#26) builds pressure. Two reaction inserts in a row (#27–28) close it. |
| 5 | Final-10-seconds rally | 56.01–70.53 | #29–40 | 12 | 1.02 s | A gets cornered, then turns it around and lands the hook (#40). The on-screen clock ticks from 0:11 to 0:02. | One 3.5 s chaotic handheld shot, then a strict alternation of 1–2 fight shots with 1 reaction (Trainer → Girlfriend → Trainer → Mother). Most shots run 0.5–1.1 s, the fastest stretch of the scene. Every ring shot carries the clock. |
| 6 | Knockdown | 70.53–74.87 | #41–43 | 3 | 1.38 s | B falls in slow motion, the camera whips onto him on the canvas as the clock hits 0:00, and the Mother sits frozen. | The only slow-mo shot (#41, cut on the punch's impact). A whip-pan entry hides the next cut (#42). A static home reaction lets the moment breathe. |
| 7 | The count | 74.87–95.55 | #44–52 | 9 | 0.96 s | Will B get up? He does, and the ref checks him. | Opens with the longest take in the scene: 8.1 s, low on the canvas from the downed B's position, with the ref counting and A waiting in the background. Then fast singles (0.9–1.7 s): B on all fours, B's trainer, Trainer, Girlfriend, A from behind, A's face, B rising. Closes with a 4.9 s handheld ref check. |
| 8 | Fight over / release | 95.55–112.45 | #53–57 | 5 | 3.38 s | A collapses to his knees, his corner and the Girlfriend rush in, and he gets the cathartic hug. | Shots lengthen sharply. Handheld moves follow bodies. A high wide gives scale (#56). Ends on a 5.9 s orbiting hug long take. |
| 9 | Waiting for the decision | 112.45–124.12 | #58–63 | 6 | 1.65 s | Suspense held in stillness: the dark arena, the Mother's proud tears, the stands, A spent, the Trainer's nerves, the announcer. | A static EWS (3.7 s) and static wides alternate with handheld MCUs. The sound drops. |
| 10 | Verdict | 124.12–133.59 | #64–67 | 4 | 2.27 s | A hears it, B celebrates, A accepts, and the Trainer consoles him with pride. | Reaction, then counter-reaction, then reaction. Medium-length handheld shots, no hurry. |
| 11 | Respect coda | 133.59–146.52 | #68–71 | 4 | 2.56 s | The champion comes to A wearing the belt, speaks into his ear, and they embrace. | A framed and isolated (3.5 s), then a 7.3 s belt/respect take. Ends on a quick OTS reverse pair (1.6 s + 0.5 s) that mirrors beat 1. |

## Editing grammar (replicate these)

1. **Reaction-insert cadence.** After every 1–4 fight shots (typically 2–3) comes a single of about 1.0 s (0.8–1.4 s) of someone with a stake in the fight. The rotation is Trainer (7) → B's trainer (3) → Girlfriend (4) → Mother at home (4) → fans (3). In the rally (beat 5) this tightens to a strict 1–2 : 1 alternation.
2. **Dirty OTS reverse pairs.** Most fight coverage is handheld tele MS/MCU from inside the ring. One fighter's out-of-focus back or shoulder fills 30–50% of the frame while the other faces the lens. The editor jumps 180° to the reverse freely, without respecting the line.
3. **Cut on the punch.** Cuts land mid-swing or on impact (for example 25.65, 30.03, 30.66, 70.53), and the next shot opens already moving.
4. **Hardware framing.** Low shots through the ropes, a corner post down the centre of frame, and the top rope slashing the foreground (#18/19/24/26/51). Two low wide-lens canvas setups with a canted top rope and visible ceiling lights act as geography resets (#14, #18).
5. **Broadcast layer.** One TV crane wide with the network score bug opens the round. During the last 11 seconds a running countdown clock is burned onto the ring shots (and once onto a Trainer CU) but kept off the Girlfriend and Mother shots. That makes it a literal ticking clock.
6. **Warm home cross-cut.** A static, amber, lamp-lit shot of the Mother is placed at each turn of the story: A dominates (#22), A traps B (#38), B goes down (#43), the fight is survived (#59). It is the only static, warm material in the fight.
7. **Real time, one slow-mo.** All action plays at 24 fps real time except the knockdown fall (about 2–3x, with muffled audio). That shot is entered on the punch's impact and left with a whip-pan blur.
8. **Hold after the climax.** Shot length roughly doubles after the knockdown, with long takes at 8.1 s (the count, from the mat's POV), 4.9 s, 5.9 s (the orbiting hug) and 7.3 s (the respect take). Quick inserts still punctuate the count.
9. **Foreground wipes.** Heads, arms and bodies pass the lens inside long handheld takes (#9, #47, #55, #67, #69) and act as hidden in-shot transitions.
10. **Mirrored bookends.** The scene opens on matched CUs of A then B (the face-off) and closes on a matched OTS pair of A then B (the respect). The match runs on eyelines across screen-left/right: A mostly screen-left and B screen-right in the two-shots.

## target_cut

- **Requirement:** a 2–3 minute demo, about 150–180 s.
- **Usable source:** **146.52 s**, after excluding the 10.05 s end card. That is **3.5 s under the 150 s minimum** and 33.5 s under 180 s.
- **Material that would extend it naturally (named only, nothing downloaded):**
  - **Before 0:00: the corner/stool break between rounds 11 and 12.** The clip opens as A stands up off his stool, so the preceding corner talk follows directly. That is the cutman working the eye, the Trainer offering to stop the fight, and A insisting on going out. It also leads straight into the existing CU face-off. About 30–60 s. Verify exact content against the film.
  - **Before that: the end of round 11.** A's knockdown, getting up, and the bell. The same arena look, so it is easy to match.
  - **After 146.52: the immediate aftermath.** The rest of the in-ring interview or exit from the ring, if present in the film. The film's later epilogue is a different location and less seamless.
- **Option with no new material:** extend the existing holds to clear 150 s. For example, add about 1 s each to #44 (the count), #57 (the hug) and #69 (the belt) and about 0.5 s to #3. The editing grammar already favours long holds in those beats.
