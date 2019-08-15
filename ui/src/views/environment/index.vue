<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button type="primary" icon="el-icon-edit" @click="handleCreate">新建环境</el-button>
      </el-col>
      <el-col :span="6">
        <el-input placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search"/>
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[dialogStatus]">
      <el-form ref="dataForm" :model="env">
        <el-form-item :label-width="formLabelWidth" label="环境名称" prop="name">
          <el-col :span="12">
            <el-input v-model="env.name" placeholder="请输入环境名称" />
          </el-col>
        </el-form-item>

        <el-form-item :label-width="formLabelWidth" label="机房名称" prop="idc">
          <el-col :span="12">
            <el-select v-model="env.idc" placeholder="请选择机房" multiple filterable style="width: 100%">
              <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
        </el-form-item>

        <el-form-item :label-width="formLabelWidth" label="环境描述" prop="desc">
          <el-col :span="12">
            <el-input v-model="env.desc" type="textarea" placeholder="请输入环境描述" />
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="dislogStatus==='create'?createData():updateData()">确 定</el-button>
      </div>
    </el-dialog>

    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="加载中..."
      border
      fit
      highlight-current-row
      style="width: 100%"
      @sort-change="sortChange">
      <el-table-column align="center" label="ID" width="200">
        <template slot-scope="scope">
          {{ scope.row.id }}
        </template>
      </el-table-column>
      <el-table-column label="环境名称" width="110">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="机房" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.idc }}</span>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="创建者" width="110" align="center">
        <template slot-scope="scope">
          {{ scope.row.created_by }}
        </template>
      </el-table-column>
      <el-table-column align="center" prop="created" label="创建时间" width="200">
        <template slot-scope="scope">
          <i class="el-icon-time"/>
          <span>{{ scope.row.created }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" prop="updated" label="更新时间" width="200">
        <template slot-scope="scope">
          <i class="el-icon-time"/>
          <span>{{ scope.row.updated }}</span>
        </template>
      </el-table-column>
      <el-table-column label="描述" align="center">
        <template slot-scope="scope">
          {{ scope.row.desc }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleUpdate(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchData" />
  </div>
</template>

<script>
import { getList } from '@/api/env'
import Pagination from '@/components/Pagination'

export default {
  components: { Pagination },
  filters: {},
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        name: undefined,
        location: undefined,
        sort: '+id'
      },
      env: {
        id: undefined,
        name: '',
        idc: '',
        desc: ''
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑环境',
        create: '创建环境'
      },
      formLabelWidth: '120px',
      options: [{
        value: '0',
        label: '机房1'
      }, {
        value: '1',
        label: '机房2'
      }]
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.listLoading = true
      getList(this.listQuery).then(response => {
        console.log(response)
        this.list = response.data.data
        this.total = response.data.total
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    },

    handleFilter() {
      this.listQuery.page = 1
      this.fetchData()
    },

    handleDelete(row) {
      this.$notify({
        message: '操作成功',
        type: 'success'
      })
    },
    sortChange(data) {
      const { prop, order } = data
      if (prop === 'id') {
        this.sortByID(order)
      }
    },
    resetForm() {
      this.env = {
        name: '',
        idc: '',
        created_by: '',
        created: '',
        updated: '',
        desc: ''
      }
    },
    handleCreate() {
      this.resetForm()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.env.name = '开发环境'
          this.env.created_by = 'admin'
          this.env.desc = ''
          // createArticle(this.temp).then(() => {
          //   this.list.unshift(this.temp)
          //   this.dialogFormVisible = false
          //   this.$notify({
          //     title: '成功',
          //     message: '创建成功',
          //     type: 'success',
          //     duration: 2000
          //   })
          // })
        }
      })
    },
    handleUpdate(row) {
      this.env = Object.assign({}, row) // copy obj
      this.env.updated = new Date(this.env.updated)
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.env)
          tempData.updated = +new Date(tempData.updated) // change Thu Nov 30 2017 16:41:05 GMT+0800 (CST) to 1512031311464
          // updateArticle(tempData).then(() => {
          //   for (const v of this.list) {
          //     if (v.id === this.temp.id) {
          //       const index = this.list.indexOf(v)
          //       this.list.splice(index, 1, this.temp)
          //       break
          //     }
          //   }
          //   this.dialogFormVisible = false
          //   this.$notify({
          //     title: '成功',
          //     message: '更新成功',
          //     type: 'success',
          //     duration: 2000
          //   })
          // })
        }
      })
    }
  }
}
</script>
