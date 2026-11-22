# media：例子单子用到的文件

用脚本画的纯色小图，没有人，只为让单子能过 `--root` 检查、能算出请求。

| 文件 | 是什么 | 谁用 |
|---|---|---|
| room_a.png | 墙、地面、地上中间一个白箱子（640×360） | first_frame、first_last 的首帧 |
| room_b.png | 同一个地方，箱子挪到右边 | first_last 的尾帧 |
| cup.png | 白底一个蓝色块，当「那只蓝色杯子」 | refs、ref_video、seedance_plain、image_edit |
| wm_s1.png | 白模站位示意：蓝色高块、绿色方块 | refs、seedance_plain、image_edit |
| previz.mp4 | 2 秒、320×180 的白模预演：蓝色方块从左往右滑 | ref_video |
