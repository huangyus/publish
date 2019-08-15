<template>
  <div>
    <editor ref="Editor" v-model="contentData" :lang="lang" :width="width" :height="height" theme="monokai" style="margin-bottom: 15px" @init="initEditor"/>
  </div>
</template>

<script>
export default {
  components: {
    editor: require('vue2-ace-editor')
  },
  props: {
    content: {
      type: String,
      default: ''
    },
    lang: {
      type: String,
      default: 'json'
    },
    width: {
      type: String,
      default: '700'
    },
    height: {
      type: String,
      default: '300'
    }
  },
  data() {
    return {
      contentData: this.content
    }
  },
  watch: {
    content: function(val) {
      this.contentData = val
    },
    contentData: function(val) {
      this.$emit('update:content', val)
    }
  },
  methods: {
    initEditor: function(editor) {
      require('brace/ext/language_tools')
      require('brace/mode/json')
      require('brace/theme/monokai')
      editor.setOptions({
        enableLiveAutocompletion: true,
        fontSize: '12pt'
      })
    }
  }
}
</script>

