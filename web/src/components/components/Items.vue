<template>
  <table style="width:100%; border-spacing: 10px;border-collapse: separate;">
    <tr v-for="(row,index) in rows" :key="'row_'+index">
      <td v-for="col in row" :key="'col_'+col.id" style="border-spacing: 0px;">
          <el-card
            style="max-width:100%"
            class="item"
            :body-style="{ padding: '0px'}"
            :shadow="'always'"
            v-if="col.item_type=='dir'"
          >
            <el-image
              fit="contain"
           
              :style="'width:100%;cursor:pointer'"
              :src="'/api/media/'+col.cover"
              @click="$router.push({path:'/photos',query:{
                  library_id: col.library_id,
                  dir_id:col.id,
                  tab:'dir_view'
              }})"
            ></el-image>
            <div class="bottom">
              <el-link
               :href="'/#/photos?library_id='+col.library_id+'&dir_id='+col.id+'&tab=dir_view'"
               type="primary"
                icon="el-icon-folder-opened"
                @click="$router.push({path:'/photos',query:{
                  library_id: col.library_id,
                  dir_id:col.id,
                  tab:'dir_view'
              }})"
                :style="'width:100%'"
              >{{ col.name }}</el-link>
            </div>
          </el-card>
          <el-card
            class="item"
            :body-style="{ padding: '0px' }"
            :shadow="'always'"
            v-if="col.item_type=='file'"
          >
            <el-image
              fit="contain"
            
              :style="'width:240px;cursor:pointer'"
              :src="'/api/media/'+col.id"
              @click="goMedia(col)"
            ></el-image>
            <div class="bottom">
              <el-link
                icon="el-icon-picture"
                @click="goMedia(col)"
                type="primary"
                :style="'width:100%;'"
              >{{ col.name }}</el-link>
            </div>
          </el-card>
          <BookCover :chapter="col" :width="width" :height="height"></BookCover>
      </td>
    </tr>
  </table>
</template>
<script>
import BookCover from "./BookCover";
export default {
  name: "Items",
  props: ["items", "screenWidth"],
  data() {
    return {
      rows: [],
      row_span: 1,
      width: 250,
      height: 320,
      cols_in_row: 12
    };
  },
  components: {
    BookCover
  },
  mounted() {
    var thumbsize = localStorage.getItem("thumbsize");
    if (thumbsize) {
      this.width = thumbsize;
      this.innerChangeWidth(thumbsize);
    }
    window.addEventListener("setItem", this.changeWidth);

    this.resize();
  },
  beforeDestroy() {
    window.removeEventListener("setItem", this.changeWidth);
  },
  watch: {
    items(val) {
      this.items = val;
      this.resize();
    },
    screenWidth(val) {
      this.screenWidth = val;
      this.resize();
    }
    // $route(to, from) {
    //   location.reload();
    //   // this.$router.go(0);
    // }
  },
  methods: {
    goMedia(media) {
      var id = media.id;
      var name = media.name;
      // 这里根据后缀名判断去向
      var ptype = name.split(".").pop();
      var file_type=media.file_type
      // var medias = new Array("mp4", "avi", "mkv");
      if (file_type == 'photo') {
        this.$router.push({
          path: "/photo",
          query: {
            photo_id: id
          }
        });
      } else {
        this.$router.push({
          path: "/video",
          query: {
            video_id: id
          }
        });
      }
    },
    resize() {
      var cols_in_row = parseInt(this.screenWidth / this.width);
      if (cols_in_row > 24) {
        cols_in_row = 24;
      }
      this.cols_in_row = cols_in_row;
      this.row_span = parseInt(24 / cols_in_row);
      var rows = new Array();
      var row = new Array();
      for (var i = 0; i < this.items.length; i++) {
        if ((i % cols_in_row == 0) & (i != 0)) {
          rows.push(row);
          row = [];
        }
        row.push(this.items[i]);
      }
      rows.push(row);
      this.rows = rows;
      console.log("cols_in_row",cols_in_row,this.screenWidth)
    },
    changeWidth(e) {
      this.width = e.newValue;
      this.innerChangeWidth();
    },
    innerChangeWidth(width) {
      this.height = (this.width / 3) * 4;
    }
  }
};
</script>
<style>
table {
  border-collapse: collapse;
  border: 0px solid black;
}
td {
  border: 0px solid black;
}
.item {
  /* box-shadow: 0 0px 5px 0 #282a32; */
  width: 240px;
}
.item:hover {
  /* transform: scale(1.1);  */
  z-index: 1000;
  box-shadow: 0 0px 10px 0 #282a32;
}
</style>