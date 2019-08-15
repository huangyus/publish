<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_apigateway']" type="primary" icon="el-icon-edit" @click="handleCreate">新建负载均衡</el-button>
      </el-col>
      <el-col :span="6">
        <el-input v-model="search" placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" @click="handleSearch" />
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
        <el-form-item :label-width="formLabelWidth" label="名称" prop="name">
          <el-col :span="12">
            <el-input v-model="form.name" autocomplete="off" placeholder="请输入负载均衡名称" />
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="环境">
          <el-col :span="12">
            <el-select v-model="form.env" placeholder="请选择上线环境" filterable style="width: 100%">
              <el-option v-for="item in envoptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="机房" prop="idc">
          <el-col :span="12">
            <el-select v-model="form.idc" placeholder="请选择机房" filterable clearable style="width: 100%" @visible-change="idcfetchData" @change="serversfetchData(form.idc)">
              <el-option v-for="item in idcoptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="机器列表" prop="servers">
          <el-row>
            <el-col :span="12">
              <el-radio-group v-model="radio">
                <el-radio :label="1">人工输入</el-radio>
                <el-radio :label="3" @change="handleChange(form.idc)">机房查找</el-radio>
              </el-radio-group>
              <el-select v-if="radio === 1" v-model="form.servers" allow-create multiple filterable default-first-option placeholder="请输入服务器IP" style="width: 396px" />
              <el-select v-if="radio === 3" v-model="form.servers" multiple filterable placeholder="请输入服务器IP" style="width: 396px">
                <el-option v-for="item in serversoptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="配置目录" prop="home">
          <el-col :span="12">
            <el-input v-model="form.home" autocomplete="off" placeholder="请输入负载均衡配置目录" />
            <el-tag type="danger">宏替换变量： ${NGINX_HOME}</el-tag>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="启停命令" prop="cmd">
          <el-col :span="12">
            <el-input v-model="form.cmd" autocomplete="off" placeholder="请输入负载均衡的启停命令" />
            <el-tag type="danger">宏替换变量： ${NGINX_RUN}</el-tag>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="部署方式" prop="layout">
          <el-col :span="12">
            <el-select v-model="form.layout" placeholder="请选择部署方式" filterable clearable style="width: 100%" @visible-change="middlewarefetchData">
              <el-option-group v-for="group in layoutoptions" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value" />
              </el-option-group>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item v-if="form.layout ==='0'" prop="custom_command">
          <el-input v-model="form.custom_command" :rows="9" autocomplete="off" type="textarea" title="可用的宏替换，（${NGINX_HOME}）nginx配置目录， （${NGINX_RUN}）nginx启动命令， （${FILENAME}）nginx配置文件名" placeholder="nginx的部署命令，请以换行分隔" />
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="项目标签">
          <el-col :span="12">
            <el-select v-model="form.tags" clearable placeholder="请选择项目标签" multiple filterable style="width: 100%" @visible-change="projectfetchData">
              <el-option v-for="item in projectoptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="描述">
          <el-col :span="12">
            <el-input v-model="form.desc" type="textarea" autocomplete="off" placeholder="请输入负载均衡描述" />
          </el-col>
        </el-form-item>
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
      <el-table-column label="负载均衡名称">
        <template slot-scope="scope">
          <router-link :to="'/apigateway/config?id=' + scope.row.id" class="link-type">{{ scope.row.name }}</router-link>
        </template>
      </el-table-column>
      <el-table-column label="主机" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.servers | serversFilter }}</span>
        </template>
      </el-table-column>
      <el-table-column label="数据中心" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.idc }}</span>
        </template>
      </el-table-column>
      <el-table-column label="环境" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.env }}</span>
        </template>
      </el-table-column>
      <el-table-column label="项⽬标签" align="center">
        <template slot-scope="scope">
          <el-tag v-for="(item, index) in scope.row.tags" :key="index">{{ item }}</el-tag>
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
          <el-button v-permission="['change_apigateway']" size="mini" type="primary" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button size="mini" @click="handleDeploy(scope.row)">发布</el-button>
          <el-button v-permission="['delete_apigateway']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />
  </div>
</template>

<script>
import * as project from '@/api/projects'
import { getList, createAPIGateWay, updateAPIGateWay, deleteAPIGateWay, deployAPIGateWay } from '@/api/apigateway'
import * as middleware from '@/api/middleware'
import * as datacenter from '@/api/datacenter'
import * as servers from '@/api/servers'
import * as group from '@/api/group'
import Pagination from '@/components/Pagination'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index' // 权限判断指令

export default {
  components: { Pagination },
  directives: { permission },
  filters: {
    serversFilter(server) {
      return JSON.parse(server).join(', ')
    }
  },
  data() {
    return {
      list: null,
      search: null,
      listLoading: true,
      total: 0,
      listQuery: {
        page: 1,
        page_size: 20,
        ordering: '-created_at'
      },
      form: {
        name: '',
        project: '',
        env: 'prd',
        idc: '',
        module: '',
        servers: [],
        cmd: '',
        desc: ''
      },
      radio: 1,
      status: '',
      textMap: {
        update: '编辑负载均衡',
        create: '创建负载均衡'
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
      idcoptions: [],
      serversoptions: [],
      projectoptions: [],
      layoutoptions: [],
      groups: [],
      dialogFormVisible: false,
      dialogLogVisible: false,
      logData: [],
      formLabelWidth: '120px',
      rules: {
        name: [{ required: true, message: '负载均衡名称必填', trigger: 'blur' }],
        version: [{ required: true, message: '版本必填', trigger: 'change' }],
        idc: [{ required: true, message: '机房必填', trigger: 'change' }],
        servers: [{ required: true, message: '服务器列表必填', trigger: 'change' }],
        cmd: [{ required: true, message: 'nginx启动命令必填', trigger: 'blur' }],
        home: [{ required: true, message: 'nginx家目录必填', trigger: 'blur' }],
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
      this.listLoading = true
      getList(this.listQuery).then(response => {
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
      })
    },

    projectfetchData() {
      project.getList({ page_size: 1000, page: 1 }).then(response => {
        this.projectoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.projectoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        console.log(this.projectoptions)
        // setTimeout(() => {}, 1.5 * 1000)
      }).catch(error => {
        console.log(error)
      })
    },

    idcfetchData() {
      datacenter.getList({ page_size: 1000, page: 1 }).then(response => {
        this.idcoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.idcoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        console.log(this.idcoptions)
        setTimeout(() => { }, 1.5 * 1000)
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

    groupfetchData(event) {
      console.log('groups:' + event)
      group.getList({ modules: event, page: 1, page_size: 1000 }).then(response => {
        this.groups = []
        for (let i = 0; i < response.data.results.length; i++) {
          const servers = []
          for (let j = 0; j < response.data.results[i].servers.length; j++) {
            servers.push({ ip: response.data.results[i].servers[j] })
          }
          this.groups.push({ name: response.data.results[i].name, servers: servers })
        }
        console.log(this.groups)
        setTimeout(() => { }, 1.5 * 1000)
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

    resetForm() {
      this.form = {
        name: '',
        project: '',
        env: 'prd',
        idc: '',
        module: '',
        servers: [],
        home: '',
        cmd: '',
        layout: '',
        custom_command: '',
        tags: [],
        desc: ''
      }
      this.radio = 1
      this.groups = []
      this.idcfetchData()
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
      // this.form.servers = JSON.parse(this.form.servers).join(', ')
      if (this.form.custom_command) {
        this.form.custom_command = JSON.parse(this.form.custom_command).join('\n')
      }
      this.status = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleDelete(row) {
      deleteAPIGateWay(row).then(response => {
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

    handleChange(idc) {
      if (idc === '') {
        alert('请选择机房')
      }
    },

    handleRediret(row) {
      window.location.href = '/#/apigateway/config/?id=' + row.id
    },

    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const data = Object.assign({}, this.form)
          data.created_by = this.user
          data.servers = JSON.stringify(data.servers)
          if (data.custom_command) {
            data.custom_command = JSON.stringify(data.custom_command.split('\n'))
          }
          console.log(data)
          console.log(this.user)
          createAPIGateWay(data).then(response => {
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
          data.servers = JSON.stringify(data.servers)
          if (data.custom_command) {
            data.custom_command = JSON.stringify(data.custom_command.split('\n'))
          }
          console.log(data)
          console.log(this.user)
          updateAPIGateWay(data).then(response => {
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
    handleDeploy(row) {
      deployAPIGateWay({ task_id: row.id, deploy_type: 'all' }).then(response => {
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
    },

    handleSearch() {
      if (this.search) {
        this.listLoading = true
        this.listQuery = { name: this.search }
        getList(this.listQuery).then(response => {
          console.log(response)
          this.list = response.data.results
          this.total = response.data.count
          this.listLoading = false
        })
      } else {
        getList().then(response => {
          console.log(response)
          this.list = response.data.results
          this.total = response.data.count
          this.listLoading = false
        })
      }
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
