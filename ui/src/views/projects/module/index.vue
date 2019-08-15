<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_modules']" type="primary" icon="el-icon-edit" @click="handleCreate">新建模块</el-button>
      </el-col>
      <el-col :span="6">
        <el-input v-model="search" placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" @click="handleSearch"/>
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[status]" :close-on-click-modal="false">
      <!--      <el-row>-->
      <!--        <el-col :span="24" style="margin-bottom: 15px;">-->
      <!--          <el-radio-group v-model="form.module_type" style="width: 100%">-->
      <!--            <el-radio :label="1" style="margin-left: 60px;float: left">业务模块</el-radio>-->
      <!--            &lt;!&ndash;            <el-radio :label="2" style="margin-right: 60px;float: right">基础模块</el-radio>&ndash;&gt;-->
      <!--          </el-radio-group>-->
      <!--        </el-col>-->
      <!--      </el-row>-->
      <!--      <div class="clearfix" />-->
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-row :gutter="24" type="flex" justify="center">
          <el-col :span="20">
            <el-form-item :label-width="formLabelWidth" label="项目名称" prop="project">
              <el-col>
                <el-select v-model="form.project" placeholder="请选择项目" filterable clearable style="width: 100%" @visible-change="projectfetchData">
                  <el-option v-for="item in projectoptions" :key="item.value" :label="item.label" :value="item.value"/>
                </el-select>
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="模块名称" prop="name">
              <el-col>
                <el-input v-model="form.name" placeholder="请输入模块名称"/>
              </el-col>
            </el-form-item>

            <el-form-item :label-width="formLabelWidth" label="架构类型" prop="arch_type">
              <el-col>
                <el-select v-model="form.arch_type" placeholder="请输入架构类型" style="width: 100%">
                  <el-option v-for="item in archoptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-col>
            </el-form-item>

            <!--            <el-form-item v-if="form.arch_type!=='nginx_gateway'" :label-width="formLabelWidth" label="网关地址" prop="gateway">-->
            <!--              <el-col>-->
            <!--                <el-input v-model="form.gateway" placeholder="请输入网关地址"/>-->
            <!--              </el-col>-->
            <!--            </el-form-item>-->
            <!--            <el-form-item v-if="form.arch_type==='nginx_gateway'" :label-width="formLabelWidth" label="网关地址" prop="gateway">-->
            <!--              <el-col>-->
            <!--                <el-select v-model="form.gateway" placeholder="请输入网关地址" style="width: 100%" clearable filterable @visible-change="upstreamsfetchData">-->
            <!--                  <el-option-group v-for="upstream in apigatewayoptions" :key="upstream.label" :label="upstream.label">-->
            <!--                    <el-option v-for="item in upstream.options" :key="item.value" :label="item.label" :value="item.value">-->
            <!--                      <span style="float: left; width: 20%">{{ item.value }}</span>-->
            <!--                    </el-option>-->
            <!--                  </el-option-group>-->
            <!--                </el-select>-->
            <!--              </el-col>-->
            <!--            </el-form-item>-->

            <el-form-item :label-width="formLabelWidth" label="环境" prop="env">
              <el-col>
                <el-select v-model="form.env" placeholder="请选择环境" filterable style="width: 100%">
                  <el-option v-for="item in envoptions" :key="item.value" :label="item.label" :value="item.value"/>
                </el-select>
                <!--<el-checkbox>启用环境</el-checkbox>-->
              </el-col>
            </el-form-item>

            <el-form-item v-if="form.module_type === 1" :label-width="formLabelWidth" label="代码仓库">
              <el-col>
                <el-tabs v-model="activeName" type="border-card" @tab-click="handleClick">
                  <el-tab-pane v-if="status === 'create' || form.repo_type === 'git'" label="GIT" name="first">
                    <el-form-item label="地址" class="block" prop="repo_url">
                      <el-col :span="16">
                        <el-input v-model="form.repo_url" placeholder="请输入git地址" size="mini"/>
                      </el-col>
                    </el-form-item>
                    <el-form-item label="用户名" class="block">
                      <el-col :span="16">
                        <el-input v-model="form.repo_user" placeholder="请输入git用户名" size="mini"/>
                      </el-col>
                    </el-form-item>
                    <el-form-item label="密码" class="block">
                      <el-col :span="16">
                        <el-input v-model="form.repo_pass" placeholder="请输入git密码" size="mini" type="password"/>
                      </el-col>
                    </el-form-item>
                  </el-tab-pane>
                  <el-tab-pane v-if="status === 'create' || form.repo_type === 'svn'" label="SVN" name="second">
                    <el-form-item label="地址" class="block" prop="repo_url">
                      <el-col :span="16">
                        <el-input v-model="form.repo_url" placeholder="请输入svn地址" size="mini" />
                      </el-col>
                    </el-form-item>
                    <el-form-item :prop="form.repo_type === 'svn'?'repo_user':''" label="用户名" class="block repo_user" >
                      <el-col :span="16">
                        <el-input v-model="form.repo_user" placeholder="请输入svn用户名" size="mini"/>
                      </el-col>
                    </el-form-item>
                    <el-form-item :prop="form.repo_type === 'svn'?'repo_pass':''" label="密码" class="block">
                      <el-col :span="16">
                        <el-input v-model="form.repo_pass" placeholder="请输入svn密码" size="mini" type="password"/>
                      </el-col>
                    </el-form-item>
                  </el-tab-pane>
                </el-tabs>
              </el-col>
            </el-form-item>
            <el-tag v-if="form.module_type === 1" style="margin-left: 45px">宿主机</el-tag>
            <el-form-item v-if="form.module_type === 1" :label-width="formLabelWidth" label="代码检出仓库" prop="repo_work">
              <el-col>
                <el-input v-model="form.repo_work" placeholder="/data/deploy" size="mini"/>
              </el-col>
            </el-form-item>
            <el-form-item v-if="form.module_type === 1" :label-width="formLabelWidth" label="排除文件">
              <el-col>
                <el-input
                  v-model="form.repo_ignore"
                  :rows="3"
                  type="textarea"
                  placeholder=".git
.svn
README.md"
                  size="mini"/>
              </el-col>
            </el-form-item>
            <el-tag v-if="form.module_type === 1" type="warning" style="margin-left: 45px">目标主机</el-tag>
            <el-form-item v-if="form.module_type === 1" :label-width="formLabelWidth" label="用户" prop="dest_user">
              <el-col>
                <el-input v-model="form.dest_user" placeholder="otmg" size="mini"/>
              </el-col>
            </el-form-item>
            <el-form-item v-if="form.module_type === 1" :label-width="formLabelWidth" label="部署路径" prop="dest_root">
              <el-col>
                <el-input v-model="form.dest_root" placeholder="/data/app" size="mini"/>
              </el-col>
            </el-form-item>
            <el-form-item v-if="form.module_type === 1" :label-width="formLabelWidth" label="版本路径" prop="dest_repo">
              <el-col>
                <el-input v-model="form.dest_repo" placeholder="/data/project" size="mini"/>
              </el-col>
            </el-form-item>
            <el-form-item v-if="form.module_type === 1" :label-width="formLabelWidth" label="版本保留数">
              <el-col>
                <el-input v-model="form.dest_keep" placeholder="7" size="mini"/>
              </el-col>
            </el-form-item>
            <el-form-item v-if="form.repo_type === 'git' && form.module_type === 1" :label-width="formLabelWidth" label="分支/tag">
              <el-col>
                <el-radio v-model="form.repo_mode" label="1" border>branch</el-radio>
                <el-radio v-model="form.repo_mode" label="2" border>tag</el-radio>
              </el-col>
            </el-form-item>
            <el-form-item v-if="form.repo_type === 'svn' && form.module_type === 1" :label-width="formLabelWidth" label="分支/tag">
              <el-col>
                <el-radio v-model="form.repo_mode" label="1" border>branch</el-radio>
                <el-radio v-model="form.repo_mode" label="2" border>tag</el-radio>
                <el-radio v-model="form.repo_mode" label="3" border>无trunk/无branches</el-radio>
              </el-col>
            </el-form-item>
            <el-form-item :label-width="formLabelWidth" label="模块描述" prop="desc">
              <el-col>
                <el-input v-model="form.desc" type="textarea" placeholder="请输入模块描述"/>
              </el-col>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="status==='create'?createData():updateData()">确 定</el-button>
      </div>
    </el-dialog>

    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="加载中..."
      border
      fit
      highlight-current-row
      style="width: 100%">

      <el-table-column type="expand">
        <template slot-scope="props">
          <el-form label-position="left" inline class="table-expand">
            <el-form-item label="项目名称">
              <span>{{ props.row.project }}</span>
            </el-form-item>
            <el-form-item label="模块名称">
              <span>{{ props.row.name }}</span>
            </el-form-item>
            <el-form-item label="环境名称">
              <span>{{ props.row.env }}</span>
            </el-form-item>
            <el-form-item label="创建者">
              <span>{{ props.row.created_by }}</span>
            </el-form-item>
            <el-form-item :label="props.row.repo_type + '地址'">
              <span>{{ props.row.repo_url }}</span>
            </el-form-item>
            <el-form-item :label="props.row.repo_type + '用户名'">
              <span>{{ props.row.repo_user }}</span>
            </el-form-item>
            <el-form-item :label="props.row.repo_type + '密码'">
              <span>{{ props.row.repo_pass }}</span>
            </el-form-item>
            <el-form-item label="代码检出仓库">
              <span>{{ props.row.repo_work }}</span>
            </el-form-item>
            <el-form-item label="用户">
              <span>{{ props.row.dest_user }}</span>
            </el-form-item>
            <el-form-item label="部署路径">
              <span>{{ props.row.dest_root }}</span>
            </el-form-item>
            <el-form-item label="版本路径">
              <span>{{ props.row.dest_repo }}</span>
            </el-form-item>
            <el-form-item label="描述">
              <span>{{ props.row.desc }}</span>
            </el-form-item>
          </el-form>
        </template>
      </el-table-column>

      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="名称" width="110">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="项目" width="110">
        <template slot-scope="scope">
          {{ scope.row.project }}
        </template>
      </el-table-column>
      <el-table-column label="环境" width="110">
        <template slot-scope="scope">
          {{ scope.row.env | envFilter }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="创建者" width="110" align="center">
        <template slot-scope="scope">
          {{ scope.row.created_by }}
        </template>
      </el-table-column>
      <el-table-column label="状态" align="center">
        <template slot-scope="scope">
          <el-popover :ref="`status-${scope.$index}`" placement="top" width="730">
            <pre v-highlightjs="scope.row.repo_result">
              <code class="hljs"/>
            </pre>
            <el-button slot="reference" :type="scope.row.status ? 'success' : 'danger'" size="mini" round>{{ scope.row.status | statusFilter }}</el-button>
          </el-popover>
          <el-button v-if="! scope.row.status" size="mini" round type="info" @click="handleRefresh(scope.row)">刷新</el-button>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created" label="创建时间" width="200">
        <template slot-scope="scope">
          <span>{{ scope.row.created_at }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="updated" label="更新时间" width="200">
        <template slot-scope="scope">
          <span>{{ scope.row.updated_at }}</span>
        </template>
      </el-table-column>
      <el-table-column label="描述" align="center">
        <template slot-scope="scope">
          {{ scope.row.desc }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="260">
        <template slot-scope="scope">
          <el-button v-permission="['change_modules']" type="primary" size="mini" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button size="mini" type="primary" @click="handleCopy(scope.row)">复制</el-button>
          <el-button v-permission="['delete_modules']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="fetchData"/>
  </div>
</template>

<script>
import * as project from '@/api/projects'
import { getList, createModules, updateModules, deleteModules, refreshModules } from '@/api/modules'
import Pagination from '@/components/Pagination'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index' // 权限判断指令

export default {
  components: { Pagination },
  directives: { permission },
  filters: {
    envFilter(env) {
      const envMap = {
        prd: '正式环境',
        test: '测试环境',
        pre: '预发环境',
        dev: '开发环境'
      }
      return envMap[env]
    },
    statusFilter(status) {
      const statusMap = {
        true: '启用',
        false: '禁用'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      activeName: 'first',
      list: null,
      search: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        page_size: 20
      },
      form: {},
      dialogFormVisible: false,
      status: '',
      textMap: {
        update: '编辑模块',
        create: '创建模块'
      },
      formLabelWidth: '120px',
      projectoptions: [],
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
      archoptions: [
        {
          value: 'nginx_gateway',
          label: 'Nginx GateWay'
        }, {
          value: 'zuul_gateway',
          label: 'Zuul GateWay'
        },
        {
          value: '',
          label: '无架构'
        }
      ],
      radio: 1,
      rules: {
        name: [{ required: true, message: '模块名称必填', trigger: 'blur' }],
        project: [{ required: true, message: '项目名称必填', trigger: 'change' }],
        repo: [{ required: true, message: '代码仓库必填', trigger: 'change' }],
        repo_url: [{ required: true, message: '地址必填', trigger: 'blur' }],
        repo_user: [{ required: true, message: '用户名必填', trigger: 'blur' }],
        repo_pass: [{ required: true, message: '密码必填', trigger: 'blur' }],
        repo_work: [{ required: true, message: '代码检出仓库必填', trigger: 'blur' }],
        dest_user: [{ required: true, message: '启动用户必填', trigger: 'blur' }],
        dest_root: [{ required: true, message: '部署路径必填', trigger: 'blur' }],
        dest_repo: [{ required: true, message: '版本路径必填', trigger: 'blur' }]
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
        console.log(response)
        this.list = response.data.results
        this.total = response.data.count
        this.listLoading = false
      })
    },
    projectfetchData() {
      project.getList().then(response => {
        this.projectoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.projectoptions.push({ 'value': response.data.results[i].name, 'label': response.data.results[i].name })
        }
        console.log(this.projectoptions)
      })
    },

    resetForm() {
      this.form = {
        name: null,
        project: null,
        env: 'prd',
        module_type: 1,
        cmd_type: false,
        repo_mode: '1',
        arch_type: null,
        repo_type: 'git',
        repo_url: null,
        repo_user: null,
        repo_pass: null,
        repo_work: null,
        repo_ignore: null,
        dest_user: null,
        dest_root: null,
        dest_repo: null,
        dest_keep: null,
        status: false,
        desc: null
      }
      this.activeName = 'first'
      this.projectfetchData()
    },
    handleCreate() {
      this.resetForm()
      this.status = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleClick(tab, event) {
      console.log(tab.label)
      if (tab.label === 'GIT') {
        this.form.repo_type = 'git'
        this.repo_mode = '1'
      } else if (tab.label === 'SVN') {
        this.form.repo_type = 'svn'
      }
    },

    handleUpdate(row) {
      this.form = Object.assign({}, row)
      this.status = 'update'
      if (this.form.repo_type === 'git') {
        this.activeName = 'first'
      }
      if (this.form.repo_type === 'svn') {
        this.activeName = 'second'
      }
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleCopy(row) {
      this.form = Object.assign({}, row)
      this.status = 'create'
      if (this.form.repo_type === 'git') {
        this.activeName = 'first'
      }
      if (this.form.repo_type === 'svn') {
        this.activeName = 'second'
      }
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleDelete(row) {
      deleteModules(row).then(() => {
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

    handleRefresh(row) {
      refreshModules({ module_id: row.id }).then(response => {
        this.$notify({
          title: '成功',
          message: '执行刷新成功',
          type: 'success',
          duration: 2000
        })
        this.fetchData()
      }).catch(error => {
        this.$notify({
          title: '失败',
          message: '执行刷新失败: ' + JSON.stringify(error.response.data),
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
          if (data.repo_work === '') { data.repo_work = '/data/deploy' }
          if (data.repo_ignore === '') { data.repo_ignore = '' }
          if (data.dest_user === '') { data.dest_user = 'otmg' }
          if (data.dest_root === '') { data.dest_root = '/data/app' }
          if (data.dest_repo === '') { data.dest_repo = '/data/project' }
          if (data.dest_keep === '') { data.dest_keep = '7' }
          console.log(data)
          console.log(this.user)
          createModules(data).then(response => {
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
              title: '失败',
              message: '创建失败: ' + JSON.stringify(error.response.data),
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
          console.log(data)
          updateModules(data).then(response => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
          }).catch(error => {
            this.$notify({
              title: '失败',
              message: '更新失败: ' + JSON.stringify(error.response.data),
              type: 'error',
              duration: 2000
            })
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
  .table-expand {
    font-size: 0;
  }

  .table-expand label {
    width: 100px;
    color: #99a9bf;
  }

  .table-expand .el-form-item {
    margin-right: 0;
    margin-bottom: 0;
    width: 50%;
  }

  .clearfix {
    background-color: #fafafa;
    border-bottom: 1px solid #eaeefb;
    /*overflow: hidden;*/
    /*height: 0;*/
    /*transition: height .2s;*/
  }

  .block label { display: inline-block; width: 80px; text-align: left; }
  .clearfix {
    padding: 0 20px 0;
    margin: 20px 0;
    line-height: 1px;
    border-left: 200px solid #dddddd;
    border-right: 200px solid #dddddd;
    text-align: center;
  }
  .repo_user {
    padding-right: 0px;
  }
</style>
