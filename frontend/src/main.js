import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Import views
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import AdminDashboard from './views/AdminDashboard.vue'
import CompanyDashboard from './views/CompanyDashboard.vue'
import StudentDashboard from './views/StudentDashboard.vue'

// Setup routes
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/admin', component: AdminDashboard, meta: { role: 'admin' } },
    { path: '/company', component: CompanyDashboard, meta: { role: 'company' } },
    { path: '/student', component: StudentDashboard, meta: { role: 'student' } },
  ]
})

// Route guard - protect pages based on role
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (to.path === '/login' || to.path === '/register') {
    next()
    return
  }

  if (!token) {
    next('/login')
    return
  }

  if (to.meta.role && to.meta.role !== role) {
    next('/login')
    return
  }

  next()
})

const app = createApp(App)
app.use(router)
app.mount('#app')