import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/projects/',
    method: 'get',
    params
  })
}

export function createProject(data) {
  return request({
    url: '/api/projects/',
    method: 'post',
    data
  })
}

export function updateProject(data) {
  return request({
    url: data.url,
    method: 'put',
    data
  })
}

export function deleteProject(data) {
  return request({
    url: data.url,
    method: 'delete'
  })
}
