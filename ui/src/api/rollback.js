import request from '@/utils/request'

export function createRollback(params) {
  return request({
    url: '/api/rollback/',
    method: 'post',
    params
  })
}

export function getList(params) {
  return request({
    url: '/api/rollback/',
    method: 'get',
    params
  })
}
