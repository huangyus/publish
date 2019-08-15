import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/bctemplate/',
    method: 'get',
    params
  })
}

export function createTemplate(data) {
  return request({
    url: '/api/bctemplate/',
    method: 'post',
    data
  })
}

export function updateTemplate(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteTemplate(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}
