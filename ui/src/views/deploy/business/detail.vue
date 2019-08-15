<template>
  <div class="app-container">
    <el-row >
      <el-table :data="list" border>
        <el-table-column label="上线单名称">
          <template slot-scope="scope">{{ scope.row.name }}</template>
        </el-table-column>
        <el-table-column label="项目名称">
          <template slot-scope="scope">{{ scope.row.project }}</template>
        </el-table-column>
        <el-table-column label="模块名称">
          <template slot-scope="scope">{{ scope.row.modules }}</template>
        </el-table-column>
        <el-table-column label="服务器列表">
          <template slot-scope="scope">{{ scope.row.servers | serversFilter }}</template>
        </el-table-column>
        <el-table-column label="版本号">
          <template slot-scope="scope">{{ scope.row.version }}</template>
        </el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status | statusFilter">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-row>
    <el-row>
      <el-col :span="24">
        <div style="height:100%" class="scroll">
          <el-scrollbar wrap-class="scroll_wrap">
            <div v-for="(item, index) in logData" :key="index" :style="{color: item.color}" class="log">
              {{ item.text }}
              <el-popover v-if="item.detail" trigger="click" placement="right-end" width="700">
                <div v-for="(text, index) in item.detail" :key="index" :style="{color: text.color}" v-html="text.text">{{ text.text }}</div>
                <el-button slot="reference" :type="item.failed ? 'failed' : 'success' | statusFilter" size="mini">详情</el-button>
              </el-popover>
            </div>
          </el-scrollbar>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as business from '@/api/business'
import * as basic from '@/api/basic'
import { detailDeploy } from '@/api/deploy'

export default {
  filters: {
    statusFilter(status) {
      const statusMap = {
        pending: 'info',
        running: '',
        failed: 'danger',
        success: 'success'
      }
      return statusMap[status]
    },
    serversFilter(servers) {
      const data = JSON.parse(servers)
      return data.join(', ')
    }
  },
  data() {
    return {
      list: null,
      logData: [],
      listQuery: {
        page: 1,
        page_size: 20,
        task_id: undefined,
        deploy_type: undefined
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.listLoading = true
      if (this.$route.query.deploy_type === 'bs') {
        this.listQuery.task_id = this.$route.query.task_id
        business.getList(this.listQuery).then(response => {
          this.list = response.data.results
          this.listLoading = false
          this.detailData()
        }).catch(error => {
          console.log(error)
        })
      }
      if (this.$route.query.deploy_type === 'bc') {
        this.listQuery.task_id = this.$route.query.task_id
        basic.getList(this.listQuery).then(response => {
          this.list = response.data.results
          this.listLoading = false
        }).catch(error => {
          console.log(error)
        })
      }
    },
    detailData() {
      this.listQuery.task_id = this.$route.query.task_id
      this.listQuery.deploy_type = this.$route.query.deploy_type
      detailDeploy(this.listQuery).then(response => {
        this.logData = response.data.log
      }).catch(error => {
        console.log(error)
      })
    }
  }
}
</script>

<style>
  .scroll {
    margin-top: 15px;
    background-color: Silver;
    /* height: 300px; */
  }
  .log {
    margin-left: 15px;
    margin-top: 15px;
    margin-bottom: 15px;
    font-size: 16px;
  }
  .scroll_wrap {
    max-height: 600px;
  }
</style>
