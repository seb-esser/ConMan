<template>
  <div class="p-3 mb-2">
    <div class="row">
      <div class="col-10">
        <table class="table .table-sm table-bordered">
          <thead>
          <tr>
            <th>ElementId</th>
            <th>Name</th>
            <th>State</th>
          </tr>
          </thead>
          <tr>
            <th>{{ ElementId }}</th>
            <th>{{ ElementName }}</th>
            <th>{{ TransactionType }}</th>
          </tr>
        </table>
      </div>
            <div class="col-2 d-grid gap-2">
              <button class="btn btn-secondary btn-sm" @click="save">Map to IFC</button>

            </div>


    </div>
  </div>


</template>

<script>
export default {
  name: "TransactionItem",
  props: {
    ElementId: Number,
    ElementName: String,
    ElementUniqueId: String,
    TransactionType: String
  },

  data() {
    return {}
  }

}
</script>

<style scoped>

</style>