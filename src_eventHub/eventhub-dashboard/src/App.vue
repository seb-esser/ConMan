<template>
  <div id="app" class="container my-5">
    <!--  <img alt="Vue logo" src="./assets/logo.png">-->
    <!--  <HelloWorld msg="Welcome to Your Vue.js App"/>-->
    <EventStream></EventStream>
  </div>
</template>

<script>
// import HelloWorld from './components/HelloWorld.vue'
import EventStream from "@/components/EventStream";

export default {
  name: 'App',
  components: {
    EventStream
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
