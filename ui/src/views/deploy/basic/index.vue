<template>
  <div class="app-container">
    <edit />
    <collapse />
    <confirm />
    <list />
  </div>
</template>

<script>
import Edit from './components/Edit'
import List from './components/List'
import Confirm from './components/Confirm'
import Collapse from './components/Collapse'
import Pagination from '@/components/Pagination'

export default {
  components: {
    Pagination,
    Edit,
    List,
    Confirm,
    Collapse
  },
  filters: {
    statusFilter(status) {
      const statusMap = {
        pending: '',
        success: 'success',
        failed: 'danger'
      }
      return statusMap[status]
    },
    serversFilter(servers) {
      if (typeof (servers) === 'string') {
        const data = JSON.parse(servers)
        return data.join(', ')
      }
      return servers.join(', ')
    }
  },
  data() {
    return {
      list: null
    }
  }
}
</script>
