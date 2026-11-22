# Wukong (2017): Monkey King and Erlang vs the Heavenly Lord, battlefield climax

Source: `wukongzhuan2017_battles.mp4` (a 376.30 s compilation of the battle scenes; all times below refer to it). Per-shot data: `shots.json` (88 entries).

## Where the battle starts and ends

- **Battle range: 176.65 s to 376.30 s (199.65 s).**
- **160.00–176.65 is not part of this battle.** It is the end of the palace-hall fight: the Monkey King in human form against Erlang, inside a hall with a giant armillary sphere. The Heavenly Lord walks into the hall at 171.62 and strikes him down.
- **176.65 is a hard jump in the compilation.** The location changes to the shattered volcanic plain, and the Monkey King is now in ape-faced battle form. The film material in between was left out of the compilation.
- **377 s: the clip ends.** The compilation stops in the middle of the last shot, at 376.30, while the colossus is impaled.
- **277.12 may hide a cut-out stretch of story.** Inside the battle, this is the only point where something may have been skipped: the duel's final explosion is followed directly by the Lord standing calmly. There is no jump to an unrelated scene anywhere inside the battle.
- **There is no giant-ape transformation in this window.** The Monkey King keeps his human-size ape form throughout. The "giant" elements are:
  - his staff, which grows to colossal size (first as the ram at 244–263, then summoned again at 284–311);
  - the Heavenly Lord's colossal armored avatar (280–376).
- **Format.** The picture is 2.39:1 scope, letterboxed inside 1280x720 (active area 1280x536). The source is 24 fps with 3:2 pulldown to 60 fps. Cut times are accurate to one source frame, about 0.04 s.

### Cut verification
- **Detector output.** PySceneDetect produced 126 shots for 176.65–376.30.
- **Merged.** 41 false splits from flashes, explosions, whip blur and strobing were merged.
- **Added.** 3 cuts the detector missed were added, at 210.15, 232.87 and 259.03.
- **Moved.** One cut was moved from 198.68 to 198.83.
- **Rule for flashes and whips.** A white or orange flash, or a whip-pan, stays inside one shot when the framing is the same on both sides. Examples: 199.30, 274.0, 292.2, and the whips in shots 62 and 70. It counts as a cut when the framing changes, for example 207.53 and 338.20.
- **Suggested split points.** For the three long one-takes I give `gen_split` times in `notes`. These are places to divide them for generation; they are not cuts in the film.

## Character and world bible (use these descriptions in every prompt)
- **Monkey King (battle form)**
  - Ape face with a wild golden-blond mane and sideburns.
  - Dark lacquered scale armor with a black cloak.
  - 2–3 ragged yellow triangular opera back-flags.
  - Red staff with gold-capped ends.
  - Human size.
- **Erlang**
  - Man with a black topknot and a glowing cyan third eye on his forehead.
  - White flowing robes over black-and-white striped lamellar chest armor.
  - Long black trident/halberd whose jagged blade glows electric blue.
- **Heavenly Lord**
  - Woman with a pale face and a tall black lacquered crown; the crown is pointed in later shots.
  - Black robes with huge sculpted winged shoulders, later a black scale-mail mantle with gold clasps.
  - Floats in the sky and commands giant black arrowhead blades and building-size carved stone swords.
- **Colossus (the Heavenly Lord's avatar)**
  - Kaiju-scale armored deity.
  - Gold-filigree halo of tendrils and ribs.
  - Layered red-gold scale skirt with gold vertical panels.
  - Round silver-teal helmet head with a horned crown.
  - Dark ridged faceplate with an amber eye glow.
  - Glowing cyan gem at the head and chest.
- **Giant staff**
  - The Monkey King's staff at colossal scale: red, ring- and spiral-banded, with gold bands.
  - Its end is a cracked, lava-veined cap that tapers into a drill point.
- **World**
  - Shattered volcanic plain of black basalt rubble with glowing ember and lava cracks, and smoke.
  - Pale teal-white overcast sky full of floating black rock fragments.
  - Huge broken stone chains criss-cross the sky.
- **Grade**
  - Desaturated teal and cyan with bleach-bypass contrast.
  - Orange ember and fire accents.
  - Sky shots are high-key; ground shots are low-key.

## Stats

| metric | value |
|---|---|
| total shots | **88** |
| total duration | 199.65 s |
| median shot length | **1.82 s** |
| mean shot length | **2.27 s** |
| shortest / longest | 0.33 s (#18) / 7.17 s (#70) |
| shot sizes | WS 36, MS 24, CU 11, EWS 6, MCU 6, MWS 4, ECU 1 |
| slow motion | **21 shots** (15 full slow-mo + 6 speed ramps) |
| angles | low 34, overhead/top-down 5 (#9, 23, 27, 54, 66), high 7, dutch 4 (#51–53, 79); the rest eye level / ground level |

## Beats

| # | time | shots | n | median | what it achieves | rhythm |
|---|---|---|---|---|---|---|
| 1 | 176.65–182.78 | 1–4 | 4 | 1.50 s | **Hero down, Lord above.** The Monkey King lies in rubble; an extreme wide reveals the Lord in the sky; she gives the order and fires a blade barrage. | Steady 1–2 s shots. Moves down→up→in (EWS→MS)→out (WS). |
| 2 | 182.78–193.17 | 5–9 | 5 | 1.13 s | **Barrage and survival.** Impacts, a run through the fire, a 5.5 s hold of him standing in the explosions, a giant stone sword dives, overhead shot of the tiny hero. | Fast (0.9–1.1 s) → **long hold #7 (5.5 s, fire ramps into slow-mo)** → fast. |
| 3 | 193.17–203.32 | 10–14 | 5 | 2.25 s | **Aerial counterattack.** He leaps and deflects blades, rides a flying giant blade, crash-lands, bursts out of a rock cluster, lands ready. | Longer action takes (2–3.4 s). Ramps on #10 and #13. |
| 4 | 203.32–211.37 | 15–21 | 7 | 1.08 s | **Erlang enters, standoff, charge, first clash.** | Very fast (0.3–0.6 s) around the clash, framed by a 2.25 s standoff and a 2.1 s dust pause. |
| 5 | 211.37–223.58 | 22–29 | 8 | 1.23 s | **Close duel exchanges.** Whip-pan cut, overhead, weapons crossing, sparks two-shot, telephoto wide, overhead again, fire/ice exchange. | Steady quick cutting (0.7–1.9 s); 2.6–2.9 s wides as breathers. No slow-mo. |
| 6 | 223.58–241.28 | 30–39 | 10 | 1.31 s | **Erlang's ice-wave special.** Wind-up, blade charge, drop and slam, ice hits the lens, the Monkey King braces, wave POV, he smashes ice, is engulfed, strains in close-up, the ice ridge dissolves into mist. | Slow-mo on the faces (#30, 34, 38). Ends on the **4.0 s aftermath hold #39**. |
| 7 | 241.28–263.73 | 40–49 | 10 | 1.73 s | **Giant-staff ram.** The staff end, grown huge, rolls in and rams Erlang; he is smashed, holds the force back (4.6 s over-the-shoulder), is pushed across the plain, and the push stalls (4.7 s). | Short shots (0.9–1.8 s) between **two long holds, #45 and #49**. |
| 8 | 263.73–277.12 | 50–54 | 5 | 2.80 s | **Grapple and final impact.** Monkey King at the trident, ape face ECU, hand over Erlang's face, 4 s slow-mo mid-air grapple, overhead white-flash explosion. | Almost all slow-mo / dutch angles. Ends on a smash-cut overhead explosion (3.25 s). |
| 9 | 277.12–297.98 | 55–61 | 7 | 2.95 s | **Both sides summon.** The Lord looks down, the colossus rises, the Monkey King's hand on the ground grows a fire orb (6.2 s), the orb becomes the staff, the colossus roars, he twirls the staff. | Slowest section; 3–6 s takes. |
| 10 | 297.98–311.87 | 62–66 | 5 | 2.03 s | **Staff becomes a bridge; ascent.** 5.6 s virtual fly-through of the staff growing, he runs up it, shot along the staff toward the gem, run plus slow-mo silhouette leap, top-down vertigo. | Long one-take, then 1–3.5 s. Ramp on #65. |
| 11 | 311.87–341.37 | 67–76 | 10 | 2.54 s | **Erlang assaults the colossus.** Extreme wide of the giant, aerial dash, flight, **7.2 s one-take** (crash, hurled boulder, giant's head hit), battle-cry MCU, extreme wide of tiny Erlang against the giant, slow-mo leap into the light, grinning close-up, crash zoom against the faceplate, chest-gem explosion. | Longest beat. Big takes (3.5–7 s) alternate with 0.9–1.8 s close-ups. Slow-mo on #73 and #74. |
| 12 | 341.37–356.15 | 77–81 | 5 | 3.50 s | **The Monkey King's drill strike.** He falls and rides the giant staff, its drill end hits the gem, he screams clinging on, the colossus head is driven back. | Long takes (3.5–4.5 s). Slow-mo on #79 and #80. |
| 13 | 356.15–376.30 | 82–88 | 7 | 2.33 s | **Impalement and the Lord's death.** The staff erupts upward (5.6 s), pierces the head, crown shatters, tip bursts through the body, the Lord's shocked MCU, her face disintegrates in light, the colossus collapses. | Slow-mo throughout (#82, 85–87). Ends on a white-out and the final wide, which is cut off. |

Overall shape: the duel half (beats 4–8, 203–277 s) is cut fast, with a median around 1.1–1.7 s. The giant half (beats 9–13, 277–376 s) slows to a median of 2.3–3.5 s, with long virtual one-takes. **Bigger scale gets longer shots.**

## Editing grammar (patterns to copy)

1. **Scale ladder around every big moment.** An extreme wide or overhead of a tiny figure against something huge (#2, 9, 27, 54, 67, 72), then a cut in to MS/CU. The giant half always establishes the colossus in a static extreme wide before close action (#67 before #68–76; #64 before #65).
2. **Wind-up → insert → payoff.** Character close-up or gesture, then a weapon or power insert, then a wide of the attack: #3→#4, #30→#31→#32, #57→#58, #59→#60–61.
3. **Every impact gets a strain or reaction close-up.** Usually slow-mo, 0.9–1.8 s: #33→#34, #37→#38, #42→#43, #78→#79, #85→#86→#87.
4. **Transitions hidden inside effects.** The editor rarely shows a clean cut at an impact:
   - fire engulfing the lens (#6→#7);
   - flash frames (#19, #76, #88; and inside #12, #54, #58);
   - foreground wipes by a rock (#12, #37), a back-flag (#40→#41), a robe (#74→#75), green debris (#77);
   - whip-pans (#22→#23, inside #62 and #70).
5. **Fixed screen geography.**
   - The Monkey King sits screen-left or bottom; the Lord, Erlang and the colossus sit screen-right or top.
   - Attacks travel right→left (blades #4–5, Erlang's charge #17–19, ice wave #32–37).
   - The Monkey King's counters travel left→right and upward (#11, #42, #46, #63–65, #78).
6. **Alternate sky and ground exposure on every cut.** High-key teal sky shots cut against dark ember-lit ground shots, so each cut lands with a jump in brightness (#4→#5, #9→#10, #11→#12, #16→#17, #66→#67).
7. **Rhythm: bursts and holds.** Bursts of 0.3–1.1 s shots around each clash are followed by one long hold of 3.5–7 s (#7, 39, 45, 49, 53, 57, 62, 70, 82). Every beat contains at least one shot of 3 s or more.
8. **Where slow motion goes.** Slow-mo is kept for faces under strain and for the death; ramps go on leaps (#10, 13, 65, 70) and on one punch (#51). Real speed is used for weapon contact.
9. **Mostly low angles and wide lenses (18–28 mm feel).** Telephoto is used only for two "observer" wides (#26, #39). Overhead top-downs mark the ends of exchanges.
10. **Color coding.** Orange fire is the Monkey King's power (fire orb, staff, explosions). Cyan is Erlang and the colossus. Teal-white sky belongs to the Lord. Keep this consistent in prompts.

## Hardest shots for current text/image-to-video, and the simplest stand-in that keeps the timing

| shot(s) | why it is hard | simplest stand-in that keeps the duration and cut |
|---|---|---|
| #62 staff growth (5.6 s, two whip-pans) | object grows at scale + camera whips | Split at the suggested points 300.30 and 301.90: (a) ground-level glide as a red pillar swells away from the camera, 2.3 s; (b) static sky with chains and debris, 1.6 s; (c) camera riding on top of a red pillar rising into the sky, 1.7 s. Join with 4–6-frame motion-blur whips in the edit. |
| #70 Erlang one-take (7.2 s) | many events, whips, character continuity | Dropped in `target_cut`. If kept, split at 324.05 and 326.85 into: Erlang crash and roll; boulder hits the giant's head; tilt down to the ember ground. |
| #77 fall, grab and ride the staff (4.5 s) | character interacting with a moving giant object | Split at 341.95 (green debris wipe): a wide of a tiny figure on the staff end plus an explosion; then a reused #79-style shot of the Monkey King clinging to a red surface, with a wind/blur background plate. |
| #56 colossus forming | assembly / morph | Slow tilt-up through fog and light rays revealing still golden armor, with drifting particles. Fade the fog to suggest formation. |
| #87 face disintegration | identity-locked face plus particle break-up | Image-to-video from a close-up of the Lord ("cracks of light spread, face crumbles into glowing particles"), or a still CU with an overlay light burst; end on a 4-frame white-out (that white-out is the cut into #88). |
| #11 riding a flying carved blade | character on a fast-moving giant prop | Environment-only shot of a giant stone blade skimming lava ground with a tiny silhouette on top; push into the carved surface with sparks (the sparks can be a separate close-up insert). |
| #10 aerial deflection | choreography against falling objects | Slow-mo leap with a staff swing silhouetted against the sky, debris drifting; skip the contact. |
| #44, #46–47 Erlang smashed and pushed | contact with a giant object, heavy blur | #44: striped black-white blur with cyan flashes (no contact needed). #46: environment-only red pillar plowing through rubble. #47: Erlang skidding with heavy motion blur. |
| #52–53 hand over the face; mid-air grapple | two-character physical contact | #52: Erlang close-up recoiling with only a furry hand edge in the foreground. #53: slow-mo two-shot with crossed weapons and almost no body motion. |
| #82–85 staff piercing the colossus | kaiju-scale destruction | Generate each as a separate still and animate it with a slow push. Destruction reads from debris drifting outward plus a cyan flare; the cut rhythm (5.6 / 2.0 / 2.4 / 3.9 s) carries it. |
| #75 crash zoom into the faceplate | in-camera crash zoom | Generate a static shot of a tiny Erlang on a giant faceplate; do the crash zoom and radial blur in post at 337.8. |

Easy wins (one subject, simple motion): #2, 3, 15, 16, 20, 30, 39, 40, 55, 57, 59, 67, 71, 74, 86.

## target_cut (about 165 s version)

Goal: 150–180 s that still reads as one continuous fight. The giant elements are kept: the staff ram, the staff summoning and growth, the colossus and the climax. Only repetitive duel exchanges are removed, and only as whole beats or whole sub-beats.

**Drop (3 blocks, 34.70 s, 15 shots):**
- **Beat 5, shots 22–29 (211.37–223.58, 12.22 s).** The second round of trades repeats beat 4's clash. Shot 21 (Monkey King rises, ready) flows straight into shot 30 (Erlang raises the trident for his special).
- **Beat 7b, shots 46–49 (253.37–263.73, 10.37 s).** A second "push and hold" that repeats #42–45. Shot 45 (Erlang holding back the giant staff) cuts to shot 50 (the Monkey King now at the trident shaft).
- **Beat 11b, shots 70–72 (320.95–333.07, 12.12 s).** A second "Erlang flies at the giant" pass, and the hardest one-take to generate. Shot 69 (Erlang flies at the colossus) cuts to shot 73 (his slow-mo leap into the light).

**Keep these shot ranges:** 1–21, 30–45, 50–69, 73–88.

| | full | target_cut |
|---|---|---|
| shots | 88 | **73** |
| duration | 199.65 s | **164.95 s** |
| median / mean shot length | 1.82 / 2.27 s | 1.83 / 2.26 s |
| slow-mo shots | 21 | 20 |

The cutting rhythm is kept: the median and mean barely move, and every remaining beat keeps its long hold. If a version nearer 150 s is needed, shorten long holds inside their shots rather than dropping more beats: #7 5.5→4 s, #57 6.2→4 s, #62 5.6→4.5 s, #82 5.6→4 s, #39 4.0→3 s. That gives about 157 s.
