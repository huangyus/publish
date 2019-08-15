<template>
  <div class="app-container">
    <el-collapse v-model="active">
      <el-collapse-item title="全局配置" name="global">
        <global-config/>
      </el-collapse-item>
      <el-collapse-item title="Map配置" name="maps">
        <maps/>
      </el-collapse-item>
      <el-collapse-item title="节点组管理" name="node">
        <upstreams/>
      </el-collapse-item>
      <el-collapse-item title="虚拟主机" name="vhost">
        <vhosts/>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script>
import GlobalConfig from './components/GlobalConfig'
import Maps from './components/Maps'
import Upstreams from './components/Upstreams'
import Vhosts from './components/Vhosts'

export default {
  components: { GlobalConfig, Maps, Upstreams, Vhosts },
  //   directives: { permission },
  data() {
    return {
      active: ['global', 'maps', 'node', 'vhost']
    }
  }
}
</script>
