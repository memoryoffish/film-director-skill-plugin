# practical：干活时查的

拍片过程中会直接用到的：配置、模型、官方提示词写法、预算数据、参考片、账本。

- [config.md](config.md)：配置和检查门槛的默认值（单次时长、分辨率、画幅、并发、配乐……），并注明对应脚本里的哪个常量或参数。
- [config-transitions.md](config-transitions.md)：衔接用的门槛（盖满、加速、复述匹配……），只在做专门的衔接时读。
- [models.md](models.md)：用过的几个视频模型（Wan 3.0、HappyHorse 1.1、Seedance 2.5）各有哪些模式、时长、声音，提示词里怎么称呼参考图，怎么接下一段，内容审核拦什么。
- [wan3-notes.md](wan3-notes.md)：Wan 3.0 实测的接口限制、提示词写法、常见毛病（自带切镜、配乐、参考图、续写、分镜单元多切……）。
- [gpt-image.md](gpt-image.md)：要一张做准的图（参考图、关键帧、表情首尾帧、字）时用 OpenAI 的 gpt-image：用前问用户、画质默认 high、参数和官方写法。
- [prompt-skills/](prompt-skills/overview.md)：两家官方的提示词优化 skill（Wan 3.0 的 wan3-pe、Seedance 2.5 的 sd25-pe）的出处、版本和下载地址，并注明哪几节和我们的哪一步有关（全文没有放进仓库）。
- [budget-data.json](budget-data.json)：预算用的典型值：一次生成调用要多久、单价、重抽系数、agent 时间和花费、本地处理、网络。数据来源、json 里没有的说明、怎么重测，写在 [budget-data.md](budget-data.md)。
- [reference-films.md](reference-films.md)：参考片：我们自己做的、可以拿来对照的片子（《纸飞机》Seedance、《沙发》《末班车》《停车场》Wan 3.0、《雪线》2:30–4:30），各自的拍法。
- [experience.md](experience.md)：经验账本：每次用户盲选或评审后，记下用的什么模型，什么事件的哪种写法和种子被选中，以及为什么。
