"""python3 -m pytest -q -p no:cacheprovider tests/   (no network, no Blender)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import jobs


def unit(extra):
    shots = [(0, 3.5, "全景，固定机位", "阿杰在画面左边。"), (3.5, 6.1, "中景", "两人击掌。")]
    return jobs.unit_job("u", shots, ["风格：写实。", "人物：阿杰。", "声音：没有配乐。"], ["阿杰", "小周"], ["a.png", "b.png"],
                         jobs.wm_guide(3, 2, "蓝色人偶就是阿杰"), 1, 7, extra_refs=extra)


def test_unit_prompt_has_schedule_refs_and_guide():
    p = unit(["s1.png", "s2.png"])["prompt"]
    assert "本单元共 2 个镜头，剧情时长 6.10 秒" in p
    assert "镜头2｜3.50–6.10 秒｜机位与景别：中景｜以“硬切”从上一镜头切入" in p
    assert "图1是阿杰，图2是小周" in p
    assert p.strip().split("\n")[-1].startswith("图3、图4依次是镜头1、镜头2开头的白模站位示意图")


def test_unit_reference_order():
    assert unit(["s1.png", "s2.png"])["reference_images"] == ["a.png", "b.png", "s1.png", "s2.png"]


def test_shot_prompt_is_slim():
    j = jobs.shot_job("s", "近景，手把钥匙插进门锁。", "声音：咔哒一声。", "k.png", 2, 4, last_frame="k2.png")
    assert j["prompt"].count("\n") == 2 and "不切镜" in j["prompt"]
    assert j["first_frame"] == "k.png" and j["last_frame"] == "k2.png" and "reference_images" not in j


def test_one_shot_guides_do_not_talk_about_a_unit():
    assert jobs.wm_guide(3, 1, "蓝色人偶就是阿杰").startswith("图3是这个镜头开头的白模站位示意图")
    assert jobs.key_guide(3, 1).startswith("图3是这个镜头开头的画面参考")
    assert "依次" not in jobs.wm_guide(3, 1, "x") + jobs.key_guide(3, 1) + jobs.video_guide(1, "x")


def test_multi_shot_guides_unchanged():
    assert jobs.video_guide(3, "蓝色替身是阿杰") == (
        "视频1是这个单元的白模预演（3 个镜头，切点和上面的时间表一致），只用来定每个镜头的机位、运镜、构图、站位、走位的路线和先后、切点：蓝色替身是阿杰。"
        "人偶只表示位置和朝向，不提供肢体动作：不要把人偶、白模的纯色质感、滑行和僵硬的姿势画进成片，人按真人自然地走和动；"
        "人和东西的样子用参考图，场景和光按文字写的来；最终画面正常彩色。")
    assert jobs.key_guide(4, 2).startswith("图4、图5依次是镜头1、镜头2开头的画面参考")


def test_ref_job_single_shot():
    g = jobs.video_guide(1, "蓝色替身是阿杰") + jobs.still_guide(3, "蓝色人偶是阿杰")
    j = jobs.ref_job("r", "全景，固定机位。阿杰走进门。", ["风格：写实。", "声音：没有配乐。"], ["阿杰", "小周"], ["a.png", "b.png"], g, 5, 6,
                     extra_refs=["s1_a.png"], video="pv.mp4")
    p = j["prompt"]
    assert p.startswith("镜头：全景，固定机位。阿杰走进门。") and "本单元" not in p and "切点" not in p
    assert "图3是这个镜头第一帧的白模站位示意图" in p
    assert j["reference_images"] == ["a.png", "b.png", "s1_a.png"] and j["reference_video"] == "pv.mp4"


def test_seedance_rewrite():
    j = unit(["s1.png", "s2.png"])
    s = jobs.for_model(j, "seedance-2.5")
    assert "seed" not in s and s["model"] == "seedance-2.5" and s["resolution"] == "720p"
    assert "@图片1是阿杰" in s["prompt"] and "@图片3、@图片4依次是" in s["prompt"] and "示意图" in s["prompt"]
    assert "图1是阿杰" in j["prompt"] and j["seed"] == 1                      # the Wan job is left as it was
    k = jobs.shot_job("s", "近景。", "声音：咔哒。", "k_a.png", 2, 4, last_frame="k_b.png", model="seedance-2.5")
    assert k["last_frame"] == "k_b.png" and "seed" not in k


def test_seedance_refuses_reference_video():
    import pytest
    with pytest.raises(ValueError):
        jobs.unit_job("u", [(0, 3, "全景", "x")], ["风格："], ["阿杰"], ["a.png"], "g", 1, 5, video="pv.mp4", model="seedance-2.5")


def test_last_frame_must_differ_from_first():
    import pytest
    with pytest.raises(ValueError):
        jobs.shot_job("s", "近景。", "声音：。", "keys/k_a.png", 2, 4, last_frame="keys/k_a.png")
