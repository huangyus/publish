import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/datacenter/',
    method: 'get',
    params
  })
}

export function createDatacenter(data) {
  return request({
    url: '/api/datacenter/',
    method: 'post',
    data
  })
}

export function updateDatacenter(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteDatacenter(data) {
  return request({
    url: data.url,
    method: 'delete',
    data
  })
}
