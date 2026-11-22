# stages：做一部片的 4 步

按做片的先后排，一步一个文件夹。每步的 overview 按同一个顺序写：这一步交出什么、这一步几篇共用的、什么情况用哪种做法、常见错和怎么查、按类型、这一步的文件。每篇方法都按这几节写：一句话 · 什么时候用 · 思路 · 好用的规则 · 生成后检查 · 案例 · 动手前查（去哪读模型笔记、官方提示词、案例、拉片资料）。伪代码、长例子、具体数字、依据、试过不好的做法放在案例里（`examples/` 各文件夹里的 `notes.md`、`notes-*.md`）。方法篇本身和具体模型无关（[按模型适配](3-generation/adapt.md) 是例外，它专讲怎么把提示词改成各家模型官方的写法）：模型的毛病在 [refs/practical/wan3-notes.md](../refs/practical/wan3-notes.md)，配置和门槛在 [refs/practical/config.md](../refs/practical/config.md)，每种方法的出处在 [refs/background/sources/by-method.md](../refs/background/sources/by-method.md)。

- [1-storyboard/](1-storyboard/overview.md)：分镜。剧本 → 节拍 → 镜头设计 → 镜头表 → 时长；镜头从零设计、借鉴或复刻。
- [2-casting/](2-casting/overview.md)：定妆与关键帧。人物、道具、场景的参考图；定妆图转成每镜的关键帧。
- [3-generation/](3-generation/overview.md)：生成与检查。一次调用放哪些镜头、提示词、台词、生成后检查和重抽。
- [4-edit/](4-edit/overview.md)：剪辑与成片。照镜头表剪、节奏、画幅、调色、声音、修补；逐镜对照、成片检查、盲选。
- [common/](common/overview.md)：几步都要用的。共用的规矩、几个词的意思、预算、进度页、探索（这份 skill 推荐的做法不合这部片时怎么试）。

两次生成之间怎么接（遮挡、续写、穿门洞、过渡段、光晕……）在 [接法库](../transitions/overview.md)：分镜时挑好写进镜头表「接」一列，生成时照它的要求拍，剪辑时照着接。
