<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_group']" type="primary" icon="el-icon-edit" @click="handleCreate">新建分组</el-button>
      </el-col>
      <el-col :span="6">
        <el-input v-model="search" placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" @click="handleSearch" />
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[status]" :close-on-click-modal="false">
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-form-item :label-width="formLabelWidth" label="项目名称" prop="project">
          <el-col :span="12">
            <el-select v-model="form.project" placeholder="请选择项目" filterable clearable style="width: 100%" @visible-change="projectfetchData" @change="modulesfetchData(form.project)">
              <el-option v-for="item in projectoptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="模块名称" prop="modules">
          <el-col :span="12">
            <el-select v-model="form.modules" placeholder="请选择模块" filterable clearable allow-create style="width: 100%" @visible-change="modulesfetchData(form.project)" @change="handleGroupName(form.project, form.modules)">
              <el-option v-for="item in modulesoptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="分组名称" prop="name">
          <el-col :span="12">
            <el-input v-model="form.name" placeholder="请输入分组名称" />
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="机房名称" prop="idc">
          <el-col :span="12">
            <el-select v-model="form.idc" placeholder="请选择机房" filterable clearable style="width: 100%" @visible-change="idcfetchData" @change="serversfetchData(form.idc)">
              <el-option v-for="item in idcoptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="机器列表" prop="servers">
          <el-col :span="12">
            <el-radio-group v-model="radio">
              <el-radio :label="1">人工输入</el-radio>
              <el-radio :label="3">机房查找</el-radio>
            </el-radio-group>
            <el-select v-if="radio === 1" v-model="form.servers" multiple filterable allow-create placeholder="请输入服务器IP" style="width: 396px" />
            <el-select v-if="radio === 3" v-model="form.servers" multiple filterable placeholder="请输入服务器IP" style="width: 396px">
              <el-option v-for="item in serversoptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="分组描述">
          <el-col :span="12">
            <el-input v-model="form.desc" type="textarea" placeholder="请输入分组描述" />
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="status==='create'?createData():updateData()">确 定</el-button>
      </div>
    </el-dialog>

    <el-table v-loading="listLoading" :data="list" element-loading-text="加载中..." border fit highlight-current-row style="width: 100%">

      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="分组名称">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="项目名称">
        <template slot-scope="scope">
          {{ scope.row.project }}
        </template>
      </el-table-column>
      <el-table-column label="IDC名称">
        <template slot-scope="scope">
          {{ scope.row.idc }}
        </template>
      </el-table-column>
      <el-table-column label="服务器列表" width="300" show-overflow-tooltip>
        <template slot-scope="scope">
          {{ scope.row.servers | serversFilter }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="创建者" width="110" align="center">
        <template slot-scope="scope">
          {{ scope.row.created_by }}
        </template>
      </el-table-column>
      <!-- <el-table-column align="center" prop="created" label="创建时间" width="200">
        <template slot-scope="scope">
          <span>{{ scope.row.created_at }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="updated" label="更新时间" width="200">
        <template slot-scope="scope">
          <span>{{ scope.row.updated_at }}</span>
        </template>
      </el-table-column> -->
      <el-table-column label="描述" align="center">
        <template slot-scope="scope">
          {{ scope.row.desc }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button v-permission="['change_group']" size="mini" type="primary" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button v-permission="['delete_group']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />
  </div>
</template>

<script>
import * as project from '@/api/projects'
import * as modules from '@/api/modules'
import * as datacenter from '@/api/datacenter'
import * as servers from '@/api/servers'
import { getList, createGroup, updateGroup, deleteGroup } from '@/api/group'
import Pagination from '@/components/Pagination'
import { mapGetters } from 'vuex'
// import XLSX from 'xlsx'
import permission from '@/directive/permission/index.js' // 权限判断指令

export default {
  components: { Pagination },
  directives: { permission },
  filters: {
    serversFilter(value) {
      return value.join(', ')
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
        page_size: 20,
        project: undefined
      },
      form: {
        name: '',
        project: '',
        idc: '',
        modules: '',
        servers: '',
        desc: ''
      },
      dialogFormVisible: false,
      status: '',
      textMap: {
        update: '编辑分组',
        create: '创建分组'
      },
      formLabelWidth: '120px',
      projectoptions: [],
      modulesoptions: [],
      idcoptions: [],
      serversoptions: [],
      checkAll: false,
      radio: 1,
      loading: false,
      rules: {
        name: [{ required: true, message: '分组名称必填', trigger: 'blur' }],
        project: [{ required: true, message: '项目名称必填', trigger: 'change' }],
        idc: [{ required: true, message: '机房名称必填', trigger: 'change' }],
        modules: [{ required: true, message: '模块名称必填', trigger: 'change' }],
        servers: [{ required: true, message: '服务器列表必填', trigger: 'change' }]
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
        // setTimeout(() => {
        this.listLoading = false
        // }, 1.5 * 1000)
      })
    },

    projectfetchData() {
      project.getList({ page: 1, page_size: 1000 }).then(response => {
        this.projectoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.projectoptions.push({ 'value': response.data.results[i].name, 'label': response.data.results[i].name })
        }
        console.log(this.projectoptions)
      })
    },
    modulesfetchData(project) {
      modules.getList({ project: project, page: 1, page_size: 1000 }).then(response => {
        this.modulesoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.modulesoptions.push({ 'value': response.data.results[i].name, 'label': response.data.results[i].name + '(' + response.data.results[i].desc + ')' })
        }
        console.log(this.modulesoptions)
      })
    },

    idcfetchData() {
      datacenter.getList({ page_size: 1000, page: 1 }).then(response => {
        this.idcoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.idcoptions.push({ 'value': response.data.results[i].name, 'label': response.data.results[i].name + '(' + response.data.results[i].location + ')' })
        }
        console.log(this.idcoptions)
      })
    },

    serversfetchData(event) {
      if (event !== '') {
        servers.getList({ idc_name: event, page_size: 1000, page: 1 }).then(response => {
          console.log(response)
          this.serversoptions = []
          for (let i = 0; i < response.data.results.length; i++) {
            this.serversoptions.push({ label: response.data.results[i].ip, value: response.data.results[i].ip })
          }
          console.log(this.serversoptions)
        })
      } else {
        this.serversoptions = []
        alert('请选择机房')
      }
    },

    resetForm() {
      this.form = {
        name: '',
        project: '',
        idc: '',
        modules: '',
        servers: [],
        desc: ''
      }
      this.radio = 1
      this.projectfetchData()
      this.idcfetchData()
    },

    handleGroupName(project, modules) {
      this.form.name = project + '_' + modules
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
      deleteGroup(row).then(() => {
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
          data.servers = JSON.stringify(data.servers)
          console.log(data)
          createGroup(data).then(response => {
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
        }
      })
    },

    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const data = Object.assign({}, this.form)
          data.created_by = this.user
          // data.role = this.roles.id.toString()
          if (typeof data.servers === 'string') {
            data.servers = data.servers.split(',')
          }
          data.servers = JSON.stringify(data.servers)
          console.log(data)
          updateGroup(data).then(response => {
            console.log(response)
            this.dialogFormVisible = false
            this.fetchData()
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

    // importExcel(file) {
    //   const types = file.name.split('.')[1]
    //   const fileType = ['xlsx', 'xls', 'csv'].some(item => item === types)
    //   if (!fileType) {
    //     alert('格式错误，请重新选择')
    //     return
    //   }
    //   console.log(file)
    //   this.file2Xlsx(file).then(tabJson => {
    //     if (tabJson && tabJson.length > 0) {
    //       console.log(tabJson)
    //       tabJson[0].forEach((v) => {
    //         this.form.servers.push(v.IP)
    //       })
    //     }
    //   })
    // },
    // file2Xlsx(file) {
    //   return new Promise(function (resolve, reject) {
    //     const reader = new FileReader()
    //     reader.onload = function (ev) {
    //       const data = ev.target.result
    //       this.wb = XLSX.read(data, {
    //         type: 'binary'
    //       })
    //       const result = []
    //       this.wb.SheetNames.forEach((sheetname) => {
    //         result.push(XLSX.utils.sheet_to_json(this.wb.Sheets[sheetname]))
    //       })
    //       resolve(result)
    //     }
    //     reader.readAsBinaryString(file.raw)
    //   })
    // },

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

.block label {
  display: inline-block;
  width: 60px;
  text-align: left;
}
</style>
