<template>
  <!-- <span> -->
  <i>
    <el-button-group>
      <el-button icon="el-icon-menu" @click="thumbSize(240)"></el-button>
      <el-button icon="el-icon-s-grid" @click="thumbSize(120)"></el-button>
    </el-button-group>
  </i>
</template>
<script>
export default {
    methods:{
        thumbSize(size){
            // 这里考虑两种大小，240（大）和120（小）
            // 纵横比直接 size*1.5
            this.$addStorageEvent(1,'thumbsize', size);
            // this.$router.go(0)
        }
    }
}
</script>