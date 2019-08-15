<template>
  <div class="app-container">
    <el-row :gutter="20" style="margin-bottom: 15px;">
      <el-col :span="1.5">
        <el-button v-permission="['add_business']" type="primary" icon="el-icon-edit" @click="handleCreate">新建上线单</el-button>
      </el-col>
      <el-col :span="6">
        <el-input v-model="search" placeholder="请输入内容" class="input-with-select">
          <el-button slot="append" icon="el-icon-search" @click="handleSearch"/>
        </el-input>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogFormVisible" :title="textMap[status]">
      <el-form ref="dataForm" :model="form" :rules="rules">
        <el-form-item :label-width="formLabelWidth" label="名称" prop="name">
          <el-col :span="12">
            <el-input v-model="form.name" placeholder="请输入上线单名称" autocomplete="off" />
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="项目" prop="project">
          <el-col :span="12">
            <el-select v-model="form.project" clearable placeholder="请选择项目" filterable style="width: 100%" @visible-change="projectfetchData">
              <el-option v-for="item in projectoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="模块" prop="modules">
          <el-col :span="12">
            <el-select v-model="form.modules" placeholder="请选择上线模块" clearable filterable style="width: 100%" @visible-change="modulesfetchData(form.project)">
              <el-option v-for="item in modulesoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="部署方式" prop="layout">
          <el-col :span="12">
            <el-select v-model="form.layout" clearable placeholder="请选择部署方式" filterable style="width: 100%" @visible-change="middlewarefetchData">
              <el-option-group v-for="group in layoutoptions" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value"/>
              </el-option-group>
            </el-select>
            <el-tag type="danger">自定义命令以串行执行</el-tag>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="版本" prop="version">
          <el-col :span="12">
            <el-select v-model="form.version" filterable clearable placeholder="请选择上线版本" style="width: 100%" no-data-text="搜索中..." @visible-change="handleVersion(form.project, form.modules)">
              <el-option v-for="item in versionoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="环境" prop="env">
          <el-col :span="12">
            <el-select v-model="form.env" placeholder="请选择上线环境" filterable style="width: 100%">
              <el-option v-for="item in envoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" :rules="form.updownline ? { required: true, message: '机房名称必填', trigger: 'change' } : []" label="机房" prop="idc">
          <el-col :span="12">
            <el-select v-model="form.idc" placeholder="请选择机房" multiple clearable filterable style="width: 100%" @visible-change="idcfetchData">
              <el-option v-for="item in idcoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth">
          <el-col :span="12">
            <el-checkbox v-model="form.updownline" border>启用上下线</el-checkbox>
            <el-tag type="danger">上下线，是配合部署过程中对Nginx网关的操作，以串行执行</el-tag>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth">
          <el-col :span="12">
            <el-checkbox v-model="form.serial" border>启用串行部署</el-checkbox>
            <el-tag type="danger">配合部署以串行执行，默认并行执行</el-tag>
          </el-col>
        </el-form-item>
        <el-form-item v-if="form.updownline" :label-width="formLabelWidth" :rules="form.updownline ? { required: true, message: '服务器分组必填', trigger: 'change' } : []" label="服务器分组" prop="servers">
          <el-col :span="12">
            <el-select v-model="form.servers" placeholder="请选择服务器分组" clearable filterable multiple style="width: 100%" @visible-change="groupfetchData(form.idc)">
              <el-option-group v-for="group in groupoptions" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value"/>
              </el-option-group>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item v-if="form.updownline" :label-width="formLabelWidth" :rules="form.updownline ? { required: true, message: 'Nginx网关必填', trigger: 'change' } : []" label="Nginx网关" prop="gateway">
          <el-col :span="12">
            <el-select v-model="form.gateway" placeholder="请选择Nginx网关" clearable filterable multiple style="width: 100%" @visible-change="apigatewayfetchData(form.idc)">
              <el-option-group v-for="gateway in apigatewayoptions" :key="gateway.label" :label="gateway.label">
                <el-option v-for="item in gateway.options" :key="item.value" :label="item.label" :value="item.value"/>
              </el-option-group>
            </el-select>
          </el-col>
        </el-form-item>
        <el-form-item :label-width="formLabelWidth" label="服务器列表" prop="servers">
          <el-row>
            <el-col :span="12">
              <el-radio-group v-model="radio">
                <el-radio :label="1">人工输入</el-radio>
                <!-- <el-radio :label="2">批量导入</el-radio> -->
                <el-radio :label="3" @change="handleChange(form.idc)">机房查找</el-radio>
              </el-radio-group>
              <el-select v-if="radio == 1" v-model="form.servers" allow-create multiple filterable default-first-option placeholder="请输入服务器IP" style="width: 100%"/>
              <!-- <el-upload v-if="radio == 2" ref="upload" :on-change="importExcel" :auto-upload="false" action="#">
                <el-button size="small" type="primary">点击上传</el-button>
                <div slot="tip">请上传.xlsx格式文件</div>
              </el-upload> -->
              <el-select v-if="radio == 3" v-model="form.servers" multiple filterable placeholder="请输入服务器IP" style="width: 100%" @visible-change="serversfetchData(form.idc)">
                <el-option v-for="item in serversoptions" :key="item.value" :label="item.label" :value="item.value"/>
              </el-select>
            </el-col>
          </el-row>
        </el-form-item>
        <!-- <el-form-item :label-width="formLabelWidth">
          <el-row v-if="radio == 1">
            <el-col v-for="(item, index) in groups" :key="index">
              <el-popover placement="left" width="300" trigger="hover">
                <el-table ref="Table" :data="item.servers" @selection-change="handleSelectionChange(index, $event)">>
                  <el-table-column type="selection" width="55"/>
                  <el-table-column label="服务器地址" property="ip"/>
                </el-table>
                <el-checkbox slot="reference" :label="item.name" border @change="toggleSelection(index, $event)">{{ item.name }}</el-checkbox>
              </el-popover>
            </el-col>
          </el-row>
        </el-form-item> -->
        <el-form-item :label-width="formLabelWidth" label="描述">
          <el-col :span="12">
            <el-input v-model="form.desc" type="textarea" autocomplete="off" placeholder="请输入上线单描述" />
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="status==='create'?createData():updateData()">确 定</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="dialogWorkflowVisible" title="新建工作流上线单">
      <el-row style="margin-bottom: 15px">
        <el-button :disabled="add" icon="el-icon-plus" circle type="primary" @click="add_steps"/>
        <el-button :disabled="del" icon="el-icon-minus" circle type="primary" @click="delete_steps"/>
      </el-row>
      <el-form ref="workflowForm" :model="form">
        <el-steps :active="workflowactive">
          <el-step v-for="item in steps" :key="item.idx" :title="item.title"/>
        </el-steps>
        <el-button :disabled="prev" style="margin-top: 12px;" @click="Prev">上一步</el-button>
        <el-button :disabled="next" style="margin-top: 12px;" @click="Next">下一步</el-button>
        <el-form-item :label-width="formLabelWidth" label="模版名称" prop="name" style="margin-top: 20px;">
          <el-input v-model="form.name" placeholder="请输入工作流模版名称" autocomplete="off" style="width: 300px"/>
        </el-form-item>
        <div v-for="(item, index) in form.steps" :key="item.idx">
          <!-- <el-form-item v-if="workflowactive===item.idx" :label-width="formLabelWidth" label="部署类型">
            <el-col :span="12">
              <el-radio v-model="form.steps[index].type" :label="1" border>业务</el-radio>
              <el-radio v-model="form.steps[index].type" :label="2" border>基础</el-radio>
            </el-col>
          </el-form-item> -->
          <el-form-item v-if="workflowactive===item.idx && form.steps[index].type===1" :label-width="formLabelWidth" :rules="{ required: true, message: '项目名称必填', trigger: 'change' }" :prop="'steps.' + index + '.project'" label="项目">
            <el-select v-model="form.steps[index].project" clearable placeholder="请选择项目" filterable style="width: 300px" @visible-change="projectfetchData" @change="modulesfetchData(form.steps[index].project)">
              <el-option v-for="item in projectoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-form-item>
          <el-form-item v-if="form.steps[index].type===2 && workflowactive===item.idx" :label-width="formLabelWidth" :rules="{ required: true, message: '组件名称必填', trigger: 'change' }" :prop="'steps.' + index + '.component'" label="组件">
            <el-col :span="12">
              <el-select v-model="form.steps[index].component" placeholder="请选择组件" filterable style="width: 300px" @visible-change="middlewarefetchData">
                <el-option v-for="item in middlewareoptions" :key="item.value" :label="item.label" :value="item.value"/>
              </el-select>
            </el-col>
          </el-form-item>
          <el-form-item v-if="workflowactive===item.idx && form.steps[index].type===1" :label-width="formLabelWidth" :rules="{ required: true, message: '模块名称必填', trigger: 'change' }" :prop="'steps.' + index + '.modules'" label="模块">
            <el-select v-model="form.steps[index].modules" placeholder="请选择上线模块" clearable filterable style="width: 300px" @visible-change="modulesfetchData(form.steps[index].project)" @change="groupfetchData(form.steps[index].modules)">
              <el-option v-for="item in modulesoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-form-item>
          <el-form-item v-if="workflowactive===item.idx" :label-width="formLabelWidth" :rules="{ required: true, message: '部署方式必填', trigger: 'change' }" :prop="'steps.' + index + '.layout'" label="部署方式">
            <el-select v-model="form.steps[index].layout" clearable placeholder="部署方式" filterable style="width: 300px" @visible-change="middlewarefetchData">
              <el-option-group v-for="group in layoutoptions" :key="group.label" :label="group.label">
                <el-option v-for="item in group.options" :key="item.value" :label="item.label" :value="item.value"/>
              </el-option-group>
            </el-select>
          </el-form-item>
          <!-- <el-form-item v-if="workflowactive===item.idx && form.steps[index].layout==='0'" prop="custom_command">
            <el-input v-model="form.steps[index].custom_command" :rows="9" autocomplete="off" type="textarea" title="可用的宏替换，（${PACKAGE}）代码包，（${FILENAME}）代码包名" placeholder="部署命令，请以换行分隔"/>
          </el-form-item> -->
          <el-form-item v-if="workflowactive===item.idx && form.steps[index].type===1" :label-width="formLabelWidth" :rules="{ required: true, message: '版本必填', trigger: 'change' }" :prop="'steps.' + index + '.version'" label="版本">
            <el-select v-model="form.steps[index].version" filterable clearable placeholder="请选择上线版本" style="width: 300px" no-data-text="搜索中..." @visible-change="handleVersion(form.steps[index].project, form.steps[index].modules)">
              <el-option v-for="item in versionoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-form-item>
          <el-form-item v-if="workflowactive===item.idx" :label-width="formLabelWidth" label="环境" prop="env">
            <el-select v-model="form.steps[index].env" placeholder="请选择上线环境" filterable style="width: 300px">
              <el-option v-for="item in envoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-form-item>
          <el-form-item v-if="workflowactive===item.idx" :label-width="formLabelWidth" label="机房">
            <el-select v-model="form.steps[index].idc" placeholder="请选择机房" clearable filterable style="width: 300px" @visible-change="idcfetchData" @change="serversfetchData(form.steps[index].idc)">
              <el-option v-for="item in idcoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-form-item>
          <el-form-item v-if="workflowactive===item.idx" :label-width="formLabelWidth" :rules="{ required: true, message: '服务器列表必填', trigger: 'change' }" :prop="'steps.' + index + '.servers'" label="服务器列表">
            <el-row>
              <el-col :span="12">
                <el-radio-group v-model="radio">
                  <el-radio :label="1">人工输入</el-radio>
                  <el-radio :label="2">批量导入</el-radio>
                  <el-radio :label="3" @change="handleChange(form.steps[index].idc)">机房查找</el-radio>
                </el-radio-group>
                <el-select v-if="workflowactive===item.idx && radio == 1" v-model="form.steps[index].servers" allow-create multiple filterable placeholder="请输入服务器IP" style="width: 300px"/>
                <el-upload v-if="radio == 2" ref="upload" :on-change="importExcel" :auto-upload="false" action="#">
                  <el-button size="small" type="primary">点击上传</el-button>
                  <div slot="tip">请上传.xlsx格式文件</div>
                </el-upload>
                <el-select v-if="workflowactive===item.idx && radio == 3" v-model="form.steps[index].servers" multiple filterable placeholder="请输入服务器IP" style="width: 300px">
                  <el-option v-for="item in serversoptions" :key="item.value" :label="item.label" :value="item.value"/>
                </el-select>
              </el-col>
            </el-row>
          </el-form-item>
          <el-form-item v-if="workflowactive===item.idx" :label-width="formLabelWidth">
            <el-row v-if="radio == 1" :gutter="5">
              <el-col v-for="(item, index) in groups" :key="index" :span="4">
                <el-popover placement="left" width="300" trigger="hover">
                  <el-table ref="Table" :data="item.servers" @selection-change="handleSelectionChange(index, $event)">>
                    <el-table-column type="selection" width="55"/>
                    <el-table-column label="服务器地址" property="ip"/>
                  </el-table>
                  <el-checkbox slot="reference" :label="item.name" border @change="toggleSelection(index, $event)">{{ item.name }}</el-checkbox>
                </el-popover>
              </el-col>
            </el-row>
          </el-form-item>
        </div>
        <el-form-item :label-width="formLabelWidth" label="描述">
          <el-input v-model="form.desc" placeholder="描述" autocomplete="off" style="width: 300px"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogWorkflowVisible = false">取 消</el-button>
        <el-button type="primary" @click="status==='create'?createData():updateData()">确 定</el-button>
      </div>
    </el-dialog>

    <el-collapse v-model="active">
      <el-collapse-item title="上线单模版" name="template">
        <el-row style="margin-bottom: 15px">
          <el-col :span="2">
            <el-select v-model="templatename" placeholder="请选择项目" size="small" @change="handleSelect">
              <el-option v-for="item in templateoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
          <el-col :span="2">
            <el-select v-model="templatepage" placeholder="请选择显示页数" size="small" style="width: 100px" @change="handleSelect">
              <el-option v-for="item in pageoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
        </el-row>
        <el-row :gutter="5">
          <el-col v-for="item in template" :span="1.5" :key="item.id" style="margin-bottom: 15px">
            <el-button round type="primary" @click="handleTemplate(item.id)">{{ item.name }}</el-button>
          </el-col>
        </el-row>
      </el-collapse-item>
    </el-collapse>

    <div style="margin-bottom: 15px" />

    <el-collapse v-model="active">
      <el-collapse-item title="工作流模版" name="workflowtemplate">
        <el-row style="margin-bottom: 15px">
          <el-col :span="3">
            <el-select v-model="workflowepage" placeholder="请选择显示页数" size="small" style="width: 100px" @change="handleWorkflowSelect">
              <el-option v-for="item in pageoptions" :key="item.value" :label="item.label" :value="item.value"/>
            </el-select>
          </el-col>
        </el-row>
        <el-row :gutter="5">
          <el-col v-for="item in workflowtemplate" :span="1.5" :key="item.id" style="margin-bottom: 15px">
            <el-button round type="primary" @click="handleWorkFlowTemplate(item.id)">{{ item.name }}</el-button>
          </el-col>
        </el-row>
      </el-collapse-item>
    </el-collapse>

    <div style="margin-bottom: 15px" />

    <el-table v-loading="listLoading" :data="list" element-loading-text="Loading" border fit highlight-current-row>
      <el-table-column type="expand">
        <template slot-scope="props">
          <div v-if="props.row.task_type==='workflow'">
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
          <el-form v-if="props.row.task_type==='simple' || props.row.task_type==='updownline'" label-position="left" inline class="table-expand">
            <el-form-item label="项目名称">
              <span>{{ props.row.project }}</span>
            </el-form-item>
            <el-form-item label="模块名称">
              <span>{{ props.row.modules }}</span>
            </el-form-item>
            <el-form-item label="环境名称">
              <span>{{ props.row.env }}</span>
            </el-form-item>
            <el-form-item label="版本号">
              <span>{{ props.row.version }}</span>
            </el-form-item>
            <el-form-item label="部署方式">
              <span>{{ props.row.layout }}</span>
            </el-form-item>
            <el-form-item label="服务器列表">
              <span>{{ props.row.servers | serversFilter }}</span>
            </el-form-item>
            <el-form-item label="描述">
              <span>{{ props.row.desc }}</span>
            </el-form-item>
          </el-form>
        </template>
      </el-table-column>

      <el-table-column align="center" label="ID" width="95">
        <template slot-scope="scope">
          {{ scope.$index }}
        </template>
      </el-table-column>
      <el-table-column label="上线单名称" show-overflow-tooltip>
        <template slot-scope="scope">
          <!-- <span class="link-type" @click="handledetailRediret(scope.row)">{{ scope.row.name }}</span> -->
          <router-link :to="'/deploy/detail??task_id=' + scope.row.id + '&deploy_type=bs'" class="link-type">{{ scope.row.name }}</router-link>
        </template>
      </el-table-column>
      <el-table-column label="项目" align="center" width="110">
        <template slot-scope="scope">
          <span>{{ scope.row.project }}</span>
        </template>
      </el-table-column>
      <el-table-column label="模块" align="center" width="110">
        <template slot-scope="scope">
          <span>{{ scope.row.modules }}</span>
        </template>
      </el-table-column>
      <el-table-column label="版本号" align="center" width="95">
        <template slot-scope="scope">
          {{ scope.row.version }}
        </template>
      </el-table-column>
      <el-table-column label="部署类型" align="center" width="120">
        <template slot-scope="scope">
          <el-tag>{{ scope.row.task_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建者" align="center" width="110">
        <template slot-scope="scope">
          {{ scope.row.created_by }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="状态" align="center" width="95">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="回滚状态" align="center" width="110">
        <template slot-scope="scope">
          <el-tag v-if="scope.row.rollback_status" :type="scope.row.rollback_status | statusFilter">{{ scope.row.rollback_status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" label="创建时间" width="160">
        <template slot-scope="scope">
          <span>{{ scope.row.created_at }}</span>
        </template>
      </el-table-column>
      <!-- <el-table-column align="center" label="更新时间">
        <template slot-scope="scope">
          <span>{{ scope.row.updated_at }}</span>
        </template>
      </el-table-column> -->
      <el-table-column label="操作" width="240">
        <template slot-scope="scope">
          <el-button v-permission="['run_deploy']" v-if="scope.row.status !== 'success'" size="mini" @click="handleRediret(scope.row)">发布</el-button>
          <el-button v-permission="['run_deploy']" v-if="scope.row.task_type==='simple'" size="mini" type="danger" @click="rollback(scope.row)">回滚</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.page_size" @pagination="fetchData"/>
  </div>
</template>

<script>
import * as project from '@/api/projects'
import * as modules from '@/api/modules'
import * as group from '@/api/group'
import * as middleware from '@/api/middleware'
import * as datacenter from '@/api/datacenter'
import * as servers from '@/api/servers'
import * as bstemplate from '@/api/bstemplate'
import * as workflowtemplate from '@/api/workflow'
import * as apigateway from '@/api/apigateway'
import { createDeploy } from '@/api/deploy'
import { createRollback } from '@/api/rollback'
import { getList, createBusiness, filterVersion, deleteBusiness } from '@/api/business'
import Pagination from '@/components/Pagination'
// import XLSX from 'xlsx'
import { mapGetters } from 'vuex'
import moment from 'moment'
import permission from '@/directive/permission/index' // 权限判断指令

export default {
  components: {
    Pagination
  },
  directives: { permission },
  filters: {
    statusFilter(status) {
      const statusMap = {
        pending: '',
        success: 'success',
        failed: 'danger'
      }
      return statusMap[status]
    },
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
      list: null,
      search: null,
      total: 0,
      listLoading: true,
      active: ['template'],
      workflowactive: 1,
      listQuery: {
        page: 1,
        page_size: 20,
        ordering: '-created_at'
      },
      form: {
        name: '',
        project: '',
        modules: '',
        version: '',
        env: 'prd',
        idc: '',
        steps: [{ type: 1, project: '', modules: '', component: '', version: '', layout: '', custom_command: '', servers: '', env: '', idc: '', idx: 1 }, { type: 1, project: '', modules: '', component: '', version: '', layout: '', custom_command: '', servers: '', env: '', idc: '', idx: 2 }, { type: 1, project: '', modules: '', component: '', version: '', layout: '', custom_command: '', servers: '', env: '', idc: '', idx: 3 }],
        task_type: 'simple',
        servers: [],
        desc: '',
        rollback_sum: 0
      },
      rollbackform: {
        rollback_version: '',
        rollback_layout: ''
      },
      checkAll: false,
      status: '',
      radio: 1,
      textMap: {
        update: '编辑上线单',
        create: '创建上线单'
      },
      isIndeterminate: true,
      projectoptions: [],
      modulesoptions: [],
      serversoptions: [],
      versionoptions: [],
      rollbackoptions: [],
      groupoptions: [],
      groups: [],
      apigatewayoptions: [],
      envoptions: [{
        value: 'prd',
        label: '正式环境'
      }, {
        value: 'test',
        label: '测试环境'
      }, {
        value: 'pre',
        label: '预发环境'
      }, {
        value: 'dev',
        label: '开发环境'
      }],
      templatename: '',
      templateoptions: [],
      templatepage: 20,
      workflowepage: 20,
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
      }],
      idcoptions: [],
      layoutoptions: [{ value: '0', label: '自定义命令' }],
      template: [],
      workflowtemplate: [],
      steps: [{ title: '步骤1', idx: 1 }, { title: '步骤2', idx: 2 }, { title: '步骤3', idx: 3 }],
      add: false,
      del: false,
      prev: false,
      next: false,
      dialogFormVisible: false,
      dialogRollbackVisible: false,
      dialogWorkflowVisible: false,
      formLabelWidth: '120px',
      rules: {
        name: [{ required: true, message: '上线单名称必填', trigger: 'blur' }],
        project: [{ required: true, message: '项目必填', trigger: 'change' }],
        modules: [{ required: true, message: '模块必填', trigger: 'change' }],
        version: [{ required: true, message: '版本必填', trigger: 'change' }],
        servers: [{ required: true, message: '服务器列表必填', trigger: 'change' }],
        layout: [{ required: true, message: '部署方式必填', trigger: 'change' }],
        custom_command: [{ required: true, message: '自定义命令必填', trigger: 'blur' }],
        rollback_version: [{ required: true, message: '回滚版本号必填', trigger: 'change' }],
        rollback_layout: [{ required: true, message: '回滚方式必填', trigger: 'change' }]
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
    this.bstemplateData()
    this.workflowtemplateData()
  },
  methods: {
    Prev() {
      this.workflowactive--
      if (this.workflowactive === 1) {
        this.prev = true
        this.next = false
      } else {
        this.next = false
      }
    },
    Next() {
      this.workflowactive++
      if (this.workflowactive === this.steps.length) {
        this.next = true
        this.prev = false
      } else {
        this.prev = false
      }
    },

    Timestamp() {
      return moment().format('YYYYMMDDHHmmss')
    },

    unique(value) {
      const data = []
      Object.keys(value).forEach(key => {
        data.push(...value[key])
      })
      return Array.from(new Set(data))
    },

    fetchData() {
      this.listLoading = true
      getList(this.listQuery).then(response => {
        this.list = response.data.results
        this.total = response.data.count
        for (let i = 0; i < this.list.length; i++) {
          if (this.list[i].steps) {
            this.list[i].steps = JSON.parse(this.list[i].steps)
          }
        }
        this.listLoading = false
      }).catch(error => {
        console.log(error)
      })
    },

    bstemplateData() {
      bstemplate.getTemplate().then(response => {
        this.template = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.template.push({ name: response.data.results[i].name, id: response.data.results[i].id })
        }
      })
      project.getList({ page_size: 1000, page: 1 }).then(response => {
        this.templateoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.templateoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        console.log(this.templateoptions)
        // setTimeout(() => {}, 1.5 * 1000)
      }).catch(error => {
        console.log(error)
      })
    },

    workflowtemplateData() {
      workflowtemplate.getList().then(response => {
        this.workflowtemplate = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.workflowtemplate.push({ name: response.data.results[i].name, id: response.data.results[i].id })
        }
      })
    },

    projectfetchData() {
      project.getList({ page_size: 1000, page: 1 }).then(response => {
        this.projectoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.projectoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        console.log(this.projectoptions)
        // setTimeout(() => {}, 1.5 * 1000)
      }).catch(error => {
        console.log(error)
      })
    },

    modulesfetchData(event) {
      console.log('project:' + event)
      modules.getList({ project: event, page: 1, page_size: 1000 }).then(response => {
        this.modulesoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.modulesoptions.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        console.log(this.modulesoptions)
        // setTimeout(() => {}, 1.5 * 1000)
      }).catch(error => {
        console.log(error)
      })
      this.form.name = this.Timestamp() + '-' + this.form.project + '-' + this.form.modules
    },

    groupfetchData(idc) {
      this.groupoptions = []
      group.getList({ idc_id: JSON.stringify(idc), page: 1, page_size: 1000 }).then(response => {
        const options = []
        for (let i = 0; i < response.data.results.length; i++) {
          const label = response.data.results[i].name
          for (let j = 0; j < response.data.results[i].servers.length; j++) {
            options.push({ value: response.data.results[i].servers[j], label: response.data.results[i].servers[j] })
          }
          this.groupoptions.push({ label: label, options: options })
        }
        console.log(this.groupoptions)
        // setTimeout(() => {}, 1.5 * 1000)
      }).catch(error => {
        console.log(error)
      })
    },

    apigatewayfetchData(idc) {
      this.apigatewayoptions = []
      apigateway.getList({ idc_id: JSON.stringify(idc), page: 1, page_size: 1000 }).then(response => {
        const options = []
        for (let i = 0; i < response.data.results.length; i++) {
          const label = response.data.results[i].idc.name
          options.push({ value: response.data.results[i].id, label: response.data.results[i].name })
          this.apigatewayoptions.push({ label: label, options: options })
        }
        console.log(this.apigatewayoptions)
      }).catch(error => {
        console.log(error)
      })
    },

    middlewarefetchData() {
      this.layoutoptions = []
      middleware.getList({ page_size: 1000, page: 1 }).then(response => {
        const label = '业务编排'
        const options = []
        for (let i = 0; i < response.data.results.length; i++) {
          options.push({ value: response.data.results[i].name, label: response.data.results[i].name })
        }
        this.layoutoptions.push({ label: label, options: options })
        this.layoutoptions.push({ label: '自定义', options: [{ value: '0', label: '自定义命令' }] })
        console.log(this.layoutoptions)
      })
    },

    idcfetchData() {
      datacenter.getList({ page_size: 1000, page: 1 }).then(response => {
        this.idcoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.idcoptions.push({ value: response.data.results[i].id, label: response.data.results[i].name + '(' + response.data.results[i].location + ')' })
        }
        console.log(this.idcoptions)
      })
    },

    handleVersion(project, module) {
      console.log('搜索：' + project + '_' + module)
      if (event !== '' && this.versionoptions.length === 0) {
        filterVersion({ p: project, m: module }).then(response => {
          this.versionoptions = []
          for (let i = 0; i < response.data.length; i++) {
            this.versionoptions.push({ value: response.data[i].id, label: response.data[i].id + ' - ' + response.data[i].message })
          }
          console.log(this.versionoptions)
        }).catch(error => {
          console.log(error)
        })
      }
    },

    handleRediret(row) {
      if (row.task_type === 'workflow') {
        window.location.href = '/#/deploy/workflowtasks/?task_id=' + row.id + '&deploy_type=workflow'
      } else {
        window.location.href = '/#/deploy/tasks/?task_id=' + row.id + '&deploy_type=bs'
      }
      console.log(row)
      let deploy_type = 'bs'
      const task_id = row.id
      if (row.task_type === 'workflow') {
        deploy_type = 'workflow'
      }
      createDeploy({ task_id: task_id, deploy_type: deploy_type }).then(response => { }).catch(error => {
        this.$notify({
          title: '错误',
          message: '创建失败： ' + error.response.data,
          type: 'error',
          duration: 2000
        })
      })
    },

    handledetailRediret(row) {
      console.log(row)
      if (row.task_type === 'workflow') {
        window.location.href = '/#/deploy/workflowdetail/?task_id=' + row.id + '&deploy_type=workflow'
      } else {
        window.location.href = '/#/deploy/detail/?task_id=' + row.id + '&deploy_type=bs'
      }
    },

    resetForm() {
      this.form = {
        name: null,
        project: null,
        modules: null,
        updownline: false,
        gateway: null,
        serial: false,
        version: null,
        layout: null,
        task_type: 'simple',
        custom_command: null,
        servers: [],
        idc: [],
        env: 'prd',
        desc: null
      }
      this.radio = 1
      this.projectfetchData()
      this.idcfetchData()
      this.middlewarefetchData()
    },
    handleCreate() {
      this.resetForm()
      this.status = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },

    handleTemplate(event) {
      bstemplate.getTemplate({ template_id: event }).then(response => {
        this.form = Object.assign({}, response.data.results[0])
        this.form.name = this.Timestamp() + '-' + this.form.project + '-' + this.form.modules
        this.form.servers = JSON.parse(this.form.servers)
        this.form.steps = [{ step: '', project: '', modules: '', version: '', layout: '', custom_command: '', servers: [], env: '', idc: '', idx: 1 }]
        this.status = 'create'
        // this.groupfetchData(this.form.idc)
        this.dialogFormVisible = true
        this.$nextTick(() => {
          this.$refs['dataForm'].clearValidate()
        })
      })
    },

    handleWorkFlowTemplate(event) {
      workflowtemplate.getList({ template_id: event, page_size: 1000 }).then(response => {
        this.form = Object.assign({}, response.data.results[0])
        this.form.steps = JSON.parse(this.form.steps)
        this.workflowactive = this.form.steps.length
        this.steps = []
        this.form.servers = []
        this.form.project = ''
        this.form.modules = ''
        this.form.task_type = 'workflow'
        this.next = true
        for (let i = 0; i < this.form.steps.length; i++) {
          if (!Array.isArray(this.form.steps[i].servers)) {
            this.form.steps[i].servers = JSON.parse(this.form.steps[i].servers)
          }
          const idx = i + 1
          const step = { title: '步骤' + idx, idx: idx }
          this.steps.push(step)
        }
        this.status = 'create'
        this.dialogWorkflowVisible = true
        this.$nextTick(() => {
          this.$refs['workflowForm'].clearValidate()
        })
      })
    },

    handleDelete(row) {
      deleteBusiness(row).then(() => {
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

    toggleSelection(idx, event) {
      console.log(idx)
      if (event) {
        this.$refs.Table[idx].toggleAllSelection()
      } else {
        this.$refs.Table[idx].clearSelection()
      }
    },

    handleSelectionChange(idx, val) {
      const servers = []
      val.forEach(v => {
        servers.push(v.ip)
      })
      this.groupservers[idx] = servers
      const data = this.unique(this.groupservers)
      console.log(data)
      this.form.servers = this.unique(this.groupservers)
    },

    createData() {
      if (this.$refs['dataForm']) {
        this.$refs['dataForm'].validate((valid) => {
          if (valid) {
            const data = Object.assign({}, this.form)
            data.created_by = this.user
            if (data.servers) {
              data.servers = JSON.stringify(data.servers)
            }
            if (data.updownline) {
              data.task_type = 'updownline'
            }
            data.gateway = JSON.stringify(data.gateway)
            // data.role = this.roles.id.toString()
            data.steps = '[]'
            console.log(data)
            // console.log(this.user)
            createBusiness(data).then(response => {
              console.log(response)
              this.dialogFormVisible = false
              this.dialogWorkflowVisible = false
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
      } else {
        this.$refs['workflowForm'].validate((valid) => {
          if (valid) {
            const data = Object.assign({}, this.form)
            data.created_by = this.user
            data.name = data.name + '-' + this.Timestamp()
            // if (!Array.isArray(data.servers)) {
            //   data.servers = data.servers.split(',')
            // }
            if (data.servers) {
              data.servers = JSON.stringify(data.servers)
            }
            if (data.steps) {
              data.steps = JSON.stringify(data.steps)
            }
            // data.role = this.roles.id.toString()
            console.log(data)
            console.log(this.user)
            createBusiness(data).then(response => {
              console.log(response)
              this.dialogFormVisible = false
              this.dialogWorkflowVisible = false
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
      }
    },

    rollback(row) {
      createRollback({ task_id: row.id, deploy_type: 'bs' }).then(response => {
        this.$notify({
          title: '成功',
          message: '创建成功',
          type: 'success',
          duration: 2000
        })
        window.location.href = '/#/deploy/rollback/?task_id=' + row.id + '&deploy_type=bs'
      }).catch(error => {
        this.$notify({
          title: '错误',
          message: '创建失败： ' + error.response.data.message,
          type: 'error',
          duration: 2000
        })
      })
    },

    serversfetchData(idc) {
      servers.getList({ page_size: 1000, page: 1, idc_id: idc }).then(response => {
        this.serversoptions = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.serversoptions.push({ value: response.data.results[i].ip, label: response.data.results[i].ip })
        }
        console.log(this.serversoptions)
        setTimeout(() => { }, 1.5 * 1000)
      })
    },

    handleChange(idc) {
      if (idc === '') {
        alert('请选择机房')
      }
    },

    // file2Xlsx(file) {
    //   return new Promise(function(resolve, reject) {
    //     const reader = new FileReader()
    //     reader.onload = function(ev) {
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

    // importExcel() {
    //   const file = this.$refs.upload.uploadFiles[0]
    //   const types = file.name.split('.')[1]
    //   const fileType = ['xlsx', 'xls', 'csv'].some(item => item === types)
    //   if (!fileType) {
    //     alert('格式错误，请重新选择')
    //     return
    //   }
    //   this.file2Xlsx(file).then(tabJson => {
    //     const servers = []
    //     if (tabJson && tabJson.length > 0) {
    //       console.log(tabJson)
    //       tabJson[0].forEach((v) => {
    //         servers.push(v.ip)
    //       })
    //     }
    //     console.log(servers)
    //     this.form.servers = servers
    //   })
    // },

    add_steps() {
      if (this.steps.length === 10) {
        this.add = true
        alert('最多只能添加10个工作流任务')
        this.del = false
      } else {
        const idx = this.steps.length + 1
        const step = { title: '步骤' + idx, idx: idx }
        this.steps.push(step)
        this.workform.steps.push({ step: '', project: '', modules: '', layout: '', custom_command: '', servers: [], env: '', idc: '', idx: idx })
        if (this.next) {
          this.next = false
        }
      }
    },

    delete_steps() {
      if (this.steps.length === 2) {
        this.del = true
        alert('最少保留2个工作流任务')
        this.add = false
      } else {
        const idx = this.steps.length - 1
        this.steps.splice(idx, 1)
        this.workform.steps.splice(idx, 1)
      }
    },

    handleSelect() {
      this.listQuery.page_size = this.templatepage
      this.listQuery.project = this.templatename
      bstemplate.getTemplate(this.listQuery).then(response => {
        this.template = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.template.push({ name: response.data.results[i].name, id: response.data.results[i].id })
        }
      })
    },
    handleWorkflowSelect() {
      this.listQuery.page_size = this.workflowepage
      workflowtemplate.getList(this.listQuery).then(response => {
        this.workflowtemplate = []
        for (let i = 0; i < response.data.results.length; i++) {
          this.workflowtemplate.push({ name: response.data.results[i].name, id: response.data.results[i].id })
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
  .link-type {
    color: #337ab7;
    cursor: pointer;
  }

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
