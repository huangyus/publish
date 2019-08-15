<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_upstreams']" type="primary" icon="el-icon-edit" @click="handleCreate">新建节点组</el-button>
      </el-col>
      <el-col :span="6">
        <el-input placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" />
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogLogVisible" title="详细日志">
      <div v-for="(item, index) in logData" :key="index" :style="{color: item.color}" class="log">
        <div v-for="(text, index) in item.detail" :key="index" :style="{color: text.color}" v-html="text.text">{{ text.text }}</div>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[status]" :close-on-click-modal="false">
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-form-item :label-width="formLabelWidth" label="节点组名称" prop="name">
          <el-col :span="12">
            <el-select v-model="form.name" allow-create filterable clearable placeholder="请输入节点组名称" style="width: 396px" @visible-change="groupfetchData" @change="change_upstream(form.name)">
              <el-option v-for="(item, index) in groupoptions" :key="index" :label="item.label" :value="item.value" />
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="节点组注释" prop="desc">
          <el-col :span="12">
            <el-input v-model="form.desc" placeholder="节点组注释" />
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="IP_HASH" prop="ip_hash">
          <el-checkbox v-model="form.ip_hash">启用根据源地址引导流量</el-checkbox>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="Keepalive" prop="keepalive">
          <el-col :span="12">
            <el-input v-model="form.keepalive" placeholder="节点组最大空闲keepalive连接数" />
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="HTTP 检测" prop="http_check">
          <el-checkbox v-model="form.http_check">启用节点 HTTP 状态检测</el-checkbox><i class="el-icon-question" />
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="TCP 检测" prop="tcp_check">
          <el-checkbox v-model="form.tcp_check">启用节点 TCP 状态检测</el-checkbox><i class="el-icon-question" />
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="是否启用" prop="status">
          <el-checkbox v-model="form.status">启用负载均衡</el-checkbox><i class="el-icon-question" />
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="部署方式" prop="layout">
          <el-col :span="12">
            <el-select v-model="form.layout" clearable placeholder="部署方式" filterable style="width: 100%" @visible-change="middlewarefetchData">
              <el-option-group v-for="group in layoutoptions" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value" />
              </el-option-group>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item v-if="form.layout ==='0'" prop="custom_command">
          <el-col>
            <el-input v-model="form.custom_command" :rows="9" type="textarea" title="可用的宏替换，（${NGINX_HOME}）nginx配置目录， （${NGINX_RUN}）nginx启动命令， （${FILENAME}）nginx配置文件名" placeholder="nginx的部署命令，请以换行分隔" />
          </el-col>
        </el-form-item>
        <div class="divider" />
        <el-row>
          <el-col :span="20">
            <el-button type="success" style="margin-top: 15px; margin-bottom: 15px" size="mini" @click="add_upstream">增加节点</el-button>
          </el-col>
        </el-row>
        <el-table :data="form.upstreams" border fit highlight-current-row>
          <el-table-column label="地址">
            <template slot-scope="scope">
              <el-form-item :prop="'upstreams.' + scope.$index + '.address'" :rules="{ required: true, message: '地址必填', trigger: 'blur' }" class="upstreams">
                <el-input v-model="scope.row.address" placeholder="地址" />
              </el-form-item>
            </template>
          </el-table-column>
          <el-table-column label="端口">
            <template slot-scope="scope">
              <el-form-item :prop="'upstreams.' + scope.$index + '.port'" :rules="{ required: true, message: '端口必填', trigger: 'blur' }" class="upstreams">
                <el-input v-model="scope.row.port" placeholder="端口" />
              </el-form-item>
            </template>
          </el-table-column>
          <el-table-column label="权重">
            <template slot-scope="scope">
              <el-form-item class="upstreams">
                <el-input v-model="scope.row.weight" placeholder="权重（1-100）" />
              </el-form-item>
            </template>
          </el-table-column>
          <el-table-column label="重试（次）">
            <template slot-scope="scope">
              <el-form-item class="upstreams">
                <el-input v-model="scope.row.max_fails" placeholder="重试次数（1-99）" />
              </el-form-item>
            </template>
          </el-table-column>
          <el-table-column label="超时（秒）">
            <template slot-scope="scope">
              <el-form-item class="upstreams">
                <el-input v-model="scope.row.fail_timeout" placeholder="超时时间（秒）" />
              </el-form-item>
            </template>
          </el-table-column>
          <el-table-column label="状态" align="center" width="50">
            <template slot-scope="scope">
              <el-form-item class="status">
                <el-checkbox v-model="scope.row.status" placeholder="状态" />
              </el-form-item>
            </template>
          </el-table-column>
          <el-table-column label="操作" align="center" width="50">
            <template slot-scope="scope">
              <a @click="del_upstream(scope.$index)"><i class="el-icon-circle-close" style="font-size: 20px" /></a>
            </template>
          </el-table-column>
        </el-table>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="status==='create'?createData():updateData()">确 定</el-button>
      </div>
    </el-dialog>

    <el-table v-loading="listLoading" :data="list" element-loading-text="Loading" border fit highlight-current-row>
      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="节点组名称">
        <template slot-scope="scope">
          <span>{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column :formatter="toHtml" label="节点" align="center" prop="upstreams" width="230">
        <!-- <template slot-scope="scope">
          <span>{{ scope.row.upstreams | capitalize }}</span>
        </template> -->
      </el-table-column>
      <el-table-column label="IP HASH" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.ip_hash ? 'success' : 'danger'">{{ scope.row.ip_hash | statusFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="KEEPALIVE" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.keepalive ? 'success' : 'danger'">{{ scope.row.keepalive | statusFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="HTTP_CHECK" align="center" width="120">
        <template slot-scope="scope">
          <el-tag :type="scope.row.http_check ? 'success' : 'danger'">{{ scope.row.http_check | statusFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="TCP_CHECK" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.tcp_check? 'success' : 'danger'">{{ scope.row.tcp_check | statusFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="节点组配置" align="center">
        <template slot-scope="scope">
          <el-popover :ref="`upstream-${scope.$index}`" placement="top" width="730">
            <pre v-highlightjs="scope.row.content">
              <code class="hljs nginx"/>
            </pre>
            <el-button slot="reference" size="mini" round>节点组配置</el-button>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status ? 'success' : 'danger'">{{ scope.row.status | statusFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" align="center">
        <template slot-scope="scope">
          {{ scope.row.created_at }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="更新时间">
        <template slot-scope="scope">
          <span>{{ scope.row.updated_at }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作" width="240">
        <template slot-scope="scope">
          <el-button v-permission="['change_upstreams']" size="mini" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button v-permission="['delete_upstreams']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          <el-button size="mini" type="info" @click="handleDeploy(scope.row)">发布</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />
  </div>
</template>

<script>
import { getList, createUpstreams, updateUpstreams, deleteUpstreams, deployUpstreams } from '@/api/upstreams'
import * as middleware from '@/api/middleware'
import * as project from '@/api/projects'
import * as modules from '@/api/modules'
import * as group from '@/api/group'
import Pagination from '@/components/Pagination'
import AceEditor from './AceEditor'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index' // 权限判断指令

export default {
  components: { Pagination, AceEditor },
  directives: { permission },
  filters: {
    capitalize(value) {
      if (!value) return ''
      value = JSON.parse(value)
      let data = ''
      for (let i = 0; i < value.length; i++) {
        data += value[i].address + ':' + value[i].port
      }
      return data
    },
    statusFilter(status) {
      if (status) {
        return '启用'
      } else {
        return '禁用'
      }
    }
  },
  //   directives: { permission },
  data() {
    return {
      list: null,
      listLoading: true,
      total: 0,
      listQuery: {
        page: 1,
        page_size: 20,
        ordering: '-created_at'
      },
      form: {
        name: '',
        upstreams: [],
        ip_hash: '',
        keepalive: '',
        http_check: '',
        tcp_check: '',
        status: '',
        desc: ''
      },
      radio: 1,
      status: '',
      disabled: false,
      // autocreated: false,
      textMap: {
        update: '编辑节点组',
        create: '创建节点组'
      },
      envoptions: [{
        value: 'prd',
        label: '正式环境'
      }, {
        value: 'test',
        label: '测试环境'
      }, {
        value: 'pre',
        label: '预发环境'
      }, {
        value: 'dev',
        label: '开发环境'
      }],
      projectoptions: [],
      moduleoptions: [],
      groupoptions: [],
      layoutoptions: [],
      rows: [{
        prop: 'address',
        label: '地址'
      }, {
        prop: 'port',
        label: '端口'
      }, {
        prop: 'weight',
        label: '权重'
      }, {
        prop: 'max_fails',
        label: '重试'
      }, {
        prop: 'fail_timeout',
        label: '超时'
      }, {
        prop: 'action',
        label: 'Action'
      }],
      dialogFormVisible: false,
      dialogLogVisible: false,
      logData: [],
      formLabelWidth: '120px',
      rules: {
        name: [{ required: true, message: '节点组名称必填', trigger: 'change' }],
        layout: [{ required: true, message: '部署方式必填', trigger: 'change' }],
        custom_command: [{ required: true, message: '自定义命令必填', trigger: 'blur' }]
      }
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
  },
  methods: {
    toHtml(value, column) {
      const html = []
      let classes = null
      let styles = null
      const upstream = JSON.parse(value[column.property])
      for (let i = 0; i < upstream.length; i++) {
        if (upstream[i].status === true) {
          classes = 'el-icon-success'
          styles = 'color: #67C23A'
        } else {
          classes = 'el-icon-error'
          styles = 'color: #F56C6C'
        }
        html.push(this.$createElement('pre', null, [this.$createElement('span', upstream[i].address + ':' + upstream[i].port), this.$createElement('i', { attrs: { class: classes }, style: styles })]))
      }
      return html
    },
    fetchData() {
      this.listLoading = true
      this.listQuery.apigateway_id = this.$route.query.id
      getList(this.listQuery).then(response => {
        this.list = response.data.results
        this.total = response.data.count
        // setTimeout(() => {
        this.listLoading = false
        // }, 1.5 * 1000)
      })
    },

    projectfetchData() {
      project.getList({ page_size: 1000, page: 1 }).then(response => {
        this.projectoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.projectoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        console.log(this.projectoptions)
        setTimeout(() => { }, 1.5 * 1000)
      }).catch(error => {
        console.log(error)
      })
    },

    modulesfetchData(event) {
      console.log('project:' + event)
      modules.getList({ project: event, page: 1, page_size: 1000 }).then(response => {
        this.moduleoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.moduleoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        console.log(this.moduleoptions)
        setTimeout(() => { }, 1.5 * 1000)
      }).catch(error => {
        console.log(error)
      })
    },

    groupfetchData() {
      group.getList({ page: 1, page_size: 1000 }).then(response => {
        this.groupoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          const servers = []
          for (let j = 0; j < response.data.results[i].servers.length; j++) {
            servers.push({ ip: response.data.results[i].servers[j] })
          }
          this.groupoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name, servers: servers })
        }
        console.log(this.groupoptions)
        // setTimeout(() => {}, 1.5 * 1000)
      }).catch(error => {
        console.log(error)
      })
    },

    middlewarefetchData() {
      this.layoutoptions = []
      middleware.getList({ page_size: 1000, page: 1 }).then(response => {
        const middlewares = {}
        response.data.results.forEach(item => {
          const options = middlewares[item.layout_arch] || []
          options.push({ value: item.name, label: item.name })
          middlewares[item.layout_arch] = options
        })
        Object.keys(middlewares).forEach(key => {
          this.layoutoptions.push({ label: key.toUpperCase(), options: middlewares[key] })
        })
      })
    },

    add_upstream() {
      const upsteam = { address: '', port: '', weight: '', max_fails: '', fail_timeout: '', status: true }
      this.form.upstreams.push(upsteam)
    },

    change_upstream(event) {
      this.form.upstreams = []
      for (let i = 0; i < this.groupoptions.length; i++) {
        if (this.groupoptions[i].label === event) {
          for (let j = 0; j < this.groupoptions[i].servers.length; j++) {
            this.form.upstreams.push({ address: this.groupoptions[i].servers[j].ip, port: '', weight: '', max_fails: '', fail_timeout: '', status: true })
          }
        }
      }
    },

    del_upstream(index) {
      this.form.upstreams.splice(index, 1)
    },

    // autoCreated() {
    //   if (this.form.project) {
    //     this.form.name = 'node-' + this.form.project
    //   } else {
    //     alert('请选择项目或者模块')
    //     this.autocreated = false
    //   }
    //   if (this.form.module) {
    //     this.form.name = this.form.name + '-' + this.form.module
    //   } else {
    //     alert('请选择项目或者模块')
    //     this.autocreated = false
    //   }
    //   if (this.form.name) {
    //     this.disabled = true
    //   }
    // },

    resetForm() {
      this.form = {
        name: '',
        upstreams: [{ address: '', port: '', weight: '', max_fails: '', fail_timeout: '', status: true }],
        ip_hash: false,
        keepalive: null,
        http_check: false,
        tcp_check: false,
        status: true,
        layout: '',
        custom_command: '',
        desc: ''
      }
      this.projectfetchData()
      this.middlewarefetchData()
    },

    handleCreate() {
      this.resetForm()
      this.dialogFormVisible = true
      this.status = 'create'
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleUpdate(row) {
      this.form = Object.assign({}, row)
      this.form.upstreams = JSON.parse(this.form.upstreams)
      this.status = 'update'
      if (this.form.custom_command) {
        this.form.custom_command = JSON.parse(this.form.custom_command).join('\n')
      }
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleDelete(row) {
      deleteUpstreams(row).then(response => {
        this.$notify({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2000
        })
        const index = this.list.indexOf(row)
        this.list.splice(index, 1)
      }).catch(error => {
        this.$notify({
          title: '错误',
          message: '删除失败： ' + JSON.stringify(error.response.data),
          type: 'error',
          duration: 2000
        })
      })
    },

    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const data = Object.assign({}, this.form)
          data.created_by = this.user
          // data.role = this.roles.id.toString()
          data.apigateway = this.$route.query.id
          data.upstreams = JSON.stringify(data.upstreams)
          if (data.custom_command) {
            data.custom_command = JSON.stringify(data.custom_command.split('\n'))
          }
          console.log(data)
          createUpstreams(data).then(response => {
            console.log(response)
            this.dialogFormVisible = false
            this.fetchData()
            this.$notify({
              title: '成功',
              message: '创建成功',
              type: 'success',
              duration: 2000
            })
          }).catch(error => {
            this.$notify({
              title: '错误',
              message: '创建失败： ' + JSON.stringify(error.response.data),
              type: 'error',
              duration: 2000
            })
          })
        }
      })
    },

    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const data = Object.assign({}, this.form)
          data.created_by = this.user
          // data.role = this.roles.id.toString()
          data.apigateway = this.$route.query.id
          if (data.upstreams) {
            const s = []
            for (let i = 0; i < data.upstreams.length; i++) {
              s.push(data.upstreams[i].status)
            }
            if (s.indexOf(true) === -1) {
              data.status = false
            } else {
              data.status = true
            }
          }
          data.upstreams = JSON.stringify(data.upstreams)
          if (data.custom_command) {
            data.custom_command = JSON.stringify(data.custom_command.split('\n'))
          }
          console.log(data)
          updateUpstreams(data).then(response => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
            this.fetchData()
          }).catch(error => {
            this.$notify({
              title: '失败',
              message: '更新失败： ' + JSON.stringify(error.response.data),
              type: 'error',
              duration: 2000
            })
          })
        }
      })
    },
    handleDeploy(row) {
      deployUpstreams({ task_id: this.$route.query.id, deploy_type: 'upstreams', category_id: row.id }).then(response => {
        this.$notify({
          title: '成功',
          message: '发布成功',
          type: 'success',
          duration: 2000
        })
      }).catch(error => {
        this.$notify({
          title: '失败',
          message: '发布失败',
          type: 'error',
          duration: 2000
        })
        this.dialogLogVisible = true
        this.logData = error.response.data
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
.divider {
  border-bottom: 1px solid #ebeef5;
}
.cell pre {
  margin: 0;
}
.upstreams {
  margin-bottom: 0px;
}
.status {
  margin-bottom: 0px;
}
</style>
