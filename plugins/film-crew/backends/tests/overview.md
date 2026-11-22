# tests：单元测试

| 文件 | 是什么 |
|---|---|
| [test_backends.py](test_backends.py) | 不连网、不读 key：Seedance 改写做两遍和一遍一样（连键的顺序）；视频还是图片、喂法、混写拒收；按 `model` 选适配、各适配的 `problem()`；方舟、MiniMax 的请求体逐个字段照官方文档的样子，`"@NAME"` 首帧怎么读；一条任务用假的接口走完（提交一次、轮询到成、写状态文件和尾帧链接；失败照记；提交的回执丢了不重发）；`request` 不连网、不跑命令、不读 key、不写文件 |

## 怎么跑

在 backends 目录里：

```
python3 -B -m unittest discover -s tests -v
```
