<template>
  <el-menu
    mode="horizontal"
    background-color="#1d1d1d"
    text-color="#fff"
    active-text-color="#ffd04b"
    :default-active="default_active"
  >
  <!-- background-color="#545c64" -->
    <el-menu-item index="s1" @click="$router.push({path:'/'})">
      <i class="el-icon-s-home"></i>
    </el-menu-item>
    <el-menu-item
      :index="library.id.toString()"
      v-for="library in librarys"
      :key="'library_'+library.id"
      @click="goLibrary(library.id,library.lib_type)"
    >
    <i :key="'library_icon_'+library.id" :class="{'el-icon-picture':library.lib_type == 'photo','el-icon-film':library.is_video=library.lib_type == 'video','el-icon-headset':library.is_music=library.lib_type == 'music','el-icon-notebook-2':library.is_novel=library.lib_type == 'novel'}"></i>
      <span>{{library.name}}</span>
    </el-menu-item>
      <User  style="float:right" v-on:libraryChangeEvent="libraryChange"></User>
    <!-- <el-menu-item style="float:right">
      <ThumbSize></ThumbSize>
    </el-menu-item> -->
  </el-menu>
</template>
<script>
import User from "./User";
import ThumbSize from "./ThumbSize";
import axios from "axios";
export default {
  data() {
    return {
      librarys: [],
      default_active: null
    };
  },
  // watch: {
  //   $route(to, from) {
  //     this.default_active = this.$route.query.library_id.toString();
  //   }
  // },
  mounted() {
    this.libraryChange();
    
  },
  components: {
    User,
    ThumbSize
  },
  methods: {
    libraryChange() {
      axios.get("/api/library").then(response => {
        this.librarys  = response.data
        if (this.$route.query.library_id) {
                        this.default_active=this.$route.query.library_id
      // for(var i in this.librarys){
      //   if(this.librarys[i]['id']==this.$route.query.library_id){
      //     this.default_active=(Number(i)).toString()
      //   }
      
          
      // }
      //  = this.$route.query.library_id.toString();
    }
      });
    },
    goLibrary(libid,lib_type){
      if (lib_type=='photo'){
        this.$router.push({path:'/photos',query:{
                  library_id: libid,
                  dir_id:0,
                  page:1
              }})
      }
      if (lib_type=='novel'){
        this.$router.push({path:'/books',query:{
                  library_id: libid,
              }})
      }
      
    }
  }
};
</script>