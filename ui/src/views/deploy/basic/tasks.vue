<template>
  <div class="app-container">
    <el-row >
      <el-table :data="list" border>
        <el-table-column label="上线单名称">
          <template slot-scope="scope">{{ scope.row.name }}</template>
        </el-table-column>
        <el-table-column v-if="this.$route.query.deploy_type === 'bs'" label="项目名称">
          <template slot-scope="scope">{{ scope.row.project }}</template>
        </el-table-column>
        <el-table-column v-if="this.$route.query.deploy_type === 'bs'" label="模块名称">
          <template slot-scope="scope">{{ scope.row.modules }}</template>
        </el-table-column>
        <el-table-column v-if="this.$route.query.deploy_type === 'bc'" label="组件名称">
          <template slot-scope="scope">{{ scope.row.component }}</template>
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
        task_id: undefined
      },
      success_servers: [],
      failed_servers: [],
      dialogFormVisible: false,
      checkAll: false,
      isIndeterminate: true,
      form: {},
      formLabelWidth: '120px',
      rules: {
        name: [{ required: true, message: '上线单名称必填', trigger: 'blur' }],
        project: [{ required: true, message: '项目必填', trigger: 'change' }],
        modules: [{ required: true, message: '模块必填', trigger: 'change' }],
        version: [{ required: true, message: '版本必填', trigger: 'change' }],
        servers: [{ required: true, message: '服务器列表必填', trigger: 'change' }],
        layout: [{ required: true, message: '部署方式必填', trigger: 'change' }]
      },
      servers: []

    }
  },
  computed: {
    ...mapGetters([
      'user',
      'roles'
    ])
  },
  created() {
    this.fetchData()
    this.Socketinit()
  },
  methods: {
    Timestamp() {
      return moment().format('YYYYMMDDHHmmss')
    },

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
      const deploy_type = this.$route.query.deploy_type
      this.listLoading = true
      this.listQuery.task_id = this.$route.query.task_id
      if (deploy_type === 'bs') {
        business.getList(this.listQuery).then(response => {
          this.list = response.data.results
          this.total = response.data.count
          setTimeout(() => {
            this.listLoading = false
          }, 1.5 * 1000)
        }).catch(error => {
          console.log(error)
        })
      }
      if (deploy_type === 'bc') {
        basic.getList(this.listQuery).then(response => {
          this.list = response.data.results
          this.total = response.data.count
          setTimeout(() => {
            this.listLoading = false
          }, 1.5 * 1000)
        }).catch(error => {
          console.log(error)
        })
      }
    }

    // handleRelunch(row) {
    //   this.form = {
    //     name: this.Timestamp() + '-' + row.project + '-' + row.modules,
    //     project: row.project,
    //     modules: row.modules,
    //     version: row.version,
    //     layout: row.layout,
    //     env: row.env,
    //     servers: this.failed_servers.length !== 0 ? this.failed_servers : JSON.parse(row.servers)
    //   }
    //   this.dialogFormVisible = true
    //   this.$nextTick(() => {
    //     this.$refs['dataForm'].clearValidate()
    //   })
    // },

    // handleCheckAll(val) {
    //   this.servers = val || []
    //   this.isIndeterminate = false
    // },

    // handleChecked(value) {
    //   const checkedCount = value.length
    //   this.checkAll = checkedCount === this.servers.length
    //   this.isIndeterminate = checkedCount > 0 && checkedCount < this.servers.length
    // },

    // Relunch() {
    //   alert('功能暂未开发')
    // }
  }
}
</script>

<style>
  .scroll {
    margin-top: 15px;
    background-color: Silver;
  }
  .log {
    margin-left: 15px;
    margin-top: 10px;
    margin-bottom: 10px;
    font-size: 16px;
  }
  .scroll_wrap {
    max-height: 800px;
  }
</style>
