# 每条规则配一个真实见过的例子（2026-11-10 在 Freesound 上抓到的结果卡片，字段原样）。
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import refsound as R  # noqa: E402

CC0, BY = "Creative Commons 0", "Attribution"
LIC = [CC0, BY]
OWL = {"queries": ["owl hoot"], "must": [["owl", "owls"]], "reject": ["music", "screech"], "dur": [1, 60], "kind": "event"}
SLAM = {"queries": ["door slam"], "must": [["door"], ["slam", "slamming", "slams", "slammed"]], "reject": ["car"], "dur": [0.3, 15], "kind": "event",
        "skip": ["lowfreq"]}
RAIN = {"queries": ["rain"], "must": [["rain", "raining"]], "reject": ["thunder"], "dur": [10, 240], "kind": "continuous", "skip": ["ambient"]}
FIRE = {"queries": ["fire crackling"], "must": [["fire", "campfire"], ["crackle", "crackling"]], "reject": [], "dur": [10, 240],
        "kind": "continuous", "skip": ["ambient"]}
THUNDER = {"queries": ["thunder"], "must": [["thunder"]], "reject": ["music"], "dur": [2, 60], "kind": "event", "skip": ["lowfreq", "tail"]}
CLOCK = {"queries": ["clock ticking"], "must": [["clock"], ["tick", "ticking"]], "reject": ["alarm"], "dur": [8, 240], "kind": "continuous"}
CORK = {"queries": ["cork pop"], "must": [["cork"], ["pop", "pops", "popping"]], "reject": ["champagne"], "dur": [0.2, 10], "kind": "event"}


def card(**kw) -> dict:
    base = {"id": 1, "title": "", "username": "u", "duration_s": 5.0, "downloads": 100, "tags": [], "uploaded": "January 2020", "year": 2020.0,
            "rating": 4.5, "n_ratings": 10, "license": CC0, "description": ""}
    return {**base, **kw}


def test_most_downloaded_hit_is_a_lip_pop() -> None:
    # 查「cork pop」下载量第一（62489 次，381 人评 4.4）：上传者自己说是用嘴唇做的
    c = card(id=202230, title="Pop sound", duration_s=0.65, downloads=62489, tags=["cork", "pop", "wine"], rating=4.4, n_ratings=381,
             description="A pop sound made with my lips, could be a cork coming out of a wine bottle.")
    assert "只是像" in R.vet(c, CORK, LIC)


@pytest.mark.parametrize("sound,c", [
    (FIRE, card(title="Fire under the rain (Crackling the pillow sound)- from Baver", duration_s=21.3, tags=["crackling", "fire", "fireplace"],
                description="this is recorded by the crackling the pillow. Sounds like a fire under the rainy weather.")),
    (THUNDER, card(title="Thunder.wav", duration_s=30.0, tags=["boom", "rumble"],
                   description="Shaking zinc to create a rumble, similar to thunder. Recorded using a Rode NT5 microphone in a sound booth.")),
    (RAIN, card(title="8-bit light rain.wav", duration_s=51.3, tags=["game", "light"],
                description="A sound made in Famitracker that could be used to portray a light rain.")),
])
def test_description_says_it_only_resembles_the_source(sound: dict, c: dict) -> None:
    assert "只是像" in R.vet(c, sound, LIC)


def test_usage_hint_without_source_word_is_not_a_hedge() -> None:
    c = card(title="Rain on window", duration_s=60.0, tags=["rain"], description="Steady rain on a window. Could be used for a cozy scene.")
    assert R.vet(c, RAIN, LIC) is None


def test_vocalized_imitation_is_rejected() -> None:
    c = card(title="Clock ticking", duration_s=11.5, tags=["clock", "ticking"], rating=None, n_ratings=0,
             description="This is the sound effect of an old clock ticking that I vocalized.")
    assert "模仿" in R.vet(c, CLOCK, LIC)


def test_source_word_must_be_in_title_or_tags() -> None:
    # 查「owl hoot」下载量第一（23038 次）：一段森林环境声，标题和标签里没有 owl
    c = card(id=70100, title="eerie_forest.mp3", duration_s=445.1, downloads=23038, tags=["ambience", "atmosphere", "birds", "crickets"],
             rating=4.5, n_ratings=342, license=BY)
    assert "没有写明声源" in R.vet(c, OWL, LIC)


def test_many_raters_and_low_average_is_rejected() -> None:
    c = card(id=266440, title="door slam", duration_s=1.03, downloads=1345, tags=["bang", "door", "slam"], rating=1.8, n_ratings=56,
             description="door slam is a sample of a door slam: the door slammed shut with a bang.")
    assert "分却低" in R.vet(c, SLAM, LIC)


def test_phone_recording_kept_when_many_listeners_rate_it_high() -> None:
    c = card(id=465697, title="Owl Hoot", duration_s=4.39, downloads=15437, tags=["animal", "forest", "hoot"], rating=4.7, n_ratings=170,
             description="A hooting owl. Recorded with mobile phone.")
    assert R.vet(c, OWL, LIC) is None
    assert "低保真" in R.vet({**c, "n_ratings": 6}, OWL, LIC)


def test_ambience_words_rejected_unless_the_sound_is_an_ambience() -> None:
    c = card(title="Owl in the city park", tags=["owl"], description="Owl calling, with traffic in the background.")
    assert "不符" in R.vet(c, OWL, LIC)
    assert R.vet(card(title="Rain", duration_s=60.0, tags=["rain", "ambience"]), RAIN, LIC) is None


def test_excluded_ids_and_licence() -> None:
    c = card(id=7, title="Owl hoot", tags=["owl"])
    assert "排除清单" in R.vet({**c, "excluded": "已用过"}, OWL, LIC)
    assert "许可" in R.vet({**c, "license": "Attribution NonCommercial"}, OWL, LIC)


def test_hyphenated_gear_names_are_recognised() -> None:
    assert R.signals(card(description="Recorded with an Audio-Technica AT2020, 24-bit."), 2026.0)["gear"]


def test_rating_count_outweighs_average() -> None:
    many = R.signals(card(rating=4.4, n_ratings=380), 2026.0)
    few = R.signals(card(rating=4.9, n_ratings=6), 2026.0)
    assert many["bayes_rating"] > few["bayes_rating"]


def test_downloads_are_discounted_by_age() -> None:
    old = R.signals(card(downloads=5000, year=2008.0), 2026.0)
    new = R.signals(card(downloads=5000, year=2024.0), 2026.0)
    assert new["score"] > old["score"]


def measures(**kw) -> dict:
    base = {"duration_s": 5.0, "peak": 0.9, "clip_fraction": 0.0, "active_fraction": 0.9, "tail_fraction": 0.1,
            "energy_share": {"<100Hz": 0.1, "100-500Hz": 0.4, "500-2kHz": 0.3, "2k-8kHz": 0.2, ">8kHz": 0.0}}
    return {**base, **kw}


def test_short_event_with_short_tail_passes_but_long_dead_tail_fails() -> None:
    assert R.judge(measures(duration_s=0.4, tail_fraction=0.67), CORK) is None
    assert "尾巴" in R.judge(measures(duration_s=2.75, tail_fraction=0.85), SLAM)
    assert R.judge(measures(duration_s=16.0, tail_fraction=0.67), THUNDER) is None


def test_low_frequency_rule_depends_on_the_sound() -> None:
    low = measures(energy_share={"<100Hz": 0.9, "100-500Hz": 0.1, "500-2kHz": 0.0, "2k-8kHz": 0.0, ">8kHz": 0.0})
    assert "100 Hz" in R.judge(low, OWL)
    assert R.judge(low, SLAM) is None


def test_continuous_sound_must_be_active_most_of_the_time() -> None:
    assert "活动比例" in R.judge(measures(duration_s=30.0, active_fraction=0.3), RAIN)
    assert R.judge(measures(duration_s=30.0, active_fraction=0.3, tail_fraction=0.0), {**OWL, "dur": [1, 60]}) is None


def test_parse_reads_the_signals_from_a_result_card() -> None:
    page = ('<div class="bw-search__result"><div data-sound-id="42" data-title="Door &amp; slam" data-username="amy" data-duration="1.5" '
            'data-num-downloads="321" data-samplerate="48000.0" data-mp3="https://cdn/42-lq.mp3"></div>'
            '<span title="License: Creative Commons 0"></span><div aria-label="Average rating of 4.4"></div>'
            '<span class="bw-rating__count">(12)</span><a href="/browse/tags/door/">door</a><span>March 3rd, 2021</span>'
            '<div class="max-h-60px x"> A <b>door</b> slammed. </div></div>')
    (r,) = R.parse(page)
    assert (r["id"], r["title"], r["downloads"], r["rating"], r["n_ratings"], r["license"]) == (42, "Door & slam", 321, 4.4, 12, CC0)
    assert r["tags"] == ["door"] and r["uploaded"] == "March 2021" and r["preview"].endswith("-hq.mp3") and r["description"] == "A door slammed."


@pytest.mark.parametrize("patch,msg", [({"kind": "loop"}, "kind"), ({"dur": [5]}, "dur"), ({"skip": ["wind"]}, "skip"), ({"must": []}, "must")])
def test_spec_is_validated(tmp_path: Path, patch: dict, msg: str) -> None:
    p = tmp_path / "spec.json"
    p.write_text(json.dumps({"sounds": {"owl": {**OWL, **patch}}}), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        R.load_spec(str(p), None)
    assert msg in str(e.value)


@pytest.mark.skipif(R.np is None or __import__("shutil").which("ffmpeg") is None, reason="要 numpy 与 ffmpeg")
def test_revet_then_check_offline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    # 两条假的预览：一条从头响到尾，一条只有开头 2 秒有声；不联网走完 search --revet 与 check
    import subprocess
    out = tmp_path / "out"
    (out / "previews" / "rain").mkdir(parents=True)
    for i, src in ((11, "anoisesrc=d=12:c=pink:a=0.3"), (12, "anoisesrc=d=2:c=pink:a=0.3,apad=whole_dur=12")):
        subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", src, "-ar", "48000", str(out / "previews" / "rain" / f"{i}.mp3")], check=True)
    rows = [card(id=11, title="Steady rain", username="a", duration_s=12.0, downloads=900, tags=["rain"], license=BY),
            card(id=12, title="Rain starts", username="b", duration_s=12.0, downloads=5000, tags=["rain"]),
            card(id=13, title="Rain and thunder", username="c", duration_s=12.0, downloads=9000, tags=["rain", "thunder"])]
    (out / "candidates.json").write_text(json.dumps({"rain": {"candidates": rows, "fetched": "2026-11-10", "now_year": 2026.86}}), encoding="utf-8")
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"n": 5, "sounds": {"rain": RAIN}}), encoding="utf-8")
    monkeypatch.setattr(R, "fetch", lambda url, tries=3: pytest.fail("不该联网"))
    for cmd in ("search", "check"):
        monkeypatch.setattr(sys, "argv", ["refsound.py", cmd, str(spec), str(out)] + (["--revet"] if cmd == "search" else []))
        R.main()
    cands = R.read(out / "candidates.json")["rain"]
    assert cands["kept"] == [12, 11] and "不符" in next(r for r in cands["candidates"] if r["id"] == 13)["rejected"]
    sel = R.read(out / "selection.json")["rain"]
    assert [f["freesound_id"] for f in sel["files"]] == [11] and sel["files"][0]["credit"].endswith("CC BY")
    assert "活动比例" in R.read(out / "checks.json")["rain"]["12"]["rejected"]
    assert "| 3 | 2 | 2 | 1 | 1 |" in (out / "TABLE.md").read_text(encoding="utf-8")
    assert "署名" in capsys.readouterr().out


@pytest.mark.parametrize("url", ["file:///etc/hosts", "http://freesound.org/x.mp3", "https://example.com/x.mp3", "https://freesound.org.evil.com/x"])
def test_fetch_only_talks_to_freesound_over_https(url: str) -> None:
    with pytest.raises(ValueError):
        R.fetch(url)


@pytest.mark.parametrize("description", [
    "This is actually NOT a cork, it is a bottle cap.",
    "It isn't really a cork but it works.",
])
def test_description_denies_the_source(description: str) -> None:
    c = card(title="Cork pop", duration_s=1.0, tags=["cork", "pop"], description=description)
    assert "不是这种声音" in R.vet(c, CORK, LIC)


def test_fake_is_rejected_wherever_it_appears() -> None:
    c = card(title="Cork pop", duration_s=1.0, tags=["cork", "pop"], description="This was actually fake, made in a studio for a game.")
    assert "模仿" in R.vet(c, CORK, LIC)


def test_must_words_do_not_match_longer_unrelated_words() -> None:
    c = card(title="Opening a wine bottle with a corkscrew", duration_s=3.0, tags=["wine", "bottle"], description="Corkscrew squeaks, then a pop.")
    assert "没有写明声源" in R.vet(c, CORK, LIC)
    assert R.has("classical music from a school", ["class"], R.VERB) == []
    assert R.has("two owls hooting", ["owl", "hoot"], R.VERB) == ["owl", "hoot"]


def test_reject_words_also_match_plurals() -> None:
    c = card(title="Door slam", duration_s=2.0, tags=["door", "slam"], description="Two cars pass outside, then a door slams loudly.")
    assert "不符" in R.vet(c, SLAM, LIC)


def test_phone_recording_of_a_mouth_imitation_is_not_trusted() -> None:
    c = card(title="Owl hoot", tags=["owl"], rating=4.7, n_ratings=170,
             description="Owl hoot recorded with my phone while I imitated it with my mouth.")
    assert "模仿" in R.vet(c, OWL, LIC)


def test_measure_survives_clips_shorter_than_one_frame() -> None:
    for n in (0, 100, 4799):
        m = R.measure(R.np.full((n, 2), 0.5))
        assert m["duration_s"] == round(n / R.SR, 2) and m["tail_fraction"] == 0.0


@pytest.mark.parametrize("patch", [{"reject": "car"}, {"queries": "owl hoot"}, {"must": [["owl", 3]]}, {"dur": ["1", 60]}])
def test_spec_types_are_validated(tmp_path: Path, patch: dict) -> None:
    p = tmp_path / "spec.json"
    p.write_text(json.dumps({"sounds": {"owl": {**OWL, **patch}}}), encoding="utf-8")
    with pytest.raises(SystemExit):
        R.load_spec(str(p), None)


def test_revet_keeps_exclusions_and_check_survives_a_missing_preview(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "out"
    (out / "previews" / "owl").mkdir(parents=True)
    rows = [card(id=1, title="Owl hoot", username="a", downloads=900, tags=["owl"], preview="https://cdn.freesound.org/previews/1-hq.mp3"),
            card(id=2, title="Owl call", username="b", downloads=500, tags=["owl"], preview="https://cdn.freesound.org/previews/2-hq.mp3")]
    (out / "candidates.json").write_text(json.dumps({"owl": {"candidates": rows, "fetched": "2026-11-10", "now_year": 2026.86}}), encoding="utf-8")
    spec, ex = tmp_path / "spec.json", tmp_path / "used.json"
    spec.write_text(json.dumps({"sounds": {"owl": OWL}}), encoding="utf-8")
    ex.write_text(json.dumps({"1": "已用过"}), encoding="utf-8")

    def offline(url: str, tries: int = 3) -> bytes:
        raise OSError("没有网络")

    monkeypatch.setattr(R, "fetch", offline)
    for extra in (["--exclude", str(ex)], []):      # 第二次不带 --exclude，1 号也不能放回来
        monkeypatch.setattr(sys, "argv", ["refsound.py", "search", str(spec), str(out), "--revet"] + extra)
        R.main()
        by_id = {r["id"]: r for r in R.read(out / "candidates.json")["owl"]["candidates"]}
        assert "排除清单" in by_id[1]["rejected"] and "下载不了" in by_id[2]["rejected"]
    cands = R.read(out / "candidates.json")
    assert cands["owl"]["kept"] == []
    cands["owl"]["kept"] = [2]      # 清单说有预览，文件却不在
    by_id[2]["preview_file"] = "previews/owl/2.mp3"
    cands["owl"]["candidates"] = list(by_id.values())
    (out / "candidates.json").write_text(json.dumps(cands), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["refsound.py", "check", str(spec), str(out)])
    R.main()
    assert "解不出来" in R.read(out / "checks.json")["owl"]["2"]["rejected"] and R.read(out / "selection.json")["owl"]["files"] == []


def test_onboard_mics_of_a_named_recorder_are_fine_and_usage_hints_are_not_ambience() -> None:
    c = card(title="school break noise outdoor.wav", duration_s=60.0, tags=["children", "playing", "school"],
             description="The children are playing in the school yard. Recorder Sony M10 internal mics.")
    kids = {"queries": ["kids"], "must": [["children", "kids"]], "reject": [], "dur": [10, 240], "kind": "continuous", "skip": ["ambient"]}
    assert R.vet(c, kids, LIC) is None
    assert "低保真" in R.vet({**c, "description": "Recorded with the internal mic of my laptop."}, kids, LIC)
    dog = {"queries": ["dog bark"], "must": [["dog"], ["bark", "barking"]], "reject": [], "dur": [0.5, 60], "kind": "event"}
    bark = card(title="Dog Bark 9", tags=["animal", "bark"], description="This is a dog barking sound. It's perfect for movies, games.")
    assert R.vet(bark, dog, LIC) is None


def test_long_ambience_words_are_caught_inside_compound_words() -> None:
    # 一条真实卡片：民俗节的现场录音，标题把 festival 连写在别的词里
    acc = {"queries": ["accordion waltz"], "must": [["accordion"]], "reject": ["band"], "dur": [8, 240], "kind": "continuous"}
    c = card(id=391806, title="Folkfestival (indoors).wav", duration_s=188.0, tags=["accordion", "dance", "folk"])
    assert "festival" in R.vet(c, acc, LIC)
    assert R.vet(card(title="Accordion-music-clean.wav", duration_s=107.0, tags=["accordion"]), acc, LIC) is None
