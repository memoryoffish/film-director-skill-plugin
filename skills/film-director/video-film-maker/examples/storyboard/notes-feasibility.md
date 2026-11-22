# 能不能拍：难镜头的改法和细节

从 [能不能拍](../../stages/1-storyboard/shot-design.md) 挪来的原文：难镜头模型偏向怎么拍、怎么改，伪代码，各案例的具体表现。正文只留了标签和一句话的改法；动手时来这里对照，再自己判断这部片要怎么改。

## 常见的难镜头和改法

各模型的具体表现见 [refs/practical/wan3-notes.md](../../refs/practical/wan3-notes.md)。

   - **剪影、逆光**：模型偏向把脸打亮 → 按正常受光生成，剪辑里压暗；或改成侧逆光、轮廓光。
   - **极端角度和景别**（贴地仰拍、正上方俯拍、荷兰角、大特写）：模型偏保守，会往平视中景拍 → 往大了写（「摄影机贴着地板往上拍」「极近：画面里只有右眼」）；镜头表里留个后备，角度退一步也讲得通。
   - **复杂多人互动**（扭打、拥抱、递东西、多人同框换角度）：会换人、脸和衣服配错、左右对调、多出人 → 每镜只放这一镜的人（见 [参考图](../../stages/2-casting/references.md)），写清各自在画面左右；身体接触尽量拆成两镜（动作 → 结果）。
   - **镜子、倒影、玻璃反光**：里面会多出人 → 构图避开镜子，或在取景框里移出画；水里的倒影单独正着生成，剪辑里翻转。
   - **巨物的尺度**：巨物常被画小 → 用环境参照写（「云海到腰」），前景放小人、旗杆、岩石。
   - **变身、长大、分身**：会多长出一个身体 → 先给几个局部大特写（毛变粗、兵器膨胀），再切到全貌；不拍「一镜长大」。
   - **道具**：状态会变的（罐子里有没有种子）会被参考图锁住，特别的型号会被换掉 → 变化放进续写或下一镜；画不对就换个镜头讲同一件事。

## 伪代码

```
for shot in shots:
    risk = hard_cases(shot)        # 剪影、开关灯、极端角度、看镜头、多人、镜子、巨物、变身、叠化、文字、道具、长镜头
    if not risk: shot.plan = "能拍"; continue
    if key_moment(shot): shot.plan, shot.fallback = "冒险", rewrite(shot, risk) or post(shot, risk) or drop(shot); continue   # 先拍一小段试
    shot.plan = rewrite(shot, risk) or post(shot, risk) or drop(shot)
    if shot.plan == "后期": shot.gen, shot.post = clean_plate(shot), post_steps(risk)
recheck(shots)                     # 改过的镜头前后还接得上（shot-design.md）
```

## 各案例里的具体表现

- [复刻《沙丘》](../films/remake-dune.md)：日落逆光剪影 3 次都是正面受光，剪辑里压暗；巨口只占画面三四成，加大描述没用。
- [复刻《亡命驾驶》](../films/remake-drive.md)：关大灯、开灯、灯影都在剪辑里做整幅亮度变化；正侧面的剪影、一头扑进车门三次都没拍成。
- [复刻《英雄》](../films/remake-hero.md)：高机位俯拍拍成平视，没有荷兰角；人物正视镜头，短调用单修；叠脸、水里的倒影、匹配叠化交给剪辑。
- [复刻《敦刻尔克》](../films/remake-dunkirk.md)：贴着仪表板往上拍的脸大多拍成平视；瞄准镜的光环在剪辑里画；换错人、脸和衣服配错。
- [拳馆大片版](../films/boxing-blockbuster.md)：「地面机位」拍成膝盖到腰的高度；墙上的镜子映出 4 处「另一个人」；手提录音机两次画成开盘机。
- [四种类型各做一部](../films/genre-tests.md)：《七号房》挂钟画不出 12:47，剪辑里重画；《播种》参考图锁住了罐里的种子。
- [动作匹配 · 抛煎饼](../edit/match-on-action/01-pancake-toss.md)：写 45° 只给 15–30°，写正侧面才到约 60°。
- 变身和巨物尺度的写法来自天神对决，见 [refs/practical/wan3-notes.md](../../refs/practical/wan3-notes.md)「生成时常见的毛病」。
