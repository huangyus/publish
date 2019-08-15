<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_datacenter']" type="primary" icon="el-icon-edit" @click="handleCreate">新建机房</el-button>
        <el-button type="primary" icon="el-icon-upload" @click="dialogFormVisible = true">同步cmdb</el-button>
        <!-- <el-button :loading="downloadLoading" class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">导出</el-button> -->
      </el-col>
      <el-col :span="6">
        <el-input v-model="search" placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" @click="handleSearch"/>
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogFormVisible" :close-on-click-modal="false" title="新建机房">
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-form-item :label-width="formLabelWidth" label="机房名称" prop="name">
          <el-col :span="12">
            <el-input v-model="form.name" autocomplete="off" placeholder="请输入机房名称"/>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="机房位置" prop="location">
          <el-col :span="12">
            <el-input v-model="form.location" autocomplete="off" placeholder="请输入机房位置"/>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="机房描述">
          <el-col :span="12">
            <el-input v-model="form.desc" type="textarea" autocomplete="off" placeholder="请输入机房描述"/>
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="status==='create'?createData():updateData()">确 定</el-button>
      </div>
    </el-dialog>

    <el-table v-loading="listLoading" :data="list" :default-sort = "{prop: 'created_at', order: 'descending'}" element-loading-text="加载中..." border fit highlight-current-row>
      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="机房名称">
        <template slot-scope="scope">
          <!-- <span class="link-type" @click="handleRediret(scope.row)">{{ scope.row.name }}</span> -->
          <router-link :to="'/datacenter/servers?idc_id=' + scope.row.id" class="link-type">{{ scope.row.name }}</router-link>
        </template>
      </el-table-column>
      <el-table-column label="机房地址" show-overflow-tooltip>
        <template slot-scope="scope">
          <span>{{ scope.row.location }}</span>
        </template>
      </el-table-column>
      <el-table-column label="创建者" align="center">
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
          <el-button v-permission="['change_datacenter']" type="primary" size="mini" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button v-permission="['delete_datacenter']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />
  </div>
</template>

<script>
import { getList, createDatacenter, updateDatacenter, deleteDatacenter } from '@/api/datacenter'
import Pagination from '@/components/Pagination'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index' // 权限判断指令

export default {
  components: { Pagination },
  filters: {},
  directives: { permission },
  data() {
    return {
      list: null,
      search: null,
      listLoading: true,
      downloadLoading: false,
      total: 0,
      form: {
        name: '',
        location: '',
        created_by: '',
        desc: ''
      },
      dialogFormVisible: false,
      status: '',
      formLabelWidth: '120px',
      listQuery: {
        page: 1,
        page_size: 20,
        idc_name: undefined
      },
      rules: {
        name: [{ required: true, message: '机房名称必填', trigger: 'blur' }],
        location: [{ required: true, message: '机房位置必填', trigger: 'blur' }]
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

    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const data = Object.assign({}, this.form)
          data.created_by = this.user
          console.log(data)
          createDatacenter(data).then(response => {
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
          const data = Object.assign({}, this.datacenter)
          console.log(data)
          updateDatacenter(data).then(() => {
            for (const v of this.list) {
              if (v.id === this.datacenter.id) {
                const index = this.list.indexOf(v)
                this.list.splice(index, 1, this.datacenter)
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
        }
      })
    },

    resetDatacenter() {
      this.form = {
        name: '',
        location: ''
      }
    },

    handleCreate() {
      this.resetDatacenter()
      this.status = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
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
    },

    handleUpdate(row) {
      this.datacenter = Object.assign({}, row)
      this.status = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleDelete(row) {
      deleteDatacenter(row).then(() => {
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

    // handleDownload() {
    //   this.downloadLoading = true
    //   import('@/vendor/Export2Excel').then(excel => {
    //     const tHeader = ['timestamp', 'title', 'type', 'importance', 'status']
    //     const filterVal = ['timestamp', 'title', 'type', 'importance', 'status']
    //     const data = this.formatJson(filterVal, this.list)
    //     excel.export_json_to_excel({
    //       header: tHeader,
    //       data,
    //       filename: 'table-list'
    //     })
    //     this.downloadLoading = false
    //   })
    // },
    handleRediret(row) {
      console.log(row)
      window.location.href = '/#/datacenter/servers/?idc_id=' + row.id
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
