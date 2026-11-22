# film-crew

**English** · [中文](README.md)

The tools a coding agent uses around the [film-director](../../skills/film-director) skill. The skill is the method: how to plan, shoot and cut a film. film-crew does the work around it: it calls the video and image models, shows the run while it is shooting, and afterwards shows people what each shot was fed and what came out.

It installs in one step. It also works without the skill: anything that writes the two hand-off files below can use it.

## What is inside

| Part | What it does | Start with |
| --- | --- | --- |
| `backends/` | Takes a job sheet (a JSON file that says what one generation needs) and calls the model's official API. `request` prints the exact request and sends nothing. Each model has a capability card: what it accepts, clip length, reference images, price. | [backends/overview.md](backends/overview.md) |
| `viewer/` | Turns a film's run folder into web pages. While shooting, a progress page where every generation is playable, with time and money so far. After the cut, a showcase (each shot's inputs next to its seconds in the film) and a node graph (what fed what). | [viewer/overview.md](viewer/overview.md) |
| `comfyui/` | Opens each shot in ComfyUI as one workflow: the images it used → its keyframes → one video node that plays the shot. Replay only. Keyframes, clips and reference images stay in the Assets panel for a person to reuse. | [comfyui/overview.md](comfyui/overview.md) |
| `formats/` | The two hand-off files, their checkers, and the script that reads a run folder into a shots manifest. | [formats/overview.md](formats/overview.md) |

The four parts talk to each other only through two files:

- **Job sheet**: what one generation needs (prompt, images, seconds, size, model). The agent writes it and `backends/` reads it.
- **Shots manifest**: what every shot of a film used and what came out. `formats/read_run.py` writes it from the run folder; `viewer/` and `comfyui/` read it.

Agents start from [SKILL.md](SKILL.md). The files an agent reads (`SKILL.md` and each `overview.md`) are written in Chinese.

## Install

**Claude Code:**

```bash
claude plugin install film-crew --marketplace memoryoffish/film-director-skill-plugin
```

The command adds the repo as a plugin marketplace if it is not added yet, then installs. If your Claude Code does not know `--marketplace`, run `claude plugin marketplace add memoryoffish/film-director-skill-plugin`, then `claude plugin install film-crew@film-director`.

**Other agents.** Copy or link `plugins/film-crew` into the agent's skills directory, for example `~/.claude/skills/` or `~/.agents/skills/`.

**Requirements.** Python 3.10+ and ffmpeg. The showcase page also needs Pillow. `comfyui/` needs your own ComfyUI. Sending jobs to another machine (`send`) needs ssh, and tmux on that machine.

**Keys.** Each adapter reads its key from an environment variable and never prints or stores it. Nothing in this repo holds a key. `request` works without any key.

| Models | Official API | Key |
| --- | --- | --- |
| Wan 3.0, HappyHorse 1.1 | Alibaba Cloud Model Studio (DashScope) | `DASHSCOPE_API_KEY` |
| Seedance 2.5, Seedance 2.0 | Volcengine Ark | `ARK_API_KEY` |
| MiniMax H3-Max | MiniMax | `MINIMAX_API_KEY` |
| gpt-image 2.6 | OpenAI Images | `OPENAI_API_KEY` |

The default addresses are the official ones. To use another region or site, set `DASHSCOPE_BASE_URL`, `ARK_BASE_URL`, `MINIMAX_BASE_URL` or `OPENAI_BASE_URL`.

## Use

`<crew>` is this folder. `<project>` is the folder the film is made in.

1. **Start the progress page** when shooting starts, and leave it running in tmux:

   ```bash
   python3 <crew>/viewer/scripts/progress.py <page folder> --jobs <project>/clips \
       --prices <crew>/backends/cards/prices.json --every 60
   ```

2. **Generate.** Write one job sheet per generation into `<project>/jobs/` (video) or `<project>/jobs_img/` (image). Look at the request first, then run it:

   ```bash
   cd <project>
   python3 <crew>/backends/scripts/filmgen.py request jobs/v01.json   # prints what would be sent
   python3 <crew>/backends/scripts/filmgen.py run jobs/v01.json       # the clip lands in clips/
   ```

3. **After the cut, write a shot table** `meta.json` in the run folder: the name of each shot, where it starts and ends in the film, and which job it came from. The film skill does not write this file by itself. The format is in [formats/overview.md](formats/overview.md). Then read the run into a manifest:

   ```bash
   python3 <crew>/formats/read_run.py films.json --out manifests/
   python3 <crew>/formats/check_manifest.py manifests/*.shots.json
   ```

4. **Show it.**

   ```bash
   python3 <crew>/viewer/scripts/console.py manifests/*.shots.json site/           # web page: the showcase
   python3 <crew>/comfyui/scripts/shots2comfy.py manifests/*.shots.json --comfy <ComfyUI folder>
   ```

   The node graph on the web page is drawn from the workflow files `shots2comfy.py` writes. To get it, run `shots2comfy.py` first, then give `console.py` the option `--workflows <ComfyUI folder>/user/default/workflows/filmkit`.

Options, what to install and what to check after each step are in that part's `overview.md`.

## What has been run

| Part | Status |
| --- | --- |
| backends: Wan 3.0 | Run with a real key through the official API (2026-11-22). |
| backends: gpt-image 2.6 | Run through an OpenAI-compatible gateway (2026-11-22). Not yet run against api.openai.com itself. |
| backends: HappyHorse 1.1, Seedance 2.5 / 2.0, MiniMax H3-Max | Written from the official docs. The request format was checked offline. Not yet run with a real key through these adapters. |
| viewer | Offline tests pass. The pages were checked by eye on a desktop window and at phone width. |
| comfyui | Checked in a real ComfyUI 0.46.0 with frontend 1.59.6. A newer frontend needs the check script run again. |
| formats | The checkers pass on the examples in `formats/examples/`. |

## Limits

- The viewer and ComfyUI need the shot table `meta.json`, which has to be written after the cut.
- The manifest is read from the run folder by file names. Retakes, and which keyframe belongs to which shot, are recognised that way.
- `comfyui/` only replays. Editing a prompt there and pressing Run generates nothing. To change a shot, tell the agent.
- The backends send local files only. Volcengine Ark takes a reference video only as a public URL, so the Ark adapter refuses a sheet that has one.

## License

[Apache-2.0](../../LICENSE).
