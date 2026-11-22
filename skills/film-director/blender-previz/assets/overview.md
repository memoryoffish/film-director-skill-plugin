# assets：免费资产

搭白模时，大多数东西用方块、圆柱就够。形状会影响 AI 模型怎么画它的东西（床、椅子、车），可以导入现成的低模：`st.asset(名字, 文件, 位置, heading=, height= 或 length=, color=)`，导入后整个涂成一个颜色，并按你给的真实尺寸缩放。

## 已经带的

- `kaykit-furniture/`：KayKit Furniture Bits 1.0（Kay Lousberg，来源 <https://kaylousberg.itch.io/furniture-bits>），CC0（许可见同目录 `LICENSE.txt`），gltf 格式，共 1 MB。里面有扶手椅、沙发、单双人床、椅子、凳子、柜子、书架、桌子（大中小、矮桌）、落地灯、台灯、地毯、相框、枕头、书、仙人掌。
  - 这一套是卡通比例，一定要给 `height` 或 `length`，把它缩到真实尺寸；放好后出平面图和静帧检查。

## 可以自己去取的（都核对过许可证）

| 名称 | 内容 | 许可 | 地址 |
|---|---|---|---|
| The Base Mesh | 1254 个真实尺寸、无贴图的基础网格：家具、厨房、建筑、街道、交通工具 | CC0 | <https://www.thebasemesh.com/model-library> |
| Kenney Furniture Kit / Building Kit / City Kit / Car Kit | 家具、墙、门洞、楼梯、街区、车的低模 | CC0 | <https://kenney.nl/assets> |
| KayKit Prototype Bits | 门、地板、柱子、斜坡、方块墙体 | CC0 | <https://kaylousberg.itch.io/prototype-bits> |
| Quaternius Universal Animation Library 1 / 2 | 带关节的假人 + 走、坐下、起身、推、抱着东西走等 160 多段免费动作 | CC0 | <https://quaternius.com/packs/universalanimationlibrary.html> |
| Poly Haven 模型 | 写实的家具和道具 | CC0 | <https://polyhaven.com/models> |
| Blender 自带的 8 张 HDRI | 环境光 | CC0 | 装 Blender 就有 |
| CMU 动捕库 | 2605 段真人动捕，含两人互动 | 可自由使用和再分发 | <http://mocap.cs.cmu.edu/> |

不要打包进来的：Quaternius 2026-08 之后的新包（新许可证不许再分发）、Mixamo（不许单独分发，不对中国区账号开放）、Bandai Namco / LAFAN1 / AMASS（不可商用或不许分发）。每一项的许可原句和核对页面在 [refs/sources/assets.md](../refs/sources/assets.md)。

## 做片经验

- 导入的模型朝向不一定对：把 `front=` 依次试成 0、90、180、270，看平面图里哪个朝向对。
- 细节多的现成模型（带摆设的柜子、带枕头的床），AI 模型会照着画出那些细节；不想要就用不带装饰的那个，或干脆用方块。
- 带骨骼动作的假人（比如上表里的 Quaternius）还没接进白模工具；现在要人做动作，就给带关节的人偶摆关键姿势，或只用胶囊替身给位置。
