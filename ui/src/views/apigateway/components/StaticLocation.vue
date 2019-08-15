<template>
  <div>
    <el-button type="success" style="margin-bottom: 15px" size="mini" @click="add_st_upstream">增加静态Location</el-button>
    <el-table :data="stupstreams" border fit highlight-current-row>
      <el-table-column label="静态类型">
        <template slot-scope="scope">
          <el-form-item :rules="{ required: true, message: '静态类型必填', trigger: 'change' }" :prop="'statics_list.' + scope.$index + '.location_type'" class="stupstreams">
            <el-select v-model="scope.row.location_type" filterable placeholder="请输入静态类型" style="width: 100%">
              <el-option v-for="item in location_type" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-form-item>
        </template>
      </el-table-column>
      <el-table-column label="静态资源路径">
        <template slot-scope="scope">
          <el-form-item :rules="{ required: true, message: '静态资源路径必填', trigger: 'blur' }" :prop="'statics_list.' + scope.$index + '.location_static'" class="stupstreams">
            <el-input v-model="scope.row.location_static" autocomplete="off" placeholder="请输入静态资源路径"/>
          </el-form-item>
        </template>
      </el-table-column>
      <el-table-column label="location名称（URL）">
        <template slot-scope="scope">
          <el-form-item :rules="{ required: true, message: 'Location URL必填', trigger: 'blur' }" :prop="'statics_list.' + scope.$index + '.location_url'" class="stupstreams">
            <el-input v-model="scope.row.location_url" autocomplete="off" placeholder="请输入Location URL" />
          </el-form-item>
        </template>
      </el-table-column>
      <el-table-column label="location注释说明">
        <template slot-scope="scope">
          <el-input v-model="scope.row.location_desc" autocomplete="off" placeholder="请输入Location注释说明" />
        </template>
      </el-table-column>
      <el-table-column label="条件参数">
        <template slot-scope="scope">
          <el-popover :ref="`condition-${scope.$index}`" placement="top" width="730">
            <div style="text-align: right; margin: auto">
              <ace-editor :content.sync="scope.row.location_condition" :lang.sync="text"/>
              <el-button size="mini" type="danger" @click="scope._self.$refs[`condition-${scope.$index}`].doClose()">取消</el-button>
              <el-button type="primary" size="mini" @click="scope._self.$refs[`condition-${scope.$index}`].doClose()">确定</el-button>
            </div>
            <el-button slot="reference">条件参数</el-button>
          </el-popover>
          <el-input v-model="scope.row.location_condition" style="display: none" />
        </template>
      </el-table-column>
      <el-table-column label="扩展参数">
        <template slot-scope="scope">
          <el-popover :ref="`extras-${scope.$index}`" placement="top" width="730">
            <div style="text-align: right; margin: auto">
              <ace-editor :content.sync="scope.row.location_extra" />
              <el-button size="mini" type="danger" @click="scope._self.$refs[`extras-${scope.$index}`].doClose()">取消</el-button>
              <el-button type="primary" size="mini" @click="scope._self.$refs[`extras-${scope.$index}`].doClose()">确定</el-button>
            </div>
            <el-button slot="reference">扩展参数</el-button>
          </el-popover>
          <el-input v-model="scope.row.location_condition" style="display: none" />
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="50">
        <template slot-scope="scope">
          <a @click="del_st_upstream(scope.$index)"><i class="el-icon-circle-close" style="font-size: 20px"/></a>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import AceEditor from './AceEditor'

export default {
  components: {
    AceEditor
  },
  props: {
    stupstreams: {
      type: Array,
      default: () => {
        return [{ location_type: '', location_static: '', location_url: '', location_desc: '', location_condition: '', location_extra: '{}' }]
      }
    }
  },
  data() {
    return {
      text: 'text',
      location_type: [{ label: 'alias', value: 'alias' }, { label: 'root', value: 'root' }]
    }
  },
  methods: {
    add_st_upstream() {
      const upsteam = { location_type: '', location_static: '', location_url: '', location_desc: '', location_condition: '', location_extra: '{}' }
      this.stupstreams.push(upsteam)
    },
    del_st_upstream(index) {
      this.stupstreams.splice(index, 1)
    }
  }
}
</script>
<style>
  .stupstreams {
    margin-bottom: 0px
  }
</style>
