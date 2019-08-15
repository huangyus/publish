import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/apigateway/maps/',
    method: 'get',
    params
  })
}

export function createMaps(data) {
  return request({
    url: '/api/apigateway/maps/',
    method: 'post',
    data
  })
}

export function updateMaps(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteMaps(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}

export function deployMaps(data) {
  return request({
    url: '/api/apigateway/deploy/',
    method: 'post',
    data
  })
}
