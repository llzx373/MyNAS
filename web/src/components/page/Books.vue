<template>

    <el-main>
    <el-divider content-position="left">
          <el-button-group>
            <el-button @click="show_new_book=true" type="primary">新增作品</el-button>
          </el-button-group>
        </el-divider>
          <Items :items="books" :screenWidth="screenWidth"></Items>


          <el-dialog title="新增作品" :visible.sync="show_new_book" width="30%">
      <el-form
        ref="chapterForm"
        :rules="chapterForm"
        :model="chapterForm"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="chapterForm.title"></el-input>
        </el-form-item>
        <el-form-item label="简介" prop="summary">
          <el-input type="textarea"  v-model="chapterForm.summary"></el-input>
        </el-form-item>
          <el-button type="primary" @click="newBook">新增作品</el-button>

      </el-form>
    </el-dialog>
</el-main>
</template>
<script>
import Items from "../../components/components/Items";
import axios from "axios";
export default {
  name: "Books",
  components: {
    Items
  },
  data() {
    return { books: [],
    screenWidth: document.body.clientWidth,
    chapterForm: {
        title: "",
        cover:null,
        summary: ""
      },
      show_new_book:false
     };
  },
  
      rules: {
        title: [{ required: true, message: "请输入名称", trigger: "blur" }],
        summary: [
          { required: true, message: "请输入简介", trigger: "blur" }
        ],
      },
  watch: {
    screenWidth(val) {
      this.screenWidth = val;
    },
    $route(to, from) {
      this.getBooks()
    }
  },
  mounted() {
      window.onresize = () => {
      return (() => {
        this.screenWidth = document.body.clientWidth;
      })();
    };
    this.getBooks()
  },
  methods: {
    getBooks() {
      var lib_id = this.$route.query.library_id;
      axios.get("/api/chapter/" + lib_id).then(response => {
        this.books = response.data;
        document.title="书库"
      });
    },
    newBook(){
        this.$refs.chapterForm.validate(valid => {
        if (valid) {
          axios
            .post("/api/chapter/"+this.$route.query.library_id, {
              title: this.chapterForm.title,
              summary: this.chapterForm.summary,
              cover: this.chapterForm.cover,
            })
            .then(response => {
                this.getBooks();
                this.show_new_book=false;
                this.$message(response.data.message);
            });
        }
      });
    }
  }
};
</script>