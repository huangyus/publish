<template>
  <div class="app-container">
    <edit/>
    <list/>
  </div>
</template>

<script>
import Edit from './components/Edit'
import List from './components/List'

export default {
  components: {
    Edit,
    List
  },
  data() {
    return {}
  }
}
</script>
