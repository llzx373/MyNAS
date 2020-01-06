<template>
  <!-- <span> -->
  <i>
    <el-button-group>
      <!-- <el-button icon="el-icon-user-solid" @click="show_userinfo=true" circle></el-button> -->
      <el-button style="height:60px;width:60px" icon="el-icon-s-tools" @click="show_library=true;" circle></el-button>
      <el-button style="height:60px;width:60px" icon="el-icon-close" @click="logout" circle></el-button>
    </el-button-group>
    <el-drawer
      name="library"
      :visible.sync="show_library"
      direction="rtl"
      :with-header="false"
      :show-close="true"
      size="40%"
    >
      <!-- <el-tabs v-model="tabName">
      <el-tab-pane label="资源库" name="library">-->
      <el-divider content-position="left">资源库</el-divider>
      <el-table :data="librarys">
        <el-table-column label="名称">
          <template slot-scope="scope">
            <el-link
              @click="changeLibraryName(scope.row.id)"
            >{{scope.row.name}}({{scope.row.status}})</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="lib_type" label="库类型"></el-table-column>
        <el-table-column prop="dir" label="根目录"></el-table-column>
        <el-table-column label="总数">
          <template slot-scope="scope">{{scope.row.count}}({{scope.row.next_count}})</template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button-group>
                <!-- {{scope.row}} -->
              <el-button v-if="scope.row.lib_type=='photo'" icon="el-icon-refresh-right" circle @click="flushLibrary(scope.row.id)"></el-button>
              <el-button icon="el-icon-delete-solid" circle @click="dropLibrary(scope.row.id)"></el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      <el-button-group style="width:100%">
        <el-button icon="el-icon-refresh-right" @click="getLibraryFull()" circle></el-button>
        <el-button icon="el-icon-plus" @click="show_new_library=true" circle></el-button>
        <!-- <el-button icon="el-icon-close" @click="logout" circle></el-button> -->
      </el-button-group>
      <el-divider content-position="left">用户设置({{username}})</el-divider>
      <el-form ref="userForm" :model="userForm" label-width="80px">
        <el-form-item label="密码">
          <el-input v-model="userForm.password" show-password></el-input>
        </el-form-item>
        <el-form-item label="新用户名">
          <el-input v-model="userForm.new_username"></el-input>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="userForm.new_password" show-password></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changeUser">修改用户</el-button>
        </el-form-item>
      </el-form>
    </el-drawer>
    <!-- 
     name: "",
        path: "",
        lib_type: "media",
        skip_dir: "",
        skip_file: "",
        support_file: ""
    -->
    <el-dialog title="新增" :visible.sync="show_new_library" width="30%">
      <el-form
        ref="newLibraryForm"
        :rules="newLibraryRules"
        :model="newLibraryForm"
        label-width="80px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="newLibraryForm.name"></el-input>
        </el-form-item>
        <el-form-item label="路径" prop="path">
          <el-input v-model="newLibraryForm.path"></el-input>
        </el-form-item>
        <el-form-item label="库类型" prop="lib_type">
          <el-radio-group v-model="newLibraryForm.lib_type" @change="changeLibraryType">
            <el-radio-button label="photo"></el-radio-button>
            <el-radio-button label="novel"></el-radio-button>
            <!-- <el-radio-button label="music"></el-radio-button> -->
            <!-- <el-radio-button label="video"></el-radio-button> -->
          </el-radio-group>
        </el-form-item>
        <!-- <el-form-item label="文件类型" prop="support_file">
          <el-input v-model="newLibraryForm.support_file"></el-input>
        </el-form-item>
        <el-form-item label="跳过目录" prop="skip_dir">
          <el-input v-model="newLibraryForm.skip_dir"></el-input>
        </el-form-item>
        <el-form-item label="跳过文件" prop="skip_file">
          <el-input v-model="newLibraryForm.skip_file"></el-input>
        </el-form-item> -->
        <el-form-item>
          <el-button type="primary" @click="newLibrary">新增库</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </i>
  <!-- </span> -->
</template>
<script>
import axios from "axios";
export default {
  name: "User",
  data() {
    return {
      show_library: false,
      show_new_library: false,
      librarys: [],
      tabName: "library",
      username: this.$cookies.get("username"),
      userForm: {
        password: "",
        new_username: this.$cookies.get("username"),
        new_password: ""
      },
      rules: {
        password: [{ required: true, message: "请输入密码", trigger: "blur" }],
        new_username: [
          { required: true, message: "请输入新的用户名", trigger: "blur" }
        ],
        new_password: [
          { required: true, message: "请输入新的密码", trigger: "blur" }
        ]
      },
      newLibraryForm: {
        name: "",
        path: "",
        lib_type: "",
        // skip_dir: "",
        // skip_file: "",
        // support_file: ""
      },
      newLibraryRules: {
        name: [{ required: true, message: "请输入名称", trigger: "blur" }],
        path: [{ required: true, message: "请输入库根路径", trigger: "blur" }],
        lib_type: [
          { required: true, message: "请选择库类型", trigger: "blur" }
        ],
        // support_file: [
        //   {
        //     required: true,
        //     message: "请输入支持的文件扩展名列表",
        //     trigger: "blur"
        //   }
        // ]
      }
    };
  },

  mounted() {
    
    this.getLibraryFull();
    if (this.timer) {
      clearInterval(this.timer);
    } else {
      this.timer = setInterval(() => {
        // 仅当前存在syncing时候执行
        if (this.show_library) {
          this.getLibraryFull();
        }
      }, 3000);
    }
  },
  destroyed() {
    clearInterval(this.timer);
  },
  methods: {
    handleClose(done) {
      this.show_library = false;
      done();
    },
    //
    getLibraryFull() {
      this.$emit("libraryChangeEvent");
      axios.get("/api/library?full=true").then(response => {
        this.librarys = response.data;
      });
    },
    flushLibrary(lib_id) {
      axios.get("/api/library/" + lib_id + "/sync").then(response => {
        this.$message(response.data.message);
      });
    },
    dropLibrary(lib_id) {
      axios.delete("/api/library/" + lib_id).then(response => {
        this.getLibraryFull();
        // var message = response.data.message;
        this.$message(response.data.message);
      });
    },
    changeLibraryType(val) {
      axios.get("/api/library/default_config").then(response => {
        var data = response.data;
        // this.newLibraryForm.skip_dir = data.skip_dir.toString();
        // this.newLibraryForm.skip_file = data.skip_file.toString();
        // this.newLibraryForm.support_file = data.supprot_file[val];
      });
    },
    newLibrary() {
      this.$refs.newLibraryForm.validate(valid => {
        if (valid) {
          axios
            .put("/api/library", {
              name: this.newLibraryForm.name,
              path: this.newLibraryForm.path,
              lib_type: this.newLibraryForm.lib_type
            })
            .then(response => {
                this.getLibraryFull();
                this.show_new_library=false;
                this.$message(response.data.message);
            });
        }
      });
      //   this.$prompt("请输入目录地址", "新增资料库地址", {
      //     confirmButtonText: "确定",
      //     cancelButtonText: "取消"
      //   }).then(({ value }) => {
      //     axios
      //       .put("/api/library", {
      //         name: value,
      //         path: value
      //       })
      //       .then(response => {
      //         this.getLibraryFull();
      //         this.$message(response.data.message);
      //       });
      //   });
    },
    changeLibraryName(lib_id) {
      //修改库名称 目前不考虑修改库路径
      this.$prompt("请输入新的库名称", "修改资源库名称", {
        confirmButtonText: "确定",
        cancelButtonText: "取消"
      }).then(({ value }) => {
        axios
          .post("/api/library/" + lib_id, {
            name: value
          })
          .then(response => {
            this.getLibraryFull();
            this.$message(response.data.message);
          });
      });
    },
    changeUser() {
      axios
        .post("/api/changeAuth", {
          username: this.username,
          password: this.userForm.password,
          new_username: this.userForm.new_username,
          new_password: this.userForm.new_password
        })
        .then(response => {
          this.$message(response.data.message);
          if (response.data.message == "修改用户成功") {
            this.$cookies.set("token", null);
            this.$cookies.set("username", null);
          }
          this.getLibraryFull();
        });
    },
    logout() {
      this.$cookies.set("token", null);
      this.$cookies.set("username", null), this.$router.push("/login");
    }
  }
};
</script>
