# refsound

从 Freesound 给一种或一批声音挑靠得住的录音：给视频选音效，或者给评测、校准、标注示例做标准参考集。

agent 听不了声音，就照听过的人留下的信号（下载量、评分人数、上传者的描述）和量出来的数（时长、能量落在哪里、尾巴多长）来筛选和排序。每条候选都留下取舍的原因，许可只取 CC0 与 CC-BY。

```bash
python3 scripts/refsound.py search <spec.json> <输出目录> [--exclude 已用过的编号.json ...] [--revet]
python3 scripts/refsound.py check  <spec.json> <输出目录>
```

- `search` 只用 Python 标准库，机器要能访问 freesound.org。它写出 `candidates.json`（全部候选与筛掉的原因）和 `previews/`（排在前面那些录音的 MP3 预览）。
- `check` 要 ffmpeg 与 numpy。它写出 `selection.json`（最后的清单，CC-BY 的带署名）、`checks.json`（每条预览量出来的数）和 `TABLE.md`（汇总表）。
- spec 怎么写、十四条规则、每条规则实测时见到的例子，都在 [GUIDE.md](GUIDE.md)；写好的 spec 例子在 `examples/sounds.json`（8 种声音）。
- 测试：`python3 -m pytest tests`。

安装：本目录是 film-director 合订版 skill 的一部分（`skills/film-director/refsound/`），跟着 film-director 一起装，装法见仓库根目录的 [README](../../../README.md)。

选材的四条基本规则出自 [vibe-motion/sound](https://github.com/vibe-motion/sound)（B 站「浙大猫学长」）。这里只借用规则，代码是另写的。
