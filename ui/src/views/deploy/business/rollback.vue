<template>
  <div class="app-container">
    <el-row>
      <el-table :data="list" border>
        <el-table-column label="上线单名称">
          <template slot-scope="scope">{{ scope.row.business.name }}</template>
        </el-table-column>
        <el-table-column label="项目名称">
          <template slot-scope="scope">{{ scope.row.business.project }}</template>
        </el-table-column>
        <el-table-column label="模块名称">
          <template slot-scope="scope">{{ scope.row.business.modules }}</template>
        </el-table-column>
        <el-table-column label="版本号">
          <template slot-scope="scope">{{ scope.row.business.version }}</template>
        </el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">
            <el-tag :type="scope.row.business.status | statusFilter">{{ scope.row.business.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="回滚状态">
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
import * as rollback from '@/api/rollback'

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
    }
  },
  data() {
    return {
      list: null,
      logData: [],
      listQuery: {
        page: 1,
        page_size: 20
      }
    }
  },
  created() {
    this.fetchData()
    this.Socketinit()
  },
  methods: {
    Socketinit() {
      const that = this
      const socket = new WebSocket(process.env.WEBSOCKET_API + '/ws/api/' + this.$route.query.task_id + '/')
      console.log(socket)
      socket.onopen = function(evt) {
        console.log('websocket opened')
      }
      socket.onmessage = function(evt) {
        evt = JSON.parse(evt.data)
        if (evt.message === 'end') {
          that.fetchData()
          socket.close()
        } else if (evt.message.failed) {
          that.failed_servers.push(evt.message.host)
          that.logData.push(evt.message)
        } else if (!evt.message.failed && evt.message.failed !== undefined) {
          that.success_servers.push(evt.message.host)
          that.logData.push(evt.message)
        } else {
          that.logData.push(evt.message)
        }
        that.fetchData()
        console.log(that.logData)
      }
      socket.onclose = function(evt) {
        console.log('websocket closed')
      }
    },
    fetchData() {
      this.listLoading = true
      this.listQuery.task_id = this.$route.query.task_id
      rollback.getList(this.listQuery).then(response => {
        this.list = response.data
        this.total = response.data.length
        this.listLoading = false
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
  height: 900px;
}
.log {
  margin-left: 15px;
  margin-top: 15px;
  font-size: 16px;
}
</style>
