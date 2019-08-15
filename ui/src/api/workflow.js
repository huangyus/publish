import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/workflow/',
    method: 'get',
    params
  })
}

export function createWorkFlow(data) {
  return request({
    url: '/api/workflow/',
    method: 'post',
    data
  })
}

export function updateWorkFlow(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteWorkFlow(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}

export function filterVersion(params) {
  return request({
    url: '/api/version/',
    method: 'get',
    params
  })
}
