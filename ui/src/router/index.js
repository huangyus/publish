import Vue from 'vue'
import Router from 'vue-router'

// in development-env not use lazy-loading, because lazy-loading too many pages will cause webpack hot update too slow. so only in production use lazy-loading;
// detail: https://panjiachen.github.io/vue-element-admin-site/#/lazy-loading

Vue.use(Router)

/* Layout */
import Layout from '../views/layout/Layout'

/**
* hidden: true                   if `hidden:true` will not show in the sidebar(default is false)
* alwaysShow: true               if set true, will always show the root menu, whatever its child routes length
*                                if not set alwaysShow, only more than one route under the children
*                                it will becomes nested mode, otherwise not show the root menu
* redirect: noredirect           if `redirect:noredirect` will no redirect in the breadcrumb
* name:'router-name'             the name is used by <keep-alive> (must set!!!)
* meta : {
    title: 'title'               the name show in submenu and breadcrumb (recommend set)
    icon: 'svg-name'             the icon show in the sidebar,
  }
**/
export const constantRouterMap = [
  { path: '/login', component: () => import('@/views/login/index'), hidden: true },
  { path: '/404', component: () => import('@/views/404'), hidden: true },

  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    name: 'Dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: 'Dashboard', icon: 'dashboard' }
    }]
  },

  {
    path: '/datacenter',
    component: Layout,
    name: '数据中心',
    children: [{
      path: 'index',
      name: '数据中心',
      component: () => import('@/views/datacenter/index'),
      meta: { title: '数据中心', icon: 'data-center' }
    }, {
      path: 'servers',
      name: '服务器列表',
      hidden: true,
      component: () => import('@/views/datacenter/servers/index'),
      meta: { title: '服务器列表' }
    }]
  },

  {
    path: '/apigateway',
    component: Layout,
    name: '负载均衡',
    children: [{
      path: '',
      name: '负载均衡',
      component: () => import('@/views/apigateway/index'),
      meta: { title: '负载均衡', icon: 'apigateway' }
    }, {
      path: 'config',
      name: '负载均衡配置',
      hidden: true,
      component: () => import('@/views/apigateway/config'),
      meta: { title: '负载均衡配置' }
    }]
  },

  {
    path: '/projects',
    component: Layout,
    name: '项目管理',
    meta: { title: '项目管理', icon: 'project' },
    // redirect: '/project',
    children: [
      {
        path: 'project',
        name: '项目配置',
        component: () => import('@/views/projects/index'),
        meta: { title: '项目配置' }
      },
      {
        path: 'module',
        name: '模块配置',
        component: () => import('@/views/projects/module/index'),
        meta: { title: '模块配置' }
      },
      {
        path: 'group',
        name: '分组配置',
        component: () => import('@/views/projects/group/index'),
        meta: { title: '分组配置' }
      }
    ]
  },

  {
    path: '/middleware',
    component: Layout,
    name: '部署编排',
    children: [{
      path: 'index',
      name: '部署编排',
      component: () => import('@/views/middleware/index'),
      meta: { title: '部署编排', icon: 'playbook' }
    }]
  },

  {
    path: '/template',
    component: Layout,
    name: '部署模版',
    meta: { title: '部署模版', icon: 'template' },
    children: [
      {
        path: 'business',
        name: '单部署模版',
        component: () => import('@/views/templates/business/index'),
        meta: { title: '单部署模版' }
      },
      {
        path: 'basic',
        name: '中间件模版',
        component: () => import('@/views/templates/basic/index'),
        meta: { title: '中间件模版' }
      },
      {
        path: 'workflow',
        name: '工作流模版',
        component: () => import('@/views/templates/workflow/index'),
        meta: { title: '工作流模版' }
      }
    ]
  },

  {
    path: '/deploy',
    component: Layout,
    name: '上线部署',
    meta: { title: '上线部署', icon: 'deploy' },
    children: [
      {
        path: 'workflow',
        name: '工作流部署',
        component: () => import('@/views/deploy/workflow/index'),
        meta: { title: '工作流部署' }
      },
      {
        path: 'business',
        name: '单业务部署',
        component: () => import('@/views/deploy/business/index'),
        meta: { title: '单业务部署' }
      },
      {
        path: 'basic',
        name: '中间件部署',
        component: () => import('@/views/deploy/basic/index'),
        meta: { title: '中间件部署' }
      },
      {
        path: 'tasks',
        name: '部署任务',
        hidden: true,
        component: () => import('@/views/deploy/business/tasks'),
        meta: { title: '部署任务' }
      },
      {
        path: 'detail',
        name: '发布详情',
        hidden: true,
        component: () => import('@/views/deploy/business/detail'),
        meta: { title: '发布详情' }
      },
      {
        path: 'rollback',
        name: '回滚',
        hidden: true,
        component: () => import('@/views/deploy/business/rollback'),
        meta: { title: '回滚详情' }
      },
      {
        path: 'wftasks',
        name: '工作流部署任务',
        hidden: true,
        component: () => import('@/views/deploy/workflow/tasks'),
        meta: { title: '部署任务' }
      },
      {
        path: 'wfdetail',
        name: '工作流部署任务',
        hidden: true,
        component: () => import('@/views/deploy/workflow/detail'),
        meta: { title: '工作流部署任务' }
      }
    ]
  },

  {
    path: '/logaudit',
    component: Layout,
    name: '日志审计',
    children: [{
      path: 'index',
      name: '日志审计',
      component: () => import('@/views/logaudit/index'),
      meta: { title: '日志审计', icon: 'log' }
    }]
  },
  // {
  //   path: '/test',
  //   component: Layout,
  //   name: '测试',
  //   children: [{
  //     path: 'index',
  //     name: '测试',
  //     component: () => import('@/views/test'),
  //     meta: { title: '测试', icon: 'log' }
  //   }]
  // },

  { path: '*', redirect: '/404', hidden: true }
]

export default new Router({
  // mode: 'history', //后端支持可开
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRouterMap
})
