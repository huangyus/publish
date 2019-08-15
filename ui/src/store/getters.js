const getters = {
  sidebar: state => state.app.sidebar,
  device: state => state.app.device,
  token: state => state.user.token,
  avatar: state => state.user.avatar,
  name: state => state.user.name,
  roles: state => state.user.roles,
  router: state => state.user.router,
  perms: state => state.user.perms,
  user: state => state.user.user,
  addRouters: state => state.permission.addRouters
}
export default getters
