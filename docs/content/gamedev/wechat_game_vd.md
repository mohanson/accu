# 独立游戏开发/Cocos Creator 微信小游戏创建视频广告页面卡顿问题解决

在不久前我为 "像素推箱" 小游戏接入 Banner 广告后, 着手开始实现推箱子游戏的最短路径求解算法. 目前用户已经可以在小游戏内部委托机器人帮助其过关, 当然是有前提的, 用户必须观看一段简短的视频广告 >_<.

在创建视频广告单元后, 微信公众平台会给出一段示例代码如下

```ts
// 创建激励视频广告实例，提前初始化
let videoAd = wx.createRewardedVideoAd({
  adUnitId: 'adunit-6bbe78c0b685ea23'
})

// 用户触发广告后，显示激励视频广告
videoAd.show().catch(() => {
  // 失败重试
  videoAd.load()
    .then(() => videoAd.show())
    .catch(err => {
      console.log('激励视频 广告显示失败')
    })
})
```

将这段代码复制到组件的 `onLoad()` 函数后, 悲剧发生了, 在低端手机上冷启动游戏时, 动画会有 2 秒左右的卡顿时间, 非常影响游戏体验. 游戏启动时, 会播放一段 1 秒左右的动画, 这个动画是我用定时器手写的, 播放动画和微信创建广告单元的动作同时执行, 导致动画十分卡顿.

一个非常直观的想法, 能不能在动画播放完毕后再创建微信视频广告单元? 为此我编写了一个定时器队列, 在该队列中, 前一个定时器执行完毕后会自动执行后一个定时器, 在游戏冷启动时, 首先将动画定时器推入队列, 之后再将创建广告单元的代码封装成一个执行一次的定时器并推入队列. 实现该定时器队列只需在任意组件中添加以下代码, 之后调用 `this.grun({callback: ff, interval: ii, repeat: rr})` 即可.

```ts
public gfin = 1

public gvec = []

public gfun(conf: any) {
    let i = 0
    let f = () => {
        conf.callback(i)
        i = i + 1
        if (i == conf.repeat) {
            if (this.gvec.length != 0) {
                let conf = this.gvec.shift()
                this.schedule(this.gfun(conf), conf.interval, conf.repeat - 1)
            } else {
                this.gfin = 1
            }
        }
    }
    return f
}

public grun(conf: any) {
    if (!this.gfin) {
        this.gvec.push(conf)
        return
    }
    this.gfin = 0
    this.schedule(this.gfun(conf), conf.interval, conf.repeat - 1)
}
```

欢迎访问微信小游戏 "像素推箱" 了解我的第一款独立游戏.

![img](../../img/gamedev/wechat_game/boxes.jpg)
