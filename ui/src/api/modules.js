import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/modules/',
    method: 'get',
    params
  })
}

export function createModules(data) {
  return request({
    url: '/api/modules/',
    method: 'post',
    data
  })
}

export function updateModules(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteModules(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}

export function refreshModules(data) {
  return request({
    url: '/api/modules/refresh/',
    method: 'post',
    data
  })
}

export function getGateway(params) {
  return request({
    url: '/api/gateway/',
    method: 'get',
    params
  })
}
