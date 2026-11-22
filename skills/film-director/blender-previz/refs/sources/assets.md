# 白模预演用的免费资产：候选表与许可证核对

核对日期：2026-11-17。每一行的许可证都写了我打开看过的页面和原句；没看到原文的标「转述，未核对原文」。大小来自下载页、接口或压缩包目录，没查到的写「未查」。读过的全部链接在 [sources.md](sources.md) 第四部分。

先说三件和原先印象不一样的事：

1. **Quaternius 从 2026-08-28 起有了自己的许可证 QAL v1.0，禁止再分发资产本身**；但它按包生效：2026 年 8 月以后发布的新包标 QAL，我们要用的 Universal Base Characters、Universal Animation Library 1 / 2 和家具包的页面仍标 CC0。详见「许可证要点」第 4 条。
2. **Blender 安装目录里自带 8 张 CC0 的 HDRI**（来自 Poly Haven），做白模预演不用另外下载。
3. **Mixamo 的 FAQ 写明不对中国区账号开放**，条款也不许把动作文件单独分发；不能当我们 skill 的默认动作来源。

---

## A. 带骨骼的人偶

| 名称 | 内容 | 许可证（核对页面 + 原句） | 下载地址 | 格式 / 骨骼 | 大小 | 适不适合白模预演 |
|---|---|---|---|---|---|---|
| **Quaternius Universal Animation Library 自带的 Mannequin** | 一个带关节的木头人假人（球形关节、没有脸和衣服），和动作库打在一个包里 | CC0。[包页面](https://quaternius.com/packs/universalanimationlibrary.html)：「Free to use in personal, educational and commercial projects. (CC0 License)」，License 栏写 CC0 并链到 CC0 原文；[itch 页](https://quaternius.itch.io/universal-animation-library)：「Asset license: Creative Commons Zero v1.0 Universal」 | [包页面](https://quaternius.com/packs/universalanimationlibrary.html)、[itch.io](https://quaternius.itch.io/universal-animation-library) | FBX、GLB；自定义的通用人形骨骼（页面：「compatible with Unreal Engine, Godot and Unity, ready for retargeting」「Compatible with other common rigs (Mixamo for example)」）；带控制器的 .blend 只在付费 Source 版里 | Standard 15 MB | **最合适**。中性假人，不带肤色和服装，动作直接能用；三个人就复制三份换纯色 |
| **Quaternius Universal Base Characters** | 全套 6 个基础人体（Superhero / Regular / Teen 三种比例 × 男女）+ 20 个发型，平均 13k 三角。**免费的 Standard 只有 2 个人体 + 5 个发型**（官方图上是一男一女、肌肉体型，页面没写是哪种比例）；全套和带绑定的 .blend 在 Source 版（$19.99） | CC0。[包页面](https://quaternius.com/packs/universalbasecharacters.html)：「Free to use in personal, educational and commercial projects. (CC0 License)」；[itch 页](https://quaternius.itch.io/universal-base-characters)：「Asset license: Creative Commons Zero v1.0 Universal」；官方 Standard 图：「2 base models and 5 hairstyles completely free... CC0」 | [包页面](https://quaternius.com/packs/universalbasecharacters.html)、[itch.io](https://quaternius.itch.io/universal-base-characters) | FBX、glTF（页面格式栏还列了 OBJ、Blend）；Humanoid 骨骼，页面写「Compatible with the Universal Animation Library」 | Standard 122 MB；Source 600 MB | 可以用，但免费的两个是带皮肤贴图、穿内衣的写实风格人体，体型偏壮；要当白模得换成纯色材质。需要区分男女体型时用 |
| **Blender Studio Human Base Meshes v1.4.1** | 一个 .blend 资产库：写实 / 风格化男女身体、**primitive_body（方块化的简化人体，男女各两种）**、头、手、脚、头骨等。从压缩包目录看只有网格，没有骨骼（我没打开 .blend 核对） | CC0。[blender.org Demo Files](https://www.blender.org/download/demo-files/)（直接抓取被拒，读的是 [Wayback 2026-11-15 快照](https://web.archive.org/web/20261115152100/https://www.blender.org/download/demo-files/)）：「Human Base Meshes v1.4.1 by Blender Studio and community contributions… 49 MB – CC0 … Requires Blender 4.2 LTS or newer」 | [download.blender.org](https://download.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip) | .blend（资产浏览器库）；无骨骼，要自己用 Rigify 等绑 | zip 50.6 MB | 比例准，适合当静态站位人偶或自己绑骨；要动起来比上面两个费事 |
| **MPFB 2（MakeHuman 的 Blender 插件）v2.0.18** | 参数化生成人体：身高、胖瘦、年龄、性别可调，带皮肤、衣服、头发；一键加骨骼 | 插件 GPL v3，生成物和核心资产 CC0。[许可证页](https://static.makehumancommunity.org/about/license.html)：「All core assets are shared under Creative Commons, CC0… You do not need to pay anything, include any copyright notices nor give attribution.」「The source code of MPFB is shared under GPL」；[FAQ](https://static.makehumancommunity.org/mpfb/faq/can_i_sell_models.html)：「All core assets (the base mesh, targets, skins…) are shared under CC0. Note that if you use a third party asset shared under a different license it is your responsibility…」；[扩展页](https://extensions.blender.org/add-ons/mpfb/)：「The addon is GPL and the asset packs are CC0 or CC-BY」 | [Blender Extensions](https://extensions.blender.org/add-ons/mpfb/)、[GitHub](https://github.com/makehumancommunity/mpfb2) | Blender 4.2+ 插件；骨骼可选 Default、GameEngine、CMU MB、Mixamo、Rigify（[文档](https://static.makehumancommunity.org/mpfb/docs/characters/rig.html)）；仓库里还有一套 openpose 骨骼定义 | 43.8 MB | 适合：要几个身高体型不同的人、又要能再分发时用它生成。社区资产包里有 CC-BY 的衣服头发，打包前逐个看 |
| **Blender Studio 角色绑定：Rain v3、Snow v4** | 两个完整的动画练习角色（卡通比例，带脸部控制、IK/FK 切换） | CC-BY 4.0。[Rain 页](https://studio.blender.org/characters/rain/)：「The rig is free to use, provided that the you respect the CC-BY license and include the credit: Rain Rig (CC) Blender Foundation \| studio.blender.org」；[Snow 页](https://studio.blender.org/characters/snow/) 同样写法 | 上面两个页面的 Download 按钮 | .blend（Blender 4.1+），CloudRig 生成的绑定，不用装插件 | Rain 64.4 MB；Snow 106.4 MB | 不太合适：有脸有衣服的卡通角色，外观会被带进成片；没有配套动作库。新的 Storm 要登录订阅才能下 |
| **Kenney Mini Characters 2.0** | 20 个小人（男 7、女 6、工人、士兵、机器人等）+ 轮椅、拐杖等配件；每个角色内置 32 段动作：idle、walk、sprint、jump、crouch、sit、drive、die、pick-up、emote-yes / no、holding-left / right / both、attack、interact-left / right、轮椅系列（我解包看过 GLB） | CC0。[资产页](https://kenney.nl/assets/mini-characters) License 栏「Creative Commons CC0」；包内 Overview：「License: CC0 1.0 Universal」 | [资产页](https://kenney.nl/assets/mini-characters)（下载按钮给签名链接） | FBX、GLB、OBJ；**骨骼只有 7 根**（root、躯干、头、两臂、两腿，没有肘和膝） | 4.0 MB | 只适合当「棋子」：标位置和朝向够用，姿态太粗，给不了姿态控制 |
| **Kenney Blocky Characters 2.0** | 18 个方块人，每个 27 段动作（walk、sit、pick-up、interact、holding 等） | CC0（[资产页](https://kenney.nl/assets/blocky-characters)；包内 Overview「License: CC0 1.0 Universal」） | [资产页](https://kenney.nl/assets/blocky-characters) | FBX、GLB、OBJ；GLB 里没有蒙皮骨骼，是节点动画 | 2.1 MB | 同上，方块头身，只能当占位 |
| **Kenney Animated Characters 1 / 2 / 3** | 一个中等体型的人 + 几套皮肤；动作只有 idle、jump、run（我解包看的是第 1 包） | CC0（[资产页](https://kenney.nl/assets/animated-characters-1) License 栏；包内 License.txt） | [1](https://kenney.nl/assets/animated-characters-1)、[2](https://kenney.nl/assets/animated-characters-2)、[3](https://kenney.nl/assets/animated-characters-3) | FBX | 第 1 包 0.58 MB | 动作太少，不推荐 |
| **KayKit：Prototype Bits 的 Dummy、Adventurers 角色包** | Prototype Bits 里有一个假人 Dummy_Base；Adventurers 免费 5 个角色。都是大头短身的 Q 版比例 | CC0。[Prototype Bits 页](https://kaylousberg.itch.io/prototype-bits)：「Free for personal and commercial use, no attribution required. (CC0 Licensed)」「Asset license: Creative Commons Zero v1.0 Universal」；GitHub 镜像里的 [LICENSE.txt](https://github.com/KayKit-Game-Assets/KayKit-Prototype-Bits-1.0/blob/main/LICENSE.txt)：「License: (Creative Commons Zero, CC0)」 | [Prototype Bits](https://kaylousberg.itch.io/prototype-bits)、[Adventurers](https://kaylousberg.itch.io/kaykit-adventurers) | FBX、glTF（Prototype Bits 还有 OBJ）；KayKit 自己的 Rig_Medium，和 KayKit Character Animations 配套 | Prototype Bits 4.8 MB | Q 版比例会把真人比例带偏，只在卡通片里考虑 |
| **Mesh2Motion** | 开源的「Mixamo 替代」网页工具：导入模型、套骨骼、挑动作、导出；自带人形模型、骨骼和动作 | 代码 MIT，美术资产 CC0。[README](https://github.com/Mesh2Motion/mesh2motion-app)：「The code and platform are all licensed under the very permissive MIT license. The art assets (3d models, rigs, animations) are all licensed under CC0.」 | [GitHub](https://github.com/Mesh2Motion/mesh2motion-app) | 只导出 GLB / glTF | 未查 | 可以当 Mixamo 的替代来给自己的人偶套动作；动作数量和质量我没看 |
| **Mixamo 的 X Bot / Y Bot 等角色** | Adobe 的在线自动绑定 + 动作库，教程里最常见的假人 | **不可单独再分发**。[Mixamo FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html)（读的是 Wayback 2026-11-14 快照）：「You can use both characters and animations royalty free for personal, commercial, and non-profit projects including: … Create films.」「Mixamo is not available for users who have a country code from China.」；Adobe 通用条款 3.6 见「许可证要点」 | mixamo.com（要 Adobe 账号） | FBX、DAE；Mixamo 骨骼 | — | 能用来做片，但不能打包进仓库；中国区账号用不了 |
| **Unreal 的 Mannequin（Manny / Quinn）** | UE 自带假人 | 转述，未核对原文：Epic 论坛和 Fab 上的 UE4 Mannequin 页面被搜索摘要描述为标着「UE-Only Content - Licensed for Use Only with Unreal Engine-based Products」。我自己打开的 [Fab 页面](https://www.fab.com/listings/0092a035-599b-48d8-8d75-34d3cda99889) 静态文本里许可栏是空的，只看到「Allows usage with AI: No」 | Fab | UE 资产 / FBX | — | 不要用：只许在 UE 项目里用，拿到 Blender 渲染再喂给视频模型不在许可范围内 |

## B. 动作库

| 名称 | 内容（和我们有关的动作） | 许可证（核对页面 + 原句） | 下载地址 | 格式 / 骨骼 | 大小 | 适不适合白模预演 |
|---|---|---|---|---|---|---|
| **Quaternius Universal Animation Library（UAL 1）v3.0** | 120 多段。**免费 Standard 里有**（按官方清单图）：Idle（普通、Talking 说话、举火把）、Walk（普通、Formal）、Jog 向前、Sprint、Sitting（Enter 坐下、Idle、Exit 起身、Talking 坐着说话）、Push 推、PickUp Table 从桌上拿、Interact、Fixing Kneeling 跪着修东西、Driving、Dance、Crouch、Jump、Roll、Punch（Jab、Cross）、Hit、Death、剑、手枪、法术。**只在 Pro / Source 里**：Push Enter / Exit、PickUp Kneeling 蹲下捡、On Counter（Give 递、Show、Angry）、Ground Sit 坐地（进 / 出）、Sitting Nodding / Look Around、Turn 90 左右、Drink、Crying、Kick、Crawling、Climb、8 个方向的 Jog、Idle Look Around / Tired。**没有**：开门、拉、抬 | CC0（出处同 A 组第一行）。清单图：「Pro and Source versions have all 120+ animations」 | [包页面](https://quaternius.com/packs/universalanimationlibrary.html)、[itch.io](https://quaternius.itch.io/universal-animation-library)、[在线预览](https://quaternius.com/animviewer.html) | FBX、GLB；每段有带和不带 root motion 两版；Source 版带 .blend 控制器绑定 | Standard 15 MB；Pro 41 MB（$9.99）；Source 46 MB（$14.99） | **首选**。走、坐下 / 起身、坐着说话、站着说话、推、从桌上拿东西都在免费版里 |
| **Quaternius Universal Animation Library 2 v2.2** | 130 多段，免费 Standard 42 段（按官方清单图）：**Walk Carry 抱着东西走**、Idle Fold Arms 抱臂、Idle Talking Phone 打电话、Idle No / Yes 摇头点头、Chest Open 开箱、Overhand Throw 扔、LayToIdle 躺到站、Consume 吃喝、Harvest / Plant Seed / Watering / TreeChopping、Knockback、Slide、ClimbUp 1m、剑和盾连招、僵尸系列 | CC0。[包页面](https://quaternius.com/packs/universalanimationlibrary2.html)：「Free to use in personal, educational and commercial projects. (CC0 License)」；清单图：「42 completely free animations… CC0」。注意：它的 [itch 页](https://quaternius.itch.io/universal-animation-library-2) 正文写 CC0，但侧栏没有「Asset license」一栏（1 代和 Base Characters 有） | [包页面](https://quaternius.com/packs/universalanimationlibrary2.html)、[itch.io](https://quaternius.itch.io/universal-animation-library-2) | FBX、GLB；同一套骨骼 | Standard 17 MB；Source 50 MB（$14.99） | 补 UAL 1 缺的：搬东西走、抱臂、打电话、点头摇头 |
| **KayKit Character Animations 1.1** | 161 段，按类分：General（idle、受击、死亡、interact）、Movement（走、跑、跳、爬、潜行、闪避、蹲）、近战、远程、Simulation（挥手、欢呼、**坐、躺**）、Tool（挖、撬锁、钓鱼、锤、干活） | CC0。[itch 页](https://kaylousberg.itch.io/kaykit-character-animations)：「Free for personal and commercial use, no attribution required. (CC0 Licensed)」「Asset license: Creative Commons Zero v1.0 Universal」；同页还有一句请求：「please don’t resell unmodified copies or claim them as your own」 | [itch.io](https://kaylousberg.itch.io/kaykit-character-animations) | FBX、glTF；KayKit 的 Rig_Medium / Rig_Large，官方说可重定向到别的人形骨骼 | Free 14 MB；Source（.blend）23 MB（$14.99） | 可作补充；是给 Q 版角色做的，搬到正常比例假人要重定向 |
| **Kenney Mini / Blocky Characters 内置动作** | 见 A 组：walk、sit、pick-up、interact、holding 等 27–32 段 | CC0（见 A 组） | 见 A 组 | 7 根骨或节点动画 | 2–4 MB | 只够给棋子用 |
| **CMU Graphics Lab Motion Capture Database** | 2605 段真人动捕，6 大类 23 小类：行走跑步、**两人互动（Human Interaction, two subjects）**、与环境互动、体育舞蹈、日常情景 | 可自由使用和再分发。[首页](http://mocap.cs.cmu.edu/)：「This dataset of motions is free for all uses.」；[FAQ](http://mocap.cs.cmu.edu/faqs.php)：「The motion capture data may be copied, modified, or redistributed without permission.」发表成果时希望致谢（给了致谢句） | [官方](http://mocap.cs.cmu.edu/)（ASF/AMC、C3D）；BVH 转换版的 GitHub 镜像 [una-dinosauria/cmu-mocap](https://github.com/una-dinosauria/cmu-mocap)（仓库没写许可证，数据本身按 CMU 的说法） | ASF/AMC、C3D；第三方 BVH；CMU 骨骼（MPFB 有 CMU MB 骨骼可直接对上） | BVH 镜像仓库约 1 GB | 能用但费工：原始动捕没清理，官方自己说手、脚趾抖，手指没数据；要挑、要裁、要重定向。两人互动的动作是别处少有的 |
| **100STYLE** | 100 种风格的行走 / 跑 / 侧步 / 倒退 / 原地，400 多万帧，同一个演员 | CC BY 4.0。[数据集页](https://www.ianxmason.com/100style/)：「For creative or commercial work please credit in an appropriate way. E.g. "The 100STYLE Dataset - Ian Mason". This work is licensed under a Creative Commons Attribution 4.0 International License.」；[Zenodo 记录](https://zenodo.org/record/8127870) 的许可字段是 cc-by-4.0 | [Zenodo](https://zenodo.org/record/8127870)；Daniel Holden 重定向到带蒙皮角色的 [FBX / BVH 版](https://github.com/orangeduck/100style-retarget) | BVH，60 fps，28 根骨的 Xsens 骨骼 | 100STYLE.zip 1.47 GB | 只有走路类。要「疲惫地走」「偷偷摸摸地走」这种带情绪的步态时有用；可再分发但要署名 |
| **Anderson Rohr 免费动捕包（8 包）** | 日常动作最全：Everyday Actions 1 / 2、Cleaning、Talking & Interacting、Crowd Reactions、Soccer、Fitness、Halloween。第 7 包有：Seated Conversation、Coffee Conversation、Seated Typing、Seated Phone Texting、Read Book、Fill Glass And Drink、Organize Objects、Get Ready And Leave、Walk And Wave、Stretch Stand And Walk、Driving 等 22 段 | **可商用，不可再分发**。[第 7 包页面](https://andersonrohr.gumroad.com/l/mocap_pack7)：「This pack can be used for free in both personal and commercial projects. Attribution is not required… You may not redistribute, resell, or repackage this pack as a standalone product.」[CG Channel 2026-09-27](https://www.cgchannel.com/2026/09/download-130-free-fbx-mocap-moves-from-anderson-rohr/) 说当时共 134 段 | [Gumroad 店铺](https://andersonrohr.gumroad.com/) | FBX，60 fps；三套骨骼：UE5 Manny、Rokoko Newton、iClone | 未查 | 很适合对戏（坐着聊天、喝咖啡聊天），但只能让用户自己去下，不能进仓库 |
| **Mixamo 动作库** | 教程里最常用的免费人形动作库（动作清单这次没逐项核对） | 可商用做片，**不可单独再分发**，中国区账号不可用（引语见 A 组和「许可证要点」） | mixamo.com | FBX；Mixamo 骨骼 | — | 用户自己有账号时可以用；skill 不能依赖它 |
| **Rokoko 免费动捕包** | 官方陆续放出的免费包（263 段合集、日常 idle、体育、电视主题等） | 说不清。[263 段合集页](https://www.rokoko.com/resources/download-263-rokoko-motion-capture-assets)：「you can use in any animation, VFX, game, 3D project you want, including for commercial use」，**没写能不能再分发**；我去找它的条款页（/legal/terms-and-conditions）是 404 | [rokoko.com 免费资源](https://www.rokoko.com/resources/download-263-rokoko-motion-capture-assets) | FBX，30 fps；页面：「exported to Mixamo, Unreal Engine (UE4 and Ue5) and Human IK skeletons」 | 未查 | 可自己下来用；不要打包 |
| **Bandai Namco Research Motiondataset 1 / 2** | 三位职业演员的风格化动捕。1：175 段、36,673 帧，内容有 walk、run、bow、call、kick、punch、dance 等；2：384,931 帧 | **CC BY-NC 4.0，不可商用**。[README](https://github.com/BandaiNamcoResearchInc/Bandai-Namco-Research-Motiondataset)：「Bandai-Namco-Research-Motiondataset-1: CC BY-NC 4.0」「…-2: CC BY-NC 4.0」 | [GitHub](https://github.com/BandaiNamcoResearchInc/Bandai-Namco-Research-Motiondataset) | BVH，30 fps | 仓库约 309 MB | 做论文演示可以；做商业片不行 |
| **LAFAN1（Ubisoft La Forge）** | 5 人、77 段、496,672 帧（约 4.6 小时），走跑、打斗、摔倒起身、推搡等 | **CC BY-NC-ND 4.0，不可商用、不可改编**。[README](https://github.com/ubisoft/ubisoft-laforge-animation-dataset)：「This dataset can be used under the Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International Public License」；重解算版 [lafan1-resolved](https://github.com/orangeduck/lafan1-resolved)：「this data is NOT licensed for commercial use」 | 上面两个仓库 | BVH（重解算版还有 FBX） | 未查 | 不要用在成片流程里 |
| **AMASS** | 把十几个动捕库统一成 SMPL 人体的大合集 | **只许非商业科研，不许分发**。[许可页](https://amass.is.tue.mpg.de/license.html)：「To use the Dataset for the sole purpose of performing non-commercial scientific research, non-commercial education, or non-commercial artistic projects」「The Dataset may not be reproduced, modified and/or made available in any form to any third party without Max-Planck’s prior written permission.」 | 注册后下载 | SMPL 参数（npz） | — | 不要用 |
| **SFU Motion Capture Database** | 舞蹈、越障、日常等 | **只许研究**。[首页](https://mocap.cs.sfu.ca/)：「This dataset of motions is free for research purposes. The data cannot be used for commercial products or resale」 | 官网 | BVH、C3D、FBX 等 | — | 不要用 |
| **ActorCore 免费动作** | 注册送 3 个角色 + 32 段动作，每月有赠品 | 转述，未核对原文：[EULA 页](https://actorcore.reallusion.com/eula) 是脚本渲染的，我没读到正文；搜索摘要说是「royalty-free… limited commercial license」，成品图像和视频可以商用和分发，没查到允许单独分发文件 | actorcore.reallusion.com/free | FBX、iMotion | — | 可自己下来用；不要打包 |
| **Truebones 免费包（FREE 500 Pak 等）** | 号称 500 段 BVH / FBX | 说不清：只在搜索摘要里看到它有一份「TERMS OF SERVICE AND USE RESTRICTIONS」，店铺页上没找到正文；免费清单里还混着带电影、游戏 IP 名字的东西 | truebones.gumroad.com | BVH、FBX | — | 不建议碰 |

## C. 家具、室内外场景、道具

| 名称 | 内容 | 许可证（核对页面 + 原句） | 下载地址 | 格式 | 大小 | 适不适合白模预演 |
|---|---|---|---|---|---|---|
| **The Base Mesh** | 1254 个基础网格，按真实尺寸做、带基础 UV、没有贴图；分类有 Furniture、Home、Kitchen、Office、Architectural、Buildings、Urban、Transportation、Lighting、Tools 等 | CC0。[首页](https://www.thebasemesh.com/)：「1250+ Base Meshes. 100% Free. CC0 License.」；[FAQ](https://www.thebasemesh.com/faq)：「these models are under the CC0 licence… There are no restrictions in how you use the Assets.」同页有一句请求：别不加修改就放到付费墙后面 | [模型库](https://www.thebasemesh.com/model-library)（一个一个下） | 页面文本里没核对到下载格式（投稿说明里收 FBX、OBJ、glTF、GLB、Blender 文件） | 单个很小，未查 | **最像白模**：本来就是无贴图、真实比例的占位模型，摆进去不用改材质，比例和真人对得上 |
| **Kenney Furniture Kit** | 140 件室内家具和构件（按文件名）：厨房 20 件、桌、休闲沙发椅（lounge）、椅、床、柜、书架、灯、地毯、浴室、电视电脑，还有墙 8 件、门洞 3 件、地板、楼梯 | CC0。[资产页](https://kenney.nl/assets/furniture-kit) License 栏「Creative Commons CC0」；包内 License.txt：「License: (Creative Commons Zero, CC0)… This content is free to use in personal, educational and commercial projects.」；[Support](https://kenney.nl/support)：「all game assets on the asset pages are public domain licensed (CC0)」 | [资产页](https://kenney.nl/assets/furniture-kit) | FBX、OBJ、glTF、DAE、STL（解包看过） | 5.1 MB | 适合：一个包配齐一间屋子，面数低、形状一眼认得出。风格是低模卡通，尺寸要对着人偶校一下 |
| **Kenney 其他包** | Building Kit（80，墙、门、窗、屋顶）、Prototype Kit（145）、City Kit Suburban（40）/ Commercial（50）/ Roads（90）/ Industrial（40）、Modular Buildings（100）、Retro Urban Kit（120）、Car Kit（45）、Food Kit（200）、Mini Shop（30） | 各资产页 License 栏都是「Creative Commons CC0」（我逐页看过这 11 个） | kenney.nl/assets/<包名> | 没逐个解包（我解包看过的三个包是 FBX、OBJ、GLB 或 glTF） | 未逐个查 | 街道、外景、车、餐桌上的东西用这些补 |
| **KayKit Furniture Bits / Prototype Bits / Restaurant Bits / City Builder Bits** | Furniture Bits 免费 50 多件（扶手椅、沙发、床、桌、椅、柜、书架、灯、地毯、相框）；Prototype Bits 64 件以上（**门、地板、柱子、斜坡、方块墙体、假人**）；Restaurant Bits 140 多件厨房和食物；City Builder Bits 32 件以上 | CC0。各 itch 页：「Free for personal and commercial use, no attribution required. (CC0 Licensed)」「Asset license: Creative Commons Zero v1.0 Universal」；GitHub 镜像 [Furniture-Bits LICENSE.txt](https://github.com/KayKit-Game-Assets/KayKit-Furniture-Bits-1.0/blob/main/LICENSE.txt)：「License: (Creative Commons Zero, CC0)」 | [Furniture](https://kaylousberg.itch.io/furniture-bits)、[Prototype](https://kaylousberg.itch.io/prototype-bits)、[Restaurant](https://kaylousberg.itch.io/restaurant-bits)、[City](https://kaylousberg.itch.io/city-builder-bits)；GitHub 组织 [KayKit-Game-Assets](https://github.com/KayKit-Game-Assets) 有 1.0 版镜像，可直接 clone | OBJ、FBX、glTF | 免费版 3.6 / 4.8 / 未查 / 4.6 MB | 适合搭墙和门洞（Prototype Bits）；家具是 Q 版比例，和真人比例的假人放一起要缩放 |
| **Quaternius 家具和城市包** | Ultimate Home Interior（123 件）、Furniture（23）、Ultimate Furniture（20）、Downtown City MegaKit（315 件模块化街区，2026-05）、Modular Streets（25）、Cars（8） | 各包页面 License 栏写 CC0（我看过这 6 页）；这些都早于 QAL 的包 | quaternius.com/packs/<包名>.html | FBX、OBJ、Blend（Downtown 是 FBX、Blend、glTF） | 未查 | 适合；Home Interior 一包够搭整套公寓 |
| **Poly Haven 模型** | 522 个写实扫描 / 手工模型（接口当天计数），其中 furniture 85 个（沙发、扶手椅、桌、柜、床、课桌椅、中式家具等）、props 176、lighting 30、appliances 22 | CC0。[许可页](https://polyhaven.com/license)：「Our assets are all licensed as CC0」「You can redistribute them, share them around, include them when sharing your own work, or even in a product you sell.」 | [polyhaven.com/models](https://polyhaven.com/models)；[公开 API](https://github.com/Poly-Haven/Public-API)（用接口做应用要写「Powered by Poly Haven」） | .blend、glTF、FBX、USD，贴图 1k–4k 可选 | 例：Sofa_01 网格 0.2–0.3 MB，贴图 1k 约 1.7 MB、4k 约 32 MB | 要家具形状很具体（比如一把特定的椅子）时用；带写实贴图，当白模要换成纯色材质 |
| **Blender 官方演示场景** | Classroom（一整间教室，Christophe Seux）、Barcelona Pavillion、Italian Flat（一套公寓）、Agent 327 Barbershop、Cozy Kitchen | 逐个不同（[Demo Files](https://www.blender.org/download/demo-files/)，读的 Wayback 快照）：Classroom「(CC0, 72 MB)」；Barcelona Pavillion「(CC-BY, 24 MB)」；Italian Flat「(CC-BY 368MB)」；Barbershop「(CC-BY, 280MB)」；Cozy Kitchen「7MB – CC-BY-SA」 | 同一页面 | .blend | 见左 | Classroom 可以直接当现成的室内白模底子（CC0）；其余要署名，Cozy Kitchen 还要求相同方式共享 |
| **Infinigen（含 Indoors）** | 普林斯顿的程序化场景生成器，在 Blender 里随机生成整套室内（房间、家具、摆设） | 代码 BSD-3-Clause（[GitHub](https://github.com/princeton-vl/infinigen) 的许可字段；README 有「Getting Started with Infinigen Indoors」一节；仓库 2026-11 仍在更新） | GitHub | Python + Blender | — | 需要很多间不同的屋子时再考虑；装和跑都重，单片用不上 |
| **Poly Pizza** | 10,700 多个低模的聚合站（收了 Quaternius、Kenney、Google Poly 等） | 逐个模型不同（CC0 或 CC-BY）。[条款](https://poly.pizza/docs/tos)：「By downloading User Content made available by other Users, you agree to adhere to the terms of the Creative Commons license that applies at the time of download.」 | [poly.pizza](https://poly.pizza/) | GLB、FBX 等 | — | 找单个道具方便；每个模型页看清是 CC0 还是 CC-BY 再用 |
| **Sketchfab 可下载模型** | 量最大，质量和许可都参差 | 逐个模型不同。[接口的许可清单](https://api.sketchfab.com/v3/licenses) 有 CC0、CC BY、BY-SA、BY-ND、BY-NC 系列，还有 Free Standard / Standard / Editorial；[Standard 条款](https://sketchfab.com/licenses) 禁止「make available the Licensed Material as a stand-alone file」 | 搜索时勾 Downloadable + 许可筛 CC0 或 CC BY（接口参数 `license=cc0`） | glTF / GLB、原始格式 | — | 找特定道具的最后手段；只取 CC0 / CC BY，别碰 Free Standard |
| **BlenderKit（现名 Blendkit）免费资产** | Blender 里直接搜的模型、材质、HDRI | 两种许可。[许可页](https://www.blenderkit.com/docs/licenses/)：Royalty Free「doesn't allow for re-sale of the asset in the same form」；CC0 不限。[FAQ](https://www.blenderkit.com/docs/licenses/licensing-faq/)：做的游戏可以卖，「if these can't be extracted by the users in an easy way」 | Blender 插件内 | .blend | — | 自己做片时顺手；Royalty Free 的不能进仓库，要打包只挑 CC0 的 |
| **ambientCG** | 材质为主，也有 HDRI 和少量模型 | CC0。[许可页](https://docs.ambientcg.com/license/)：「All ambientCG assets are provided under the Creative Commons CC0 1.0 Universal License.」「You can include the raw files in your project」 | [ambientcg.com](https://ambientcg.com/) | 贴图、EXR | — | 白模阶段基本用不上材质；HDRI 见 D 组 |
| **Fab（含 Megascans）免费内容** | Epic 的商店 | **不可再分发**。[Fab Standard License 摘要](https://www.fab.com/eula)：「You may not: Resell or redistribute the asset for free on a standalone basis」；它也写了「usage is not limited to Unreal Engine」 | fab.com | 多种 | — | 自己用可以，不能打包；每个条目还有一栏「Allows usage with AI」，是 No 的不要拿来喂模型 |

## D. HDRI / 天空

| 名称 | 内容 | 许可证（核对页面 + 原句） | 下载地址 | 格式 | 大小 | 适不适合白模预演 |
|---|---|---|---|---|---|---|
| **Blender 自带的 8 张世界 HDRI** | city、courtyard、forest、interior、night、studio、sunrise、sunset（就是视口材质预览用的那几张） | CC0。Blender 源码里的 [license.txt](https://github.com/blender/blender/blob/main/release/datafiles/studiolights/world/license.txt)：「All HDRIs are licensed as CC0. These were created by Greg Zaal (Poly Haven https://polyhaven.com).」 | 不用下：在 Blender 安装目录的 `datafiles/studiolights/world/*.exr` | EXR，1K | 随 Blender | **首选**：白模只要一个均匀的环境光，这 8 张够了，脚本里直接按路径加载 |
| **Poly Haven HDRI** | 997 张（接口当天计数）：室外 705、室内 301、studio 96、夜景 61、纯天空 59 | CC0（出处同 C 组 Poly Haven） | [polyhaven.com/hdris](https://polyhaven.com/hdris)；文件直链形如 `https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/1k/<名字>_1k.exr` | HDR、EXR，1k 起 | 例：studio_small_08 的 1k 1.0–1.5 MB、2k 3.8–5.9 MB、4k 14–24 MB | 要特定时间和天气的光（黄昏、阴天、夜里的室内）时从这里挑，1k 就够 |
| **ambientCG HDRI** | 440 张（接口计数） | CC0（出处同 C 组 ambientCG） | [ambientcg.com](https://ambientcg.com/) | 未查 | 未查 | 备选 |
| **Open HDRI** | 60 张实拍，最高 29K（室外 43、室内 17、studio 12） | CC0。[许可页](https://openhdri.org/license)：「All HDRI maps provided by Open HDRI are released under the CC0 (Creative Commons Zero) license」。同页又写「presenting them as "your own original HDRI" is misleading and not permitted」，这句超出了 CC0 本身 | [openhdri.org](https://openhdri.org/) | EXR，32 位 | 高分辨率很大，未查 | 备选；白模用不着 29K |
| **CGEES、HDRMaps、HDRI Skies、iHDRI** | 其他免费 HDRI 站 | 转述，未核对原文（搜索摘要）：CGEES 自称 CC0；HDRMaps 是自定许可、不许再分发；HDRI Skies 和 iHDRI 只说可商用，没标 CC0 | 各站 | — | — | 用不上，前三行已经够 |

---

## 许可证要点

### 1. 可以直接打包进我们的 skill 仓库再分发（CC0 或等同）

- Quaternius 的 **Universal Animation Library 1 / 2（含 Mannequin）、Universal Base Characters、Ultimate Home Interior、Furniture、Downtown City MegaKit** 等 2026 年 8 月以前发布的包（见第 4 条的保留意见）。
- **Kenney** 全部资产页上的包；**KayKit** 的免费版；**The Base Mesh**；**Poly Haven**（模型、HDRI、贴图）；**ambientCG**；**Open HDRI**；**Blender 自带的 8 张 HDRI**；**Blender Studio Human Base Meshes**；Blender 演示场景里的 **Classroom**；**MPFB 生成的人体和它的核心资产**；**Mesh2Motion 的模型、骨骼、动作**。
- **CMU Mocap**：不是 CC0，但原话是「may be copied, modified, or redistributed without permission」「free for all uses」，等同于可以打包；发表时按它给的句子致谢。
- KayKit、The Base Mesh 页面上各有一句「别原样转卖 / 别放付费墙后」的请求。这是请求，不是许可条件；本仓库免费公开分发，不冲突。

### 2. 可以再分发但要署名（CC-BY）

- **Blender Studio 的 Rain、Snow 绑定**（CC-BY 4.0）：页面给了署名写法，照抄：`Rain Rig (CC) Blender Foundation | studio.blender.org`、`Snow Rig (CC) Blender Foundation | studio.blender.org`。
- **100STYLE**（CC BY 4.0）：页面给的写法是 `The 100STYLE Dataset - Ian Mason`；学术用途另引论文。
- **Blender 演示场景** Barcelona Pavillion、Italian Flat、Agent 327 Barbershop（CC-BY）：写作者名和「CC-BY」，附来源链接。Cozy Kitchen 是 CC-BY-SA，改过的版本也得用同样的许可发出去。
- **MPFB 社区资产包**里的部分衣服头发、**Poly Pizza / Sketchfab** 上标 CC-BY 的模型：逐个记下作者和链接。
- CC BY 4.0 的通用要求：写作者、给许可证链接、说明有没有改动。放一个 `CREDITS.md` 逐条列出即可。

### 3. 只能让用户自己去下，不能再分发

- **Mixamo**：Adobe 通用条款（2025-10-03 版）3.6 Content Files 原句：「You may reproduce and distribute Content Files only in connection with your End Use, however, under no circumstances can you distribute the Content Files on a stand-alone basis, outside of the End Use.」（条款正文读自 [Adobe 页面加载的片段](https://main--da-cc--adobecom.aem.live/cc-shared/fragments/legal/terms-existing.plain.html)，[adobe.com/legal/terms.html](https://www.adobe.com/legal/terms.html) 直接抓是 403）。FAQ 另写明中国区账号不可用。
- **Anderson Rohr 免费动捕包**：「You may not redistribute, resell, or repackage this pack as a standalone product.」
- **Fab / Megascans**：「You may not: Resell or redistribute the asset for free on a standalone basis」。
- **BlenderKit 的 Royalty Free 资产**、**Sketchfab 的 Free Standard / Standard**、**ActorCore**（转述）。
- **非商用、连自己做商业片都不行的**：Bandai Namco（CC BY-NC）、LAFAN1（CC BY-NC-ND）、AMASS（非商业科研，且不许给第三方）、SFU（只许研究）。SMPL / SMPL-X 人体同属这一类（转述：Anny 的 README 提到 SMPL-X「non-commercial use only」，我没去读 SMPL 的许可原文）。
- **Unreal Mannequin**：转述为只许用在 UE 项目里，不要拿出来。

### 4. 许可证说不清或自相矛盾的

- **Quaternius**（最要紧）。站点导航里的 [License 页](https://quaternius.com/license.html) 现在是「Quaternius Asset License (QAL) v1.0, Last updated: 8/28/2026」，3(a) 写：「You may not extract, repackage, sublicense, sell, or otherwise redistribute the Assets (in original or modified form) as a standalone asset, asset pack, stock file, template, or similar product, whether for free or for payment」。但是：
  - 它是按包标的。我逐页看了：2026-08 的 Bestiary - Dungeon Monsters Kit 和 2026-11 的 Characters - Fantasy Races 的 License 栏写 QAL 并链到这一页；UBC（2025-08）、UAL 1（2025-03）、UAL 2（2026-01）、Downtown City MegaKit（2026-05）、家具各包的 License 栏仍写 CC0 并链到 CC0 原文。
  - QAL 第 7 条：「Changes will not apply retroactively to Assets you've already obtained under an earlier version」。
  - Wayback 里这一页最早的存档是 2026-08-29，和「8/28/2026」对得上。
  - 矛盾处：[FAQ](https://quaternius.com/faq.html) 还写着「All models are under the CC0 License」，和新包标 QAL 对不上；UAL 2 的 itch 页侧栏没有「Asset license」一栏，而 1 代和 UBC 有。
  - 我的读法：UBC、UAL 1 / 2 和旧家具包目前可以按 CC0 打包。稳妥起见，打包时把包页面和 itch 页存一份存档（带日期），以后每次更新资产先回去看一眼 License 栏有没有改成 QAL；新出的包一律不打包。
- **Rokoko 免费包**：只写了可商用，没写能否再分发，条款页 404。按不可再分发处理。
- **Truebones**：没找到条款正文，且免费清单里有带影视游戏 IP 的内容。不用。
- **Open HDRI**：标 CC0，又加了「不许说成自己原创」的话。照 CC0 用没问题，别自称原创即可。
- **CMU 的 BVH 镜像仓库**：GitHub 仓库本身没放许可证文件，依据是 CMU 官网那两句。
- **Rigify 生成的绑定**：我没核对，只提醒一句：Rigify 生成的 .blend 里会带一段界面脚本（随 Blender 以 GPL 发布）。要分发自己绑好的 .blend 时再去查清楚。

---

## 推荐组合：室内两三个人对戏的白模预演

最省事、全部可以放进仓库的一套（合计约 40 MB，不算 Blender）：

| 用途 | 用什么 | 为什么 |
|---|---|---|
| 人偶 | **UAL 1 包里的 Mannequin**，复制成两三份，每人一个纯色 | 中性关节假人，不带肤色、发型、服装，不会把外观带进成片；和动作库同一套骨骼，不用重定向。CC0 |
| 动作 | **UAL 1 Standard + UAL 2 Standard**（FBX / GLB 导入 Blender，用 NLA 拼） | 免费版就有：走、正式步态、站着说话、坐下 / 坐着 / 坐着说话 / 起身、推、从桌上拿、通用 Interact、抱臂、打电话、点头摇头、抱着东西走。CC0，共 32 MB |
| 房间 | **KayKit Prototype Bits**（门、地板、墙块）或 **Kenney Building Kit**（墙、门、窗） | 几分钟围出一间屋子，门洞和窗的位置清楚。CC0，各约 5 MB |
| 家具 | 先用 **The Base Mesh**（真实尺寸、无贴图）；一次想配齐就用 **Kenney Furniture Kit**（140 件，5.1 MB） | The Base Mesh 的比例和假人对得上；Kenney 的要对着假人身高缩放一次。都是 CC0 |
| 环境光 | **Blender 自带的 interior.exr 或 studio.exr** | 零下载，CC0 |

缺口和补法：

- **开门、拉、抬重物、蹲下捡**：免费版没有。开门先用 Interact 顶；蹲下捡（PickUp Kneeling）、Push 的进入和退出、坐着点头、递东西（Counter Give）、原地转 90 度在 UAL 1 Pro 里（$9.99，同样 CC0）。「拉」和「两人抬」两个库都没有，要自己摆关键帧，或从 CMU 里找。
- **更生活化的对戏**（坐着聊天、喝咖啡聊天、打字、看手机）：Anderson Rohr 的免费包最对口，但只能在 skill 里写下载地址让用户自己取；它是 UE5 Manny 骨骼，要重定向到 UAL 的假人上。
- **需要男女、高矮胖瘦分得开**：用 MPFB 生成几个人体（输出 CC0），换纯色材质；骨骼选 Rigify 或 Mixamo 类型后把 UAL 的动作重定向过去。这一步比直接用 Mannequin 多不少功夫，只在体型差别对画面要紧时做。
- **现成的整间屋子**：Blender 演示文件 Classroom（CC0，72 MB），打开把材质统一成灰色就是白模。
