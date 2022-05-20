<template>
  <div id="app" class="container my-5">
    <!--    <img alt="Vue logo" src="./assets/logo.png">-->
    <h1 class="text-center">Transaction Tracker for Revit</h1>
    <TransactionBoard/>
  </div>
</template>

<script>
import TransactionBoard from "@/components/TransactionBoard";


export default {
  name: 'App',
  components: {
    TransactionBoard
  },

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
