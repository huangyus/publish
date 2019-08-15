import request from '@/utils/request'

export function login(username, password) {
  return request({
    url: '/api/api-token-auth/',
    method: 'post',
    data: {
      username,
      password
    }
  })
}

export function getInfo(params) {
  return request({
    url: '/api/user/',
    method: 'get',
    params
  })
}

export function logout() {
  return request({
    url: '/user/logout',
    method: 'post'
  })
}
