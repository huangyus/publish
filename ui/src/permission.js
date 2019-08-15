import router from './router'
import store from './store'
import NProgress from 'nprogress' // Progress 进度条
import 'nprogress/nprogress.css'// Progress 进度条样式
import { Message } from 'element-ui'
import { getToken } from '@/utils/auth' // 验权

NProgress.configure({ showSpinner: false }) // NProgress Configuration

// function hasPermission(roles, permissionRoles) {
//   if (roles.name[0].name.indexOf('admin') >= 0) return true // admin permission passed directly
//   if (!permissionRoles) return true
//   return roles.router.some(router => permissionRoles.indexOf(router.path) >= 0)
// }

const whiteList = ['/login'] // 不重定向白名单
router.beforeEach((to, from, next) => {
  NProgress.start()
  if (getToken()) {
    if (to.path === '/login') {
      next({ path: '/' })
      NProgress.done() // if current page is dashboard will not trigger	afterEach hook, so manually handle it
    } else {
      const hasRoles = store.getters.roles && store.getters.roles.length > 0
      if (hasRoles) {
        next()
      } else {
        try {
          store.dispatch('GetInfo').then(response => {
            // console.log(store.getters.roles)
            // console.log(store.getters.router)
            store.dispatch('GenerateRouters', store.getters.router).then(() => {
              console.log('addrouters', store.getters.addRouters)
              router.addRoutes(store.getters.addRouters)
              next({ ...to, replace: true })
            })
          })
        } catch (error) {
          store.dispatch('FedLogOut').then(() => {
            Message.error(error.Message || '验证失败,请重新登录')
            next({ path: '/login' })
          })
        }
      }
    }
  } else {
    if (whiteList.indexOf(to.path) !== -1) {
      next()
    } else {
      next(`/login?redirect=${to.path}`) // 否则全部重定向到登录页
      NProgress.done()
    }
  }
})

router.afterEach(() => {
  NProgress.done() // 结束Progress
})
