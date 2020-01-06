<template>
  <div>
    <el-tree
    :draggable="true"
      node-key="id"
      :default-expand-all="true"
      :data="chapter_children"
      :props="defaultProps"
      @node-click="handleNodeClick"
      @node-contextmenu="handleNodeContextMenu"
      @node-drop="handleNodeDrag"
      :highlight-current="true"
      :expand-on-click-node="false"
    >
      <span class="custom-tree-node" slot-scope="{ node, data }">
        <span v-if="data.id!=$route.query.chapter_id"> {{data.order_id}}. [{{data.word_count}}字] {{ node.label }}</span>
        <b v-if="data.id==$route.query.chapter_id">{{data.order_id}}. [{{data.word_count}}字] {{ node.label }}</b>
      </span>
    </el-tree>
    <el-dialog
      :title="'新增章节到'+newChapterForm.parent_name"
      :visible.sync="newChapterShow"
      width="30%"
    >
      <el-form ref="newChapterForm" :rules="rules" :model="newChapterForm" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="newChapterForm.title"></el-input>
        </el-form-item>
        <el-form-item label="简介" prop="summary">
          <el-input type="textarea" v-model="newChapterForm.summary"></el-input>
        </el-form-item>
        <el-button type="primary" @click="newChapter">新增章节</el-button>
      </el-form>
    </el-dialog>
    <el-dialog
      :title="'修改章节属性:'+changeChapterForm.title"
      :visible.sync="changeChapterShow"
      width="50%"
    >
      <el-form ref="changeChapterForm" :rules="changeChapterRules" :model="changeChapterForm" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="changeChapterForm.title"></el-input>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="changeChapterForm.status">
                <el-radio-button label="草稿"></el-radio-button>
                <el-radio-button label="写作中"></el-radio-button>
                <el-radio-button label="已完成"></el-radio-button>
                <el-radio-button label="已废弃"></el-radio-button>
            </el-radio-group>
        </el-form-item>
        <el-form-item label="目标字数" prop="dest_word_count">
          <el-input type="input" v-model.number="changeChapterForm.dest_word_count"></el-input>
        </el-form-item>
        <el-button type="primary" @click="changeChapter">提交修改</el-button>
      </el-form>
    </el-dialog>
    <div
      v-if="showChapterMenu"
      style="position: fixed;top: 0;right: 0;bottom: 0;left: 0;background:rgba(0, 0, 0, 0);z-index:2000"
      @click="showChapterMenu=false"
    >
      <el-menu
        :style="'position: fixed;left:'+chapterMenuPosition.x+'px;top:'+chapterMenuPosition.y+'px;box-shadow: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04)' "
        background-color="#545c64"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <el-menu-item @click="newChapterShow=true">
          <i class="el-icon-document-add"></i>
          <span slot="title">新增子章节</span>
        </el-menu-item>
        <el-menu-item @click="changeChapterShow=true">
          <i class="el-icon-edit"></i>
          <span slot="title">修改章节属性</span>
        </el-menu-item>
        <el-menu-item @click="handleNodeDelete()">
          <i class="el-icon-document-delete"></i>
          <span slot="title">删除当前章节</span>
        </el-menu-item>
      </el-menu>
    </div>
  </div>
</template>
<script>
import axios from "axios";
export default {
  props:["treeChange"],
  watch: {
    treeChange(val) {
        this.treeChange=val;
        this.flushChapterTree();
    }
  },
  data() {
    return {
      chapter_children: [],
      defaultProps: {
        label: "title"
      },
      newChapterShow: false,
      newChapterForm: {
        parent: 0,
        parent_name: "",
        title: "",
        summary: ""
      },
      rules: {
        title: [{ required: true, message: "请输入名称", trigger: "blur" }],
        summary: [{ required: true, message: "请输入简介", trigger: "blur" }]
      },
      changeChapterShow: false,
      changeChapterForm: {
        chapter_id: 0,
        title: "",
        status:"",
        dest_word_count:0
      },
      changeChapterRules: {
        title: [{ required: true, message: "请输入名称"}],
        status: [{ required: true, message: "请选择状态" }],
dest_word_count: [{ required: true, message: "请输入目标字数"},{ type: 'number', message: '目标字数必须为数字值'}],
      },
      showChapterMenu: false,
      chapterMenuPosition: {
        x: 0,
        y: 0
      }
    };
  },
  mounted() {
    this.flushChapterTree();
  },
  methods: {

    handleNodeDrag(node,last_node,pos,event){
      var lib_id = this.$route.query.library_id;
      var node_id=node.data.id;
      var dest_id=last_node.data.id;
      // 这里放置节点 步骤为： 提交当前节点，目标节点，目标位置到api，api完成操作之后，重新渲染菜单
      axios.post("/api/chapter/" + lib_id + "/" + node_id+"/change_pos",{
        'dest_chapter':dest_id,
        'dest_position':pos
      }).then(response => {
          this.flushChapterTree();
            this.$message(response.data.message);
            axios.get("/api/books/" + lib_id + "/sync").then(response => {
                this.$message(response.data.message);
            })
      })
    },
    flushChapterTree() {
      var lib_id = this.$route.query.library_id;
      var chapter_id = this.$route.query.chapter_id;
      axios.get("/api/chapter/" + lib_id + "/" + chapter_id+"?full=true").then(response => {
        if (response.data.parents.length == 0) {
          this.chapter_children = response.data.children.children;
        } else {
          var book=response.data.parents.pop()
          axios
            .get(
              "/api/chapter/" +
                lib_id +
                "/" +
                book.id +
                "?full=true"
            )
            .then(response => {
              this.chapter_children = response.data.children.children;
              book.children=[]
              this.chapter_children.unshift(book)
            });
        }
      });
    },
    handleNodeContextMenu(event, data, node, component) {
      // 这里展开菜单
      this.chapterMenuPosition.x = event.clientX;
      this.chapterMenuPosition.y = event.clientY;
      this.newChapterForm.parent = data.id;
      this.newChapterForm.parent_name = data.title;

      this.changeChapterForm.chapter_id=data.id;
      this.changeChapterForm.title=data.title;
      this.changeChapterForm.status=data.status;
      this.changeChapterForm.dest_word_count=data.dest_word_count;
      this.showChapterMenu = true;
    },
    handleNodeClick(data, node, component) {
      this.$router.push({
        path: "/book",
        query: {
          library_id: this.$route.query.library_id,
          chapter_id: data.id
        }
      });
    },
    handleNodeDelete() {
      var lib_id = this.$route.query.library_id;
      var chapter_id = this.newChapterForm.parent;
      axios.get("/api/chapter/" + lib_id + "/" + chapter_id).then(response => {
        var chapter = response.data;
        axios
          .delete("/api/chapter/" + lib_id + "/" + chapter_id)
          .then(response => {
            // 对于删除当前章节的情况，跳转到上级
            if (this.newChapterForm.parent == this.$route.query.chapter_id) {
              this.$router.push({
                path: "/book",
                query: {
                  library_id: lib_id,
                  chapter_id: chapter.parents[1].id
                }
              });
            }
            this.flushChapterTree();
            this.$message(response.data.message);
            axios.get("/api/books/" + lib_id + "/sync").then(response => {
                this.$message(response.data.message);
            })
          });
      });
    },
    changeChapter() {
        this.$refs.changeChapterForm.validate(valid => {
        if (valid) {
            var lib_id = this.$route.query.library_id;
            var chapter_id = this.changeChapterForm.chapter_id;
            axios.get("/api/chapter/" + lib_id + "/" + chapter_id).then(response => {
                var update_id = response.data.update_id + Number(1);
                axios
                .put("/api/chapter/" + lib_id + "/" + chapter_id, {
                    title : this.changeChapterForm.title,
                    status : this.changeChapterForm.status,
                    dest_word_count : this.changeChapterForm.dest_word_count,
                    update_id: update_id
                })
                .then(response => {
                    this.utime=response.data.utime
                    this.$emit("changeChapter");
                    this.flushChapterTree();
                    this.changeChapterShow = false;
                    this.$message(response.data.message);
                });
            });
        }});
    },
    newChapter() {
      this.$refs.newChapterForm.validate(valid => {
        if (valid) {
          axios
            .post(
              "/api/chapter/" +
                this.$route.query.library_id +
                "/" +
                this.newChapterForm.parent,
              {
                title: this.newChapterForm.title,
                summary: this.newChapterForm.summary
              }
            )
            .then(response => {
              this.flushChapterTree();
              this.newChapterShow = false;
              this.$message(response.data.message);
              axios.get("/api/books/" + lib_id + "/sync").then(response => {
                this.$message(response.data.message);
            })
              this.$router.push({
                path: "/book",
                query: {
                library_id: this.$route.query.library_id,
                chapter_id: response.data.chapter.id
                }
      });
            });
        }
      });
    }
  }
};
</script>