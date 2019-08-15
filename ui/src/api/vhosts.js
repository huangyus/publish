import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/apigateway/vhosts/',
    method: 'get',
    params
  })
}

export function createVhosts(data) {
  return request({
    url: '/api/apigateway/vhosts/',
    method: 'post',
    data
  })
}

export function updateVhosts(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteVhosts(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}

export function deployVhosts(data) {
  return request({
    url: '/api/apigateway/deploy/',
    method: 'post',
    data
  })
}
