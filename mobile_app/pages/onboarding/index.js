// 页面1：引导页（3 屏价值 → 微信授权 → 录第一张票）
const api = require('../../utils/api')

const STEPS = [
  { icon: '🎫', title: '录票不丢', desc: '买完随手记一注，纸票丢了也有底' },
  { icon: '🔔', title: '开奖自动提醒', desc: '开奖前微信通知你，不用记开奖时间' },
  { icon: '🏆', title: '中了就告诉你', desc: '自动核对开奖，中没中一目了然' },
]

Page({
  data: {
    steps: STEPS,
    current: 0,
    loading: false,
  },

  onLoad() {
    // 协议守卫：未同意协议则回协议页
    if (!wx.getStorageSync('atlas_terms_agreed')) {
      wx.redirectTo({ url: '/pages/terms/index' })
      return
    }
  },

  onSwiperChange(e) {
    this.setData({ current: e.detail.current })
  },

  next() {
    if (this.data.current < STEPS.length - 1) {
      this.setData({ current: this.data.current + 1 })
    } else {
      this.start()
    }
  },

  async start() {
    // 微信授权登录（openid 由后端以模拟 openid 提供，真实接入 wx.login 后换 code）
    if (this.data.loading) return
    this.setData({ loading: true })
    try {
      // 验证阶段：用随机 openid；真实接入改为 wx.login → code → 后端换 openid
      const openid = 'demo_openid_' + Date.now()
      const auth = await api.auth(openid, '大乐透', '每周')
      getApp().setAuth(auth)
      api.track('mobile_opened', auth.user_id, { page: 'onboarding' })
      wx.navigateTo({ url: '/pages/ticket_entry/index' })
    } catch (e) {
      wx.showToast({ title: '登录失败，请重试', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },
})
