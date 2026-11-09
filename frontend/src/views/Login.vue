<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center auth-bg">
    <div class="card auth-card shadow-lg">
      <div class="card-body p-5">

        <div class="text-center mb-4">
          <div class="logo-icon mb-3"></div>
          <h2 class="fw-bold text-white">Placement Portal</h2>
          <p class="text-muted">Sign in to your account</p>
        </div>

        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

        <div class="mb-3">
          <label class="form-label text-light">Username</label>
          <input v-model="username" type="text" class="form-control custom-input" placeholder="Enter username" />
        </div>

        <div class="mb-4">
          <label class="form-label text-light">Password</label>
          <input v-model="password" type="password" class="form-control custom-input" placeholder="Enter password" />
        </div>

        <button @click="login" :disabled="loading" class="btn btn-orange w-100 fw-bold py-2">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>

        <p class="text-center text-muted mt-4 mb-0">
          Don't have an account?
          <router-link to="/register" class="text-orange">Register here</router-link>
        </p>

      </div>
    </div>
  </div>
</template>

<script>
import axios from '../axios'

export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false
    }
  },
  methods: {
    async login() {
      if (!this.username || !this.password) {
        this.error = 'Please enter username and password'
        return
      }
      this.loading = true
      this.error = ''
      try {
        const res = await axios.post('/auth/login', {
          username: this.username,
          password: this.password
        })
        localStorage.setItem('token', res.data.access_token)
        localStorage.setItem('role', res.data.role)
        localStorage.setItem('username', res.data.username)

        if (res.data.role === 'admin') this.$router.push('/admin')
        else if (res.data.role === 'company') this.$router.push('/company')
        else this.$router.push('/student')

      } catch (err) {
        this.error = err.response?.data?.message || 'Login failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.auth-bg {
  background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
}
.auth-card {
  width: 100%;
  max-width: 420px;
  background: #1e1e2e;
  border: 1px solid #3a3a5c;
  border-radius: 16px;
}
.logo-icon {
  font-size: 48px;
}
.custom-input {
  background: #2a2a3e;
  border: 1px solid #3a3a5c;
  color: #ffffff;
}
.custom-input:focus {
  background: #2a2a3e;
  border-color: #f97316;
  color: #ffffff;
  box-shadow: 0 0 0 0.2rem rgba(249, 115, 22, 0.25);
}
.btn-orange {
  background: linear-gradient(135deg, #f97316, #ea580c);
  border: none;
  color: white;
}
.btn-orange:hover {
  background: linear-gradient(135deg, #ea580c, #c2410c);
  color: white;
}
.text-orange {
  color: #f97316;
  text-decoration: none;
  font-weight: 600;
}
</style>