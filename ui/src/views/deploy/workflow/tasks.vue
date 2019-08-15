<template>
  <div class="app-container">
    <el-row style="margin-top: 20px">
      <el-steps :active="active" align-center>
        <el-step v-for="item in steps" :key="item.index" :title="'步骤' + item.idx" :status="item.status"/>
      </el-steps>
    </el-row>
    <el-row :gutter="20" type="flex" justify="center">
      <el-col v-for="item in steps" :key="item.index" :span="12">
        <el-form label-position="left" inline class="table-workflow-expand">
          <el-form-item label="项目名称">
            <span>{{ item.project }}</span>
          </el-form-item>
          <el-form-item label="模块名称">
            <span>{{ item.modules }}</span>
          </el-form-item>
          <el-form-item label="版本号">
            <span>{{ item.version }}</span>
          </el-form-item>
          <el-form-item label="服务器列表">
            <span>{{ item.servers | serversFilter }}</span>
          </el-form-item>
          <el-form-item label="描述">
            <span>{{ item.desc }}</span>
          </el-form-item>
        </el-form>
      </el-col>
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
import { getList } from '@/api/workflow'
import { mapGetters } from 'vuex'
import moment from 'moment/moment'

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
      if (typeof (servers) === 'string') {
        const data = JSON.parse(servers)
        return data.join(', ')
      }
      return servers.join(', ')
    }
  },
  data() {
    return {
      logData: [],
      active: 1,
      steps: [],
      listQuery: {
        page_size: 20,
        page: 1
      }
    }
  },
  computed: {
    ...mapGetters([
      'user',
      'roles'
    ])
  },
  watch: {
    steps: function(val, nval) {
      console.log(val)
      if (val.length > nval.length) {
        this.Socketinit()
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    /**
     * @return {string}
     */
    Timestamp() {
      return moment().format('YYYYMMDDHHmmss')
    },

    Socketinit() {
      const that = this
      setTimeout(() => {}, 30 * 1000)
      // for (let i = 1; i <= that.steps.length; i++) {
      const socket = new WebSocket(process.env.WEBSOCKET_API + '/ws/api/' + this.$route.query.task_id + '/')
      console.log(socket)
      socket.onopen = function(evt) {
        console.log('websocket opened')
      }
      socket.onmessage = function(evt) {
        evt = JSON.parse(evt.data)
        if (evt.message.step > that.active) {
          that.active++
          console.log('active: ' + that.active)
        }
        if (evt.message === 'end') {
          that.fetchData()
          socket.close()
        } else if (evt.message.failed) {
          // that.failed_servers.push(evt.message.host)
          that.logData.push(evt.message)
        } else if (!evt.message.failed && evt.message.failed !== undefined) {
          // that.success_servers.push(evt.message.host)
          that.logData.push(evt.message)
        } else {
          that.logData.push(evt.message)
        }
        that.fetchData()
        // console.log(that.logData)
      }
      socket.onclose = function(evt) {
        console.log('websocket closed')
      }
      // }
    },

    fetchData() {
      this.listLoading = true
      this.listQuery.task_id = this.$route.query.task_id
      getList(this.listQuery).then(response => {
        this.list = response.data.results
        this.total = response.data.count
        this.steps = JSON.parse(response.data.results[0].steps)
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
    /* height: 300px; */
  }
  .log {
    margin-left: 15px;
    margin-top: 15px;
    margin-bottom: 15px;
    font-size: 16px;
  }
  .scroll_wrap {
    max-height: 600px
  }
  .table-workflow-expand label {
    width: 100px;
    color: #99a9bf;
  }

  .table-workflow-expand .el-form-item {
    /* margin-right: 0; */
    margin-left: 35%;
    margin-bottom: 0;
    /* width: 50%; */
    display:block;
  }
  .table-workflow-expand span {
    word-break:normal; width:auto; display:block; white-space:pre-wrap;word-wrap : break-word ;overflow: hidden ;
  }
</style>
