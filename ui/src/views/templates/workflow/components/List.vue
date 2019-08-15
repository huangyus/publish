<template>
  <div>
    <el-table v-loading="listLoading" :data="list" element-loading-text="Loading" border fit highlight-current-row>
      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="模版名称" show-overflow-tooltip>
        <template slot-scope="scope">
          <span>{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="创建者" align="center" width="110">
        <template slot-scope="scope">
          {{ scope.row.created_by }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="创建时间" width="160">
        <template slot-scope="scope">
          <span>{{ scope.row.created_at }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240">
        <template slot-scope="scope">
          <el-button v-permission="['change_businesstemplate']" size="mini" type="primary" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button v-permission="['change_businesstemplate']" size="mini" type="primary" @click="handleCpoy(scope.row)">复制</el-button>
          <el-button v-permission="['delete_businesstemplate']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.page_size" @pagination="fetchData" />
  </div>
</template>

<script>
import { getList, deleteTemplate } from '@/api/wftemplate'
import Pagination from '@/components/Pagination'
import permission from '@/directive/permission/index' // 权限判断指令

import bus from '@/assets/eventBus'

export default {
  components: {
    Pagination
  },
  directives: { permission },
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
      list: null,
      rows: [],
      total: 0,
      listQuery: {
        page: 1,
        page_size: 20
      },
      form: {}
    }
  },
  mounted() {
    const that = this
    bus.$on('List', function() {
      that.fetchData()
    })
    bus.$on('Search', function(evt) {
      that.handleSearch(evt)
    })
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.listLoading = true
      getList(this.listQuery).then(response => {
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
      }).catch(error => {
        console.log(error)
      })
    },

    handleCpoy(row) {
      bus.$emit('templateCopy', row)
    },

    handleUpdate(row) {
      bus.$emit('templateUpdate', row)
    },

    handleDelete(row) {
      deleteTemplate(row).then(() => {
        this.$notify({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2000
        })
        const index = this.list.indexOf(row)
        this.list.splice(index, 1)
      })
    },

    handleSearch(search) {
      if (search) {
        this.listQuery = { name: search }
      }
      this.listLoading = true
      getList(this.listQuery).then(response => {
        console.log(response)
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
      })
    }
  }
}
</script>

<style>
.table-expand label {
  width: 100px;
  color: #99a9bf;
}
.table-workflow-expand label {
  width: 100px;
  color: #99a9bf;
}
.table-workflow-expand span {
  word-break: normal;
  width: auto;
  display: block;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow: hidden;
}
</style>
