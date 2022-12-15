<template>
  <ModelViewer />
</template>

<script>
import { defineComponent } from 'vue';

// Components
// import HelloWorld from '../components/HelloWorld.vue';
import ModelViewer from '../components/ModelViewer.vue';

export default defineComponent({
  name: 'HomeView',

  components: {
    ModelViewer,
  },
});
</script>
