# Dune (2021) "Sandworm Attack": beat sheet and cutting breakdown

Source: `dune2021_sandworm_attack.mp4` (1280x720 @ 23.976 fps). The picture is letterboxed at **2.39:1**: the active area is 1280x536 at y=92.
Usable scene: **0.000–109.401 s**. A hard cut at 109.401 leads into the end card, which is excluded.
Shot list with per-shot fields: `shots.json`, 34 shots.
Prequel source: `dune2021_sandwalk.mp4` (1280x720 @ 30 fps, a 24p telecine with every 5th frame duplicated, also 2.39:1 at y=92, 77.6 s, burned-in subtitles to be ignored). Its shot list is `shots_sandwalk.json` (18 shots, times relative to that clip). In the tables below, times prefixed **sw** refer to the sandwalk clip; unprefixed times refer to the attack clip.

What the clip actually shows: this is the mother-and-son flight across open sand to a rock outcrop, the face-off with the worm, and the worm diving away. It is not the spice-harvester sequence.

Cut-detection note: the original auto list found 11 shots. A per-frame normalized-difference pass plus visual checks of every boundary (contrast-stretched frames) found **34**. The missed cuts were mostly in the bright, low-contrast chase (0–40 s) and in the face-off (50–92 s). Shot 20 (39.96–50.38) is nearly black and heavily macro-blocked, but it is one continuous take with no hidden cut. Shot 33 brightens at ~99.4 s because sand spray rolls in; the framing is unchanged, so it is not a cut.

## Stats

| metric | value |
|---|---|
| shots | 34 |
| scene length | 109.40 s |
| mean shot length | 3.22 s |
| median shot length | 2.29 s |
| min / max | 0.75 s (shot 1) / 10.84 s (shot 33) |
| chase half (shots 1–19, 0–39.96 s) | ASL 2.10 s, median 1.46 s |
| standoff half (shots 20–34, 39.96–109.40 s) | ASL 4.63 s, median 3.46 s |

Shot sizes: EWS 5 · WS 7 · MWS 5 · MS 3 · MCU 6 · CU 7 · ECU 1. Nearly everything is very wide or close. There are only 3 true medium shots.

Transitions: every cut is a straight cut. There are 0 dissolves, 0 speed ramps and no visible slow motion. Two cuts are cut-on-action: 9→10 (the get-up) and 18→19 (the dive onto the rock).

Sound shape (RMS envelope, for timing only):
- 0–47 s: loud and continuous (run, worm roar).
- ~49–52 s: drops to near silence.
- 57–70 s: stays very quiet. There is a brief swell around 71–74 s, then quiet low-level sound from 76–92 s.
- 93–109 s: loud again as the worm dives.

Dialogue was not verified.

## Sandwalk prequel (dune2021_sandwalk.mp4)

The scene: at sunset the Son scouts the open sand and they agree to cross after dark using the broken-rhythm "sand-walk". Hard cut to night: navigation by sky and compass, fatigue, the sand-walk seen twice, a climb, then rest on a dune slope. It ends on the Mother's profile looking screen-left.

Cut detection: the auto list found 11 shots; there are **18**. The last auto "shot" (39.8–77.6) actually contains 8 shots. I checked the suspected cuts at 37.0, 58.4, 60.1 and 74.9 frame by frame; they are continuous camera moves or eyeline changes, not cuts. The 39.6 candidate is a subtitle change only.

| metric | value |
|---|---|
| shots | 18 |
| length | 77.60 s |
| mean / median shot length | 4.31 s / 3.88 s |
| min / max | 1.97 s (sw 10 compass insert) / 11.37 s (sw 7 walk-away) |

Shot sizes: CU 5 (including one insert) · MCU 3 · MS 2 · MWS 1 · WS 5 · EWS 2. Every cut is a straight cut; there are no dissolves.

The day→night time skip (sw 7→8 at 33.0) is a **hard cut carried by the grade change**: warm gold becomes moon-blue, with the moon in frame.

Dialogue (timing only; the replica has no text): lines at sw 0–4.4, 7.4–19.7, 19.9–21.2 (Mother), 21.4–24.7 and 37.9–39.6; no lines after 40 s.

## Script by beat

Rows S1–S7 are the sandwalk prequel and precede B1 in the combined demo. **Bold** shots are kept; struck-through shots are dropped (see target_cut).

| # | time | shots | what happens | purpose | cutting rhythm |
|---|---|---|---|---|---|
| S1 | sw 0.00–9.77 | **sw 1–2** | Profile CU of the Son with binoculars at sunset, the Mother soft behind him. He lowers them. POV EWS: the sun touching a horizon of dark dunes. | The plan: cross after dark, into danger. | Two long holds: 5.5 / 4.3 s. |
| S2 | sw 9.77–21.63 | ~~sw 3~~, **sw 4–6** | (Handheld: he stows the binoculars and explains — dropped.) Low silhouette two-shot by a rock outcrop, him fiddling with straps. OTS MCU: he looks up at her. Reverse MCU: she nods. | The method is agreed; she follows his lead. | 3.6 / 3.7 / 2.3 / 2.2 s, shot/reverse. |
| S3 | sw 21.63–33.00 | **sw 7** (trimmed to 21.63–29.63) | Steadicam follow from behind: he turns and sets off into the dunes, she follows, the light warming to gold. | Departure. | One 11.4 s breather (8.0 s kept). |
| S4 | sw 33.00–43.03 | **sw 8–11** | Hard cut to night: dirty two-shot from behind, both looking at a large moon. Son CU looks up at the sky, then down. Insert: compass in his palm. Mother CU, eyes closed, opens them and turns. | Night; navigation; fatigue. | 2.5 / 2.3 / 2.0 / 3.2 s. |
| S5 | sw 43.03–57.07 | ~~sw 12~~, **sw 13–14** | (WS rest stop with a dropped pack — dropped.) High-angle WS: both sand-walk in stutter-steps, spins and lunges. EWS: two specks under the moon. | The method seen for the first time; scale. | 4.9 / 4.6 / 4.5 s. |
| S6 | sw 57.07–69.90 | **sw 15–16** | Handheld climb up a steep dune; the camera swings from him to her clawing up behind. Follow WS: they sand-walk up the dune (drags, sideways kicks, freezes) and the moon tilts into frame. | Effort; the method has become routine. | 5.8 / 7.0 s. |
| S7 | sw 69.90–77.60 | **sw 17–18** | Son sits on the slope looking out, the Mother's hood soft in the foreground. Mother CU: lifts her bowed head into profile, looking screen-left. | Rest; hand-off to the attack. | 3.7 / 4.0 s. |
| B1 | 0.00–3.50 | 1–3 | The clip opens mid-scene. The Mother (low-angle MCU) stares back over her shoulder, then the Son (MCU) does the same. He wheels round and bolts, and the handheld camera lurches after him. Wide high angle: both plunge down a dune face. | Alarm, then the decision to run. | Very fast (0.75 / 1.29 / 1.46 s), reaction-to-reaction. |
| B2 | 3.50–16.02 | 4–6 | Locked-off EWS: two specks run left→right across a vast flat under a giant dune ridge (4.3 s). Long-lens tracking two-shot: they sprint straight at the lens while a dust wake rolls on the horizon between them (6.2 s). Reverse from behind: they head for the dark rocks (2.0 s). | Scale, exposure, the threat behind, the goal ahead. | Long holds that act as breathers inside the chase. |
| B3 | 16.02–25.65 | 7–11 | Running singles, Mother then Son (tele, tracking back). The Son passes the lens and reveals the dust wave. He has fallen: a low WS shows him sprawled, then scrambling up. Chaotic ground-level CU: bodies tangle, one hauls the other up, they lurch out of frame right, and the frame holds empty on the dust wave. Follow from behind toward the rocks. | Personal peril and the fall. | 1.5 / 1.8 / 1.5 / 3.4 / 1.5 s. |
| B4 | 25.65–30.16 | 12 | One long-lens tracking-back shot of the Son sprinting at the lens. A dome of sand swells behind him, he glances back, and the dome keeps growing. | Escalation through duration. | Single 4.5 s hold. |
| B5 | 30.16–39.96 | 13–19 | Crosscut. The Son runs from behind; the Mother reaches the rock and spins round. Her CU looking screen-left cuts to her POV: the worm breaches behind the running Son in a full-width dust explosion (2.9 s). He runs with his arm out toward her; her terrified CU; he dives onto the rock and rises. | The chase climaxes with the monster's first reveal. | Fastest stretch: 1.17 / 0.88 / 0.83 / 2.92 / 1.46 / 1.21 / 1.33 s. |
| B6 | 39.96–50.38 | 20 | Near-black EWS from behind the Son, a tiny silhouette at bottom centre. A wall of dust and worm body rises over him and slowly clears to show the rim of the maw. Sound drains away. | The gear change from action to awe. | A single 10.4 s hold. |
| B7 | 50.38–68.44 | 21–26 | Face-off. Son CU looking up, with the Mother soft behind him. EWS of the reared worm, maw to the lens, over two specks. Mother CU. Son MS, braced. Reverse OTS: the maw fills the frame, with his hooded head in the foreground. Son MCU. | Standoff in shot/reverse-shot. The Son stays put. | Even, slow: 2.6 / 3.9 / 1.6 / 2.8 / 4.3 / 2.9 s. |
| B8 | 68.44–81.25 | 27–29 | 8.6 s ECU POV drifting across the baleen-like filaments into the throat. Son MCU, tighter, eyes catching a glint, calm. The Mother turns her head to look at him. | The turn from fear to calm understanding. | Long, then medium, then a quick one: 8.6 / 3.0 / 1.25 s. |
| B9 | 81.25–92.38 | 30–32 | Deep two-shot: Son in front, Mother behind at the rock wall. The EWS of the worm repeats with an identical setup and holds 6 s. Mother CU looking up. | The standoff is held; tension through stillness. | 1.7 / 6.0 / 3.5 s. |
| B10 | 92.38–109.40 | 33–34 | Dirty frame through a rock gap: the worm's head slides down and its body sweeps left→right as it dives, then a wall of sand spray fills the gap (10.8 s). EWS aftermath: the pair at the foot of the rock, the dive's dust plume rising, a gust swallowing them (6.2 s). | Release and exhale. | Two long holds (10.8 / 6.2 s). |

## Editing grammar (must replicate)

1. **Two-speed structure.** The first 40 s are cut fast (median 1.46 s). After the dive onto the rock, the cutting flips to long holds (median 3.46 s, with 10.4 / 8.6 / 10.8 s takes). The hinge is the cut-on-action into shot 19 followed by the 10 s near-black shot 20. The demo must keep this hinge.
2. **No middle ground in scale.** EWS specks alternate directly with face CUs/MCUs. The worm only appears at EWS or as an ECU of the maw, never at medium scale. Humans and worm are never shown at a comparable size except in the OTS (shot 25).
3. **Threat staged in depth (Z-axis).** The runners come straight at a long lens, and the dust wake, mound or breach swells directly behind them (shots 5, 8, 12, 16). Lateral movement appears only once, in the EWS (shot 4). Several shots end when the subject exits frame and the empty frame shows the threat (shots 8, 10).
4. **Breathers inside the chase.** The fast cutting is broken by single long tele holds (6.2 s two-shot, 4.5 s mound) that let the size of the threat grow inside one shot.
5. **The Mother as audience proxy.** Her reaction CUs bracket each of the Son's beats: 32.2, 37.4, 56.8, 80.0, 88.9 s. In the chase her CU looking screen-left cuts straight to her POV of the breach (eyeline match).
6. **Progressive punch-in on the Son during the face-off:** CU looking up (21) → MS braced (24) → MCU (26) → tighter MCU, eyes to lens (28). His gaze moves from looking up and screen-left to looking into the lens.
7. **The worm is frontal and symmetric.** It is always facing the lens dead-on and centred (22, 25, 27, 31). Humans are shot from low angles, looking up.
8. **Repeated setups.** The EWS worm tableau is used twice with identical framing (22, 31). the Son's MCU is repeated (26, 28). The "from behind toward the rocks" follow is repeated (6, 11, 13, 17).
9. **Camera language by type.** Handheld for human-scale chaos (2, 7, 10, 13, 17). Smooth vehicle tracking-back on long lenses for runners (5, 8, 12). Locked-off for every scale and creature shot (4, 16, 20, 22, 31, 33, 34).
10. **Foreground occlusion for intimacy with the creature.** The OTS hood silhouette in front of the maw (25) and the out-of-focus rock framing the dive (33).
11. **Sound drop.** The full roar cuts out to near silence at the start of the face-off (~50 s) and returns on the dive (~93 s). Cut the picture to that envelope.
12. **Look.** 2.39:1, overcast flat light, desaturated teal-grey sand and sky, no sun or hard shadows. Many face shots are high-key against blown-out haze. The rise shot (20) is the one very dark moment.
13. **Sandwalk pacing (prequel).** The prequel is slower and even (median 3.9 s), with no fast cutting at all. That makes the attack's 1.5 s chase cutting land as a shock. Do not speed the prequel up.
14. **Sandwalk framing (prequel).**
    - Dialogue is covered in shot/reverse MCUs with a soft OTS foreground (sw 5/6).
    - Dirty frames with a foreground silhouette (sw 8, 10, 17) keep the two characters physically close.
    - EWS specks under the moon (sw 14) set up the attack's EWS specks (attack 4, 22, 31).
    - The method is shown twice, from two angles (high sw 13, behind sw 16), so it reads as deliberate without words.

## Recast (new, original identities; costumes stay close so the shots read the same)

Both characters wear half-masks over nose and mouth in every shot, so on screen their identity is mostly **eyes, brows and the edge of the hood**. Pin these features in the reference images.

- **The Son (young-noble role) → "Teo Amari".** 17, of mixed Ethiopian and Armenian heritage. Lean and long-necked, with warm medium-brown skin. Deep-set very dark brown eyes under heavy, straight black brows, and a thin pale scar nicking his left eyebrow. Close-cropped black curls, mostly hidden by the hood. Costume (keep): charcoal-grey hooded cloak-wrap over a dark ribbed desert survival suit, matte black half-mask with a small tube at the jaw, teal-green canvas backpack with chest straps.
- **The Mother (noblewoman role) → "Dr. Meera Lindqvist-Rao".** 44, of Tamil and Swedish heritage. Olive-tan skin, large dark-hazel almond eyes with fine crow's-feet, and thick dark brows. A single silver streak at the left temple shows at the hood edge. Costume (keep): cream/oatmeal gauze scarf wrapped over a grey hood and both shoulders, matte black half-mask, olive-grey survival suit with a utility vest.
- **The creature (not a person; optional differentiation).** A colossal sand-burrowing worm. For the shots to work it needs a circular maw ringed with thousands of pale radial filaments around a dark throat. To keep the design original, give it a basalt-plated hide with ochre mineral streaks instead of copying the film's exact skin.
- No other characters appear on screen.
- The sandwalk prequel uses the same two identities and costumes. The Son's mask reads as a ridged black respirator half-mask in the sunset close-ups (sw 1), so keep that detail. The binoculars and the palm compass are the only props.

## target_cut

**Combined demo = sandwalk (trimmed, 65.67 s, 16 shots) + attack 0–109.40 (109.40 s, 34 shots) = 175.07 s, 50 shots.** That is inside the 160–180 s target. Combined median shot length is 2.9 s, mean 3.5 s.

The attack clip alone (109.4 s) is a complete story but too short. An earlier draft guessed that a "dawn dig-out" beat would be the extension; this is replaced by the real preceding scene, the night sandwalk. The harvester beat is an unrelated, earlier sequence.

### Kept sandwalk shots (in/out in the sandwalk clip, then position in the combined demo)

| demo | src shot | sw in–out | dur | demo time | size |
|---|---|---|---|---|---|
| C1 | sw 1 | 0.000–5.500 | 5.50 | 0.00–5.50 | CU profile, binoculars |
| C2 | sw 2 | 5.500–9.767 | 4.27 | 5.50–9.77 | EWS sunset POV |
| C3 | sw 4 | 13.400–17.133 | 3.73 | 9.77–13.50 | WS silhouette two-shot |
| C4 | sw 5 | 17.133–19.433 | 2.30 | 13.50–15.80 | MCU OTS (Son) |
| C5 | sw 6 | 19.433–21.633 | 2.20 | 15.80–18.00 | MCU (Mother nods) |
| C6 | sw 7 | 21.633–29.633 (trimmed; source runs to 33.000) | 8.00 | 18.00–26.00 | MWS→WS walk-away |
| C7 | sw 8 | 33.000–35.500 | 2.50 | 26.00–28.50 | WS dirty, moon |
| C8 | sw 9 | 35.500–37.833 | 2.33 | 28.50–30.83 | CU looks up/down |
| C9 | sw 10 | 37.833–39.800 | 1.97 | 30.83–32.80 | CU insert, compass |
| C10 | sw 11 | 39.800–43.033 | 3.23 | 32.80–36.03 | CU Mother eyes closed→opens |
| C11 | sw 13 | 47.967–52.567 | 4.60 | 36.03–40.63 | WS high angle, sand-walk |
| C12 | sw 14 | 52.567–57.067 | 4.50 | 40.63–45.13 | EWS specks under moon |
| C13 | sw 15 | 57.067–62.867 | 5.80 | 45.13–50.93 | MS handheld climb |
| C14 | sw 16 | 62.867–69.900 | 7.03 | 50.93–57.97 | WS sand-walk, moon tilts in |
| C15 | sw 17 | 69.900–73.567 | 3.67 | 57.97–61.63 | MS Son resting (dirty) |
| C16 | sw 18 | 73.567–77.600 | 4.03 | 61.63–65.67 | CU Mother → profile screen-left |
| C17–C50 | attack 1–34 | 0.000–109.401 | 109.40 | 65.67–175.07 | as in `shots.json` |

Dropped:
- **sw 3** (9.77–13.40): a handheld explanation shot that only works with dialogue.
- **sw 12** (43.03–47.97): a rest stop that repeats sw 17.
- **sw 7 tail** (29.63–33.00): trimmed so the shot fits one ~8 s generation.

To land nearer 160 s, also drop sw 11 (−3.23) and trim sw 1 to 1.0–5.5 (−1.0), giving ~170.8 s. Keep sw 13 and sw 16: together they are the only picture-only explanation of the sand-walk.

### Night → morning transition (time skip; prequel C16 → attack C17)

Use a **hard cut**, the same grammar the film uses for its own day→night skip at sw 33.0. No dissolve or fade: neither clip has any.

- **Eyeline match on the Mother.** C16 ends on her moonlit profile looking screen-left over the dunes. C17 (attack shot 1) opens on her in the grey morning looking back over her shoulder, also screen-left. The same look, hours later, now alarmed.
- **Grade does the time skip.** Keep the prequel's night shots clearly blue-dark with the moon visible (C7, C12, C14). The attack opens flat overcast grey-cyan with no moon. Don't let the two grades converge, or the skip won't read.
- **Sound.** Pre-lap a low distant rumble ~0.5–1 s under the tail of C16, so the cut feels caused by a sound she hears.
- Optional: if the skip still reads as continuous, add one 2–3 s generated EWS at first light of the two specks walking, reusing C12's framing in a dawn grey grade. That makes 177–178 s, still within target. It is not in the film, so it's off by default.

### Dialogue-dependent moments and how picture alone carries them

| moment | relies on | picture-only solution |
|---|---|---|
| The line about crossing after dark in worm territory (C1–C2) | spoken plan | The binocular look → sunset POV, with the sun visibly on the horizon. The hard cut to moonlight (C7) pays it off. |
| Sand-walk explanation (sw 3, dropped) and the Mother's short yes (C5) | the explanation | The Mother's two clear nods in C5 carry her consent. The method itself is shown, not told (see below). |
| The Son telling her to follow and copy his moves (C6) | instruction | In the walk-away, make the Son's first steps visibly broken (stop, drag, skip) and have the Mother copy each move a beat later. |
| His line doubting the direction (C9) | spoken doubt | The compass-in-palm insert after he looks at the sky (C8) carries it. Keep the device clearly pointing; a faint glow is optional. |
| Why they walk oddly (never stated in these clips) | backstory | Show the gait twice (C11 high angle, C14 from behind). Then the attack opens with a look back at a threat, so the cause and effect reads. Optionally put one very faint rumble under C14. |

## Hard shots (for current T2V/I2V) and the closest simplification

| shot | why it's hard | simplification that keeps framing and timing |
|---|---|---|
| 16 breach behind runner (33.03–35.95) | Huge creature erupting, a dust explosion and a running human all in one take | I2V from a keyframe: locked-off long lens with the Son small at bottom centre running at the lens. Keep the worm mostly inside the dust, with only the arched maw rim and filaments visible at top centre. Let the dust do the motion. |
| 20 dark rise (39.96–50.38, 10.4 s) | Near-black and low contrast, and longer than one model clip | Generate brighter (normal exposure) as 2×5 s, or 5 s plus a hold extension, then grade down in post. Keep the tiny silhouette at bottom centre and only dust drift; reveal the maw rim at the end. |
| 25 maw OTS / 27 maw ECU (8.6 s) | Thousands of radial filaments flicker and morph; a long take | Build a clean keyframe of the maw first, then I2V with "static" or "very slow push" only. Make 27 two 4–5 s segments with a hidden cut on the filaments. Accept fewer, thicker filaments. |
| 10 tangled bodies (20.77–24.19) | Limbs tangling in extreme close-up and soft focus, which models garble | Ground-level static camera: the Son on one knee is pulled up by the Mother, they run out of frame right, and the frame holds 0.5 s on the dust wave. Keep the shallow focus and the empty-frame exit. |
| 9 fall and scramble (19.27–20.77) | Body physics in sand | Start the shot already on hands and knees, rise and run toward the lens. |
| 19 dive onto rock (38.62–39.96) | Fast full-body landing and rise | Start the shot as he lands crouched on the rock and rises turning right. The cut-on-action still reads. |
| 33 dive through rock gap (10.8 s) | A large textured body sweeping across, then a sand wall; long | Two segments: (a) the ridged body slides left→right behind a static out-of-focus rock, 5 s; (b) a sand-spray wall surges and whites out the gap, 5 s. Join them on the brightening. |
| 2 whip-follow bolt (0.75–2.04) | Handheld whip that follows a spinning body | Static MCU: he looks back, spins and drops out of frame bottom-right. Add the lurch as a quick camera shake or cut. |
| 4 / 22 / 31 / 34 EWS with specks | Tiny figures vanish or deform | Keep the figures at least 3–5% of frame height. For 22/31, generate one EWS plate and reuse it for both, as the film does. |
| 5 / 12 long-lens runners (6.2 s, 4.5 s) | Consistent run cycle plus a growing dust mound | "Camera tracking backward at subject speed". One clip each; if a model caps at 5 s, trim shot 5 to ~5 s. |
| sw 13 / sw 16 sand-walk gait (4.6 s, 7.0 s) | Models smooth any walk into a regular cycle; the deliberate stutter-step, drag, kick and freeze gets lost | Prompt explicit beats: "step, pause, drag foot, sideways kick, freeze, two quick steps". Split sw 16 into 2×3.5 s if needed, and keep the moon tilt-in for the second half. A fallback for sw 13 is a static high angle with a slow spin-and-stop by the Mother. |
| sw 15 handheld climb with camera swing (5.8 s) | Body on all fours on a steep slope, plus a camera that switches subject | Two segments joined on the swing: (a) the Son crawls up the slope in profile, 3 s; (b) the Mother crawls up behind him with his cloak as a soft wedge in the foreground, 3 s. |
| sw 7 walk-away (8.0 s kept) | Long Steadicam follow with a light change | One 8 s generation, or 5 s + 3 s split on the cloak flare. Do the gold warm-up in the grade, not the prompt. |
| sw 8 / sw 14 moon shots | Huge moon plus small second moon; very dark plates | Generate at normal exposure and grade down. A single moon is acceptable; keep it at top-right (sw 8) or top-centre (sw 14). |
| sw 1 binoculars to face (5.5 s) | Hand/prop interaction at CU | Start with the binoculars already lowering at ~1 s in; the profile hold carries the rest. |

General: generate wide, then crop to 2.39:1. Lock both characters with eye-region reference images, since the masks hide the rest of the face. Grade the attack shots to the flat teal-grey look so the cuts match. Use three separate grades for the prequel: warm sunset (C1–C5), golden walk (C6) and moon-blue night (C7–C16).
