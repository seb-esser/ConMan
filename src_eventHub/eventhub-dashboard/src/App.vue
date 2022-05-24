<template>
  <v-app>

    <v-navigation-drawer>
      <!-- Header -->
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="text-h6">
            BIM-Event-Hub
          </v-list-item-title>
          <v-list-item-subtitle>
            version control for BIM models
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>


      <!-- the actual menu -->
      <v-divider></v-divider>

      <v-list>
        <v-list-item
            v-for="item in items"
            :key="item.title"
            router :to="item.route"
        >
          <v-list-item-content>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar app>
      <!-- -->
    </v-app-bar>

    <!-- Sizes your content based upon application components -->
    <v-main>

      <!-- Provides the application the proper gutter -->
      <v-container fluid>

        <!-- If using vue-router -->
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app>
      <!-- -->
    </v-footer>

  </v-app>
</template>

<script>

export default {
  name: 'App',

  data() {
    return {
      drawer: true,
      items: [
        //  This list controls the entries given in the left navigation bar.
        //  If adding a new item, remember to add a new route to the router as well.

        {title: 'Home', icon: 'mdi-view-home', route: "/"},
        {title: 'Dashboard', icon: 'mdi-view-dashboard', route: "/dashboard"},
        {title: 'About', icon: 'mdi-help-box', route: "/about"},
      ],
      right: null,
    }
  },
}
</script>
