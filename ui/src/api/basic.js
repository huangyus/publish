import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/basic/',
    method: 'get',
    params
  })
}

export function createBasic(data) {
  return request({
    url: '/api/basic/',
    method: 'post',
    data
  })
}

export function deleteBasic(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}
