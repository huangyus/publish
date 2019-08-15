import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/servers/',
    method: 'get',
    params
  })
}

export function createServer(data) {
  return request({
    url: '/api/servers/',
    method: 'post',
    data
  })
}

export function updateServer(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteServer(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}
