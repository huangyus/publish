<template>
  <div class="app-container">
    <edit/>
    <confirm/>
    <list/>
  </div>
</template>

<script>
import Edit from './components/Edit'
import Confirm from './components/Confirm'
import List from './components/List'

export default {
  components: {
    Edit,
    List,
    Confirm
  },
  data() {
    return {}
  }
}
</script>
