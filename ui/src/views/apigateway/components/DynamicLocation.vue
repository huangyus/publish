<template>
  <div>
    <el-button type="success" style="margin-bottom: 15px" size="mini" @click="add_dy_upstream">增加动态Location</el-button>
    <el-table :data="dyupstreams" border fit highlight-current-row>
      <el-table-column label="动态类型">
        <template slot-scope="scope">
          <el-form-item :rules="{ required: true, message: '动态类型必填', trigger: 'change' }" :prop="'dynamics_list.' + scope.$index + '.location_type'" class="dyupstreams">
            <el-select v-model="scope.row.location_type" filterable placeholder="请输入动态类型" style="width: 100%" @change="handleChange">
              <el-option v-for="item in location_type" :key="item.label" :label="item.label" :value="item.value"/>
            </el-select>
          </el-form-item>
        </template>
      </el-table-column>
      <el-table-column label="负载均衡">
        <template slot-scope="scope">
          <el-form-item :rules="{ required: true, message: '负载均衡必填', trigger: 'change' }" :prop="'dynamics_list.' + scope.$index + '.location_upstream'" class="dyupstreams">
            <el-select v-if="scope.row.location_type === 'upstream'" v-model="scope.row.location_upstream" autocomplete="off" placeholder="负载均衡">
              <el-option v-for="item in location_upstream" :key="item.label" :label="item.label" :value="item.value"/>
            </el-select>
            <el-input v-else v-model="scope.row.location_upstream" autocomplete="off" placeholder="负载均衡"/>
          </el-form-item>
        </template>
      </el-table-column>
      <el-table-column label="location名称（URL）">
        <template slot-scope="scope">
          <el-form-item :rules="{ required: true, message: 'Location URL必填', trigger: 'blur' }" :prop="'dynamics_list.' + scope.$index + '.location_url'" class="dyupstreams">
            <el-input v-model="scope.row.location_url" autocomplete="off" placeholder="请输入Location URL" />
          </el-form-item>
        </template>
      </el-table-column>
      <el-table-column label="反向代理(URL)">
        <template slot-scope="scope">
          <el-form-item :prop="'dynamics_list.' + scope.$index + '.location_proxy_url'" class="dyupstreams">
            <el-input v-model="scope.row.location_proxy_url" autocomplete="off" placeholder="请输入反向代理 URL" />
          </el-form-item>
        </template>
      </el-table-column>
      <el-table-column label="location注释说明">
        <template slot-scope="scope">
          <el-input v-model="scope.row.location_desc" autocomplete="off" placeholder="请输入location注释说明" />
        </template>
      </el-table-column>
      <el-table-column label="条件参数">
        <template slot-scope="scope">
          <el-popover :ref="`condition-${scope.$index}`" placement="top" width="730">
            <div style="text-align: right; margin: auto">
              <ace-editor :lang.sync="text" :content.sync="scope.row.location_condition" />
              <el-button size="mini" type="danger" @click="scope._self.$refs[`condition-${scope.$index}`].doClose()">取消</el-button>
              <el-button type="primary" size="mini" @click="scope._self.$refs[`condition-${scope.$index}`].doClose()">确定</el-button>
            </div>
            <el-button slot="reference">条件参数</el-button>
          </el-popover>
          <el-input v-model="scope.row.location_condition" style="display: none" />
        </template>
      </el-table-column>
      <el-table-column label="LUA代码">
        <template slot-scope="scope">
          <el-popover :ref="`lua-${scope.$index}`" placement="top" width="730">
            <div style="text-align: right; margin: auto">
              <ace-editor :content.sync="scope.row.location_lua" :lang.sync="text" />
              <el-button size="mini" type="danger" @click="scope._self.$refs[`lua-${scope.$index}`].doClose()">取消</el-button>
              <el-button type="primary" size="mini" @click="scope._self.$refs[`lua-${scope.$index}`].doClose()">确定</el-button>
            </div>
            <el-button slot="reference">LUA代码</el-button>
          </el-popover>
          <el-input v-model="scope.row.location_lua" style="display: none" />
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
          <el-input v-model="scope.row.location_extra" style="display: none" />
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center" width="50">
        <template slot-scope="scope">
          <a @click="del_dy_upstream(scope.$index)"><i class="el-icon-circle-close" style="font-size: 20px"/></a>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import AceEditor from './AceEditor'
import { getList } from '@/api/upstreams'

export default {
  components: {
    AceEditor
  },
  props: {
    dyupstreams: {
      type: Array,
      default: () => {
        return [{ location_type: '', location_upstream: '', location_url: '', location_proxy_url: '', location_desc: '', location_condition: '', location_lua: '{}', location_extra: '{}' }]
      }
    }
  },
  data() {
    return {
      listQuery: {
        page: 1,
        page_size: 20
      },
      location_upstream: this.dyupstreams,
      text: 'text',
      location_type: [{ label: 'upstream', value: 'upstream' }, { label: 'proxy_pass', value: 'proxy_pass' }, { label: 'uwsgi_pass', value: 'uwsgi_pass' }, { label: 'fastcgi_pass', value: 'fastcgi_pass' }]
    }
  },
  methods: {
    add_dy_upstream() {
      const upsteam = { location_type: '', location_upstream: '', location_url: '', location_proxy_url: '', location_desc: '', location_condition: '', location_lua: '{}', location_extra: '{}' }
      this.dyupstreams.push(upsteam)
    },
    del_dy_upstream(index) {
      this.dyupstreams.splice(index, 1)
    },
    handleChange(event) {
      if (event === 'upstream') {
        this.listQuery.apigateway_id = this.$route.query.id
        this.listQuery.page_size = 1000
        getList(this.listQuery).then(response => {
          this.location_upstream = []
          for (let i = 0; i < response.data.results.length; i++) {
            this.location_upstream.push({ value: response.data.results[i].name, label: response.data.results[i].name })
          }
          console.log(this.location_upstream)
        }).catch(error => {
          console.log(error)
        })
      }
    }
  }
}
</script>
<style>
  .dyupstreams {
    margin-bottom: 0px
  }
</style>
