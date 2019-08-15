import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/apigateway/upstreams/',
    method: 'get',
    params
  })
}

export function createUpstreams(data) {
  return request({
    url: '/api/apigateway/upstreams/',
    method: 'post',
    data
  })
}

export function updateUpstreams(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteUpstreams(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}

export function deployUpstreams(data) {
  return request({
    url: '/api/apigateway/deploy/',
    method: 'post',
    data
  })
}
