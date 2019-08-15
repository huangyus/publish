<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_globalconfig']" v-if="list.length===0" type="primary" icon="el-icon-edit" @click="handleCreate">新建全局配置</el-button>
        <el-button v-permission="['change_globalconfig']" v-if="list.length>0" type="primary" icon="el-icon-edit" @click="handleUpdate(config)">修改全局配置</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button @click="handleDeploy(config)">发布</el-button>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogLogVisible" title="详细日志">
      <div v-for="(item, index) in logData" :key="index" :style="{color: item.color}" class="log">
        {{ item.text }}
        <div v-for="(text, index) in item.detail" :key="index" :style="{color: text.color}" v-html="text.text">{{ text.text }}</div>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[status]" :close-on-click-modal="false">
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-form-item :label-width="formLabelWidth" label="全局配置" prop="layout"/>
        <el-form-item prop="">
          <el-input v-model="form.content" :rows="18" type="textarea" placeholder="请粘贴Nginx全局配置"/>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="部署方式" prop="layout">
          <el-col :span="13">
            <el-select v-model="form.layout" clearable placeholder="部署方式" filterable style="width: 100%" @visible-change="middlewarefetchData">
              <el-option-group v-for="group in layoutoptions" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value"/>
              </el-option-group>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item v-if="form.layout ==='0'" prop="custom_command">
          <el-input v-model="form.custom_command" :rows="9" type="textarea" title="可用的宏替换，（${NGINX_HOME}）nginx配置目录， （${NGINX_RUN}）nginx启动命令， （${FILENAME}）nginx配置文件名" placeholder="nginx的全局配置部署命令，请以换行分隔"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="status==='create'?createData():updateData()">确 定</el-button>
      </div>
    </el-dialog>

    <el-table :data="list" :show-header="false" border>
      <el-table-column>
        <template slot-scope="scope">
          <pre v-highlightjs="scope.row.content">
              <code class="hljs nginx"/>
          </pre>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { getList, createGlobalConfig, updateGlobalConfig, deployGlobalConfig } from '@/api/globalconfig'
import * as middleware from '@/api/middleware'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index' // 权限判断指令

export default {
  components: { editor: require('vue2-ace-editor') },
  filters: {},
  directives: { permission },
  data() {
    return {
      // disabled: false,
      // checked: false,
      // worker: false,
      // defaults: '1',
      // custom: null,
      // text: null,
      config: null,
      status: null,
      list: [],
      listQuery: {
        page: 1,
        page_size: 20
      },
      form: {
        content: null
      },
      layoutoptions: [],
      textMap: {
        update: '编辑全局配置',
        create: '创建全局配置'
      },
      dialogFormVisible: false,
      dialogLogVisible: false,
      logData: [],
      formLabelWidth: '120px',
      rules: {
        content: [{ required: true, message: '全局配置必填', trigger: 'blur' }],
        // user: [{ required: true, message: '启动用户必填', trigger: 'blur' }],
        // group: [{ required: true, message: '启动用户组必填', trigger: 'blur' }],
        // pid_path: [{ required: true, message: 'PID路径必填', trigger: 'blur;' }],
        // worker_connections: [{ required: true, message: '最大连接数必填', trigger: 'blur' }],
        // keepalive_timeout: [{ required: true, message: 'KeepAlive必填', trigger: 'blur' }],
        // client_max_body_size: [{ required: true, message: '请求正文大小必填', trigger: 'blur' }],
        // access_log: [{ required: true, message: '日志必填', trigger: 'blur' }],
        // error_log: [{ required: true, message: '错误日志必填', trigger: 'blur' }],
        // log_format: [{ required: true, message: '日志格式必填', trigger: 'change' }],
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
    fetchData() {
      this.listQuery.apigateway_id = this.$route.query.id
      getList(this.listQuery).then(response => {
        if (response.data.results.length !== 0) {
          this.list = response.data.results
          this.config = response.data.results[0]
        } else {
          this.list = []
          this.config = null
        }
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

    resetForm() {
      this.form = {
        content: null
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
      this.status = 'update'
      if (this.form.custom_command) {
        this.form.custom_command = JSON.parse(this.form.custom_command).join('\n')
      }
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const data = Object.assign({}, this.form)
          data.created_by = this.user
          // data.role = this.roles.id.toString()
          data.apigateway = this.$route.query.id
          if (data.custom_command) {
            data.custom_command = JSON.stringify(data.custom_command.split('\n'))
          }
          console.log(data)
          createGlobalConfig(data).then(response => {
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
          // data.apigateway_id = this.$route.query.id
          // data.log_format = JSON.stringify(data.log_format)
          if (data.custom_command) {
            data.custom_command = JSON.stringify(data.custom_command.split('\n'))
          }
          console.log(data)
          updateGlobalConfig(data).then(response => {
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
      deployGlobalConfig({ task_id: this.$route.query.id, deploy_type: 'globalconfig', category_id: row.id }).then(response => {
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
.global-expand {
    font-size: 0;
}
.global-expand label {
    width: 90px;
    color: #99a9bf;
}
.global-expand .el-form-item {
    margin-right: 0;
    margin-bottom: 20px;
    width: 50%;
}
.global-expand .el-input {
    width: 600px;
}
.global-expand .el-textarea {
    width: 600px;
    display: block
}
</style>
