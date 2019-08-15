<template>
  <div>
    <el-table v-loading="listLoading" :data="list" element-loading-text="Loading" border fit highlight-current-row>
      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="上线单名称" show-overflow-tooltip>
        <template slot-scope="scope">
          <router-link :to="'/deploy/wfdetail??task_id=' + scope.row.id + '&deploy_type=workflow'" class="link-type">{{ scope.row.name }}</router-link>
        </template>
      </el-table-column>
      <el-table-column label="项目" align="center" width="110">
        <template slot-scope="scope">
          <span>{{ scope.row.project }}</span>
        </template>
      </el-table-column>
      <el-table-column label="模块" align="center" width="110">
        <template slot-scope="scope">
          <span>{{ scope.row.modules }}</span>
        </template>
      </el-table-column>
      <el-table-column label="版本号" align="center" width="95">
        <template slot-scope="scope">
          {{ scope.row.version }}
        </template>
      </el-table-column>
      <el-table-column label="部署类型" align="center" width="120">
        <template slot-scope="scope">
          <el-tag>{{ scope.row.task_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建者" align="center" width="110">
        <template slot-scope="scope">
          {{ scope.row.created_by }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="状态" align="center" width="95">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="回滚状态" align="center" width="110">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.rollback_status" :type="scope.row.rollback_status | statusFilter">{{ scope.row.rollback_status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" label="创建时间" width="160">
        <template slot-scope="scope">
          <span>{{ scope.row.created_at }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240">
        <template slot-scope="scope">
          <el-button v-permission="['run_deploy']" v-if="scope.row.status !== 'success'" size="mini" @click="handleRediret(scope.row, 'deploy')">发布</el-button>
          <!--          <el-button v-permission="['run_deploy']" v-if="scope.row.task_type==='simple'" size="mini" type="danger" @click="handleRediret(scope.row, 'rollback')">回滚</el-button>-->
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.page_size" @pagination="fetchData" />
  </div>
</template>

<script>
import { createDeploy } from '@/api/deploy'
import { getList, deleteWorkFlow } from '@/api/workflow'
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
      total: 0,
      list: null,
      listQuery: {
        page_size: 20,
        page: 1
      }
    }
  },
  mounted() {
    const that = this
    bus.$on('ConfirmDeploy', function(event) {
      that.handleDeploy(event)
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
        for (let i = 0; i < this.list.length; i++) {
          if (this.list[i].steps) {
            this.list[i].steps = JSON.parse(this.list[i].steps)
          }
        }
        this.listLoading = false
      }).catch(error => {
        console.log(error)
      })
    },

    handleDelete(row) {
      deleteWorkFlow(row).then(() => {
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

    handleRediret(row, type) {
      this.rows = []
      if (row.confirm && type === 'deploy') {
        this.rows.push(row)
        bus.$emit('dialogConfirmVisible', true)
        bus.$emit('Confirmstatus', 'confirm')
        bus.$emit('Confirmrows', this.rows)
      // } else if (type === 'rollback') {
      //   this.rows.push(row)
      //   bus.$emit('dialogConfirmVisible', true)
      //   bus.$emit('Confirmstatus', 'rollback')
      //   bus.$emit('Confirmrows', this.rows)
      } else {
        this.handleDeploy(row.id)
      }
    },

    handleDeploy(task_id) {
      createDeploy({ task_id: task_id, deploy_type: 'workflow' }).then(() => {}).catch(error => {
        this.$notify({
          title: '错误',
          message: '创建失败： ' + error.response.data,
          type: 'error',
          duration: 2000
        })
      })
      window.location.href = '/#/deploy/wftasks/?task_id=' + task_id + '&deploy_type=workflow'
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
</style>
