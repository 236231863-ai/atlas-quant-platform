// Atlas Mobile MVP - 小程序入口
// 验证阶段：微信授权 → 全局 user_id（U 编号）

App({
  globalData: {
    user_id: '',
    openid: '',
    api_base: 'http://127.0.0.1:8000/api/mobile/v1',
  },

  onLaunch() {
    const auth = wx.getStorageSync('atlas_auth') || null
    if (auth && auth.user_id) {
      this.globalData.user_id = auth.user_id
      this.globalData.openid = auth.openid
    }
  },

  setAuth(auth) {
    this.globalData.user_id = auth.user_id
    this.globalData.openid = auth.openid
    wx.setStorageSync('atlas_auth', auth)
  },

  isAuthed() {
    return !!this.globalData.user_id
  },
})
