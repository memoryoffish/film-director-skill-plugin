# 盲选和审阅页

一句话：同一个剧本做出几版时，做一个盲选页：几版同步播放、只标字母，来源另存在页面外的对照表里；要逐条评的时候，每条下面放评论框和勾选，底部一个按钮把评价下载成一份文件。

## 什么时候用

同一剧本有好几版要挑；一批片子或一批改动要让人逐条看、逐条评。

## 思路

1. **盲选页**：
   - 一个剧本一组，组里每版只标字母（A、B、C……）；字母和来源（哪条流水线、哪一版）记在页面外的对照表里，选完再揭。
   - 一组的几版同步播放：一个播放 / 暂停按钮、一条进度条管整组。几版转成同样的分辨率、帧率、黑边，看不出谁是谁。
   - 片子长时可以截同一段剧情对照：每版写出这段的起止秒和「看第几秒附近」，场景用中性的话描述，不暗示哪版好。
2. **审阅页**：每一条（一个视频、一条改动）下面一个评论框和一个勾选，评论自动存在浏览器里；底部「保存评论和选择」把勾选和评论下载成一份 .md，交回来照着改。每一轮换一个浏览器存储的键名，这样旧评论不会混进来。
3. 页面和视频只放在允许放的地方（本机，或用户同意的服务器）。没人回答时只放本机，交片用自己按检查挑出的那一版（见 [规矩](../common/rules.md)「没人回答时」）。

```
versions = shuffle(group.versions); key = {letter: v.source for letter, v in zip("ABCDEF", versions)}
save(key, outside_page)                                         # 页面里只有字母
encode(each, same size / fps / bars) → media/<group>/<letter>.mp4
page: per group one play/pause + one scrubber driving all videos; per item <textarea> + <checkbox>
footer: download(choices + comments as .md)
```

## 最后一步：用户盲选，接着改

片子做完不算完。把要比的东西做成盲选页给用户：同一部片的两三版（关键镜头换写法或换种子），或者关键镜头的几条候选。用户选完、写了评语，揭开以后照着改：换成选中的那条，重拍点名的段落（「最后 7 秒不好」就只重拍最后 7 秒），再给用户看改过的。改到用户说好为止。

每一轮的选择和评语都记进 [经验账本](../../refs/practical/experience.md)：用的什么模型、拍的是什么事件（或哪一镜）、提示词怎么写、种子、选没选、为什么。

```
while not user_ok:
    page = blind(versions_or_candidates)                  # 只标字母，对照表放页面外
    picks, notes = user_review(page)
    film = revise(film, picks, notes)                      # 换成选中的、重拍点名的段落
    log_experience(model, event, writing, seed, picks, notes)
```

## 好用的规则

- 页面上和文件名里只有字母，不出现名字、版本号、工具名。
- 同步播放才比得出节奏；分开看容易只记得最后看的那一版。
- 评价文件按轮次存档；下一轮的页面只放改过的最新版。

## 案例

- [人物肖像和表情盲评](../../examples/films/faces-tests-20261117.md)：新版 skill 重拍的《末班车》《沙发》和旧版盲比，两部都选了旧版（新版动作不如旧版，也可能是运气和种子）。
- [拳馆大片版](../../examples/films/boxing-blockbuster.md)：同一剧本的 6 个版本放在同一个盲选页里同步播放挑选。
