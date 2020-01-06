<template>
  <el-card :body-style="{ padding: '0px' }" v-if="chapter.item_type=='chapter'"  style="box-shadow: 0 0px 5px 0 #282a32;width:240px">
    <div slot="header" class="clearfix" :style="'width:'+width-40+'px;'">
      <span>{{ chapter.title }}</span>
    </div>
    <el-image
      :style="'width:'+width+'px;cursor:pointer;'"
      :src="imgsrc"
      @click="$router.push({path:'/book',query:{
                  library_id:chapter.library_id,
                  chapter_id: chapter.chapter_id
              }})"
    >
    </el-image>
    <div class="bottom">
      <el-button-group :style="'width:'+width+'px;border-spacing: 0px;'">
        <input @change="uploadCoverSubmit(chapter.chapter_id)" name="file" type="file" :id="'cover_'+chapter.chapter_id" style="display:none">

        <el-button type="primary" icon="el-icon-picture" @click="uploadCover(chapter.chapter_id)"></el-button>
        <el-button type="success" icon="el-icon-edit" @click="showEdit=true"></el-button>
        <el-button type="danger" icon="el-icon-delete"></el-button>
      </el-button-group>
    </div>
    <el-dialog :title="'修改作品《'+chapter.title+'》'" :visible.sync="showEdit" width="30%">
      <el-form
        :v-if="showEdit"
        ref="chapterForm"
        :rules="rules"
        :model="chapterForm"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="chapterForm.title"></el-input>
        </el-form-item>
        <el-form-item label="简介" prop="summary">
          <el-input type="textarea" v-model="chapterForm.summary"></el-input>
        </el-form-item>
        <el-button type="primary" @click="editBook(chapter.chapter_id)">修改作品</el-button>
      </el-form>
    </el-dialog>
  </el-card>
</template>
<script>
import axios from "axios";
export default {
  name: "BookCover",
  data() {
    return {
      disable_up:true,
      imgsrc:this.$cookies.get('hostname')+
        "/api/chapter/" +
        this.chapter.library_id +
        "/" +
        this.chapter.chapter_id +
        "/cover",
      showEdit: false,
      chapterForm: {
        title: this.chapter.title,
        cover: null,
        summary: this.chapter.summary
      },
      rules: {
        title: [{ required: true, message: "请输入名称", trigger: "blur" }],
        summary: [{ required: true, message: "请输入简介", trigger: "blur" }]
      }
    };
  },
  methods: {
    uploadCover(chapter_id){
      document.getElementById("cover_"+chapter_id).click()
    },
    uploadCoverSubmit(chapter_id){
      // var form=document.getElementById('cover_submit_'+chapter_id)
      
      var files=document.getElementById("cover_"+chapter_id).files
      // data.append('file', file);
      const file = new Blob([files[0]], { type: 'image/png' });
      const data = new FormData();
      data.append("file",file,file.filename)

      // const file = new Blob([files[0]]);
      axios
            .post(
              "/api/chapter/" + this.$route.query.library_id + "/" + chapter_id+"/cover",
              data,
              {
                headers:{
                  'Content-Type':'multipart/form-data'
                }
              }
            )
            .then(response => {
                this.imgsrc =this.$cookies.get('hostname')+
                "/api/chapter/" +
                this.chapter.library_id +
                "/" +
                this.chapter.chapter_id +
                "/cover/"+Math.random(),
                this.$message(response.data.message);
            })
    },
    upSuccess(response, file, fileList){
        this.disable_up=true;
    },
    editBook(chapter_id) {
      this.$refs.chapterForm.validate(valid => {
        if (valid) {
          axios
            .put(
              "/api/chapter/" + this.$route.query.library_id + "/" + chapter_id,
              {
                title: this.chapterForm.title,
                summary: this.chapterForm.summary,
                cover: this.chapterForm.cover
              }
            )
            .then(response => {
              this.showEdit = false;
                this.$message(response.data.message);
            });
        }
      });
    }
  },

  props: ["chapter", "width", "height"]
};
</script>