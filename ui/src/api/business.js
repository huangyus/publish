import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/business/',
    method: 'get',
    params
  })
}

export function filterVersion(params) {
  return request({
    url: '/api/version/',
    method: 'get',
    params
  })
}

export function createBusiness(data) {
  return request({
    url: '/api/business/',
    method: 'post',
    data
  })
}

export function updateBusiness(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteBusiness(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}
