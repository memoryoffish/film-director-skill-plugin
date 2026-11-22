# tests：scripts/ 的离线测试

都用合成的视频和声音，不联网、不调用模型。跑法（要 ffmpeg、numpy、opencv、pytest）：

```bash
CUDA_VISIBLE_DEVICES= python3 -m pytest -q -p no:cacheprovider tests/
```

- [test_occut.py](test_occut.py)：`wan.py`（任务参数、参考图和参考视频的组合、回执丢了不重发、断点续跑）和 `occut.py`（盖满判断、剪点选择、场景分、方向和速度、帧精确拼接、开头加速、接缝叠化、调用标注、声音交叉时音量不下陷、模型自带切镜只在接缝附近才重拍、按分镜表接龙重拍）。
- [test_movie.py](test_movie.py)：`movie.py`（plan 校验、满屏红色的剪点、续写接缝找对得上的帧、复述放慢时把上一段剪到还对得上的地方、模型重画输入时报问题）。
- [test_tools.py](test_tools.py)：搬进来的测量和剪辑工具（`env10.py`、`audio_probe.py`、`peaks.py`、`optical_edit.py` 的光晕和 `glowlen.py`、`camfx.py center --box`、`colorfill.py`、`track_toss.py`），以及检查这些脚本里有没有写死的路径。
- [test_budget.py](test_budget.py)：预算估算（续写算输入、重抽系数、单价）、快慢判断、实际花费统计。
- [test_asr.py](test_asr.py)：`asr.py`（装了哪个语音识别就用哪个、都没装时怎么退出、只切要的那几秒、时间换回片内秒数；不加载模型）。
- [test_progress.py](test_progress.py)：进度页：每一次生成一个播放器、生成中的占位、状态的先后、单元顺序和粗剪。
