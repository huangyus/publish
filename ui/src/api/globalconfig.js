import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/apigateway/globalconfig/',
    method: 'get',
    params
  })
}

export function createGlobalConfig(data) {
  return request({
    url: '/api/apigateway/globalconfig/',
    method: 'post',
    data
  })
}

export function updateGlobalConfig(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deployGlobalConfig(data) {
  return request({
    url: '/api/apigateway/deploy/',
    method: 'post',
    data
  })
}
