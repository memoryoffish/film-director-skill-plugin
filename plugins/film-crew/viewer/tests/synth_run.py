"""造一个小的拍片运行目录（只用标准库），把读法里的几种分支都走到：测试用。

    python3 synth_run.py <目录>          # 在 <目录> 里写出运行目录（没有成片；要成片另外用 ffmpeg 做 film.mp4）

八镜：
  A1 首帧生视频；关键帧 k_A1 用的白模在子目录（wm/room/A1_a.png），还用了基准画面 k_D（出图记录在 jobs_img/）
  A2 首尾帧；视频 v2 报错后重抽成 v2r（换了首帧、种子），首帧 k_A2_a 重画成 k_A2_a2，尾帧从首帧派生
  A3、A4 一条生成 U1_t1 切成两镜；prompt 写「图2、图3依次是镜头1、镜头2」；参考图里有放在 keys/ 的场景图 ref_plate
  A5 参考图生视频，同时给了首帧和参考视频；生成结果记在 clips/r5.json（SUCCEEDED）；关键帧 k_A5 出图记录写着 ok: false；
     没有按镜头名的白模静帧，白模取 k_A5 出图时用的那张（wm/D.png）
  A6 任务名只在剪辑表 edl.json 里；首帧写的是绝对路径
  A7 没有视频任务（白模静帧有，没喂进去）；jobs/ 里另有一条没人用的文生视频 v7，要「每镜都有任务」时让 A7 用它
  A8 首帧在 kf9/（出图记录放在图旁边），尾帧在 img/（出图记录在 imgjobs/）
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
import zlib


def png(w: int, h: int, rgb: tuple = (120, 120, 120)) -> bytes:
    """一张纯色 PNG。"""
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def make_run(root: pathlib.Path) -> pathlib.Path:
    root = root.resolve()
    w = lambda rel, data: (root / rel).parent.mkdir(parents=True, exist_ok=True) or (root / rel).write_bytes(
        data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False, indent=1).encode())
    pics = ["wm/room/A1_a.png", "wm/A2_a.png", "wm/A2_b.png", "wm/A3_a.png", "wm/A4_a.png", "wm/A6_a.png", "wm/A7_a.png",
            "wm/A8_a.png", "wm/D.png", "refs/girl.png", "keys/k_A1.png", "keys/k_D.png", "keys/k_A2_a.png", "keys/k_A2_a2.png",
            "keys/k_A2_b.png", "keys/k_A3_a.png", "keys/k_A4_a.png", "keys/ref_plate.png", "keys/k_A5.png", "keys/k_A6.png",
            "kf9/k_A8.png", "img/A8_end.png"]
    for i, rel in enumerate(pics):
        w(rel, png(32 if "refs" not in rel else 18, 18 if "refs" not in rel else 32, (40 * i % 255, 90, 160)))
    w("previz_cut.mp4", b"not a real video; only has to exist")
    w("refs/README.md", "# 参考图\n\n- `girl.png`：女孩，全身\n".encode())
    w("wm/notes.json", {"notes": {"A2": "门开着，她在门里", "A2_end": "她站起来", "A3": "教室后排", "room/A1": "子目录里的站位"}})
    w("meta.json", {"title": "合成", "genre": "测试", "model": "Wan 3.0（720P）；关键帧 gpt-image", "seconds": 20.0,
                    "recon": "从剪辑表重建的镜头表",
                    "shots": [{"name": "A1", "t0": 0, "t1": 3, "what": "首帧生视频", "feed": "关键帧当首帧（v1）"},
                              {"name": "A2", "t0": 3, "t1": 6, "what": "首尾帧，重抽过", "feed": "首尾帧（v2r）"},
                              {"name": "A3", "t0": 6, "t1": 8, "what": "单元第一镜", "source": "U1_t1 第1镜"},
                              {"name": "A4", "t0": 8, "t1": 10, "what": "单元第二镜", "source": "U1_t1 第2镜"},
                              {"name": "A5", "t0": 10, "t1": 12, "what": "参考图生视频", "clip": "r5"},
                              {"name": "A6", "t0": 12, "t1": 14, "what": "剪辑表里找任务"},
                              {"name": "A7", "t0": 14, "t1": 16, "what": "没有任务"},
                              {"name": "A8", "t0": 16, "t1": 20, "what": "关键帧不在 keys/", "clip": "v8"}]})
    w("jobs/v1.json", {"name": "v1", "prompt": "Image 1 drives the shot.", "first_frame": "keys/k_A1.png", "duration": 3, "seed": 7,
                       "model": "wan3.0-video", "resolution": "720P", "prompt_extend": False})
    w("jobs/v2.json", {"name": "v2", "prompt": "old prompt", "first_frame": "keys/k_A2_a.png", "last_frame": "keys/k_A2_b.png",
                       "duration": 3, "seed": 1})
    w("jobs/v2r.json", {"name": "v2r", "prompt": "new prompt", "first_frame": "keys/k_A2_a2.png", "last_frame": "keys/k_A2_b.png",
                        "duration": 3, "seed": 2})
    w("jobs/U1_t1.json", {"name": "U1_t1", "prompt": "图2、图3依次是镜头1、镜头2开头的画面参考。",
                          "reference_images": ["refs/girl.png", "keys/k_A3_a.png", "keys/k_A4_a.png", "keys/ref_plate.png"],
                          "duration": 4, "model": "seedance-2.5"})
    w("jobs/r5.json", {"name": "r5", "prompt": "follow the reference video", "first_frame": "keys/k_A5.png",
                       "reference_images": ["refs/girl.png"], "video": "previz_cut.mp4", "duration": 2})
    w("jobs/v6.json", {"name": "v6", "prompt": "absolute path", "first_frame": str(root / "keys" / "k_A6.png"), "duration": 2})
    w("jobs/v7.json", {"name": "v7", "prompt": "text only", "duration": 2})
    w("jobs/v8.json", {"name": "v8", "prompt": "keyframes elsewhere", "first_frame": "kf9/k_A8.png", "last_frame": "img/A8_end.png"})
    w("edl.json", {"shots": [{"shot": "A6", "clip": "v6 0-48"}]})
    w("keys/k_A1.json", {"ok": True, "job": {"name": "k_A1", "size": "1536x864", "prompt": "Image 1 is the blocking.",
                                             "images": ["wm/room/A1_a.png", "keys/k_D.png", "refs/girl.png"]}})
    w("jobs_img/k_D.json", {"prompt": "the base frame", "images": ["wm/D.png"]})
    w("keys/k_A2_a.json", {"ok": True, "job": {"prompt": "first try", "images": ["wm/A2_a.png", "refs/girl.png"]}})
    w("keys/k_A2_a2.json", {"ok": True, "job": {"prompt": "second try", "images": ["wm/A2_b.png", "refs/girl.png"]}})
    w("keys/k_A2_b.json", {"ok": True, "job": {"prompt": "end frame from the first", "images": ["wm/A2_b.png", "keys/k_A2_a2.png"]}})
    w("keys/k_A3_a.json", {"ok": True, "job": {"prompt": "A3", "images": ["wm/A3_a.png"]}})
    w("keys/k_A4_a.json", {"ok": True, "job": {"prompt": "A4", "images": ["wm/A4_a.png", "refs/girl.png"]}})
    w("keys/k_A5.json", {"ok": False, "job": {"prompt": "A5", "images": ["wm/D.png", "refs/girl.png"]}})
    w("keys/k_A6.json", {"prompt": "A6", "images": ["wm/A6_a.png"]})
    w("kf9/k_A8.json", {"prompt": "A8 first", "images": ["wm/A8_a.png", "refs/girl.png"]})
    w("imgjobs/A8_end.json", {"prompt": "A8 end", "images": ["wm/A8_a.png"]})
    w("clips/results.jsonl", ("\n".join(json.dumps(x) for x in [
        {"name": "v1", "ok": True, "utc": "2026-11-01T10:00:00"},
        {"name": "v2", "ok": False, "error": "SetLimitExceeded", "utc": "2026-11-01T10:01:00"},
        {"name": "v2r", "ok": True, "utc": "2026-11-01T10:05:00"}]) + "\n").encode())
    w("clips/r5.json", {"name": "r5", "status": "SUCCEEDED", "submitted_utc": "2026-11-01T10:07:00"})
    return root


if __name__ == "__main__":
    print(make_run(pathlib.Path(sys.argv[1])))
