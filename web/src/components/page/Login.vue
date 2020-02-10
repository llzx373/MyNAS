<template>
  <div class="loginBackground">
    
    <div class="loginDialog"><h3 class="loginTitle">MyNAS by llzx373</h3>
      <el-form :model="loginForm" ref="loginForm" :rules="rules">
        <el-form-item prop="hostname">
          <el-input type="text" v-model="loginForm.hostname" placeholder="服务器地址"></el-input>
        </el-form-item>
        <el-form-item prop="username">
          <el-input type="text" v-model="loginForm.username" placeholder="用户名"></el-input>
        </el-form-item>
        <el-form-item  prop="password">
          <el-input v-model="loginForm.password" placeholder="密码" show-password></el-input>
        </el-form-item>
        <el-form-item>
          <el-button style="float:right" type="primary" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>
<script>
import axios from "axios";
function vailUsername(rule, value, callback) {
  //为了避免sql注入 用户名仅允许字母数字组合
  // 密码不需要校验，密码进入sql前，会进行加盐md5处理
  var reg = /^[A-Za-z0-9]{1,30}$/;
  if (reg.test(value)) {
    callback();
  } else {
    callback(new Error("用户名仅允许字母数字组合"));
  }
}
export default {
  name: "Login",
  data() {
    return {
      loginForm: {
        username: "",
        password: "",
        hostname:this.$cookies.get("hostname")
      },
      rules: {
        username: [
          { required: true, message: "请输入用户名", trigger: "blur" },
          {
            validator: vailUsername,
            message: "用户名仅允许字母数字组合",
            trigger: "blur"
          }
        ],
        password: [{ required: true, message: "请输入密码", trigger: "blur" }]
      }
    };
  },
  methods: {
    handleLogin() {
      document.title="登录页面"
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          let form = this.loginForm;
          this.loading = true;
          var hostname=form.hostname;
          if (hostname==null ||hostname==''){
            hostname=window.location.protocol+"//"+window.location.hostname+":"+window.location.port
            console.log(hostname)
          }
          this.$cookies.set("hostname",hostname)
          axios.post("/api/login", {
              
              username: form.username,
              password: form.password
            }).then(response => {
              if (response.data.token) {
                this.$cookies.set("token", response.data.token);
                this.$cookies.set("username", form.username);
                this.$router.push("/");
              } else {
                this.$message({
                  type: "info",
                  message: "用户名或密码错误"
                });
                this.loading = false;
              }
            });
        } else {
          this.$message({
            type: "info",
            message: "用户名或密码错误"
          });
        }
      });
    }
  }
};
</script>
<style>
.loginBackground {
  margin: 0 auto;
  background-color: rgba(0,0,0,.85);
  position: fixed;top: 0;right: 0;bottom: 0;left: 0;
  align-items: center;
}
.loginTitle{
  color: rgba(255,255,255,.5);
  text-align:center;
}
.loginDialog {
  position: absolute;
  
  left: 50%;
  top: 50%; 
  transform: translate(-50%,-50%);
  
  background: linear-gradient(to bottom,#444,#333);
  padding: 35px 35px 15px 35px;
  width: 320px;
}
</style>