import request from '@/utils/request'

export function createDeploy(params) {
  return request({
    url: '/api/deploy/',
    method: 'post',
    params
  })
}

export function detailDeploy(params) {
  return request({
    url: '/api/deploy/',
    method: 'get',
    params
  })
}
