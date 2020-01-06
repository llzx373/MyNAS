<template>
  <div id="app">
    
    <Header v-if="!public_view"></Header>
    <!-- <el-container> -->
      <router-view />
      <!-- <el-footer style="text-align:right">MyNAS by llzx373</el-footer> -->
    <!-- </el-container> -->
  </div>
  
</template>
<script>
import Header from "./components/components/Header";
function startWith(str,head){
  var reg=new RegExp("^"+head);
  return reg.test(str);
}
export default {
  name: "App",
  data() {
    return {
      public_view: true
    };
  },
  watch: {
    $route(to, from) {
      this.public_view= (startWith(to.path,'/public') ||startWith(to.path,'/login'))
    }
  },
  mounted(){
    var path=this.$route.path;
    this.public_view= (startWith(path,'/public') ||startWith(path,'/login'))
  },
  components:{
    Header,
  }
};
</script>

<style>

	html {
overflow-y: scroll;
/* background-color:#dde0e2; */
}
</style>
