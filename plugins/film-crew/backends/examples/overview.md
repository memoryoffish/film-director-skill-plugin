# examples：例子单子、命令和结果

| 在哪 | 是什么 |
|---|---|
| [smoke/](smoke/overview.md) | 每家接口一张最短的单子：Wan 3.0 那条真跑过（`send` 到服务器），MiniMax H3-Max、gpt-image 两张用来看 `request` 打印什么 |

单子格式的例子（每种喂法一张，还有一张交给 Seedance 的）在 [../../formats/examples/jobs/](../../formats/examples/jobs/overview.md)。

## 常用命令

都在项目目录里跑；`<本目录>` 是 backends 这个文件夹。

```
# 看会发什么（不发、不传、不读 key）
python3 <本目录>/scripts/filmgen.py request jobs/*.json

# 在这台机器上出图，放进 keys/（要 OPENAI_API_KEY）
python3 <本目录>/scripts/filmgen.py run jobs_img/k_s01.json jobs_img/k_s02.json --out keys

# 视频送到另一台机器上跑（要 FILM_SEND_HOST、FILM_SEND_REMOTE；key 在那台机器上）；没等完（退出码 3）就再调一次
python3 <本目录>/scripts/filmgen.py send . --wait 540
```

单元测试怎么跑，在 [tests/overview.md](../tests/overview.md)。
