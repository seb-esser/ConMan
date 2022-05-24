import {createRouter, createWebHashHistory} from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import HomeView from "@/views/HomeView";

const routes = [
    {
        path: '/',
        name: 'HomeView',
        component: HomeView
    },
    {
        path: '/dashboard',
        name: 'DashboardView',
        component: DashboardView
    },
    {
        path: '/about',
        name: 'AboutView',
        // route level code-splitting
        // this generates a separate chunk (about.[hash].js) for this route
        // which is lazy-loaded when the route is visited.
        component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
    }
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export default router
