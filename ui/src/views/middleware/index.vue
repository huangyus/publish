<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_middlewares']" type="primary" icon="el-icon-edit" @click="handleCreate">新建编排</el-button>
      </el-col>
      <el-col :span="6">
        <el-input v-model="search" placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" @click="handleSearch" />
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[status]" :close-on-click-modal="false">
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-form-item :label-width="formLabelWidth" label="编排名称" prop="name">
          <el-col :span="12">
            <el-input v-model="form.name" autocomplete="off" placeholder="请输入编排文件名称" />
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="编排架构" prop="layout_arch">
          <el-col :span="12">
            <el-select v-model="form.layout_arch" autocomplete="off" placeholder="请输入编排架构类型" style="width: 100%">
              <el-option v-for="item in layoutarch" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="编排版本" prop="version">
          <el-col :span="12">
            <el-input v-model="form.version" autocomplete="off" placeholder="请输入编排文件版本号" />
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="编排代码" prop="content" style="margin-bottom: 0px">
          <el-col :span="12">
            <el-tag type="danger">可用变量，deploy_project, deploy_root, module_name, package, package_name</el-tag>
            <el-input v-model="form.content" style="display: none" />
          </el-col>
        </el-form-item>
        <el-tabs v-if="form.layout_arch === 'bash'" tab-position="left" style="height: 400px;">
          <el-tab-pane label="部署前命令">
            <codemirror v-model="form.deploy_pre" :options="cmOptions1" style="width: 730px; height: 400px; margin-bottom: 20px" />
            <el-form-item>
              <el-input v-model="form.deploy_pre" style="display: none" />
            </el-form-item>
          </el-tab-pane>
          <el-tab-pane label="部署的命令">
            <codemirror v-model="form.deploy_release" :options="cmOptions1" style="width: 730px; height: 400px; margin-bottom: 20px" />
            <el-form-item>
              <el-input v-model="form.deploy_release" style="display: none" />
            </el-form-item>
          </el-tab-pane>
          <el-tab-pane label="部署后命令">
            <codemirror v-model="form.deploy_post" :options="cmOptions1" style="width: 730px; height: 400px; margin-bottom: 20px" />
            <el-form-item>
              <el-input v-model="form.deploy_post" style="display: none" />
            </el-form-item>
          </el-tab-pane>
          <el-tab-pane label="部署的间隔">
            <el-form-item>
              <el-col :span="12">
                <el-input v-model="form.deploy_delay" />
              </el-col>
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
        <codemirror v-if="form.layout_arch !== 'bash'" v-model="form.content" :options="form.layout_arch === 'bash_simple' ? cmOptions1 : cmOptions" style="width: 800px; height: 400px; margin-left: 50px; margin-bottom: 20px" />
        <el-form-item :label-width="formLabelWidth" label="编排描述" style="margin-top: 20px">
          <el-col :span="12">
            <el-input v-model="form.desc" autocomplete="off" />
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="status === 'create' ? createData() : updateData()">确 定</el-button>
      </div>
    </el-dialog>

    <el-table v-loading="listLoading" :data="list" element-loading-text="Loading" border fit highlight-current-row>
      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="编排文件名称">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="编排文件版本" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.version }}</span>
        </template>
      </el-table-column>
      <el-table-column label="编排架构" width="110" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.layout_arch }}</span>
        </template>
      </el-table-column>
      <el-table-column label="创建者" width="110" align="center">
        <template slot-scope="scope">
          {{ scope.row.created_by }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="创建时间" width="200">
        <template slot-scope="scope">
          <span>{{ scope.row.created_at }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="更新时间" width="200">
        <template slot-scope="scope">
          <span>{{ scope.row.updated_at }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="描述">
        <template slot-scope="scope">
          <span>{{ scope.row.desc }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button v-permission="['change_middlewares']" size="mini" type="primary" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button v-permission="['delete_middlewares']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total > 0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />
  </div>
</template>

<script>
import {
  getList,
  createMiddleware,
  updateMiddleware,
  deleteMiddleware
} from '@/api/middleware'
import Pagination from '@/components/Pagination'
import { codemirror } from 'vue-codemirror'
import 'codemirror/lib/codemirror.css'
import 'codemirror/mode/yaml/yaml'
import 'codemirror/mode/shell/shell'

import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index' // 权限判断指令

export default {
  components: {
    Pagination,
    codemirror
  },
  filters: {
    statusFilter(status) {
      const statusMap = {
        published: 'success',
        draft: 'gray',
        deleted: 'danger'
      }
      return statusMap[status]
    }
  },
  directives: { permission },
  data() {
    return {
      list: null,
      search: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        page_size: 20
      },
      status: '',
      textMap: {
        update: '编辑编排',
        create: '创建编排'
      },
      cmOptions: {
        lineNumbers: true,
        mode: 'text/x-yaml'
      },
      cmOptions1: {
        lineNumbers: true,
        mode: 'text/x-sh'
      },
      form: {},
      layoutarch: [
        {
          value: 'saltstack',
          label: 'SaltStack State'
        },
        {
          value: 'ansible',
          label: 'Ansible Playbook'
        },
        {
          value: 'bash',
          label: 'Bash 编排'
        },
        {
          value: 'bash_simple',
          label: 'Bash 脚本'
        }
      ],
      layoutype: [
        {
          value: 'basic',
          label: '基础编排'
        },
        {
          value: 'business',
          label: '业务编排'
        }
      ],
      dialogFormVisible: false,
      formLabelWidth: '120px',
      rules: {
        name: [{ required: true, message: '编排名称必填', trigger: 'blur' }],
        layout_arch: [
          { required: true, message: '编排架构类型必填', trigger: 'change' }
        ],
        layout_type: [
          { required: true, message: '编排类型必填', trigger: 'change' }
        ],
        version: [{ required: true, message: '编排版本必填', trigger: 'blur' }],
        content: [{ required: true, message: '编排代码必填', trigger: 'blur' }]
      }
    }
  },
  computed: {
    ...mapGetters(['user', 'roles'])
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

    resetForm() {
      this.form = {
        name: null,
        version: null,
        content: null,
        deploy_pre: null,
        deploy_release: null,
        deploy_post: null,
        deploy_delay: null,
        desc: null
      }
    },

    handleCreate() {
      this.resetForm()
      this.status = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleUpdate(row) {
      this.form = Object.assign({}, row)
      if (this.form.layout_arch === 'bash') {
        const content = JSON.parse(this.form.content)
        this.form.deploy_pre = content.deploy_pre
        this.form.deploy_release = content.deploy_release
        this.form.deploy_post = content.deploy_post
        this.form.deploy_delay = content.deploy_delay
      }
      this.status = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleDelete(row) {
      deleteMiddleware(row).then(() => {
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
      if (this.form.layout_arch === 'bash') {
        this.form.content = JSON.stringify({
          deploy_pre: this.form.deploy_pre,
          deploy_release: this.form.deploy_release,
          deploy_post: this.form.deploy_post,
          deploy_delay: this.form.deploy_delay
        })
      }
      this.$refs['dataForm'].validate(valid => {
        if (valid) {
          const data = Object.assign({}, this.form)
          data.created_by = this.user
          console.log(data)
          createMiddleware(data)
            .then(response => {
              console.log(response)
              this.dialogFormVisible = false
              this.fetchData()
              this.$notify({
                title: '成功',
                message: '创建成功',
                type: 'success',
                duration: 2000
              })
            })
            .catch(error => {
              this.$notify({
                title: '失败',
                message: '创建失败： ' + JSON.stringify(error.response.data),
                type: 'success',
                duration: 2000
              })
            })
        }
      })
    },

    updateData() {
      if (this.form.layout_arch === 'bash') {
        this.form.content = JSON.stringify({
          deploy_pre: this.form.deploy_pre,
          deploy_release: this.form.deploy_release,
          deploy_post: this.form.deploy_post,
          deploy_delay: this.form.deploy_delay
        })
      }
      this.$refs['dataForm'].validate(valid => {
        if (valid) {
          const data = Object.assign({}, this.form)
          console.log(data)
          updateMiddleware(data)
            .then(() => {
              for (const v of this.list) {
                if (v.id === this.form.id) {
                  const index = this.list.indexOf(v)
                  this.list.splice(index, 1, this.form)
                  break
                }
              }
              this.dialogFormVisible = false
              this.$notify({
                title: '成功',
                message: '更新成功',
                type: 'success',
                duration: 2000
              })
            })
            .catch(error => {
              console.log(error.response.data)
            })
        }
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
.CodeMirror {
  height: auto;
  border: 1px solid #ddd;
}
.CodeMirror-scroll {
  max-height: 400px;
}
.CodeMirror pre {
  padding-left: 7px;
  line-height: 1.25;
}
</style>
