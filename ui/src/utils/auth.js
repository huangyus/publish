import Cookies from 'js-cookie'

const TokenKey = 'Token'
const RouterKey = 'Router'
const RoleKey = 'Role'
const PermsKey = 'Perms'
const expires = new Date(new Date().getTime() + 60 * 60 * 1000)

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
  return Cookies.set(TokenKey, token, { expires: expires })
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}

export function getRouter() {
  return Cookies.get(RouterKey)
}

export function setRouter(router) {
  return Cookies.set(RouterKey, router, { expires: expires })
}

export function removeRouter() {
  return Cookies.remove(RouterKey)
}

export function getRole() {
  return Cookies.get(RoleKey)
}

export function setRole(role) {
  return Cookies.set(RoleKey, role, { expires: expires })
}

export function removeRole() {
  return Cookies.remove(RoleKey)
}

export function getPerms() {
  return Cookies.get(PermsKey)
}

export function setPerms(perms) {
  return Cookies.set(PermsKey, perms, { expires: expires })
}

export function removePerms() {
  return Cookies.remove(PermsKey)
}
