<template>
  <el-main>
    <el-form :inline="true">
      <el-button @click="random()">随便看看</el-button>
      <el-select  style="width:120px" v-model="search_range" placeholder="时间范围">
        <el-option label="最近新增" value="recent"></el-option>
        <el-option label="所有条目" value="all"></el-option>
      </el-select>
      <el-form-item  v-if="search_range=='recent'" label="最近数量范围:">
       <el-input 
        style="width:100px"
        v-model="recent_num"
      ></el-input>
      </el-form-item>
      <el-select  style="width:100px" v-model="search_item_type" placeholder="目标类型">
        <el-option label="目录" value="dir"></el-option>
        <el-option label="文件" value="file"></el-option>
      </el-select>
       <el-select  style="width:100px" v-if="search_item_type=='file'" v-model="search_file_type" placeholder="文件类型">
        <el-option label="视频" value="video"></el-option>
        <el-option label="图片" value="photo"></el-option>
      </el-select>
      <el-form-item label="结果条目数:">
         <el-select  style="width:100px" v-model="search_count">
           <el-option value="12"></el-option>
        <el-option value="24"></el-option>
        <el-option value="48"></el-option>
        <el-option value="96"></el-option>
      </el-select>
      </el-form-item>
     
      <el-input
        style="width:445px"
        v-model="search_keyword"
        placeholder="请输入搜索条件"
        @keyup.enter.native="search"
      ></el-input>
      <el-button icon="el-icon-search" @click="search()"></el-button>
    </el-form>
    <Items v-if="items" :items="items" :screenWidth="screenWidth"></Items>
  </el-main>
</template>


<script>
import axios from "axios";
import Items from "../../components/components/Items";
import User from "../../components/components/User";
import ThumbSize from "../../components/components/ThumbSize";
export default {
  name: "LibraryView",
  props: {
    library_id: null
  },
  data() {
    return {
      librarys: null,
      screenWidth: document.body.clientWidth,
      cols_in_row: 12,
      items: [],
      search_keyword: "",
      search_item_type: "dir",
      search_library: null,
      search_count: 12,
      search_range: "all",
      recent_num:1000,
      search_file_type:"video"
    };
  },
  components: {
    Items,
    User,
    ThumbSize
  },
  mounted() {
    window.onresize = () => {
      return (() => {
        this.screenWidth = document.body.clientWidth;
      })();
    };
    this.random();
  },
  methods: {
    search() {
      console.log("search", this.search_keyword);
      var lib_id = this.library_id;
      var url = "";
      if (lib_id != null) {
        url =
          "/api/library/search?count="+this.search_count+"&library=" +
          lib_id +
          "&keyword=" +
          this.search_keyword +
          "&item_type=" +
          this.search_item_type;
      } else {
        url =
          "/api/library/search?count="+this.search_count+"&keyword=" +
          this.search_keyword +
          "&item_type=" +
          this.search_item_type;
      }
      axios.get(url).then(response => {
        this.items = response.data;
      });
    },
    random() {
      var lib_id = this.library_id;
      var url="/api/library/random?count="+this.search_count
      if (this.search_range=='recent'){
        url=url+"&new_add="+this.recent_num
      }
      url=url+"&item_type="+this.search_item_type
      if (this.search_item_type=='file'){
        url=url+"&file_type="+this.search_file_type
      }
      if (lib_id != null) {
        url=url+"&library=" + lib_id
        
      }
      axios.get(url).then(response => {
          this.items = response.data;
        });
    },
    
  },
  watch: {
    screenWidth(val) {
      this.screenWidth = val;
    },
    $route(to, from) {
      this.random()
      // location.reload();
      // this.$router.go(0);
    }
  }
};
</script>


<style>
</style>