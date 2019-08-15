<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_business']" type="primary" icon="el-icon-edit" @click="handleCreate">新建模版</el-button>
      </el-col>
      <el-col :span="6">
        <el-input v-model="search" placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" @click="handleSearch" />
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogFormVisible" :close-on-click-modal="false" title="新建工作流模版">
      <el-row type="flex" justify="space-between" style="padding-bottom: 20px">
        <el-col :span="6">
          <el-button :disabled="add" icon="el-icon-plus" circle type="success" @click="add_steps" />
        </el-col>
        <el-col :span="6">
          <el-button :disabled="del" icon="el-icon-minus" circle type="success" style="float: right" @click="delete_steps" />
        </el-col>
      </el-row>
      <el-row>
        <el-steps :active="active">
          <el-step v-for="item in steps" :key="item.idx" :title="item.title" />
        </el-steps>
      </el-row>
      <el-row type="flex" justify="space-between">
        <el-col :span="6">
          <el-button :disabled="prev" type="primary" @click="Prev">上一步</el-button>
        </el-col>
        <el-col :span="6">
          <el-button :disabled="next" style="float: right" type="primary" @click="Next">下一步</el-button>
        </el-col>
      </el-row>
      <el-row type="flex" justify="center">
        <el-form ref="dataForm" :model="form" :rules="rules">
          <el-form-item :label-width="formLabelWidth" label="名称" prop="name" style="margin-top: 20px;">
            <el-input v-model="form.name" placeholder="请输入工作流模版名称" style="width: 400px" />
          </el-form-item>
          <el-form-item :label-width="formLabelWidth" label="二次确认">
            <el-checkbox v-model="form.confirm">启用</el-checkbox>
          </el-form-item>
          <div v-for="(item, index) in form.steps" :key="item.idx">
            <el-form-item v-if="active===item.idx" :label-width="formLabelWidth" :rules="{ required: true, message: '项目名称必填', trigger: 'change' }" :prop="'steps.' + index + '.project'" label="项目">
              <el-select v-model="form.steps[index].project" clearable placeholder="请选择项目" filterable style="width: 400px" @visible-change="projectfetchData" @change="modulesfetchData(form.steps[index].project)">
                <el-option v-for="item in projectoptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="active===item.idx" :label-width="formLabelWidth" :rules="{ required: true, message: '模块名称必填', trigger: 'change' }" :prop="'steps.' + index + '.modules'" label="模块">
              <el-select v-model="form.steps[index].modules" placeholder="请选择上线模块" clearable filterable style="width: 400px" @visible-change="modulesfetchData(form.steps[index].project)">
                <el-option v-for="item in modulesoptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="active===item.idx" :label-width="formLabelWidth" :rules="{ required: true, message: '部署方式必填', trigger: 'change' }" :prop="'steps.' + index + '.layout'" label="部署方式">
              <el-select v-model="form.steps[index].layout" clearable placeholder="部署方式" filterable style="width: 400px" @visible-change="middlewarefetchData">
                <el-option-group v-for="group in layoutoptions" :key="group.label" :label="group.label">
                  <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value" />
                </el-option-group>
              </el-select>
            </el-form-item>
            <el-form-item v-if="active===item.idx" :label-width="formLabelWidth" :rules="{ required: true, message: '版本必填', trigger: 'change' }" :prop="'steps.' + index + '.version'" label="版本">
              <el-select v-model="form.steps[index].version" filterable clearable placeholder="请选择上线版本" style="width: 400px" no-data-text="搜索中..." @visible-change="handleVersion(form.steps[index].project, form.steps[index].modules)">
                <el-option v-for="item in versionoptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="active===item.idx" :label-width="formLabelWidth" label="环境" prop="env">
              <el-select v-model="form.steps[index].env" placeholder="请选择上线环境" filterable style="width: 400px">
                <el-option v-for="item in envoptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="active===item.idx" :label-width="formLabelWidth" :rules="form.steps[index].updownline ? { required: true, message: '机房名称必填', trigger: 'change' } : []" :prop="'steps.' + index + '.idc'" label="机房">
              <el-select v-model="form.steps[index].idc" placeholder="请选择机房" clearable multiple filterable style="width: 400px" @visible-change="idcfetchData">
                <el-option v-for="item in idcoptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="active===item.idx" :label-width="formLabelWidth">
              <el-col :span="12">
                <el-checkbox v-model="form.steps[index].updownline" border>启用上下线</el-checkbox>
                <el-tag type="danger">上下线，是配合部署过程中对Nginx网关的操作，以串行执行</el-tag>
              </el-col>
            </el-form-item>
            <el-form-item v-if="active===item.idx" :label-width="formLabelWidth">
              <el-col :span="12">
                <el-checkbox v-model="form.steps[index].serial" border>启用串行部署</el-checkbox>
                <el-tag type="danger">配合部署以串行执行，默认并行执行</el-tag>
              </el-col>
            </el-form-item>
            <el-form-item v-if="form.steps[index].idc.length !== 0 && active===item.idx" :label-width="formLabelWidth" label="服务器分组">
              <el-col :span="12">
                <el-select v-model="form.steps[index].servers" placeholder="请选择服务器分组" clearable filterable multiple style="width: 100%" @visible-change="groupfetchData(form.steps[index].idc)">
                  <el-option-group v-for="group in groupoptions" :key="group.label" :label="group.label">
                    <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value" />
                  </el-option-group>
                </el-select>
              </el-col>
            </el-form-item>
            <el-form-item v-if="form.steps[index].updownline && active===item.idx" :label-width="formLabelWidth" :rules="form.steps[index].updownline ? { required: true, message: 'Nginx网关必填', trigger: 'change' } : []" :prop="'steps.' + index + '.gateway'" label="Nginx网关">
              <el-col :span="12">
                <el-select v-model="form.steps[index].gateway" placeholder="请选择Nginx网关" clearable filterable multiple style="width: 100%" @visible-change="apigatewayfetchData(form.steps[index].idc)">
                  <el-option-group v-for="gateway in apigatewayoptions" :key="gateway.label" :label="gateway.label">
                    <el-option v-for="item in gateway.options" :key="item.value" :label="item.label" :value="item.value" />
                  </el-option-group>
                </el-select>
              </el-col>
            </el-form-item>
            <el-form-item v-if="active===item.idx" :label-width="formLabelWidth" :rules="{ required: true, message: '服务器列表必填', trigger: 'change' }" :prop="'steps.' + index + '.servers'" label="服务器列表">
              <el-row>
                <el-col :span="12">
                  <el-radio-group v-model="radio">
                    <el-radio :label="1">人工输入</el-radio>
                    <el-radio :label="3" @change="handleChange(form.steps[index].idc)">机房查找</el-radio>
                  </el-radio-group>
                  <el-select v-if="active===item.idx && radio === 1" v-model="form.steps[index].servers" allow-create multiple filterable placeholder="请输入服务器IP" style="width: 400px" />
                  <el-select v-if="active===item.idx && radio === 3" v-model="form.steps[index].servers" multiple filterable placeholder="请输入服务器IP" style="width: 400px">
                    <el-option v-for="item in serversoptions" :key="item.value" :label="item.label" :value="item.value" />
                  </el-select>
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item v-if="active===item.idx" :label-width="formLabelWidth" label="描述">
              <el-input v-model="form.steps[index].desc" placeholder="描述" autocomplete="off" style="width: 400px" />
            </el-form-item>
          </div>
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
import { createTemplate, updateTemplate, deleteTemplate } from '@/api/wftemplate'
import { filterVersion } from '@/api/workflow'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index' // 权限判断指令

import bus from '@/assets/eventBus'

export default {
  directives: { permission },
  data() {
    return {
      search: null,
      active: 1,
      form: {},
      status: null,
      radio: 1,
      textMap: {
        update: '编辑上线单',
        create: '创建上线单'
      },
      listQuery: {
        page: 1,
        page_size: 20
      },
      projectoptions: [],
      modulesoptions: [],
      serversoptions: [],
      versionoptions: [],
      rollbackoptions: [],
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
      idcoptions: [],
      layoutoptions: [],
      steps: [
        { title: '步骤1', idx: 1 },
        { title: '步骤2', idx: 2 },
        { title: '步骤3', idx: 3 }
      ],
      add: false,
      del: false,
      prev: false,
      next: false,
      dialogFormVisible: false,
      formLabelWidth: '120px',
      rules: {
        name: [{ required: true, message: '上线单名称必填', trigger: 'blur' }]
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
    bus.$on('templateUpdate', function(event) {
      that.handleUpdate(event)
    })
    bus.$on('templateCopy', function(event) {
      that.handleCopy(event)
    })
  },
  methods: {
    Prev() {
      this.active--
      if (this.active === 1) {
        this.prev = true
        this.next = false
      } else {
        this.next = false
      }
    },
    Next() {
      this.active++
      if (this.active === this.steps.length) {
        this.next = true
        this.prev = false
      } else {
        this.prev = false
      }
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
    },

    groupfetchData(idc) {
      this.groupoptions = []
      this.listQuery.idc = JSON.stringify(idc)
      this.listQuery.page_size = 1000
      if (this.form.project) {
        this.listQuery.project = this.form.project
      }
      if (this.form.modules) {
        this.listQuery.modules = this.form.modules
      }
      group.getList(this.listQuery).then(response => {
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
          this.idcoptions.push({ value: response.data.results[i].id, label: response.data.results[i].name + '(' + response.data.results[i].location + ')' })
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
      if (event !== '' && this.versionoptions.length === 0) {
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
        confirm: false,
        steps: [
          { idx: 1, project: null, modules: null, version: null, layout: null, updownline: false, serial: false, gateway: null, servers: null, env: 'prd', idc: [], desc: null },
          { idx: 2, project: null, modules: null, version: null, layout: null, updownline: false, serial: false, gateway: null, servers: null, env: 'prd', idc: [], desc: null },
          { idx: 3, project: null, modules: null, version: null, layout: null, updownline: false, serial: false, gateway: null, servers: null, env: 'prd', idc: [], desc: null }
        ]
      }
      this.radio = 1
    },

    handleCreate() {
      this.resetForm()
      this.status = 'create'
      this.prev = true
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleUpdate(row) {
      this.form = Object.assign({}, row)
      this.form.steps = JSON.parse(this.form.steps)
      this.active = this.form.steps.length
      this.steps = []
      for (let i = 0; i < this.form.steps.length; i++) {
        const index = i + 1
        const step = { title: '步骤' + index, idx: index }
        this.steps.push(step)
      }
      this.status = 'update'
      this.next = true
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleCopy(row) {
      this.form = Object.assign({}, row)
      this.form.steps = JSON.parse(this.form.steps)
      this.active = this.form.steps.length
      this.steps = []
      for (let i = 0; i < this.form.steps.length; i++) {
        const index = i + 1
        const step = { title: '步骤' + index, idx: index }
        this.steps.push(step)
      }
      this.next = true
      this.status = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
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

    handleSearch() {
      bus.$emit('Search', this.search)
    },

    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const data = Object.assign({}, this.form)
          data.created_by = this.user
          if (data.servers) {
            data.servers = JSON.stringify(data.servers)
          }
          if (data.steps) {
            data.steps = JSON.stringify(data.steps)
          }
          data.task_type = 'workflow'
          console.log(data)
          createTemplate(data).then(response => {
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

    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const data = Object.assign({}, this.form)
          data.created_by = this.user
          if (data.servers) {
            data.servers = JSON.stringify(data.servers)
          }
          if (data.steps) {
            data.steps = JSON.stringify(data.steps)
          }
          console.log(data)
          updateTemplate(data).then(response => {
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

    add_steps() {
      if (this.steps.length === 10) {
        this.add = true
        this.$notify.error({
          title: '错误',
          message: '最多只能添加10个工作流任务'
        })
        this.del = false
      } else {
        const idx = this.steps.length + 1
        const step = { title: '步骤' + idx, idx: idx }
        this.del = false
        this.steps.push(step)
        this.form.steps.push({ idx: idx, project: null, modules: null, version: null, layout: null, updownline: false, serial: false, gateway: null, servers: null, env: null, idc: null, desc: null })
        if (this.next) {
          this.next = false
        }
      }
    },

    delete_steps() {
      if (this.steps.length === 2) {
        this.del = true
        this.$notify.error({
          title: '错误',
          message: '最少保留2个工作流任务'
        })
        this.add = false
      } else {
        const idx = this.steps.length - 1
        this.add = false
        this.steps.splice(idx, 1)
        this.form.steps.splice(idx, 1)
        this.active = idx
      }
    }
  }
}
</script>
