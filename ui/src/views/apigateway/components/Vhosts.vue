<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_vhosts']" type="primary" icon="el-icon-edit" @click="handleCreate">新建虚拟主机</el-button>
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

    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[status]" :close-on-click-modal="false" width="80%">
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-tabs type="border-card">
          <el-tab-pane label="基础配置">
            <el-form-item :label-width="formLabelWidth" label="域名" prop="domain">
              <el-col :span="12">
                <el-input v-model="form.domain" autocomplete="off" placeholder="请输入域名，多域名请用空格(或者逗号)分隔" />
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="端口">
              <el-col :span="12">
                <el-input v-model="form.port" autocomplete="off" placeholder="请输入端口" />
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="限流配置">
              <el-col :span="12">
                <el-input v-model="form.rate_limit" type="textarea" autocomplete="off" placeholder="请输入限流配置" />
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="访问日志" prop="access_log">
              <el-col :span="12">
                <el-input v-model="form.access_log" autocomplete="off" placeholder="请输入访问日志路径" />
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="错误日志" prop="error_log">
              <el-col :span="12">
                <el-input v-model="form.error_log" autocomplete="off" placeholder="请输入错误日志" />
              </el-col>
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
            <el-form-item :label-width="formLabelWidth" label="是否启用" prop="status">
              <el-checkbox v-model="form.status">启用虚拟主机</el-checkbox><i class="el-icon-question" />
            </el-form-item>
            <el-form-item v-if="form.layout ==='0'" prop="custom_command">
              <el-input v-model="form.custom_command" :rows="9" autocomplete="off" type="textarea" title="可用的宏替换，（${NGINX_HOME}）nginx配置目录， （${NGINX_RUN}）nginx启动命令， （${FILENAME}）nginx配置文件名" placeholder="nginx的部署命令，请以换行分隔" />
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="附加参数(json)">
              <el-col :span="12">
                <ace-editor :content.sync="form.extras" width="670" height="300" @update:content="form.extras=$event" />
              </el-col>
              <el-input v-model="form.extras" style="display: none" />
            </el-form-item>
          </el-tab-pane>
          <el-tab-pane label="证书配置">
            <el-form-item :label-width="formLabelWidth" label="证书状态">
              <el-col :span="12">
                <el-checkbox v-model="form.ssl_status">启用</el-checkbox>
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="HTTPS端口">
              <el-col :span="12">
                <el-input v-model="form.ssl_port" :disabled="disabled" autocomplete="off" placeholder="请输入HTTPS端口" />
                <el-checkbox v-model="form.ssl_port_default" @change="handleCheck">默认端口</el-checkbox>
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="保留原端口">
              <el-col :span="12">
                <el-checkbox v-model="form.http_status">启用</el-checkbox>
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="证书">
              <el-col :span="12">
                <el-input v-model="form.ssl_cert_body" :rows="9" type="textarea" autocomplete="off" placeholder="请粘贴证书文件（.ctr）正文" />
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="私钥">
              <el-col :span="12">
                <el-input v-model="form.ssl_key_body" :rows="9" type="textarea" autocomplete="off" placeholder="请粘贴私钥文件（.key）正文" />
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="附加参数(json)">
              <el-col :span="12">
                <ace-editor :content.sync="form.ssl_extras" width="670" height="300" />
              </el-col>
              <el-input v-model="form.ssl_extras" style="display: none" />
            </el-form-item>
          </el-tab-pane>
          <el-tab-pane label="Location配置">
            <dynamic-location :dyupstreams="form.dynamics_list" />
            <div class="divider" style="margin: 20px" />
            <static-location :stupstreams="form.statics_list" />
          </el-tab-pane>
        </el-tabs>
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
      <el-table-column label="域名" width="300" show-overflow-tooltip>
        <template slot-scope="scope">
          <span>{{ scope.row.domain }}</span>
        </template>
      </el-table-column>
      <el-table-column label="端口" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.port }}</span>
        </template>
      </el-table-column>
      <el-table-column label="SSL状态" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.ssl_status? 'success' : 'danger'">{{ scope.row.ssl_status | statusFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="SSL端口" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.ssl_port }}</span>
        </template>
      </el-table-column>
      <el-table-column label="保留HTTP端口" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.http_status? 'success' : 'danger'">{{ scope.row.http_status | statusFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="vhost配置" align="center">
        <template slot-scope="scope">
          <el-popover :ref="`vhost-${scope.$index}`" placement="top" width="730">
            <pre v-highlightjs="scope.row.content">
              <code class="hljs nginx"/>
            </pre>
            <el-button slot="reference" size="mini" round>vhost配置</el-button>
          </el-popover>
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status? 'success' : 'danger'">{{ scope.row.status | statusFilter }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="200" align="center">
        <template slot-scope="scope">
          {{ scope.row.created_at }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="更新时间" width="200">
        <template slot-scope="scope">
          <span>{{ scope.row.updated_at }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作" width="240">
        <template slot-scope="scope">
          <el-button v-permission="['change_vhosts']" size="mini" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button v-permission="['delete_vhosts']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          <el-button size="mini" type="info" @click="handleDeploy(scope.row)">发布</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />
  </div>
</template>

<script>
import { getList, createVhosts, updateVhosts, deleteVhosts, deployVhosts } from '@/api/vhosts'
import * as middleware from '@/api/middleware'
import Pagination from '@/components/Pagination'
import DynamicLocation from './DynamicLocation'
import StaticLocation from './StaticLocation'
import AceEditor from './AceEditor'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index' // 权限判断指令

export default {
  components: {
    Pagination,
    DynamicLocation,
    StaticLocation,
    AceEditor
  },
  directives: { permission },
  filters: {
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
        domain: '',
        port: '',
        access_log: '',
        error_log: '',
        extras: '{}',
        ssl_status: false,
        ssl_port: '',
        ssl_port_default: false,
        http_status: false,
        ssl_cert_body: '',
        ssl_key_body: '',
        ssl_extras: '',
        dynamics_list: [],
        statics_list: [],
        desc: ''
      },
      layoutoptions: [],
      disabled: false,
      checked: false,
      status: '',
      textMap: {
        update: '编辑虚拟主机',
        create: '创建虚拟主机'
      },
      dialogFormVisible: false,
      dialogLogVisible: false,
      logData: [],
      formLabelWidth: '120px',
      rules: {
        domain: [{ required: true, message: '域名必填', trigger: 'blur' }],
        // port: [{ required: true, message: '端口必填', trigger: 'blur' }],
        // access_log: [{ required: true, message: '访问日志必填', trigger: 'blur' }],
        // error_log: [{ required: true, message: '错误日志必填', trigger: 'blur' }],
        layout: [{ required: true, message: '部署方式必填', trigger: 'blur' }],
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
    fetchData() {
      this.listLoading = true
      this.listQuery.apigateway_id = this.$route.query.id
      getList(this.listQuery).then(response => {
        this.list = response.data.results
        this.total = response.data.count
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
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

    handleCheck(val) {
      console.log(val)
      if (val) {
        this.disabled = true
        this.form.ssl_port = '443'
      } else {
        this.disabled = false
        this.form.ssl_port = ''
      }
    },

    resetForm() {
      this.form = {
        domain: '',
        port: '',
        access_log: '',
        error_log: '',
        layout: '',
        custom_command: '',
        status: true,
        extras: '{}',
        ssl_status: false,
        ssl_port: '',
        ssl_port_default: false,
        http_status: false,
        ssl_cert_body: '',
        ssl_key_body: '',
        ssl_extras: '{}',
        dynamics_list: [{ location_type: '', location_upstream: '', location_url: '', location_proxy_url: '', location_desc: '', location_condition: '', location_lua: '{}', location_extra: '{}' }],
        statics_list: [{ location_type: '', location_static: '', location_url: '', location_desc: '', location_condition: '', location_extra: '{}' }],
        desc: ''
      }
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
      this.form.dynamics_list = JSON.parse(this.form.dynamics_list)
      this.form.statics_list = JSON.parse(this.form.statics_list)
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
      deleteVhosts(row).then(response => {
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
          data.dynamics_list = JSON.stringify(data.dynamics_list)
          data.statics_list = JSON.stringify(data.statics_list)
          if (data.custom_command) {
            data.custom_command = JSON.stringify(data.custom_command.split('\n'))
          }
          console.log(data)
          console.log(this.user)
          createVhosts(data).then(response => {
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
          data.dynamics_list = JSON.stringify(data.dynamics_list)
          data.statics_list = JSON.stringify(data.statics_list)
          if (data.custom_command) {
            data.custom_command = JSON.stringify(data.custom_command.split('\n'))
          }
          console.log(data)
          updateVhosts(data).then(response => {
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
      deployVhosts({ task_id: this.$route.query.id, deploy_type: 'vhosts.d', category_id: row.id }).then(response => {
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
</style>

