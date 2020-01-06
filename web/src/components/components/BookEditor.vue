<template>
  <div>
    <!-- 最后更新时间：{{utime}} -->
    <el-form v-if="!contextEdit">
      <el-form-item>
        <el-input
          :disabled="edit_disable"
          :autosize="{ minRows: min_height}"
          resize="none"
          :show-word-limit="true"
          ref="context"
          type="textarea"
          v-model="context"
        ></el-input>
      </el-form-item>
    </el-form>
    <!-- <vueEditorMd  :options="codemirror_options" v-if="contextEdit" :value="context" @changeContext="changeContextEditor"></vueEditorMd> -->
    <codemirror ref="cm" :options="codemirror_options" v-if="contextEdit" v-model="context"></codemirror>
  </div>
</template>
<script>
import axios from "axios";
import { codemirror } from "vue-codemirror";
import "codemirror/lib/codemirror.css";
import "codemirror/mode/gfm/gfm.js";
import "codemirror/mode/javascript/javascript";
import "codemirror/mode/clike/clike";
import "codemirror/mode/go/go";
import "codemirror/mode/htmlmixed/htmlmixed";
import "codemirror/mode/http/http";
import "codemirror/mode/php/php";
import "codemirror/mode/python/python";
import "codemirror/mode/http/http";
import "codemirror/mode/sql/sql";
import "codemirror/mode/vue/vue";
import "codemirror/mode/xml/xml";
import "codemirror/addon/selection/active-line.js";
import "codemirror/addon/display/autorefresh.js";

// import "codemirror/addon/edit/continuelist.js";
// import "codemirror/addon/display/panel.js";
// import "./buttons.js";
// import CodeMirror from "codemirror";
// import $ from "jquery";
// import cmResize from 'cm-resize';

export default {
  name: "BookEditor",
  props: {
    section: "",
    min_height: 0,
    chapter_id: 0,
    contextEdit: false,
    editChange: 0,
  },
  components: {
    codemirror
  },
  data() {
    return {
      context: "",
      utime: null,
      context_change: false,
      edit_disable: false,

      codemirror_options: {
        tabSize: 4,
        line: true,
        mode: "gfm",
        lineNumbers: true,
        lineWrapping: true,
        readOnly: this.edit_disable,
        styleActiveLine: true,
        autoRefresh: true
        
      },
      cm:null
    };
  },
  watch: {
    context(val) {
      this.context = val;
      this.context_change = true;
      this.changeContextEditor(val);
    },
    editChange(val) {
      this.editChange = val;
      this.getContext();
    },
    chapter_id(val) {
      this.context_change = false;
      this.chapter_id = val;
      this.getContext();
    }
    // $route(to, from) {
    //   this.context_change = false;
    //   this.getContext();
    //   this，
    // }
  },
  mounted() {
    this.getContext();
    // if (this.contextEdit) {
    //     this.cm = this.$refs.cm.codemirror;
    // }
    this.last_chapter_id = this.chapter_id;
    if (this.timer) {
      clearInterval(this.timer);
    } else {
      this.timer = setInterval(() => {
        // 仅当前存在syncing时候执行
        if (this.context_change) {
          this.updateContext();
        }
      }, 1000);
    }
  },
  // updated(){
  //   if (this.contextEdit) {
  //       var editor = this.$refs.cm.codemirror;
  //       editor.refresh();
  //   }
  // },
  methods: {
    // handleContextMenu(event){
    //     this.show_edit_menu=true
    //     this.editMenuPosition.x = event.clientX;
    //   this.editMenuPosition.y = event.clientY;
    // },
    // save() {
    //   self.updateContext();
    // },
    changeContextEditor(context) {
      if (this.contextEdit) {
        var editor = this.$refs.cm.codemirror;
        // startSize = [cmElement.clientWidth, cmElement.clientHeight];
        var lineCount = editor.lineCount();
        const cmElement = editor.display.wrapper;
        // if (lineCount>10){
        // if (this.contextEdit) {
        // var editor = this.$refs.cm.codemirror;
        // editor.setValue(this.context);
        // editor.refresh();
        // }
        // editor.setSize('auto','auto')
        // editor.setValue(context)
        // editor.refresh()
        // }else{
        //   editor.setSize('auto','720px')
        // }
      }
    },
    getContext() {
      this.edit_disable = true;
      var lib_id = this.$route.query.library_id;
      axios
        .get("/api/chapter/" + lib_id + "/" + this.chapter_id)
        .then(response => {
          this.context = response.data[this.section];
          this.utime = response.data.utime;
          this.edit_disable = false;
          if (this.contextEdit) {
            var editor = this.$refs.cm.codemirror;
            // editor.setValue(this.context);\
            // editor.refresh();
            // editor.focus()
          }
          // this.changeContextEditor(this.context)
        });
    },
    updateContext() {
      var lib_id = this.$route.query.library_id;
      axios
        .get("/api/chapter/" + lib_id + "/" + this.chapter_id)
        .then(response => {
          var update_id = response.data.update_id + Number(1);
          axios
            .put("/api/chapter/" + lib_id + "/" + this.chapter_id, {
              [this.section]: this.context,
              update_id: update_id
            })
            .then(response => {
              this.utime = response.data.utime;
              this.$emit("changeChapter");
              this.context_change = false;
              // this.changeContextEditor(this.context)
            });
        });
    }
  },
  destroyed() {
    clearInterval(this.timer);
  }
};
</script>
<style>
</style>