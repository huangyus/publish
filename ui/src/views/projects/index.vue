<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_projects']" type="primary" icon="el-icon-edit" @click="handleCreate">新建项目</el-button>
      </el-col>
      <el-col :span="6">
        <el-input v-model="search" placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" @click="handleSearch"/>
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[status]" :close-on-click-modal="false">
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-form-item :label-width="formLabelWidth" label="项目名称" prop="name">
          <el-col :span="12">
            <el-input v-model="form.name" placeholder="请输入项目名称"/>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="开发人员" prop="dv_user">
          <el-col :span="12">
            <el-input v-model="form.dv_user" placeholder="请输入开发人员"/>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="运维人员" prop="sa_user">
          <el-col :span="12">
            <el-input v-model="form.sa_user" placeholder="请输入运维人员"/>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="项目描述" prop="desc">
          <el-col :span="12">
            <el-input v-model="form.desc" type="textarea" placeholder="请输入项目描述"/>
          </el-col>
        </el-form-item>
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

      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="项目名称" width="110">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="开发人员" width="110">
        <template slot-scope="scope">
          {{ scope.row.dv_user }}
        </template>
      </el-table-column>
      <el-table-column label="运维人员" width="110">
        <template slot-scope="scope">
          {{ scope.row.sa_user }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="创建者" width="110" align="center">
        <template slot-scope="scope">
          {{ scope.row.created_by }}
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
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button v-permission="['change_projects']" size="mini" type="primary" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button v-permission="['delete_projects']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.page_size"
      @pagination="fetchData"/>
  </div>
</template>

<script>
import { getList, createProject, updateProject, deleteProject } from '@/api/projects'
import Pagination from '@/components/Pagination'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index.js' // 权限判断指令

export default {
  components: { Pagination },
  directives: { permission },
  data() {
    return {
      activeName: 'first',
      list: null,
      total: 0,
      search: null,
      listLoading: true,
      listQuery: {
        page: 1,
        page_size: 20,
        name: ''
      },
      form: {
        name: '',
        dv_user: '',
        sa_user: '',
        desc: ''
      },
      dialogFormVisible: false,
      status: '',
      textMap: {
        update: '编辑项目',
        create: '创建项目'
      },
      formLabelWidth: '120px',
      rules: {
        name: [{ required: true, message: '服务器名称必填', trigger: 'blur' }]
      }
    }
  },
  computed: {
    ...mapGetters([
      'user'
      // 'roles'
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

    resetForm() {
      this.form = {
        name: '',
        created_by: '',
        desc: ''
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
      this.status = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleDelete(row) {
      deleteProject(row).then(() => {
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
          console.log(data)
          console.log(this.user)
          createProject(data).then(response => {
            // console.log(response)
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
          updateProject(data).then(response => {
            // for (const v of this.list) {
            //   if (v.id === this.form.id) {
            //     const index = this.list.indexOf(v)
            //     this.list.splice(index, 1, this.form)
            //     break
            //   }
            // }
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
    width: 90px;
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

  .block label { display: inline-block; width: 60px; text-align: left; }
</style>
