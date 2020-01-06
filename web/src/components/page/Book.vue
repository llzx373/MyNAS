<template>
  <el-container>
     
    <el-aside>
      <ChapterTree :treeChange="treeChange" @changeChapter="changeChapter"></ChapterTree>
    </el-aside>
    <el-main>
      <el-tabs style="width:100%" v-model="tabName" type="card" @tab-click="changeTab">
        <el-tab-pane label="编辑" name="edit">
          <BookEditor  ref="cmedit" :contextEdit='true' :chapter_id="chapter.id"  @changeChapter="changeChapter" :section="'context'" :min_height="28"></BookEditor>
        </el-tab-pane>
        <el-tab-pane label="预览" name="preview">
            <vue-markdown ref="md" :source="preview"></vue-markdown>
        </el-tab-pane>
        <el-tab-pane v-if="fullchildren.length>0" label="大纲" name="summary">
            <div v-for="child in fullchildren" :key="'child_'+child.id">
                <el-divider>{{child.title}}</el-divider>
                <BookEditor  :editChange="editChange" :chapter_id="child.id" :section="'summary'" :min_height="5"></BookEditor>

            </div>
        </el-tab-pane>
        <el-tab-pane   v-if="fullchildren.length>0" label="任务" name="task">
          <el-table :data="fullchildren" row-key="id">
            <el-table-column prop="title" label="标题"></el-table-column>
            <el-table-column prop="word_count" label="本字数章节"></el-table-column>
            <el-table-column prop="chapter_word_count" label="字数总计"></el-table-column>
            <el-table-column prop="dest_word_count" label="预计总计" ></el-table-column>
            <el-table-column prop="status" label="当前状态" ></el-table-column>
            <el-table-column prop="utime" label="最后更新时间" ></el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-main>
    <el-aside style="width:221px;text-align:center">
      <el-divider>任务({{chapter.word_count}}/{{chapter.dest_word_count}})</el-divider>
      <el-progress
        :width="64"
        style="margin:0 auto"
        :percentage="task.percent"
        :status="task.status"
        type="circle"
      ></el-progress>
      <el-divider>摘要</el-divider>

      <BookEditor :chapter_id="chapter.id" :section="'summary'" :min_height="5"></BookEditor>

      <el-divider>笔记</el-divider>
      <BookEditor :chapter_id="chapter.id"  :section="'note'" :min_height="8"></BookEditor>
    </el-aside>
  </el-container>
</template>
<script>
import axios from "axios";
import ChapterTree from "../components/ChapterTree";
import BookEditor from "../components/BookEditor";
import VueMarkdown from 'vue-markdown'
import Prism from 'prismjs';
export default {
  components: {
    ChapterTree,
    BookEditor,
     VueMarkdown 
  },
  data() {
    return {
      tabName: "edit",
      chapter: {},
      task: {
        status: "success",
        percent: 100
      },
      fullchildren: [],
      preview:"",
      treeChange:0,
      editChange:0
    };
  },
  mounted() {
    this.getContext();
    this.flushTask()
  },
  watch: {
    $route(to, from) {
        this.context_change = false;
        this.getContext();
        this.flushTask()

        this.changeTab(null)
    }
  },
  updated(){
  },
  methods: {
    flushTask(){
        var lib_id = this.$route.query.library_id;
      var chapter_id = this.$route.query.chapter_id;
         axios
          .get("/api/chapter/" + lib_id + "/" + chapter_id + "?full=true")
          .then(response => {
            this.fullchildren = response.data.children.children;
          });
    },
    changeTab(tab) {
      var lib_id = this.$route.query.library_id;
      var chapter_id = this.$route.query.chapter_id;
      if (tab ===null){
        var name = this.tabName;
      }
      else{
          var name = tab.name;
      }
      
      this.tabName=name;
     
      if (name == "task") {
          this.flushTask()
      }
      if (name=="preview"){
          axios.get("/api/chapter/" + lib_id + "/" + chapter_id+"/preview").then(response => {
              this.preview=response.data.context
              Prism.highlightAll();
          })
          
      }
      
      if (name == "edit") {
         this.editChange+=1
          this.getContext()
      }
    },
    getContext() {
      var lib_id = this.$route.query.library_id;
      var chapter_id = this.$route.query.chapter_id;
      axios.get("/api/chapter/" + lib_id + "/" + chapter_id).then(response => {
        this.chapter = response.data;
        document.title=this.chapter.title
        Prism.highlightAll();
        if (this.chapter.dest_word_count < 0) {
          this.task = {
            status: "success",
            percent: 100
          };
        } else {
          var percent = Number(
            this.chapter.word_count / (this.chapter.dest_word_count / 100)
          );
          if (0<= percent&&percent <= 25) {
            this.task = {
              status: "exception",
              percent: percent
            };
          } else if (25<percent &&percent < 100) {
            this.task = {
              status: "warning",
              percent: percent
            };
          } else {
            this.task = {
              status: "success",
              percent: 100
            };
          }
        }
      });
    },
    changeChapter() {
      this.getContext();
      this.flushTask();
      this.treeChange+=1
    }
  },
    // render()
    // render: h => h(Book)
};
</script>