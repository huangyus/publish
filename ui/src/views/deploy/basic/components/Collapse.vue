<template>
  <el-row style="padding-bottom: 20px">
    <el-collapse v-model="active">
      <el-collapse-item title="上线单模版" name="1">
        <!-- <el-row style="margin-bottom: 15px">
          <el-col :span="4">
            <el-select v-model="project" placeholder="请选择项目" size="small" style="width: 100%" @change="handleSelect" @visible-change="projectfetchData">
              <el-option v-for="item in projectoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
          <el-col :span="2">
            <el-select v-model="page_size" placeholder="请选择显示页数" size="small" style="width: 100%" @change="handleSelect">
              <el-option v-for="item in pageoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
        </el-row> -->
        <el-row :gutter="5">
          <el-col v-for="(item, index) in templates" :span="1.5" :key="index" style="margin-bottom: 15px">
            <el-button round type="primary" @click="handleTemplate(item.id)">{{ item.name }}</el-button>
          </el-col>
        </el-row>
      </el-collapse-item>
    </el-collapse>
  </el-row>
</template>
<script>
import * as project from '@/api/projects'
import * as bctemplate from '@/api/bctemplate'
import moment from 'moment'

import bus from '@/assets/eventBus'

export default {
  data() {
    return {
      active: ['1'],
      project: null,
      page_size: 20,
      templates: [],
      projectoptions: [],
      pageoptions: [{
        value: 20,
        label: '20条/页'
      }, {
        value: 30,
        label: '30条/页'
      }, {
        value: 50,
        label: '50条/页'
      }, {
        value: 100,
        label: '100条/页'
      }]
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    /**
     * @return {string}
     */
    Timestamp() {
      return moment().format('YYYYMMDDHHmmss')
    },

    fetchData() {
      this.listLoading = true
      bctemplate.getList({ page_size: 20, page: 1 }).then(response => {
        for (let i = 0; i < response.data.results.length; i++) {
          this.templates.push({ name: response.data.results[i].component, id: response.data.results[i].id })
        }
      }).catch(error => {
        console.log(error)
      })
    },

    projectfetchData() {
      project.getList({ page_size: this.page_size, page: 1 }).then(response => {
        this.projectoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.projectoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        console.log(this.projectoptions)
      }).catch(error => {
        console.log(error)
      })
    },

    // handleSelect() {
    //   bctemplate.getList({ project: this.project, page_size: this.page_size, page: 1 }).then(response => {
    //     this.templates = []
    //     for (let i = 0; i < response.data.results.length; i++) {
    //       this.templates.push({ name: response.data.results[i].name, id: response.data.results[i].id })
    //     }
    //   })
    // },

    handleTemplate(row_id) {
      bus.$emit('Template', row_id)
    }

  }
}
</script>
