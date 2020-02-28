<template>
  <!-- <el-main> -->
    <el-tabs   v-model="tabName" type="border-card" @tab-click="switchTab">
      <el-tab-pane class='library_tab' label="目录视图" name="dir_view">
        <el-breadcrumb v-if="fdir.library" separator="/">
          <el-breadcrumb-item></el-breadcrumb-item>
          <el-breadcrumb-item
            :to="{path:'/photos',query:{
                  library_id: fdir.library.id,
                  dir_id:0,
                  page:1
              }}"
          >{{fdir.library.name}}</el-breadcrumb-item>
          <el-breadcrumb-item
            v-for="parent in fdir.parents"
            :key="'parent_'+parent.id"
            :to="{path:'/photos',query:{
                  library_id: fdir.library.id,
                  dir_id:parent.id,
                  page:Math.ceil((parent.sub_order_id+1)/30)
              }}"
          >{{ parent.name }}</el-breadcrumb-item>
        </el-breadcrumb>
       
        <div>
          <el-divider content-position="left">
            <el-link :disabled="page<=1" @click="goPage(page-1)">上一页</el-link>
            {{page}} / {{page_count}}
            <el-link :disabled="page>=page_count" @click="goPage(page+1)">下一页</el-link>
          </el-divider>
          
          <Items v-if="fdir.items" :items="fdir.items" :screenWidth="screenWidth"></Items>
          <el-divider content-position="left">
            <el-link :disabled="page<=1" @click="goPage(page-1)">上一页</el-link>
            {{page}} / {{page_count}}
            <el-link :disabled="page>=page_count" @click="goPage(page+1)">下一页</el-link>
          </el-divider>
          
        </div>
      </el-tab-pane>
      <el-tab-pane label="资源视图" name="library_view">
        <LibraryView :library_id="$route.query.library_id"></LibraryView>
        </el-tab-pane>
    </el-tabs>
  <!-- </el-main> -->
</template>

<script>
import Items from "../components/Items";
import LibraryView from "../components/LibraryView";
// import ThumbSize from "../../components/components/ThumbSize";
import axios from "axios";
export default {
  name: "library",
  data() {
    return {
      librarys: [],
      fdir: {},
      items_per_page: 30,
      page: 1,
      screenWidth: document.body.clientWidth,
      cols_in_row: 12,
      tabName: "dir_view",
      random_dirs: [],
      search_dirs: [],
      search_keyword: "",
      search_item_type:"dir",
      search_library:null
    };
  },
  computed: {
    page_count() {
      return Math.max(1, Math.ceil(this.fdir.item_count / this.items_per_page));
    }
  },
  components: {
    Items,
    LibraryView
  },
  mounted() {
    document.documentElement.style.overflow = "auto";
    window.onresize = () => {
      return (() => {
        this.screenWidth = document.body.clientWidth;
      })();
    };
    this.getCurrentPage();
  },
  watch: {
    screenWidth(val) {
      this.screenWidth = val;
    },
    $route(to, from) {
      this.getCurrentPage();
      this.random();
    }
  },
  methods: {
    search() {
      var lib_id = this.$route.query.library_id;
      axios
        .get(
          "/api/library/search?count=12&library=" +
            lib_id +
            "&keyword=" +
            this.search_keyword+
            "&item_type="+this.search_item_type
        )
        .then(response => {
          this.search_dirs = response.data;
        });
    },
    random() {
      var lib_id = this.$route.query.library_id;
      axios
        .get("/api/library/random?count=12&library=" + lib_id)
        .then(response => {
          this.random_dirs = response.data;
        });
    },
    getCurrentPage() {
      let library_id = this.$route.query.library_id;
      let dir_id = this.$route.query.dir_id;
      var page = this.$route.query.page;
      if (this.$route.query.tab) {
        this.tabName = this.$route.query.tab;
      }
      if (page) {
        this.page = page;
      } else {
        this.page = 1;
      }
      axios
        .get(
          "/api/library/" +
            library_id.toString() +
            "/" +
            dir_id.toString() +
            "?page=" +
            this.page
        )
        .then(response => {
          this.fdir = response.data;
          if (dir_id == 0) {
            document.title = this.fdir.library.name;
          } else {
            document.title = this.fdir.dir.name;
          }
        });
    },
    goPage(page) {
      this.$router.push({
        path: "/photos",
        query: {
          library_id: this.$route.query.library_id,
          dir_id: this.$route.query.dir_id,
          page: page
        }
      });
    },
    switchTab(tab) {
      var name = tab.name;
      if (name == "library_view") {
        this.random();
      }
    }
  }
};
</script>
<style>
.library_tab {
  /* background-color:#4C5061; */
}
.el-tabs__item.is-active {
  /* background-color:#4C5061; */
}
</style>