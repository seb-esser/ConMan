<template>
  <div class="border border-secondary">

    <h4 class="m-0"><p align="left">Event</p></h4>

    <TransactionItem
        v-for="{ElementId, ElementName, ElementUniqueId, TransactionType, IfcGuid} in bundle.MsgBundle"
        :key="ElementId"
        :ElementId=ElementId
        :ElementName=ElementName
        :ElementUniqueId=ElementUniqueId
        :TransactionType=TransactionType
        :IfcGuid=IfcGuid
    >

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