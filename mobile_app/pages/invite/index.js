// Beta 邀请页（v4.9.1 Beta Distribution）
// 种子用户扫码落地页：展示 Beta 说明 → 开始使用（协议→引导→录票）

Page({
  data: {
    features: [
      { icon: '🎫', title: '录票不丢', desc: '买完随手记，纸票丢了有底' },
      { icon: '🔔', title: '开奖提醒', desc: '开奖前微信通知你' },
      { icon: '🏆', title: '自动兑奖', desc: '中了就告诉你，不漏一注' },
    ],
  },

  start() {
    // 进入协议页（同意后进引导）
    wx.navigateTo({ url: '/pages/terms/index' })
  },
})
