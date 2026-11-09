<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center auth-bg py-5">
    <div class="card auth-card shadow-lg">
      <div class="card-body p-5">

        <div class="text-center mb-4">
          <div class="logo-icon mb-3"></div>
          <h2 class="fw-bold text-white">Create Account</h2>
          <p class="text-muted">Register as Student or Company</p>
        </div>

        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
        <div v-if="success" class="alert alert-success py-2">{{ success }}</div>

        <!-- Role Selection -->
        <div class="mb-4">
          <label class="form-label text-light">I am a</label>
          <div class="d-flex gap-3">
            <button @click="role = 'student'" :class="['btn w-50 role-btn', role === 'student' ? 'role-active' : 'role-inactive']">
              Student
            </button>
            <button @click="role = 'company'" :class="['btn w-50 role-btn', role === 'company' ? 'role-active' : 'role-inactive']">
              Company
            </button>
          </div>
        </div>

        <!-- Common Fields -->
        <div class="mb-3">
          <label class="form-label text-light">Username</label>
          <input v-model="form.username" type="text" class="form-control custom-input" placeholder="Enter username" />
        </div>

        <div class="mb-3">
          <label class="form-label text-light">Email</label>
          <input v-model="form.email" type="email" class="form-control custom-input" placeholder="Enter email" />
        </div>

        <div class="mb-3">
          <label class="form-label text-light">Password</label>
          <input v-model="form.password" type="password" class="form-control custom-input" placeholder="Enter password" />
        </div>

        <!-- Student Fields -->
        <template v-if="role === 'student'">
          <div class="mb-3">
            <label class="form-label text-light">Full Name</label>
            <input v-model="form.full_name" type="text" class="form-control custom-input" placeholder="Enter full name" />
          </div>
          <div class="row">
            <div class="col mb-3">
              <label class="form-label text-light">Branch</label>
              <select v-model="form.branch" class="form-select custom-input">
                <option value="" disabled>Select Branch</option>
                <option value="Computer Science">Computer Science</option>
                <option value="Electronics">Electronics</option>
                <option value="Electrical">Electrical</option>
                <option value="Mechanical">Mechanical</option>
                <option value="Civil">Civil</option>
                <option value="Chemical">Chemical</option>
                <option value="Biotechnology">Biotechnology</option>
              </select>
            </div>
            <div class="col mb-3">
              <label class="form-label text-light">Year</label>
              <input v-model="form.year" type="number" class="form-control custom-input" placeholder="e.g. 3" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label text-light">CGPA</label>
            <input v-model="form.cgpa" type="number" step="0.1" class="form-control custom-input" placeholder="e.g. 8.5" />
          </div>
          <div class="mb-3">
            <label class="form-label text-light">Phone</label>
            <input v-model="form.phone" type="text" class="form-control custom-input" placeholder="Enter phone number" />
          </div>
        </template>

        <!-- Company Fields -->
        <template v-if="role === 'company'">
          <div class="mb-3">
            <label class="form-label text-light">Company Name</label>
            <input v-model="form.company_name" type="text" class="form-control custom-input" placeholder="Enter company name" />
          </div>
          <div class="mb-3">
            <label class="form-label text-light">Industry</label>
            <input v-model="form.industry" type="text" class="form-control custom-input" placeholder="e.g. IT, Finance" />
          </div>
          <div class="mb-3">
            <label class="form-label text-light">Location</label>
            <input v-model="form.location" type="text" class="form-control custom-input" placeholder="e.g. Chennai" />
          </div>
          <div class="mb-3">
            <label class="form-label text-light">Website</label>
            <input v-model="form.website" type="text" class="form-control custom-input" placeholder="e.g. https://company.com" />
          </div>
          <div class="mb-3">
            <label class="form-label text-light">HR Contact</label>
            <input v-model="form.hr_contact" type="text" class="form-control custom-input" placeholder="HR email or phone" />
          </div>
          <div class="mb-3">
            <label class="form-label text-light">Company Overview / Description</label>
            <textarea v-model="form.description" class="form-control custom-input" rows="3" placeholder="Describe your company..."></textarea>
          </div>
        </template>

        <button @click="register" :disabled="loading" class="btn btn-orange w-100 fw-bold py-2 mt-2">
          {{ loading ? 'Creating account...' : 'Create Account' }}
        </button>

        <p class="text-center text-muted mt-4 mb-0">
          Already have an account?
          <router-link to="/login" class="text-orange">Sign in</router-link>
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
      role: 'student',
      error: '',
      success: '',
      loading: false,
      form: {
        username: '',
        email: '',
        password: '',
        full_name: '',
        branch: '',
        year: '',
        cgpa: '',
        phone: '',
        company_name: '',
        industry: '',
        location: '',
        website: '',
        hr_contact: '',
        description: ''
      }
    }
  },
  methods: {
    async register() {
      this.error = ''
      this.success = ''

      if (!this.form.username || !this.form.email || !this.form.password) {
        this.error = 'Username, email and password are required'
        return
      }

      this.loading = true
      try {
        const payload = {
          ...this.form,
          role: this.role
        }
        await axios.post('/auth/register', payload)
        this.success = 'Account created successfully! Redirecting to login...'
        setTimeout(() => this.$router.push('/login'), 2000)
      } catch (err) {
        this.error = err.response?.data?.message || 'Registration failed'
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
  max-width: 480px;
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
.custom-input::placeholder {
  color: #666688;
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
.role-btn {
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s;
}
.role-active {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
  border: none;
}
.role-inactive {
  background: #2a2a3e;
  color: #aaaacc;
  border: 1px solid #3a3a5c;
}
</style>