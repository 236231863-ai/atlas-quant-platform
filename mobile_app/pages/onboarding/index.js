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
    // 真实微信登录：wx.login → code → 后端 code2session → openid → U_ID
    if (this.data.loading) return
    this.setData({ loading: true })
    try {
      // 1. wx.login 获取临时 code
      const loginRes = await new Promise((resolve, reject) => {
        wx.login({ success: resolve, fail: reject })
      })
      if (!loginRes.code) throw new Error('wx.login 无 code')
      // 2. 调后端 /api/auth/wechat/login
      const auth = await api.wechatLogin(loginRes.code, '大乐透', '每周')
      getApp().setAuth({ user_id: auth.user_id, openid: auth.openid })
      api.track('mobile_opened', auth.user_id, { page: 'onboarding', is_new: auth.is_new })
      wx.navigateTo({ url: '/pages/ticket_entry/index' })
    } catch (e) {
      console.error('登录失败', e)
      wx.showToast({ title: '登录失败，请重试', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },
})
