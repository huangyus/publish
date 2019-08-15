import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/bstemplate/',
    method: 'get',
    params
  })
}

export function createTemplate(data) {
  return request({
    url: '/api/bstemplate/',
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
