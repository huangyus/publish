import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/group/',
    method: 'get',
    params
  })
}

export function createGroup(data) {
  return request({
    url: '/api/group/',
    method: 'post',
    data
  })
}

export function updateGroup(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteGroup(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}
