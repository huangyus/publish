import Mock from 'mockjs'
import loginAPI from './login'
// import envAPI from './env'
// import projectAPI from './projects'
// import datacenterAPI from './datacenter'
// import middlewareAPI from './middleware'
// import businessAPI from './business'
// import basicAPI from './basic'

Mock.XHR.prototype.proxy_send = Mock.XHR.prototype.send
Mock.XHR.prototype.send = function() {
  if (this.custom.xhr) {
    this.custom.xhr.withCredentials = this.withCredentials || false
  }
  this.proxy_send(...arguments)
}

// 登录相关
Mock.mock(/\/user\/login/, 'post', loginAPI.login)
Mock.mock(/\/user\/logout/, 'post', loginAPI.logout)
Mock.mock(/\/user\/info.*/, 'get', loginAPI.getUserInfo)

// 项目环境相关
// Mock.mock(/\/env/, 'get', envAPI.getList)

// 项目相关
// Mock.mock(/\/projects/, 'get', projectAPI.getList)

// 数据中心
// Mock.mock(/\/datacenter/, 'get', datacenterAPI.getList)

// 组件管理
// Mock.mock(/\/middleware/, 'get', middlewareAPI.getList)

// 上线部署 - 业务部署
// Mock.mock(/\/business/, 'get', businessAPI.getList)
// Mock.mock(/\/business/, 'get', basicAPI.getList)

export default Mock
