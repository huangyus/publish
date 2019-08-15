import store from '@/store'

export default{
  inserted(el, binding, vnode) {
    const { value } = binding
    const perms = store.getters.perms

    if (value && value instanceof Array && value.length > 0) {
      const permissionRoles = value

      const hasPermission = perms.some(perm => {
        return permissionRoles.includes(perm.codename)
      })

      if (!hasPermission) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    } else {
      throw new Error(`need roles! Like v-permission="['admin','editor']"`)
    }
  }
}
