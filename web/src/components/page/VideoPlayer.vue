<template>
  <div style="position: fixed;top: 0;right: 0;bottom: 0;left: 0;">
    <div
      id="mouse_info"
      @mouseenter="enter_bar"
      @mouseleave="leave_bar"
      @mousedown="click_bar"
      v-if="ffmpeg.onbar"
      :style="'z-index:3000;width:1px;top: 80%;height:28px;text-align:center;line-height: 28px;position: fixed;left:'+ffmpeg.mouse.x+'px;background-color:#4C5061'"
    >
      <!-- <div style="background-color:#4C5061'">{{ffmpeg.mouse.time|formatTime}}</div> -->
    </div>

    <div
      style="position: absolute;top:0%;right:0%;background-color:rgba(0, 0, 0, 0) ;display: flex;z-index:2000"
    >
      <el-button-group>
        <el-button icon="el-icon-info" @click="show_info=true"></el-button>
        <el-button v-if="!ffmpeg.use" @click="switch_to_ffmpeg()">HTML5</el-button>
        <el-button v-if="ffmpeg.use" @click="switch_to_html5()">FFMPEG</el-button>
        <el-button
          icon="el-icon-close"
          @click="$router.push({
          path: '/photos',
          query: {
            library_id: video_src.library_id,
            dir_id: video_src.parent,
            page: 1
          }
        })"
        ></el-button>
      </el-button-group>
      <el-dialog title="提示" :visible.sync="show_info" width="30%" :modal="false">
        <a
          :href="$cookies.get('hostname')+'/api/media/' + $route.query.video_id + '?cache=origin'"
        >{{this.video_src.name}}</a>
        <span>{{video_info}}</span>
      </el-dialog>
    </div>
    <div v-if="player&&ffmpeg.use" class="customProcessBar">
      <el-button-group v-if="ffmpeg.use" style="width:90px">
        <el-button
          size="mini"
          icon="el-icon-video-play"
          v-if="!ffmpeg.playing"
          @click="switch_start_pause()"
        ></el-button>
        <el-button
          size="mini"
          icon="el-icon-video-pause"
          v-if="ffmpeg.playing"
          @click="switch_start_pause()"
        ></el-button>
        <el-button size="mini" icon="el-icon-full-screen" @click="switch_fullscreen()"></el-button>
      </el-button-group>
      <div style="height: 28px;background-color:#ffffff">
        <div
          style="width:720px;height:100%"
          @mousemove="over_bar"
          @mouseleave="leave_bar"
          @mouseenter="enter_bar"
          @mousedown="click_bar"
        >
          <div
            :style="'height:100%;width:'+720.0*(player.currentTime()+ffmpeg.start)/ffmpeg.total+'px;background-color:#4C5061'"
          ></div>
          <div
            v-if="ffmpeg.onbar"
            :style="'z-index:3000;width:100px;height:28px;text-align:center;line-height: 28px;position: fixed;left:'+ffmpeg.mouse.timex+'px;background-color:#4C5061'"
          >
            <div style="background-color:#4C5061'">{{ffmpeg.mouse.time|formatTime}}</div>
          </div>
        </div>
      </div>
      <div
        style="width:100px;background-color:#282a32;color:white;text-align:center;line-height: 28px;"
      >- {{ffmpeg.total-(player.currentTime()+ffmpeg.start)|formatTime}}</div>
      <el-slider
        input-size="mini"
        @change="switch_volume()"
        style="height:28px;width:100px;background-color:gray"
        v-model="ffmpeg.volume"
      ></el-slider>
    </div>
    <div
      style="position: static; width: 100%;height: 100%;display: flex;justify-content: center;align-items: center;background-color:#4C5061;"
    >
      <video
        style="margin-top: 0px; height: 100%;
  width:100%;box-shadow: 0 0px 32px 0 #282a32;"
        ref="videoPlayer"
        class="video-js"
      ></video>
      <!-- <video
        style="margin-top: 0px; height: 100%;
  width:100%;box-shadow: 0 0px 32px 0 #282a32;"
      :src="this.$cookies.get('hostname')+'/api/media/' + this.$route.query.video_id + '?cache=origin'"
        controls="controls"
      ></video>-->
    </div>
  </div>
</template>

<script>
// 新增ffmpeg后端解码的播放器，处理网页无法支持的视频
// 后端接口为两个:
// 1 获取视频信息并发起解码的/api/video/hls/<video_id> 单纯获取视频信息的 /api/video/<video_id>
// 2 返回文件的/api/video/hls/<filename>
// 视频播放采用hls协议
// 播放器实现为：取消videojs原生控制组件，另外单独写
// 进度条功能：播放/暂停 声音控制 进度条：已经播放时长/已经编码时长/总时长

import axios from "axios";
import videojs from "video.js";
import "videojs-flash";
import "flv.js";
import "../components/videojs-flvjs.js";
export default {
  name: "VideoPlayer",
  data() {
    return {
      video_src: {},

      player: null,
      options: {
        controls: true,
        autoplay: false,
        techOrder: [, "html5", "Flvjs"]
      },
      show_info: false,
      video_info: "",
      ffmpeg: {
        use: false,
        playing: false,
        start: 0,
        total: 0,
        volume: 100,
        onbar: false,
        mouse: {
          time: 0,
          x: 0,
          y: 0,
          timex: 0
        }
      }
    };
  },
  mounted() {
    this.getVideo();
    // this.switch_to_ffmpeg();
  },
  beforeDestroy() {
    if (this.player) {
      this.player.dispose();
    }
  },
  filters: {
    formatTime(time) {
      // 这里假设最大单位是小时，不假设天级别计数单位
      //入参是毫秒总数，计时忽略毫秒
      var h = time / 3600;
      var m = (time % 3600) / 60;
      var s = time % 60;

      return Math.floor(h) + ":" + Math.floor(m) + ":" + Math.floor(s);
    }
  },
  methods: {
    over_bar(event) {
      this.ffmpeg.mouse.x = event.clientX;
      this.ffmpeg.mouse.timex = event.layerX - 50;
      this.ffmpeg.mouse.time = (this.ffmpeg.total * (event.layerX - 90)) / 720;
    },
    enter_bar(event) {
      this.ffmpeg.onbar = true;
    },
    leave_bar(event) {
      this.ffmpeg.onbar = false;
    },
    click_bar(event) {
      this.ffmpeg_play_from(this.ffmpeg.mouse.time);
    },
    ffmpeg_play_from(start) {
      let video_id = this.$route.query.video_id;
      axios
        .get("/api/video/hls/" + video_id + "?start=" + start)
        .then(response => {
          this.ffmpeg.start = start;
          this.player.controls(false);
          console.log("hide")
          // console.log(this.$refs.videoPlayer)
          this.player.src([
            {
              src: this.$cookies.get("hostname") + "/api/video/hls/index.m3u8",
              type: "application/x-mpegURL"
            }
          ]);
          this.player.ready(() => {
            this.ffmpeg.volume = this.player.volume() * 100;
            if (this.ffmpeg.playing) {
              this.player.play();
            }
          });
        });
    },
    switch_fullscreen() {
      if (this.player.isFullscreen()) {
        this.player.exitFullscreen();
      } else {
        this.player.requestFullscreen();
      }
    },
    switch_volume() {
      this.player.volume(this.ffmpeg.volume / 100.0);
    },
    switch_start_pause() {
      if (this.player.paused()) {
        this.player.play();
        this.ffmpeg.playing = true;
      } else {
        this.player.pause();
        this.ffmpeg.playing = false;
      }
    },
    switch_to_ffmpeg() {
      this.ffmpeg.use = true;
      let video_id = this.$route.query.video_id;
      axios.get("/api/video/" + video_id).then(response => {
        this.ffmpeg.total = response.data.duration;
        this.ffmpeg.start = 0;
        this.ffmpeg_play_from(0);
      });
    },
    switch_to_html5() {
      let video_id = this.$route.query.video_id;
      this.ffmpeg.use = false;
      axios.get("/api/file/" + video_id).then(response => {
        this.video_src = response.data;
      });
      this.player.userActive(true);
      this.player.src([
        {
          src:
            this.$cookies.get("hostname") +
            "/api/media/" +
            this.$route.query.video_id +
            "?cache=origin",
          type: this.video_src.mimetypes
        }
      ]);
    },
    show_video_info() {
      this.$alert(this.video_info, "视频信息", {
        confirmButtonText: "确认",
        callback: action => {}
      });
    },
    getVideo() {
      let video_id = this.$route.query.video_id;
      axios.get("/api/file/" + video_id).then(response => {
        this.video_src = response.data;

        document.title = this.video_src.name;
        this.options.sources = [
          {
            src:
              this.$cookies.get("hostname") +
              "/api/media/" +
              this.$route.query.video_id +
              "?cache=origin",
            type: this.video_src.mimetypes
          }
        ];
        this.player = videojs(this.$refs.videoPlayer, this.options);
        axios.get("/api/file/" + video_id + "/video_info").then(response => {
          this.video_info = response.data.video_info;
        });
      });
    }
  }
};
</script>
<style>
.customProcessBar {
  position: absolute;
  top: 80%;
  left: 50%;
  background-color: rgba(0, 0, 0, 0);
  display: flex;
  z-index: 2000;
  opacity: 1;
  transform: translateX(-50%);
}
.customProcessBar:hover {
  opacity: 1;
}
</style>