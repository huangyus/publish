<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_business']" type="primary" icon="el-icon-edit" @click="handleCreate">新建上线单</el-button>
      </el-col>
      <el-col :span="6">
        <el-input v-model="search" placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" @click="handleSearch" />
        </el-input>
      </el-col>
    </el-row>
    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[status]" :close-on-click-modal="false">
      <el-row type="flex" justify="center">
        <el-form ref="dataForm" :model="form" :rules="rules">
          <el-form-item :label-width="formLabelWidth" label="名称" prop="name">
            <el-col :span="20">
              <el-input v-model="form.name" placeholder="请输入上线单名称" autocomplete="off" />
            </el-col>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" label="项目" prop="project">
            <el-col :span="20">
              <el-select v-model="form.project" clearable placeholder="请选择项目" filterable style="width: 100%" @visible-change="projectfetchData">
                <el-option v-for="item in projectoptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-col>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" label="模块" prop="modules">
            <el-col :span="20">
              <el-select v-model="form.modules" placeholder="请选择上线模块" clearable filterable style="width: 100%" @visible-change="modulesfetchData(form.project)">
                <el-option v-for="item in modulesoptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-col>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" label="部署方式" prop="layout">
            <el-col :span="20">
              <el-select v-model="form.layout" clearable placeholder="请选择部署方式" filterable style="width: 100%" @visible-change="middlewarefetchData">
                <el-option-group v-for="group in layoutoptions" :key="group.label" :label="group.label">
                  <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value" />
                </el-option-group>
              </el-select>
              <el-tag type="danger">自定义命令以串行执行</el-tag>
            </el-col>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" label="版本" prop="version">
            <el-col :span="20">
              <el-select v-model="form.version" filterable clearable placeholder="请选择上线版本" style="width: 100%" no-data-text="搜索中..." @visible-change="handleVersion(form.project, form.modules)">
                <el-option v-for="item in versionoptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-col>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" label="定时任务" prop="cron">
            <el-col :span="20">
              <el-checkbox v-model="form.cron">启用定时任务</el-checkbox>
            </el-col>
          </el-form-item>
          <el-form-item v-if="form.cron" :label-width="formLabelWidth" prop="periodic">
            <el-col :span="20">
              <div class="rect">
                <el-date-picker v-model="form.periodic" type="datetime" placeholder="选择日期时间" default-time="00:00:00" value-format="yyyy-MM-dd HH:mm:ss" style="width: 100%;"/>
              </div>
            </el-col>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" label="环境" prop="env">
            <el-col :span="20">
              <el-select v-model="form.env" placeholder="请选择上线环境" filterable style="width: 100%">
                <el-option v-for="item in envoptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-col>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" :rules="form.updownline ? { required: true, message: '机房名称必填', trigger: 'change' } : []" label="机房" prop="idc">
            <el-col :span="20">
              <el-select v-model="form.idc" placeholder="请选择机房" multiple style="width: 100%" @visible-change="idcfetchData">
                <el-option v-for="(item, index) in idcoptions" :key="index" :label="item.label" :value="item.value" />
              </el-select>
            </el-col>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth">
            <el-col :span="20">
              <el-checkbox v-model="form.updownline" border>启用上下线</el-checkbox>
              <el-tag type="danger">上下线，是配合部署过程中对Nginx网关的操作，以串行执行</el-tag>
            </el-col>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth">
            <el-col :span="20">
              <el-checkbox v-model="form.serial" border>启用串行部署</el-checkbox>
              <el-tag type="danger">配合部署以串行执行，默认并行执行</el-tag>
            </el-col>
          </el-form-item>
          <el-form-item v-if="form.idc.length > 0" :label-width="formLabelWidth" label="服务器分组">
            <el-col :span="20">
              <el-select v-model="form.servers" placeholder="请选择服务器分组" clearable filterable multiple style="width: 100%" @visible-change="groupfetchData(form.project, form.modules, form.idc)">
                <el-option-group v-for="group in groupoptions" :key="group.label" :label="group.label">
                  <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value" />
                </el-option-group>
              </el-select>
            </el-col>
          </el-form-item>
          <el-form-item v-if="form.updownline" :label-width="formLabelWidth" :rules="form.updownline ? { required: true, message: 'Nginx网关必填', trigger: 'change' } : []" label="Nginx网关" prop="gateway">
            <el-col :span="20">
              <el-select v-model="form.gateway" placeholder="请选择Nginx网关" clearable filterable multiple style="width: 100%" @visible-change="apigatewayfetchData(form.idc)">
                <el-option-group v-for="gateway in apigatewayoptions" :key="gateway.label" :label="gateway.label">
                  <el-option v-for="item in gateway.options" :key="item.value" :label="item.label" :value="item.value" />
                </el-option-group>
              </el-select>
            </el-col>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" label="服务器列表" prop="servers">
            <el-row>
              <el-col :span="20">
                <el-radio-group v-model="radio">
                  <el-radio :label="1">人工输入</el-radio>
                  <el-radio :label="3" @change="handleChange(form.idc)">机房查找</el-radio>
                </el-radio-group>
                <el-select v-if="radio === 1" v-model="form.servers" allow-create multiple filterable default-first-option placeholder="请输入服务器IP" style="width: 100%" />
                <el-select v-if="radio === 3" v-model="form.servers" multiple filterable placeholder="请输入服务器IP" style="width: 100%" @visible-change="serversfetchData(form.idc)">
                  <el-option v-for="item in serversoptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" label="二次确认">
            <el-checkbox v-model="form.confirm">启用</el-checkbox>
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" label="描述">
            <el-col :span="20">
              <el-input v-model="form.desc" type="textarea" autocomplete="off" placeholder="请输入上线单描述" />
            </el-col>
          </el-form-item>
        </el-form>
      </el-row>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="status==='create'?createData():updateData()">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import * as project from '@/api/projects'
import * as modules from '@/api/modules'
import * as group from '@/api/group'
import * as middleware from '@/api/middleware'
import * as datacenter from '@/api/datacenter'
import * as servers from '@/api/servers'
import * as apigateway from '@/api/apigateway'
import { filterVersion, createBusiness } from '@/api/business'
import * as bstemplate from '@/api/bstemplate'
import moment from 'moment'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index' // 权限判断指令

import bus from '@/assets/eventBus'

export default {
  directives: { permission },
  data() {
    return {
      search: null,
      status: null,
      radio: 1,
      form: {
        idc: []
      },
      projectoptions: [],
      modulesoptions: [],
      serversoptions: [],
      versionoptions: [],
      groupoptions: [],
      apigatewayoptions: [],
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
      idcoptions: [
        { label: 'AAAA', value: 'AAAAA' },
        { label: 'BBBB', value: 'BBBB' },
        { label: 'CCCC', value: 'CCCC' }
      ],
      layoutoptions: [],
      dialogFormVisible: false,
      formLabelWidth: '100px',
      textMap: {
        update: '编辑上线单',
        create: '创建上线单',
        confirm: '部署二次确认',
        rollback: '回滚二次确认'
      },
      rules: {
        name: [{ required: true, message: '上线单名称必填', trigger: 'blur' }],
        project: [{ required: true, message: '项目必填', trigger: 'change' }],
        modules: [{ required: true, message: '模块必填', trigger: 'change' }],
        version: [{ required: true, message: '版本必填', trigger: 'change' }],
        // servers: [{ required: true, message: '服务器列表必填', trigger: 'change' }],
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
  mounted() {
    const that = this
    bus.$on('Template', function(event) {
      that.handleTemplate(event)
    })
  },
  methods: {
    /**
     * @return {string}
     */
    Timestamp() {
      return moment().format('YYYYMMDDHHmmss')
    },

    projectfetchData() {
      project.getList({ page_size: 1000, page: 1 }).then(response => {
        this.projectoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.projectoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        console.log(this.projectoptions)
      }).catch(error => {
        console.log(error)
      })
    },

    modulesfetchData(event) {
      console.log('project:' + event)
      modules.getList({ project: event, page: 1, page_size: 1000 }).then(response => {
        this.modulesoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.modulesoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        console.log(this.modulesoptions)
      }).catch(error => {
        console.log(error)
      })
      this.form.name = this.Timestamp() + '-' + this.form.project + '-' + this.form.modules
    },

    groupfetchData(project, modules, idc) {
      this.groupoptions = []
      group.getList({ project: project, modules: modules, idc: JSON.stringify(idc), page: 1, page_size: 1000 }).then(response => {
        const options = []
        for (let i = 0; i < response.data.results.length; i++) {
          const label = response.data.results[i].name + '(' + response.data.results[i].idc + ')'
          for (let j = 0; j < response.data.results[i].servers.length; j++) {
            options.push({ value: response.data.results[i].servers[j], label: response.data.results[i].servers[j] })
          }
          this.groupoptions.push({ label: label, options: options })
        }
        console.log(this.groupoptions)
      }).catch(error => {
        console.log(error)
      })
    },

    apigatewayfetchData(idc) {
      this.apigatewayoptions = []
      apigateway.getList({ idc_id: JSON.stringify(idc), page: 1, page_size: 1000 }).then(response => {
        const options = []
        for (let i = 0; i < response.data.results.length; i++) {
          const label = response.data.results[i].idc.name
          options.push({ value: response.data.results[i].id, label: response.data.results[i].name })
          this.apigatewayoptions.push({ label: label, options: options })
        }
        console.log(this.apigatewayoptions)
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

    idcfetchData() {
      datacenter.getList({ page_size: 1000, page: 1 }).then(response => {
        this.idcoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.idcoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name + '(' + response.data.results[i].location + ')' })
        }
        console.log(this.idcoptions)
      })
    },

    serversfetchData(idc) {
      servers.getList({ page_size: 1000, page: 1, idc_id: idc }).then(response => {
        this.serversoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.serversoptions.push({ value: response.data.results[i].ip, label: response.data.results[i].ip })
        }
        console.log(this.serversoptions)
        setTimeout(() => { }, 1.5 * 1000)
      })
    },

    handleVersion(project, module) {
      console.log('搜索：' + project + '_' + module)
      if (this.versionoptions.length === 0) {
        filterVersion({ p: project, m: module }).then(response => {
          this.versionoptions = []
          for (let i = 0; i < response.data.length; i++) {
            this.versionoptions.push({ value: response.data[i].id, label: response.data[i].id + ' - ' + response.data[i].message })
          }
          console.log(this.versionoptions)
        }).catch(error => {
          console.log(error)
        })
      }
    },

    resetForm() {
      this.form = {
        name: null,
        project: null,
        modules: null,
        updownline: false,
        gateway: null,
        serial: false,
        version: null,
        layout: null,
        task_type: 'simple',
        custom_command: null,
        servers: [],
        idc: [],
        env: 'prd',
        confirm: false,
        desc: null,
        cron: false,
        periodic: ''
      }
      this.radio = 1
    },
    handleCreate() {
      this.resetForm()
      this.status = 'create'
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
          if (data.servers) {
            data.servers = JSON.stringify(data.servers)
          }
          if (data.updownline) {
            data.task_type = 'updownline'
          }
          if (data.cron) {
            data.task_type = 'cron'
          }
          data.gateway = JSON.stringify(data.gateway)
          console.log(data)
          createBusiness(data).then(response => {
            console.log(response)
            this.dialogFormVisible = false
            bus.$emit('List')
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
    handleSearch() {
      bus.$emit('Search', this.search)
    },

    handleTemplate(row_id) {
      bstemplate.getList({ template_id: row_id }).then(response => {
        this.form = Object.assign({}, response.data.results[0])
        this.form.name = this.Timestamp() + '-' + this.form.project + '-' + this.form.modules
        this.form.servers = JSON.parse(this.form.servers)
        this.status = 'create'
        this.dialogFormVisible = true
        this.$nextTick(() => {
          this.$refs['dataForm'].clearValidate()
        })
      })
    }
  }
}
</script>

<style>
  .rect {
    border:2px solid #a1a1a1;
    padding:10px 40px;
    background:#dddddd;
    border-radius:25px;
    -moz-border-radius:25px;
  }
</style>
