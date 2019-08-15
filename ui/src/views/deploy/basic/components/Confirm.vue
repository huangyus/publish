<template>
  <el-dialog :visible.sync="dialogConfirmVisible" :title="textMap[status]">
    <el-table :data="rows" :show-header="false" border>
      <el-table-column>
        <template slot-scope="scope">
          <el-form label-position="left" inline class="table-expand">
            <el-form-item label="上线单名称">
              <span>{{ scope.row.name }}</span>
            </el-form-item>
            <el-form-item label="项目名称">
              <span>{{ scope.row.project }}</span>
            </el-form-item>
            <el-form-item label="中间件">
              <span>{{ scope.row.component }}</span>
            </el-form-item>
            <el-form-item label="版本号">
              <span>{{ scope.row.version }}</span>
            </el-form-item>
            <el-form-item label="部署类型">
              <el-tag>{{ scope.row.task_type }}</el-tag>
            </el-form-item>
          </el-form>
        </template>
      </el-table-column>
    </el-table>
    <div slot="footer" class="dialog-footer">
      <el-button @click="dialogConfirmVisible = false">取 消</el-button>
      <el-button type="primary" @click="status==='confirm' ? handleDeploy(rows[0].id) : handleRollback(rows[0].id)">确 定</el-button>
    </div>
  </el-dialog>
</template>

<script>
import bus from '@/assets/eventBus'

export default {
  data() {
    return {
      rows: [],
      status: null,
      dialogConfirmVisible: false,
      textMap: {
        update: '编辑上线单',
        create: '创建上线单',
        confirm: '部署二次确认',
        rollback: '回滚二次确认'
      }
    }
  },
  mounted() {
    const that = this
    bus.$on('dialogConfirmVisible', function(event) {
      that.dialogConfirmVisible = event
    })
    bus.$on('Confirmstatus', function(event) {
      that.status = event
    })
    bus.$on('Confirmrows', function(event) {
      that.rows = event
    })
  },
  methods: {
    handleDeploy(row_id) {
      bus.$emit('ConfirmDeploy', row_id)
    },

    handleRollback(row_id) {
      bus.$emit('ConfirmRollback', row_id)
    }
  }
}
</script>
