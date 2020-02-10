<template>
  <div id="photo_pad" ref="photo_pad" style="position: fixed;top: 0;right: 0;bottom: 0;left: 0;">
    <!-- {{ photo }} -->
    <div class="photo_operation"
    >
      <el-button-group class="normal_operation">
        <el-button
          v-if="pre_dir"
          icon="el-icon-d-arrow-left"
          @click="toDir(pre_dir.library_id,pre_dir.id)"
        ></el-button>
        <el-button>{{photo.name}}({{photo.order_id+1}}/{{dir.count }})</el-button>
        <el-button
          v-if="next_dir"
          icon="el-icon-d-arrow-right"
          @click="toDir(next_dir.library_id,next_dir.id)"
        ></el-button>
        <el-button icon="el-icon-picture" v-if="origin==1" @click="setOrigin(0)" name="origin_show"></el-button>
        <el-button
          icon="el-icon-picture-outline"
          v-if="origin!=1"
          @click="setOrigin(1)"
          name="compress_show"
        ></el-button>
        <el-button icon="el-icon-full-screen" @click="switch_fullscreen()"></el-button>
        <el-button
          icon="el-icon-reading"
          v-if="double_page"
          @click="setDouble(false)"
          name="origin_show"
        ></el-button>
        <el-button
          icon="el-icon-mobile"
          v-if="!double_page"
          @click="setDouble(true)"
          name="origin_show"
        ></el-button>
         <el-button
          v-if="!read_right"
          @click="read_right=true"
        >从左向右读</el-button>
        <el-button
          v-if="read_right"
          @click="read_right=false"
        >从右向左读</el-button>
       
      </el-button-group>
       <el-button icon="el-icon-close" @click="toDir(dir.library_id,dir.id)"></el-button>
    </div>
    
    <div
      v-if="photo.pre"
      style="position: absolute;top:50%;left:0%; height:80%; width:50% ;background:rgba(0, 0, 0, 0) ;display: flex;transform: translateY(-50%); cursor: url('/static/bt_prev.png'),pointer;"
      @click="prePhoto"
    >
      <button
        class="pre_next"
        style="position: absolute;top:50%; width: 48px;height: 64px;background:rgba(0, 0, 0, 0) url('/static/bt_prev.png');display: flex;transform: translateY(-50%);border: none;cursor: url('/static/bt_prev.png'),pointer;"
        v-if="photo.pre"
        @click="prePhoto"
      ></button>
    </div>
    <div
      v-if="photo.next"
      style="position: absolute;top:50%;right:0%; height:80%; width:50% ;background:rgba(0, 0, 0, 0);display: flex;transform: translateY(-50%);cursor: url('/static/bt_next.png'),pointer;"
      @click="nextPhoto"
    >
      <button
        class="pre_next"
        style="position: absolute;top:50%;right:0%;  width: 48px;height: 64px;background:rgba(0, 0, 0, 0) url('/static/bt_next.png') no-repeat scroll;display: flex;transform: translateY(-50%);border: none;cursor:url('/static/bt_next.png'),pointer;"
        v-if="photo.next"
        @click="nextPhoto"
      ></button>
    </div>

    <!-- </div> -->

    <div  v-if="!read_right"
      style="position: static; width: 100%;height: 100%;display: flex;justify-content: center;align-items: center;background-color:#4C5061;"
    >
      <!-- <transition :name="slide"  class="mainimg" > -->

            <img key='cur' id="mm" v-show="show" :src="photo_src" @load="loadIMG()" class="mainimg"/>
      <img key='next'  v-show="next&&double_page&&show" :src="getNextPhotoFile(next)" class="mainimg"/>

      <!-- </transition> -->
    </div>
     <div v-if="read_right"
      style="position: static; width: 100%;height: 100%;display: flex;justify-content: center;align-items: center;background-color:#4C5061;"
    >
      <!-- <transition :name="slide"  class="mainimg" > -->
        <img key='next'  v-show="next&&double_page&&show" :src="getNextPhotoFile(next)" class="mainimg"/>
            <img key='cur' id="mm" v-show="show" :src="photo_src" @load="loadIMG()" class="mainimg"/>
      

      <!-- </transition> -->
    </div>
  </div>
</template>
<script>
// import { slider, slideritem } from 'vue-concise-slider';
import axios from "axios";
import { rafThrottle, isFirefox } from "element-ui/src/utils/util";
import { on, off } from "element-ui/src/utils/dom";
export default {
  name: "Photo",
  data() {
    return {
      photo: {},
      photo_src: "",
      dir: {},
      pre: null,
      next: null,
      pre_dir: null,
      next_dir: null,
      origin: 0,
      show: false,
      cache: null,
      next_cache: null,
      cache_url: "",
      slide: "slideRight",
      is_next: false,
      double_page: false,
      read_right:false,
      full_screen:false
    };
  },
  mounted() {
    this.getPhoto();
    this.keyBoardInstall();
  },
  beforeDestroy() {
    this.keyBoardunInstall();
  },
  methods: {
    switch_fullscreen(){

      if (this.full_screen){
        this.full_screen=false
        // console.log(element)
        this.$refs.photo_pad.ownerDocument.exitFullscreen();
        //  Document
      }else{
        this.full_screen=true
        this.$refs.photo_pad.requestFullscreen()
      }
    },
    getNextPhotoFile(next) {
      if (next != null) {
        return this.getPhotoFile(next.id);
      } else {
        return "/";
      }
    },
    loadIMG() {
      // if (this.slide==  "slideLeft"){
      //   45this.slide="slideRight"
      // }
      if (!this.is_next) {
        this.slide = "slideLeft";
      } else {
        this.slide = "slideRight";
      }
      this.show = true;
    },
    getPhotoFile(photo_id) {
      var url = "";
      this.origin = this.$cookies.get("origin");
      if (this.origin == 1) {
        url = this.$cookies.get('hostname')+"/api/media/" + photo_id + "?cache=origin";
      } else {
        url = this.$cookies.get('hostname')+"/api/media/" + photo_id + "?cache=false";
      }
      // return url
      // 这里视图走localstorage，但大小太过受限，无法处理
      return this.getCache(url);
    },
    getPhoto() {
      let photo_id = this.$route.query.photo_id;
      axios.get("/api/file/" + photo_id + "?full=true").then(response => {
        this.photo = response.data;
        this.dir = this.photo.dir;
        this.pre = this.photo.pre;
        this.next = this.photo.next;
        this.pre_dir = this.photo.pre_dir;
        this.next_dir = this.photo.next_dir;
        this.photo_src = this.getPhotoFile(this.photo.id);
        if (this.next_photo) {
          this.nextCache(this.getPhotoFile(this.next_photo.id));
        }
        document.title = this.dir.name;
      });
    },
    nextPhoto() {
      this.slide = "slideLeft";
      this.is_next = true;
      this.show = false;
      //这里单独判断应该去文件夹还是文件

      var photo_route_to = null;
      if (this.next.item_type == "file") {
        //对于double page，继续走一页
        if (this.double_page && this.next != null) {
          axios
            .get("/api/file/" + this.next.id + "?full=true")
            .then(response => {
              var next = response.data;
              if (next.next) {
                this.$router.push({
                  path: "/photo",
                  query: {
                    photo_id: next.next.id
                  }
                });
                this.getPhoto();
              } else {
                this.$router.push({
                  path: "/photo",
                  query: {
                    photo_id: this.photo.next.id
                  }
                });
                this.getPhoto();
              }
            });
        } else {
          this.$router.push({
            path: "/photo",
            query: {
              photo_id: this.next.id
            }
          });
          this.getPhoto();
        }
      } else {
        this.$router.push({
          path: "/photos",
          query: {
            library_id: this.next.library_id,
            dir_id: this.next.id,
            page: 1
          }
        });
      }
    },
    prePhoto() {
      if (this.pre.item_type == "file") {
        this.slide = "slideRight";
        this.is_next = false;
        this.show = false;
        //对于double page，继续走一页
        var photo_route_to = null;
        if (this.double_page && this.pre != null) {
          axios
            .get("/api/file/" + this.pre.id + "?full=true")
            .then(response => {
              var pre = response.data;
              if (pre.pre) {
                this.$router.push({
                  path: "/photo",
                  query: {
                    photo_id: pre.pre.id
                  }
                });
                this.getPhoto();
              } else {
                this.$router.push({
                  path: "/photo",
                  query: {
                    photo_id: this.pre.id
                  }
                });
                this.getPhoto();
              }
            });
        } else {
          this.$router.push({
            path: "/photo",
            query: {
              photo_id: this.pre.id
            }
          });
          this.getPhoto();
        }
        
      } else {
        this.$router.push({
          path: "/photos",
          query: {
            library_id: this.pre.library_id,
            dir_id: this.pre.id,
            page: 1
          }
        });
      }
    },
    toDir(library_id, dir_id) {
      // 如果目录存在文件，则跳转到第一个文件，否则跳到目录
      // 如果是当前目录，跳转到当前目录
      if (dir_id == this.dir.id) {
        this.$router.push({
          path: "/photos",
          query: {
            library_id: library_id,
            dir_id: dir_id
          }
        });
      } else {
        axios
          .get(
            "/api/library/" + library_id + "/" + dir_id + "?items_per_page=1"
          )
          .then(response => {
            var dir = response.data;
            if (dir.item_count > 0) {
              this.$router.push({
                path: "/photo",
                query: {
                  photo_id: dir.items[0].id
                }
              });
              this.slide = "zoom";
              this.show = false;
              this.getPhoto();
            } else {
              this.$router.push({
                path: "/photos",
                query: {
                  library_id: library_id,
                  dir_id: dir_id
                }
              });
            }
          });
      }

      // location.reload();
      // this.$router.go(0);
    },
    setOrigin(val) {
      this.$cookies.set("origin", val);
      this.origin = val;
      this.getPhoto();
    },
    setDouble(val) {
      this.double_page = val;
      this.getPhoto();
    },
    keyBoardInstall() {
      this._keyDownHandler = rafThrottle(e => {
        const keyCode = e.keyCode;
        switch (keyCode) {
          case 27: //ESC
            this.toDir(this.dir.library_id, this.dir.id);
            break;
          case 37: //PRE 左方向键
            this.prePhoto();
            break;
          case 39: //NEXT 右方向键
            this.nextPhoto();
            break;
                    }
      });
      on(document, "keydown", this._keyDownHandler);
    },
    keyBoardunInstall() {
      off(document, "keydown", this._keyDownHandler);
    },
    getCache(url) {
      var cached_url = localStorage.getItem("cached_url");
      var img = document.getElementById("main_img");
      if (cached_url) {
        if (cached_url == url) {
          // 如果缓存命中，直接返回cache
          this.cache = this.next_src;
          // localStorage.setItem("next_src",null);
          return this.cache;
        }
      }
      return url;
    },
    nextCache(url) {
      var xhr = new XMLHttpRequest();
      var filereader = new FileReader();
      xhr.open("GET", url, true);
      xhr.responseType = "blob";
      xhr.addEventListener("load", () => {
        if (xhr.status === 200) {
          var blob = xhr.response;
          filereader.onload = function(evt) {
            var result = evt.target.result;
            try {
              this.next_cache = result;
              this.cache_url = url;
              // localStorage.setItem("next_src", result);
              // localStorage.setItem("cached_url", url);
            } catch (e) {
              console.log(url + " storage failed:" + e);
            }
          };
          filereader.readAsDataURL(blob);
        }
      });
      xhr.send();
    }
  }
};
</script>
<style scoped >

.mainimg {
  margin-top: 0px;
  max-height: 100%;
  max-width:100%;
  box-shadow: 0 0px 32px 0 #282a32;
}
.photo_operation{
  position: absolute;top:0%;right:0%;background-color:rgba(0, 0, 0, 0) ;display: flex;
}

.photo_operation:hover{
  opacity: 1;
}
.normal_operation{
  opacity: 0.2;
}
.normal_operation:hover{
  opacity: 1;
}

</style>