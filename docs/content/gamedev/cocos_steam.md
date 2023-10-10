# 独立游戏开发/Cocos Creator 发布到 Steam

前后耗时整整 1 个月时间, 终于将游戏发布到 Steam 了! 发布游戏到 Steam 其实并不难, 这么耗时其实大部分时间都是在 "等". Steam 对于首次发行游戏的主体有一些要求, 在支付 Steam Direct 费用后需要至少等待一个月才能发行游戏. 具体原因不详, 我觉得这个政策挺奇怪的.

<iframe src="https://store.steampowered.com/widget/2511610/" frameborder="0" width="646" height="190"></iframe>

## Cocos 项目编译到 Windows 平台

项目构建中遇到了两个小问题, 记录如下:

### 修改默认分辨率

打开 `native\engine\common\Classes\Game.cpp`, 修改

```text
_windowInfo.height = 960;
_windowInfo.width  = 540;
```

### 修改默认图标

默认图标是 Cocos Creator 的 Logo, 修改成自己游戏的 Logo 会更加美观. 替换 `native\engine\win64\res\game.ico` 即可.

## 发布到 Steam

大致操作步骤如下:

0. 创建 Steam 开发者帐户. 访问 [Steam 开发者网站](https://partner.steamgames.com/)并创建一个 Steam 开发者帐户. 这里需要填写税收信息, 因为我不符合任何美国税收减免政策, 因此任何一份游戏卖出都需要向美国政府纳税. 同时, 我要向 Steam 支付 100 美元的 Steam Direct 费用, 当我的游戏收入超过 1000 美元时, Steam 会退还这笔钱. 据称此举的目的是减少开发者向 Steam 提交垃圾应用的数量.
0. 准备游戏宣传资料. 包括游戏名称, 描述, 截图, 宣传视频, 图标等. 这些资料将用于游戏的商店页面和推广. 这一步骤还是挺麻烦的, 对于独立开发者来说得自己作图和制作宣传视频. 由于我的游戏是一个像素游戏, 因此我自己制作了一个像素视频制作工具: [aiball-creator](https://github.com/mohanson/aiball-creator).
0. 创建游戏商店页面. 在 Steam 开发者后台, 您将获得一个名为"应用"的页面. 在这个页面上, 填写游戏的详细信息, 例如游戏描述, 发布日期, 支持的平台等等. 同时需要上传游戏资料, 如图标, 截图和预告片.
0. 准备游戏构建版本. 如果游戏是多平台的, 如 Windows, Mac 或 Linux, 需要准备多个游戏版本.
0. 上传游戏版本. 使用 [Steamworks SDK](https://partner.steamgames.com/doc/sdk) 上传游戏内容. 如果是在 Windows 上操作 Steamworks SDK, 可以使用目录下的 `SteamPipeGUI.zip` 这个 GUI 工具, 操作起来较为方便.
0. 设置定价和发行计划.
0. 审核和准备发布. 总共需要审核三处地方: 商店页面, 游戏本体和定价. 审核过程中我被 steam 打回了一次, 原因是:
    0. 游戏窗口标题栏和商店名称不符.
    0. 宣传图中游戏名和商店名称不符.
0. 发布游戏. 发布游戏有几个限制:
    0. 商店页面, 游戏本体和定价已经通过审核.
    0. 商店页面必须至少维持两周时间的"即将推出"状态.
    0. 距离你第一次支付 Steam Direct 费用至少一个月时间.

Steam 应用页面显示我最早可以在 8 月 1 日发布游戏, 但实际上我在 8 月 1 日上午的时候并不能发布游戏, 在晚上 6 点 30 分再登陆上去看的时候就可以点击"发行游戏"了.

商店地址: <https://store.steampowered.com/app/2511610/_/>
