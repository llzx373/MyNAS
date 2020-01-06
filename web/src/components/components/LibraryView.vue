<template>
  <el-main>
    <!-- <el-divider content-position="left"> -->
    <el-button-group>
      <el-button @click="random()">随便看看</el-button>
      <el-button @click="new_random()">最近新增</el-button>
      <el-button @click="random_video()">随便看看视频</el-button>
      <el-button @click="new_random_video()">最近新增视频</el-button>
    </el-button-group>
    <el-input style="width:445px" v-model="search_keyword" placeholder="请输入搜索条件" @keyup.enter.native="search">
      <el-select style="width:80px" v-model="search_item_type" slot="prepend" placeholder="目标类型">
        <el-option label="目录" value="dir"></el-option>
        <el-option label="文件" value="file"></el-option>
      </el-select>
      <el-button slot="append" icon="el-icon-search" @click="search()"></el-button>
    </el-input>
    <!-- </el-divider> -->
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
      search_library: null
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
        console.log("search",this.search_keyword)
      var lib_id = this.library_id;
      var url = "";
      if (lib_id != null) {
        url =
          "/api/library/search?count=12&library=" +
          lib_id +
          "&keyword=" +
          this.search_keyword +
          "&item_type=" +
          this.search_item_type;
      } else {
        url =
          "/api/library/search?count=12&keyword=" +
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
      if (lib_id == null) {
        axios.get("/api/library/random?count=12").then(response => {
          this.items = response.data;
        });
      } else {
        axios
          .get("/api/library/random?count=12&library=" + lib_id)
          .then(response => {
            this.items = response.data;
          });
      }
    },
    new_random() {
      var lib_id = this.library_id;
      if (lib_id==null) {
        axios
          .get("/api/library/random?count=12&new_add=1000")
          .then(response => {
            this.items = response.data;
          });
      } else {
        axios
          .get("/api/library/random?count=12&new_add=1000&library=" + lib_id)
          .then(response => {
            this.items = response.data;
          });
      }
    },
    new_random_video() {
        var lib_id = this.library_id;
        console.log('lib_id',lib_id)
        if (lib_id == null) {
        axios
          .get("/api/library/random?count=12&new_add=1000&file_type=video&item_type=file")
          .then(response => {
            this.items = response.data;
          });
      } else {
        axios
          .get("/api/library/random?count=12&new_add=1000&file_type=video&item_type=file&library=" + lib_id)
          .then(response => {
            this.items = response.data;
          });
      }
    },
    random_video() {
        var lib_id = this.library_id;
        if (lib_id == null) {
        axios
          .get("/api/library/random?count=12&file_type=video&item_type=file")
          .then(response => {
            this.items = response.data;
          });
      } else {
        axios
          .get("/api/library/random?count=12&file_type=video&item_type=file&library=" + lib_id)
          .then(response => {
            this.items = response.data;
          });
      }
    },
  },
  watch: {
    screenWidth(val) {
      this.screenWidth = val;
    },
    $route(to, from) {
      // location.reload();
      // this.$router.go(0);
    }
  }
};
</script>


<style>
</style>