import request from '@/utils/request'

export function getList(params) {
  return request({
    url: '/api/dashboard/',
    method: 'get',
    params
  })
}
export function getListPie(params) {
  return request({
    url: '/api/dashboardpie/',
    method: 'get',
    params
  })
}
