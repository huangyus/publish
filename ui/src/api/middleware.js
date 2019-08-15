import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/middleware/',
    method: 'get',
    params
  })
}

export function createMiddleware(data) {
  return request({
    url: '/api/middleware/',
    method: 'post',
    data
  })
}

export function updateMiddleware(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteMiddleware(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}
