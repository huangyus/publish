<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button type="primary" icon="el-icon-edit" @click="handleCreate">新建Map</el-button>
      </el-col>
      <el-col :span="6">
        <el-input placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search"/>
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogLogVisible" title="详细日志">
      <div v-for="(item, index) in logData" :key="index" :style="{color: item.color}" class="log">
        <!-- {{ item.text }} -->
        <!-- <el-popover v-if="item.detail" trigger="click" placement="right-end" width="700"> -->
        <div v-for="(text, index) in item.detail" :key="index" :style="{color: text.color}" v-html="text.text">{{ text.text }}</div>
        <!-- <el-button slot="reference" :type="item.failed ? 'failed' : 'success' | statusFilter" size="mini">详情</el-button> -->
        <!-- </el-popover> -->
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[status]" :close-on-click-modal="false">
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-form-item :label-width="formLabelWidth" label="Map注释" prop="desc">
          <el-col :span="12">
            <el-input v-model="form.desc" autocomplete="off" placeholder="Map注释" />
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="是否启用" prop="status">
          <el-checkbox v-model="form.status">启用Map</el-checkbox><i class="el-icon-question"/>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="部署方式" prop="layout">
          <el-col :span="12">
            <el-select v-model="form.layout" clearable placeholder="部署方式" filterable style="width: 300px" @visible-change="middlewarefetchData">
              <el-option-group v-for="group in layoutoptions" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value"/>
              </el-option-group>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item v-if="form.layout ==='0'" prop="custom_command">
          <el-col>
            <el-input v-model="form.custom_command" :rows="9" autocomplete="off" type="textarea" title="可用的宏替换，（${NGINX_HOME}）nginx配置目录， （${NGINX_RUN}）nginx启动命令， （${FILENAME}）nginx配置文件名" placeholder="nginx的部署命令，请以换行分隔"/>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="Map内容" prop="content">
          <el-input v-model="form.content" :rows="9" type="textarea"/>
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
      <el-table-column label="Map名称">
        <template slot-scope="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Map配置" align="center">
        <template slot-scope="scope">
          <el-popover :ref="`upstream-${scope.$index}`" placement="top" width="730">
            <pre v-highlightjs="scope.row.content">
              <code class="hljs nginx"/>
            </pre>
            <el-button slot="reference" size="mini" round>Map配置</el-button>
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
          <el-button v-permission="['change_maps']" size="mini" type="primary" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button v-permission="['delete_maps']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          <el-button size="mini" @click="handleDeploy(scope.row)">发布</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />
  </div>
</template>

<script>
import { getList, createMaps, deleteMaps, updateMaps, deployMaps } from '@/api/maps'
import * as middleware from '@/api/middleware'
import * as project from '@/api/projects'
import * as modules from '@/api/modules'
// import * as group from '@/api/group'
import Pagination from '@/components/Pagination'
import AceEditor from './AceEditor'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index.js' // 权限判断指令

export default {
  components: { Pagination, AceEditor },
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
        config: [{ variable: '', name: '', status: true }],
        maps: [{ address: '', status: true }],
        status: true,
        layout: '',
        custom_command: '',
        desc: ''
      },
      radio: 1,
      status: '',
      disabled: false,
      autocreated: false,
      textMap: {
        update: '编辑Map',
        create: '创建Map'
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
      dialogFormVisible: false,
      dialogLogVisible: false,
      logData: [],
      formLabelWidth: '120px',
      rules: {
        content: [{ required: true, message: 'map内容必填', trigger: 'blur' }],
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
    this.middlewarefetchData()
  },
  methods: {
    toHtml(value, column) {
      console.log(value, column)
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
        html.push(this.$createElement('pre', null, [this.$createElement('span', upstream[i].address), this.$createElement('i', { attrs: { class: classes }, style: styles })]))
      }
      return html
    },
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

    add_map() {
      const map = { address: '', status: true }
      this.form.maps.push(map)
    },
    add_name() {
      const c = { variable: '', name: '', status: true }
      this.form.config.push(c)
    },

    del_map(index) {
      this.form.maps.splice(index, 1)
    },
    del_name(index) {
      this.form.config.splice(index, 1)
    },

    resetForm() {
      this.form = {
        config: [{ variable: '', name: '', status: true }],
        maps: [{ address: '', status: true }],
        status: true,
        layout: '',
        custom_command: '',
        content: '',
        desc: ''
      }
      this.projectfetchData()
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
      this.form.maps = JSON.parse(this.form.maps)
      this.form.config = JSON.parse(this.form.config)
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
      deleteMaps(row).then(response => {
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

    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const data = Object.assign({}, this.form)
          data.created_by = this.user
          // data.role = this.roles.id.toString()
          data.apigateway = this.$route.query.id
          data.maps = JSON.stringify(data.maps)
          data.config = JSON.stringify(data.config)
          if (data.custom_command) {
            data.custom_command = JSON.stringify(data.custom_command.split('\n'))
          }
          console.log(data)
          createMaps(data).then(response => {
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
          data.apigateway_id = this.$route.query.id
          //   if (data.upstreams) {
          //     const s = []
          //     for (let i = 0; i < data.upstreams.length; i++) {
          //       s.push(data.upstreams[i].status)
          //     }
          //     if (s.indexOf(true) === -1) {
          //       data.status = false
          //     } else {
          //       data.status = true
          //     }
          //   }
          data.maps = JSON.stringify(data.maps)
          data.config = JSON.stringify(data.config)
          //   if (data.custom_command) {
          //     data.custom_command = JSON.stringify(data.custom_command.split('\n'))
          //   }
          console.log(data)
          updateMaps(data).then(response => {
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
      deployMaps({ task_id: this.$route.query.id, deploy_type: 'maps', category_id: row.id }).then(response => {
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
    border-bottom: 1px solid #ebeef5
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
