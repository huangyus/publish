<template>
  <div>
    <el-table v-loading="listLoading" :data="list" element-loading-text="Loading" border fit highlight-current-row>
      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="中间件" show-overflow-tooltip>
        <template slot-scope="scope">
          <span>{{ scope.row.component }}</span>
          <!-- <router-link :to="'/deploy/detail??task_id=' + scope.row.id + '&deploy_type=bc'" class="link-type">{{ scope.row.name }}</router-link> -->
        </template>
      </el-table-column>
      <!-- <el-table-column label="项目" align="center" width="110">
        <template slot-scope="scope">
          <span>{{ scope.row.project }}</span>
        </template>
      </el-table-column>
      <el-table-column label="中间件" align="center" width="110">
        <template slot-scope="scope">
          <span>{{ scope.row.component }}</span>
        </template>
      </el-table-column> -->
      <el-table-column label="版本" align="center" width="110">
        <template slot-scope="scope">
          <span>{{ scope.row.version }}</span>
        </template>
      </el-table-column>
      <!-- <el-table-column label="部署类型" align="center" width="120">
        <template slot-scope="scope">
          <el-tag>{{ scope.row.task_type }}</el-tag>
        </template>
      </el-table-column> -->
      <el-table-column label="创建者" align="center" width="110">
        <template slot-scope="scope">
          {{ scope.row.created_by }}
        </template>
      </el-table-column>
      <!-- <el-table-column class-name="status-col" label="状态" align="center" width="95">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="线上版本" align="center" width="110">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.current" type="success">{{ scope.row.current ? '当前': '' }}</el-tag>
        </template>
      </el-table-column> -->
      <el-table-column align="center" label="创建时间" width="160">
        <template slot-scope="scope">
          <span>{{ scope.row.created_at }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240">
        <template slot-scope="scope">
          <el-button size="mini" type="primary" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button size="mini" type="primary" @click="handleCpoy(scope.row)">复制</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.page_size" @pagination="fetchData" />
  </div>
</template>

<script>
import { createDeploy } from '@/api/deploy'
import { createRollback } from '@/api/rollback'
import { getList, deleteTemplate } from '@/api/bctemplate'
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
      }
    }
  },
  mounted() {
    const that = this
    bus.$on('ConfirmDeploy', function(event) {
      that.handleDeploy(event)
    })
    bus.$on('ConfirmRollback', function(event) {
      that.handleRollback(event)
    })
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

    handleRediret(row, type) {
      this.rows = []
      if (row.confirm && type === 'deploy') {
        this.rows.push(row)
        bus.$emit('dialogConfirmVisible', true)
        bus.$emit('Confirmstatus', 'confirm')
        bus.$emit('Confirmrows', this.rows)
      } else if (type === 'rollback') {
        this.rows.push(row)
        bus.$emit('dialogConfirmVisible', true)
        bus.$emit('Confirmstatus', 'rollback')
        bus.$emit('Confirmrows', this.rows)
      } else {
        this.handleDeploy(row.id)
      }
    },

    handleDeploy(task_id) {
      createDeploy({ task_id: task_id, deploy_type: 'bs' }).then(() => {}).catch(error => {
        this.$notify({
          title: '错误',
          message: '创建失败： ' + error.response.data,
          type: 'error',
          duration: 2000
        })
      })
      window.location.href = '/#/deploy/tasks/?task_id=' + task_id + '&deploy_type=bs'
    },

    handleRollback(task_id) {
      createRollback({ task_id: task_id, deploy_type: 'bs' }).then(() => {}).catch(error => {
        this.$notify({
          title: '错误',
          message: '创建失败： ' + error.response.data.message,
          type: 'error',
          duration: 2000
        })
      })
      window.location.href = '/#/deploy/rollback/?task_id=' + task_id + '&deploy_type=bs'
    },

    handleUpdate(row) {
      bus.$emit('templateUpdate', row)
    },

    handleCpoy(row) {
      bus.$emit('templateCopy', row)
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
.link-type {
  color: #337ab7;
  cursor: pointer;
}
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
