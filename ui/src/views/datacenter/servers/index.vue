<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_servers']" type="primary" icon="el-icon-edit" @click="handleCreate">新建服务器</el-button>
        <el-button type="primary" icon="el-icon-upload" @click="dialogFormVisible = true">同步cmdb</el-button>
        <el-button :loading="downloadLoading" class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">导出</el-button>
        <el-button class="filter-item" type="primary" icon="el-icon-upload2" @click="dialogUploadVisible = true">导入</el-button>
      </el-col>
      <el-col :span="6">
        <el-input v-model="search" placeholder="请输入服务器名称搜索" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" @click="handleSearch"/>
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogUploadVisible" :limit="3" :on-exceed="handleExceed" :file-list="fileList" :close-on-click-modal="false" title="上传服务器">
      <el-upload ref="upload" :auto-upload="false" action="#">
        <el-button slot="trigger" size="small" type="primary">选择文件</el-button>
        <el-button style="margin-left: 10px;" size="small" type="success" @click="submitUpload">上传到服务器</el-button>
        <div slot="tip" class="el-upload__tip">只能上传.xlxs文件，且不超过20M</div>
      </el-upload>
      <!-- <div slot="footer" class="dialog-footer">
        <el-button @click="dialogUploadVisible = false">取 消</el-button>
        <el-button type="primary" @click="dialogUploadVisible = false">确 定</el-button>
      </div> -->
    </el-dialog>

    <el-dialog :visible.sync="dialogFormVisible" title="新建服务器">
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-form-item :label-width="formLabelWidth" label="服务器名称" prop="hostname">
          <el-col :span="12">
            <el-input v-model="form.hostname" autocomplete="off" placeholder="请输入服务器名称"/>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="服务器IP" prop="ip">
          <el-col :span="12">
            <el-input v-model="form.ip" autocomplete="off" placeholder="请输入服务器IP"/>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="服务器描述" prop="desc">
          <el-col :span="12">
            <el-input v-model="form.desc" type="textarea" autocomplete="off" placeholder="请输入服务器描述"/>
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
      <el-table-column label="服务器名称">
        <template slot-scope="scope">
          {{ scope.row.hostname }}
        </template>
      </el-table-column>
      <el-table-column label="服务器IP" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.ip }}</span>
        </template>
      </el-table-column>
      <el-table-column label="创建者" width="200" align="center">
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
          <el-button v-permission="['change_servers']" type="primary" size="mini" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button v-permission="['delete_servers']" size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />
  </div>
</template>

<script>
import { getList, createServer, updateServer, deleteServer } from '@/api/servers'
import Pagination from '@/components/Pagination'
import { parseTime } from '@/utils'
import XLSX from 'xlsx'
import { mapGetters } from 'vuex'
import permission from '@/directive/permission/index' // 权限判断指令

export default {
  components: { Pagination },
  directives: { permission },
  filters: {},
  data() {
    return {
      list: null,
      search: null,
      listLoading: true,
      downloadLoading: false,
      total: 0,
      form: {
        idc: '',
        hostname: '',
        ip: '',
        desc: ''
      },
      dialogFormVisible: false,
      dialogUploadVisible: false,
      uploadData: [],
      fileList: [],
      status: '',
      formLabelWidth: '120px',
      listQuery: {
        page: 1,
        page_size: 20,
        idc_id: ''
      },
      rules: {
        hostname: [{ required: true, message: '服务器名称必填', trigger: 'blur' }],
        ip: [{ required: true, message: '服务器IP必填', trigger: 'blur' }]
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
      this.listQuery.idc_id = this.$route.query.idc_id
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
          // data.role = this.roles.id.toString()
          data.idc = this.$route.query.idc_id
          console.log(data)
          createServer(data).then(response => {
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
          console.log(data)
          updateServer(data).then(() => {
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
        }
      })
    },

    resetServers() {
      this.form = {
        idc: '',
        hostname: '',
        ip: '',
        desc: ''
      }
    },

    handleCreate() {
      this.resetServers()
      this.status = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleFilter() {
      if (this.search) {
        this.listQuery = { hostname: this.search }
      } else {
        this.listQuery = {}
      }
      console.log('search: ' + this.listQuery)
      this.fetchData()
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
      deleteServer(row).then(() => {
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

    handleExceed(files, fileList) {
      this.$message.warning(`当前限制选择 1 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`)
    },

    submitUpload() {
      const file = this.$refs.upload.uploadFiles[0]
      const types = file.name.split('.')[1]
      const idc = this.$route.query.idc_id
      const fileType = ['xlsx', 'xls', 'csv'].some(item => item === types)
      if (!fileType) {
        alert('格式错误，请重新选择')
        return
      }
      console.log(file)
      this.file2Xlsx(file).then(tabJson => {
        this.uploadData = []
        if (tabJson && tabJson.length > 0) {
          console.log(tabJson)
          tabJson[0].forEach((v) => {
            this.uploadData.push({ idc: idc, hostname: v.hostname, ip: v.ip, created_by: this.user, role: this.roles.id.toString(), desc: '' })
          })
        }
        console.log(this.uploadData)
        createServer(this.uploadData).then(response => {
          console.log(response)
          this.dialogUploadVisible = false
          this.fetchData()
          this.$notify({
            title: '成功',
            message: '上传成功',
            type: 'success',
            duration: 2000
          })
        }).catch(error => {
          this.$notify({
            title: '失败',
            message: '上传失败： ' + JSON.stringify(error.response.data),
            type: 'error',
            duration: 2000
          })
        })
      })
    },

    file2Xlsx(file) {
      return new Promise(function(resolve, reject) {
        const reader = new FileReader()
        reader.onload = function(ev) {
          const data = ev.target.result
          this.wb = XLSX.read(data, {
            type: 'binary'
          })
          const result = []
          this.wb.SheetNames.forEach((sheetname) => {
            result.push(XLSX.utils.sheet_to_json(this.wb.Sheets[sheetname]))
          })
          resolve(result)
        }
        reader.readAsBinaryString(file.raw)
      })
    },

    handleDownload() {
      this.downloadLoading = true
      import('@/vendor/Export2Excel').then(excel => {
        const tHeader = ['hostname', 'ip']
        const filterVal = ['hostname', 'ip']
        const data = this.formatJson(filterVal, this.list)
        excel.export_json_to_excel({
          header: tHeader,
          data,
          filename: '服务器列表'
        })
        this.downloadLoading = false
      })
    },

    formatJson(filterVal, jsonData) {
      return jsonData.map(v => filterVal.map(j => {
        if (j === 'timestamp') {
          return parseTime(v[j])
        } else {
          return v[j]
        }
      }))
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
