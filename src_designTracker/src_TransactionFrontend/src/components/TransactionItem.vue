<template>
  <div class="p-0">
    <p align="left">
    Id: {{ElementId}} - Name: {{ElementName}} TransactionType: {{TransactionType}} IfcGUID: {{IfcGuid}}
    </p>
  </div>
<!--  <div class="p-0 mb-2">-->
<!--    <div class="row">-->
<!--      <div class="col-10">-->
<!--        <table class="table .table-sm table-bordered">-->

<!--          <tr>-->
<!--            <th>{{ ElementId }}</th>-->
<!--            <th>{{ ElementName }}</th>-->
<!--            <th>{{ TransactionType }}</th>-->
<!--          </tr>-->
<!--        </table>-->
<!--      </div>-->
<!--    </div>-->
<!--  </div>-->


</template>

<script>
export default {
  name: "TransactionItem",
  props: {
    ElementId: {type: Number, default:0},
    ElementName: {type: String, default: "unknown", required: false},
    ElementUniqueId: {type: String, default: ""},
    TransactionType: {type: String, default: ""},
    IfcGuid: {type: String, default: "n/a"},
  },
  beforeMount: () => {
      if(this.ElementName.length === 0){
        this.ElementName = "unknown";
      }
  },

  data() {
    return {}
  }

}
</script>

<style scoped>

</style>