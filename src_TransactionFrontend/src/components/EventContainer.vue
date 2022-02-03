<template>
  <div>

    <h4 class="mb-3">Event</h4>

    <TransactionItem
        v-for="i in bundle.MsgBundle"
        :key="i.ElementId"
        :ElementId=i.ElementId
        :ElementName=i.ElementName
        :ElementUniqueId=i.ElementUniqueId
        :TransactionType=i.TransactionType>

    </TransactionItem>

  </div>

</template>

<script>
import TransactionItem from "@/components/TransactionItem";

export default {
  name: "EventContainer",
  components: {
    TransactionItem
  },

  props: {
    bundle: Object,
  },

  // watch: {
  //   bundle: function (newval, oldval) {
  //     console.log("Changes in EventContainer: ");
  //     console.log(oldval);
  //     console.log(newval);
  //   }
  // },

  data() {
    return {

      transactionName: "TransactionName"
    }
  },

}
</script>

<style scoped>

</style>