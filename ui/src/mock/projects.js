import Mock from 'mockjs'
import { param2Obj } from '@/utils'

const List = []
const count = 40

for (let i = 0; i < count; i++) {
  List.push(Mock.mock({
    id: Mock.Random.id(),
    name: Mock.mock('@cword(2)'),
    git_url: Mock.mock('@county(true)'),
    git_username: Mock.mock('@cword(2)'),
    git_password: Mock.mock('@cword(2)'),
    svn_url: Mock.mock('@county(true)'),
    svn_username: Mock.mock('@county(true)'),
    svn_password: Mock.mock('@county(true)'),
    created_by: Mock.mock('@cname'),
    created: Mock.Random.now('yyyy-MM-dd HH:mm:ss'),
    updated: Mock.Random.now('yyyy-MM-dd HH:mm:ss'),
    desc: ''
  }))
}

export default {
  getList: config => {
    const { name, location, page = 1, limit = 20, sort } = param2Obj(config.url)

    let mockList = List.filter(item => {
      if (name && item.name !== +name) return false
      if (location && item.location !== location) return false
      return true
    })

    if (sort === '-id') {
      mockList = mockList.reverse()
    }

    const pageList = mockList.filter((item, index) => index < limit * page && index >= limit * (page - 1))

    return {
      total: mockList.length,
      data: pageList
    }
  }
}
