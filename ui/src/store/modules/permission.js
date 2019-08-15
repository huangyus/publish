import { constantRouterMap } from '@/router'

/**
 * 递归过滤异步路由表，返回符合用户角色权限的路由表
 * @param routes asyncRouterMap
 * @param roles
 */
function filterAsyncRouter(routes, roles) {
  const res = []

  if (roles.length !== 0) {
    roles.forEach(role => {
      routes.forEach(route => {
        const tmp = { ...route }
        if (role.name === tmp.name) {
          res.push(tmp)
        }
        if (tmp.children && tmp.name !== 'Dashboard') {
          tmp.children = filterAsyncRouter(tmp.children, roles)
        }
        // if (role.name === tmp.name) {
        //   res.push(tmp)
        // } else if (route.children) {
        //   route.children.forEach((index, children) => {
        //     const child = { ...children }
        //     if (role.name === child.name) {
        //       res.children.push(child)
        //     }
        //   })
        // }
      })
    })
  } else {
    console.log(routes)
    routes.forEach(route => {
      if (route.name === 'Dashboard') {
        res.push(route)
      }
    })
  }

  return res
}

const permission = {
  state: {
    routers: constantRouterMap,
    addRouters: []
  },
  mutations: {
    SET_ROUTERS: (state, routers) => {
      state.addRouters = routers
      state.routers = constantRouterMap.concat(routers)
    }
  },
  actions: {
    GenerateRouters({ commit }, data) {
      return new Promise(resolve => {
        const router = data
        // if (roles.includes('admin')) {
        //   accessedRouters = constantRouterMap
        // } else {
        //   accessedRouters = filterAsyncRouter(roles)
        // }
        const accessedRouters = filterAsyncRouter(constantRouterMap, router)
        commit('SET_ROUTERS', accessedRouters)
        resolve()
      })
    }
  }
}

export default permission
