import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/apigateway/index/',
    method: 'get',
    params
  })
}

export function createAPIGateWay(data) {
  return request({
    url: '/api/apigateway/index/',
    method: 'post',
    data
  })
}

export function updateAPIGateWay(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteAPIGateWay(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}

export function deployAPIGateWay(data) {
  return request({
    url: '/api/apigateway/deploy/',
    method: 'post',
    data
  })
}
