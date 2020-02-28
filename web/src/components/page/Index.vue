<template>
  <LibraryView></LibraryView>
</template>

<script>
import axios from "axios";
import LibraryView from "../components/LibraryView";
export default {
  name: "Index",
  data() {
    return {
    };
  },
  components: {
   LibraryView
  },
  mounted() {
      document.title = "MyNAS首页";
  }
};
</script>
