<template>
  <el-dialog :visible.sync="dialogConfirmVisible" :title="textMap[status]">
    <el-table :data="rows" :show-header="false" border>
      <el-table-column>
        <template slot-scope="props">
          <div>
            <el-steps :active="props.row.steps.length" align-center>
              <el-step v-for="item in props.row.steps" :key="item.index" :title="'步骤' + item.idx" :status="item.status"/>
            </el-steps>
            <el-row :gutter="20" type="flex" justify="center">
              <el-col v-for="item in props.row.steps" :key="item.index" :span="12">
                <el-form label-position="left" inline class="table-workflow-expand">
                  <el-form-item label="项目名称">
                    <span>{{ item.project }}</span>
                  </el-form-item>
                  <el-form-item label="模块名称">
                    <span>{{ item.modules }}</span>
                  </el-form-item>
                  <el-form-item label="环境名称">
                    <span>{{ item.env }}</span>
                  </el-form-item>
                  <el-form-item label="版本号">
                    <span>{{ item.version }}</span>
                  </el-form-item>
                  <el-form-item label="部署方式">
                    <span>{{ item.layout }}</span>
                  </el-form-item>
                  <el-form-item label="服务器列表">
                    <span>{{ item.servers | serversFilter }}</span>
                  </el-form-item>
                  <el-form-item label="描述">
                    <span>{{ item.desc }}</span>
                  </el-form-item>
                </el-form>
              </el-col>
            </el-row>
          </div>
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
  filters: {
    serversFilter(servers) {
      if (typeof (servers) === 'string') {
        const data = JSON.parse(servers)
        return data.join(', ')
      }
      return servers.join(', ')
    }
  },
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

  .table-workflow-expand label {
    width: 100px;
    color: #99a9bf;
  }

  .table-workflow-expand .el-form-item {
    margin-left: 35%;
    margin-bottom: 0;
    display:block;
  }
  .table-workflow-expand span {
    word-break:normal; width:auto; display:block; white-space:pre-wrap;word-wrap : break-word ;overflow: hidden ;
  }
  .el-select-dropdown__item {
    max-width: 600px;
  }
</style>
