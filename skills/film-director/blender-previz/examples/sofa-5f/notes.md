# 《沙发》五楼那一段：一个白模，九个机位

把一部已有的片子里空间关系错得最多的一段（34 秒，9 个镜头）用白模重拍。原片只用文字和人物参考图，这一段里：平台尽头没有门、门跑到左边、门口没有沙发、反打两人没换边、结尾沙发停在平台中间还往后滑。重拍后这几处都对了。Wan 3.0，720P，2026-11-17。这一段的成片没有放进仓库；用白模重拍的《沙发》全片（2:12、39 镜，不是这里这一段的那一版）见[画廊](https://memoryoffish.github.io/films/)。

门的开向要单独看：s53 钥匙开门，门在白模里往屋里开、提示词里也写了「往屋里推开」，但放进分镜单元的三种喂法（每镜一张关键帧、每镜一张白模静帧、预演当参考视频）门都往外开，或看不出往哪开；只有单拍「关键帧当首帧 + 尾帧」（尾帧里门已经往屋里开到底）门才往屋里开。下面表里的「全对」只核对了机位、站位和换边，没核对门的开向。成片的 s53 用的是首帧 + 尾帧，其余 8 镜用单元 + 每镜一张关键帧。

文件：[fin_scene.py](fin_scene.py)（场景）、[make_fin.py](make_fin.py)（关键帧提示词和视频任务）、[cut_fin.py](cut_fin.py)（裁和拼）。这三个是当时照实跑的脚本，路径指向当时的实验目录；新项目用 `scripts/` 里整理过的工具。make_fin.py 依赖的 make_jobs.py 没有带上，fin_scene.py 要放在 blocking.py 旁边才跑得起来，只当提示词和任务的范本看。

## 场景

- 一个场景：五楼平台 2.4 × 3.2 米，北墙正中一扇门（合页在左，往屋里开），门后一间屋；西半边 9 级楼梯上来，东半边栏杆；西墙上一块红色方块标楼层号。
- 三个人偶：阿杰（蓝，1.83 米，眼镜）、小周（红，1.66 米，反戴帽）、大妈（枣红，卷发）；沙发是一块 2.0 × 0.88 的绿色方块。
- 时间线 33.8 秒，9 个镜头，9 个机位都架在这一个场景里：

| 镜头 | 秒 | 机位 | 焦距 |
|---|---|---|---|
| s51 推沙发到门口 | 0–3.5 | 楼梯口上方越过栏杆，高 2.05 米 | 27 |
| s52 击掌 | 3.5–6.1 | 平视侧面双人 | 34 |
| s53 钥匙开门 | 6.1–9.6 | 门右侧、阿杰右肩后，拍锁和手 | 45 |
| s54 门开了，沙发比门宽 | 9.6–13.0 | 身后全景 | 30 |
| s55 扶手顶在墙上 | 13.0–15.4 | 特写 | 45 |
| s56 反打 | 15.4–17.95 | 屋里隔着门框往外拍 | 30 |
| s57 两张脸 | 17.95–21.2 | 屋里近景 | 40 |
| s61 屋里靠门坐下 | 21.2–26.4 | 屋里低机位 | 30 |
| s62 大妈坐上沙发 | 26.4–33.8 | 平台全景 | 32 |

- 搭的过程里改过的：特写机位一开始拍不到手和锁，挪到右肩后、手用 `hands=` 够到锁；全景被栏杆挡住人，抬高机位；反打改成从屋里隔着门框拍，这样门框把「这是同一扇门」带进了画面；人偶按 1.80 米建模却按 1.75 缩放，高了 3%，改了除数。
- `st.flips(shots)` 报出 s55→s56 两人换边（有意的反打），提示词里就明写了阿杰在画面右边。

## 关键帧

11 张（9 镜的首帧 + s51、s53 的尾帧），`gpt-image-2.6-sunburst` high，1536x864。先出主帧 s51_a（白模 + 两个人物图 + 沙发图），其余都从主帧派生。11 张都和白模对得上；s56、s57 一开始把楼层号画到了反方向的墙上，提示词里加一句「楼层号被开着的门扇挡住，画面里没有」后重画了这两张。

一张派生帧的任务（反打 s56）：

```
{"name": "f_s56_a", "batch": 2, "size": "1536x864", "images": ["out/fin/s56_a.png", "gpt/out/f_s54_a.png", "server/inputs/ajie.png", "server/inputs/xz.png"]}

Image 2 is a film still: two young men stand with their backs to the camera in front of an old dark-green sofa that blocks an open doorway on a narrow apartment landing. Image 1 is a 3D blocking render (white model) of the reverse angle of the same moment: the camera is now inside the empty flat, looking out through the open doorway at the two men from the front. Draw that reverse shot as a photorealistic film still, 16:9.

Keep from Image 2: the same two men and their clothes, the same sofa, the same landing (old green lower walls, yellowed white upper walls, small paper ads), the same warm afternoon light and film look.

Framing, positions and poses exactly as in Image 1, a frame within a frame:
- Foreground: the inside of the flat, in shade. The dark vertical strip on the left is the door jamb with a bare white room wall beside it; the large brown surface on the right is the open door leaf, close to the camera.
- Through the doorway: the green band across the bottom of the opening is the BACK of the sofa's backrest (plain dark-green velvet), wider than the doorway so its ends disappear behind the frame on both sides.
- Behind the sofa the two men stand side by side facing the camera, seen from the thighs up. The red mannequin on the LEFT is XIAOZHOU: the shorter, stocky, round-faced young man from Image 4 (red baseball cap worn backwards, white basketball jersey with blue trim, black shorts, black sneakers). The blue mannequin on the RIGHT is AJIE: the tall, thin young man from Image 3 (same face, short black hair, black square glasses, grey T-shirt with a green cartoon dinosaur on the chest, dark blue jeans, white sneakers). Both look at the doorway with blank, sweaty faces, mouths closed, arms hanging.
- Behind them: the landing, the faded-red iron railing at waist height, and beyond it the open stairwell with its far wall and a window (the pale blue rectangle) letting in warm daylight. This is the top floor: the stairs only go down, so no steps are visible above the railing.
- The red painted 5 of Image 2 is on the wall that is now on the right-hand side, hidden behind the open door leaf: no painted number is visible anywhere in this shot.

The mannequins and boxes in Image 1 are only position markers: do not draw any mannequin, flat plastic white-model shading, square chest plates, subtitles or watermark. Nobody looks at the camera.
```

## 视频：四种喂法都拍了一遍

三个单元：U5a = s51–s53（9.6 秒，生成 10 秒）、U5b = s54–s57（11.6 秒，生成 12 秒）、U6 = s61–s62（12.6 秒，生成 13 秒）。每种 2 个种子。

| 喂法 | 结果（逐帧看） |
|---|---|
| 单元 + 每镜一张关键帧当参考图 | 9 镜的机位、站位、换边全对，2 个种子都是；三个单元之间地方的样子最统一。s53 的门往外开或看不出方向。成片除 s53 外用的这一路 |
| 单元 + 每镜一张白模静帧当参考图 | 9 镜的机位、站位、换边全对，2 个种子都是；没有人偶进画面。场景细节三个单元之间略有出入；s62 有一条带了一点缓慢推近，结尾大妈看了镜头。s53 的门往外开或看不出方向 |
| 单镜 + 关键帧当首帧（s51、s53 加尾帧），整段提示词 | 9 镜里 3 镜跑偏，两个种子都跑：s53 门一开外面多出一段带楼层号和沙发的楼道；s55 切到一个全景；s56 沙发靠背变成正面朝镜头滑走 |
| 同上，提示词只留动作、机位、声音 | 9 镜 0 跑偏，2 个种子都是；s53 门往屋里开（靠尾帧）。成片的 s53 用这一路 |
| 单元 + 预演当参考视频 | 站位对，s53 的门往外开或看不出方向；见 [feeding-tests](../feeding-tests.md) |

- 单元的切点：量到的和时间表差 0.03 秒以内。
- 原片结尾沙发往后滑：帧差 23–27；新版 4–5（第 7 秒处）。

### 完整提示词：单元 + 每镜一张白模静帧

```
{"name": "U5a_URI_s9101", "shot": "U5a", "variant": "URI", "seed": 9101, "duration": 10, "resolution": "720P", "ratio": "16:9", "audio": true, "prompt_extend": false, "reference_images": ["inputs/ajie.png", "inputs/xz.png", "inputs/sofa.png", "inputs/fin/s51_a.png", "inputs/fin/s52_a.png", "inputs/fin/s53_a.png"]}

本单元共 3 个镜头，剧情时长 9.60 秒；下面所有时间都是成片内的秒数，从 0 开始。成片必须按分镜时间表剪接成这 3 个镜头：相邻镜头交界的秒数就是切点，切点处机位与景别立即改变；表中没有的切点不要加，表中有的切点不能省，不合并、不调换，只用硬切，没有叠化。
9.60 秒之后直到成片结束，延续最后一个镜头的画面与运动，不要切到新镜头。
镜头1｜0.00–3.50 秒｜机位与景别：全景，固定机位，从楼梯口上方越过红漆栏杆往平台尽头的木门拍｜开场
  画面：木门关着。阿杰在画面左边、小周在画面右边，都背对镜头，弓着腰，双手按在墨绿色沙发的前沿，一步一步把沙发往门那边推，沙发在水泥地上蹭着往前滑，最后靠背贴上门所在的那面墙，停住。两人浑身是汗。
镜头2｜3.50–6.10 秒｜机位与景别：中景，固定机位，平视｜以“硬切”从上一镜头切入
  画面：沙发已经横在门前。阿杰在画面左边、面朝右，小周在画面右边、面朝左，两人刚直起腰，喘着气，对视着笑了出来，各举起靠镜头这一侧的手，在两人中间“啪”地击了一下掌，然后手放下。两人身后是沙发和关着的木门。
镜头3｜6.10–9.60 秒｜机位与景别：近景，固定机位，拍门锁和阿杰的手｜以“硬切”从上一镜头切入
  画面：画面下沿是沙发靠背的顶边。阿杰的右手从画面左上方伸进来，把钥匙插进旧木门右侧的黄铜门锁，拧了一下，“咔哒”一声，然后把门往屋里推开：门的合页在左边，门扇向里转开，露出门里的空屋子。画面里只有手和前臂，没有脸。

风格：写实的电影画面，35mm 胶片质感，细腻颗粒，自然的暖色调；冷面喜剧的拍法：机位固定、构图端正，人物的表情和停顿清清楚楚；画面里只有下面写到的人。
参考图：图1是阿杰，图2是小周，图3是那张墨绿色沙发。每张图只用来锁住这个人（或这张沙发）的长相、衣服和颜色；不照搬图里的灰色背景、构图、光线、姿势和视线，只用图里的人和沙发。
人物：阿杰：二十五六岁的中国男青年，个子很高、偏瘦，短黑发，戴一副方框黑框眼镜，穿一件胸前印着绿色卡通恐龙的灰色短袖T恤、深蓝色牛仔裤、白色运动鞋。 小周：二十五六岁的中国男青年，比阿杰矮一个头，圆脸，微胖，戴一顶帽檐朝后反扣的红色棒球帽，穿一件白色镶蓝边的宽松篮球背心、黑色运动短裤、黑色运动鞋。
沙发：一张旧的墨绿色绒布三人沙发，约两米长，方正的宽扶手，三块墨绿色坐垫，深棕色的木质短腿，靠背上有一块磨得发白的旧痕。
场景：一栋没有电梯的老居民楼的楼道，很窄。墙下半截刷着旧绿漆墙裙、上半截是发黄的白墙，水泥地面，墙上贴着开锁、通下水道的白底黑字小广告；周六下午暖黄的阳光从楼梯间的窗斜照进来。这里是五楼，也是顶楼：楼梯从下面上来，到这个小平台为止，平台靠楼梯的一边是褪色红漆的铁栏杆；平台尽头那面墙的正中只有一扇旧的深棕色木门，就是他们的家门，门锁在门的右侧，门往屋里开；左边墙上用红漆刷着很大的楼层号「5」。
声音：像纪录片一样现场录的同期声：老楼道的回声、喘气声、布面摩擦声、远处窗外的鸟叫；这个镜头里还有沙发腿蹭水泥地的闷响、最后靠背撞上墙的一声闷响；清脆的一声击掌；钥匙串的叮当声、钥匙插进锁孔和拧开门锁的咔哒声、旧门轴的吱呀声。所有人自始至终都没说话，嘴都闭着；没有任何人声、没有任何配乐（没有鼓、弦乐、钢琴、合成器、持续的低音铺底、合唱、哼唱、任何旋律）。安静的时候就让它安静。
要求：画面里没有任何字幕、水印；除了墙上的楼层号和小广告，没有别的可读文字。人物视线按分镜表写的方向看，不看镜头。
图4、图5、图6依次是镜头1、镜头2、镜头3开头的白模站位示意图，只用来定每个镜头的机位、构图和站位：蓝色人偶的位置、朝向、姿势和动作就是阿杰的，红色人偶的就是小周的，枣红色人偶的就是大妈的，绿色方块就是沙发的位置和方向，棕色的是门，红色栏杆是楼梯口的铁栏杆，墙上的红色方块是楼层号「5」的位置，门、墙、地面的位置和透视也照它。不要把人偶、白模的纯色质感、胸前的白牌画进成片；人和沙发的样子用前面几张参考图，场景的样子按文字写的来。
```

### 换成关键帧时，最后一句换成

```
图4、图5、图6依次是镜头1、镜头2、镜头3开头的画面参考（同一个地方、同样的人和沙发）：每个镜头的机位、景别、构图、每个人的位置和朝向都照对应的那张图；人的长相和衣服以前面的人物参考图为准。
```

参考图换成 `["inputs/ajie.png", "inputs/xz.png", "inputs/sofa.png", "img_f/f_s51_a.png", "img_f/f_s52_a.png", "img_f/f_s53_a.png"]`。

### 换成参考视频时，最后一句换成

```
视频1是这个单元的白模预演（3 个镜头，切点和上面的时间表一致），只用来定每个镜头的机位、构图、站位、动作的先后和切点：蓝色人偶的位置、朝向、姿势和动作就是阿杰的，红色人偶的就是小周的，枣红色人偶的就是大妈的，绿色方块就是沙发的位置和方向，棕色的是门，红色栏杆是楼梯口的铁栏杆，墙上的红色方块是楼层号「5」的位置。不要把人偶、白模的纯色质感、僵硬的姿势画进成片：人按真人自然地动；人和沙发的样子用参考图，场景和光按文字写的来；最终画面正常彩色。
```

任务里多一项 `"reference_video": "inputs/fin/pv_U5a.mp4"`，参考图只留人物和道具。

### 单镜首帧 + 尾帧，瘦提示词（s53 开门）

```
{"name": "s53_GFL2_s9301", "shot": "s53", "variant": "GFL2", "seed": 9301, "duration": 4, "resolution": "720P", "ratio": "16:9", "audio": true, "prompt_extend": false, "first_frame": "img_f/f_s53_a.png", "last_frame": "img_f/f_s53_b.png"}

镜头：近景，固定机位，拍门锁和阿杰的手。画面下沿是沙发靠背的顶边。阿杰的右手从画面左上方伸进来，把钥匙插进旧木门右侧的黄铜门锁，拧了一下，“咔哒”一声，然后把门往屋里推开：门的合页在左边，门扇向里转开，露出门里的空屋子。画面里只有手和前臂，没有脸。
声音：像纪录片一样现场录的同期声：老楼道的回声、喘气声、布面摩擦声、远处窗外的鸟叫；这个镜头里还有钥匙串的叮当声、钥匙插进锁孔和拧开门锁的咔哒声、旧门轴的吱呀声。所有人自始至终都没说话，嘴都闭着；没有任何人声、没有任何配乐（没有鼓、弦乐、钢琴、合成器、持续的低音铺底、合唱、哼唱、任何旋律）。安静的时候就让它安静。
要求：全片只有这一个镜头，从头到尾机位固定，不切镜、不换角度、不叠化；画面延续首帧的样子（写实的电影画面，35mm 胶片质感）；没有任何字幕、水印；人物不看镜头。
```

## 裁和拼

- 单元：`cuts()` 量切点，取离时间表最近的那个（0.9 秒以内），按它裁出每一镜；整段取单元的前「时间表总长」秒。
- 首帧 + 尾帧的片段取靠后的一段（让它落在尾帧上），只有首帧的取开头。
- 每段两端 30 毫秒的声音淡入淡出再拼，接缝没有爆音。
