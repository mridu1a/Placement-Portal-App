<template>
  <div class="dashboard-bg min-vh-100">

    <!-- Navbar / Header -->
    <nav class="navbar px-4 py-3 dashboard-nav">
      <span class="navbar-brand text-white fw-bold" @click="setView('dashboard')" style="cursor: pointer;">Placement Portal</span>
      <div class="d-flex align-items-center gap-2 flex-wrap text-muted">
        <span>Welcome, <span class="text-orange fw-bold">{{ username }}</span></span>
        <span>|</span>
        <a href="#" @click.prevent="setView('profile')" class="text-orange text-decoration-none fw-bold hover-underline">edit profile</a>
        <span>|</span>
        <a href="#" @click.prevent="setView('history')" class="text-orange text-decoration-none fw-bold hover-underline">History</a>
        <span>|</span>
        <a href="#" @click.prevent="logout" class="text-danger text-decoration-none fw-bold hover-underline">logout</a>
      </div>
    </nav>

    <div class="container-fluid px-4 py-4">

      <!-- View: Application History -->
      <div v-if="currentView === 'history'" class="fade-in">
        <div class="form-card mb-4">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="text-white fw-bold mb-0">Student Application History</h4>
            <button @click="setView('dashboard')" class="btn btn-outline-orange btn-sm fw-bold px-4">Back</button>
          </div>
          <div class="student-meta mb-4">
            <p class="text-light mb-1"><strong>Student Name:</strong> {{ dashboard.student_name }}</p>
            <p class="text-light mb-0"><strong>Department:</strong> {{ dashboard.branch }}</p>
          </div>
          <div class="table-wrapper">
            <table class="table custom-table">
              <thead>
                <tr>
                  <th>Drive No.</th>
                  <th>Job Title</th>
                  <th>Results</th>
                  <th>Remark</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="applications.length === 0">
                  <td colspan="4" class="text-center text-muted py-4">No applications in history.</td>
                </tr>
                <tr v-for="(app, index) in applications" :key="app.application_id">
                  <td class="text-muted fw-bold">#{{ app.application_id }}</td>
                  <td class="text-white fw-bold">{{ app.job_title }}</td>
                  <td>
                    <span :class="['status-badge', `status-${app.status}`]">{{ app.status }}</span>
                  </td>
                  <td class="text-muted small">{{ app.feedback || 'None' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- View: Organization Details -->
      <div v-else-if="currentView === 'company'" class="fade-in">
        <div class="form-card mb-4" v-if="selectedCompany">
          <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
              <h3 class="text-white fw-bold mb-1">{{ selectedCompany.company_name }}</h3>
              <p class="text-orange mb-0">{{ selectedCompany.industry }} · {{ selectedCompany.location }}</p>
            </div>
            <button @click="setView('dashboard')" class="btn btn-outline-orange btn-sm fw-bold px-4">Back</button>
          </div>

          <div class="row g-4 mb-4">
            <div class="col-md-8">
              <h5 class="text-orange fw-bold mb-2">Overview</h5>
              <div class="p-3 bg-dark-card rounded text-muted whitespace-pre">
                {{ selectedCompany.description || 'No description provided by the company.' }}
              </div>
            </div>
            <div class="col-md-4">
              <div class="drive-meta-card p-3 rounded">
                <p class="mb-2 text-light"><strong>Website:</strong> <a :href="formatWebsite(selectedCompany.website)" target="_blank" class="text-orange text-decoration-none fw-bold hover-underline">{{ selectedCompany.website || 'N/A' }}</a></p>
                <p class="mb-0 text-light"><strong>HR Contact:</strong> {{ selectedCompany.hr_contact || 'N/A' }}</p>
              </div>
            </div>
          </div>

          <div>
            <h5 class="text-orange fw-bold mb-3">Current Drives</h5>
            <div class="row g-3" v-if="selectedCompany.drives && selectedCompany.drives.length > 0">
              <div class="col-md-4" v-for="drive in selectedCompany.drives" :key="drive.id">
                <div class="drive-card">
                  <h6 class="text-white fw-bold mb-2">{{ drive.job_title }}</h6>
                  <p class="text-muted small mb-3">Deadline: {{ formatDate(drive.application_deadline) }}</p>
                  <button @click="setView('drive', drive.id)" class="btn btn-sm btn-orange w-100 fw-bold">
                    View Details
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="text-muted py-3">No active placement drives for this company.</div>
          </div>
        </div>
      </div>

      <!-- View: Drive Details -->
      <div v-else-if="currentView === 'drive'" class="fade-in">
        <div class="form-card mb-4" v-if="selectedDrive">
          <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
              <h3 class="text-white fw-bold mb-1">{{ selectedDrive.job_title }}</h3>
              <p class="text-orange fw-bold mb-0">{{ selectedDrive.company_name }}</p>
            </div>
            <button @click="goBackFromDrive()" class="btn btn-outline-orange btn-sm fw-bold px-4">Back</button>
          </div>

          <div class="row g-4">
            <div class="col-md-8">
              <div class="mb-4">
                <h5 class="text-orange fw-bold mb-2">Job Description</h5>
                <div class="p-3 bg-dark-card rounded text-muted whitespace-pre">
                  {{ selectedDrive.job_description || 'No job description provided.' }}
                </div>
              </div>

              <div class="mb-4">
                <h5 class="text-orange fw-bold mb-2">Eligibility Criteria</h5>
                <div class="p-3 bg-dark-card rounded text-muted">
                  <p class="mb-1"><strong>Eligible Branches:</strong> {{ selectedDrive.eligibility_branch || 'All Branches' }}</p>
                  <p class="mb-1"><strong>Minimum CGPA:</strong> {{ selectedDrive.eligibility_cgpa || 'None' }}</p>
                  <p class="mb-0"><strong>Year:</strong> {{ selectedDrive.eligibility_year || 'Any' }}</p>
                </div>
              </div>
            </div>

            <div class="col-md-4">
              <div class="drive-meta-card p-3 rounded mb-3">
                <div class="text-center mb-3">
                  <div class="logo-placeholder mx-auto mb-2">C</div>
                  <h6 class="text-white mb-0 fw-bold">{{ selectedDrive.company_name }}</h6>
                </div>
                <hr class="border-secondary" />
                <p class="mb-2 text-light"><strong>Location:</strong> {{ selectedDrive.location || 'N/A' }}</p>
                <p class="mb-2 text-light"><strong>Salary:</strong> {{ selectedDrive.salary || 'N/A' }}</p>
                <p class="mb-3 text-light"><strong>Deadline:</strong> {{ formatDate(selectedDrive.application_deadline) }}</p>

                <button v-if="!selectedDrive.already_applied"
                  @click="applyDrive(selectedDrive.id)"
                  class="btn btn-orange w-100 fw-bold">
                  Apply Now
                </button>
                <button v-else disabled class="btn btn-secondary w-100 fw-bold">
                  Already Applied
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- View: Standard Dashboard -->
      <div v-else class="fade-in">
        <!-- Student Info Header Card -->
        <div class="student-header-card mb-4">
          <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
            <div>
              <h4 class="text-white fw-bold mb-1">{{ dashboard.student_name }}</h4>
              <span class="text-muted">{{ dashboard.branch }} · Year {{ dashboard.year }} · CGPA {{ dashboard.cgpa }}</span>
            </div>
            <button @click="setView('profile')" class="btn btn-outline-orange fw-bold px-4">
              Edit Profile
            </button>
          </div>
        </div>

        <!-- Dashboard Tabs -->
        <div class="tab-bar mb-4">
          <button v-for="tab in tabs" :key="tab.key"
            @click="activeTab = tab.key"
            :class="['tab-btn', activeTab === tab.key ? 'tab-active' : '']">
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab Content: Drives -->
        <div v-if="activeTab === 'drives'">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="text-white mb-0">Available Placement Drives</h5>
            <input v-model="search" @input="searchDrives" type="text"
              class="form-control custom-input w-25" placeholder="Search drives..." />
          </div>

          <div v-if="drives.length === 0" class="empty-state">
            <p>No approved drives available right now.</p>
          </div>

          <div class="row g-3" v-else>
            <div class="col-md-4" v-for="drive in drives" :key="drive.id">
              <div class="drive-card d-flex flex-column justify-content-between">
                <div>
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="text-white fw-bold mb-0">{{ drive.job_title }}</h6>
                    <span v-if="drive.already_applied" class="status-badge status-applied">Applied</span>
                  </div>
                  <p class="text-orange small fw-bold mb-1">{{ drive.company_name }}</p>
                  <p class="text-muted small mb-2">{{ drive.drive_name }}</p>
                  <div class="drive-meta mb-3">
                    <div><span class="meta-label">Location:</span> {{ drive.location || '-' }}</div>
                    <div><span class="meta-label">Salary:</span> {{ drive.salary || '-' }}</div>
                    <div><span class="meta-label">Deadline:</span> {{ formatDate(drive.application_deadline) }}</div>
                  </div>
                </div>
                <button @click="setView('drive', drive.id)" class="btn btn-outline-orange btn-sm w-100 fw-bold">
                  View Details
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab Content: Organizations -->
        <div v-if="activeTab === 'organizations'">
          <h5 class="text-white mb-3">Registered Organizations</h5>
          <div v-if="organizations.length === 0" class="empty-state">
            <p>No registered organizations available.</p>
          </div>

          <div class="row g-3" v-else>
            <div class="col-md-4" v-for="org in organizations" :key="org.id">
              <div class="drive-card d-flex flex-column justify-content-between">
                <div>
                  <h6 class="text-white fw-bold mb-1">{{ org.company_name }}</h6>
                  <p class="text-orange small mb-2">{{ org.industry }}</p>
                  <p class="text-light small mb-3 text-truncate-2">{{ org.description || 'No overview description available.' }}</p>
                  <p class="text-muted small mb-3">{{ org.location || 'Not Specified' }}</p>
                </div>
                <button @click="setView('company', org.id)" class="btn btn-outline-orange btn-sm w-100 fw-bold">
                  View Details
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab Content: Applied Drives (Applications) -->
        <div v-if="activeTab === 'applications'">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="text-white mb-0">Applied Drives</h5>
            <button @click="exportCSV" class="btn btn-outline-orange fw-bold px-4">
              Export as CSV
            </button>
          </div>
          <div v-if="applications.length === 0" class="empty-state">
            <p>You haven't applied to any drives yet.</p>
          </div>
          <div class="table-wrapper" v-else>
            <table class="table custom-table">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Drive Name</th>
                  <th>Job Title</th>
                  <th>Applied On</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applications" :key="app.application_id">
                  <td class="text-muted">{{ app.company_name }}</td>
                  <td class="text-muted">{{ app.drive_name }}</td>
                  <td class="text-muted">{{ app.job_title }}</td>
                  <td class="text-muted">{{ formatDate(app.application_date) }}</td>
                  <td>
                    <span :class="['status-badge', `status-${app.status}`]">{{ app.status }}</span>
                  </td>
                  <td>
                    <button @click="setView('drive', app.drive_id)" class="btn btn-sm btn-outline-orange fw-bold">
                      View Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tab Content: Profile -->
        <div v-if="activeTab === 'profile'">
          <div class="form-card">
            <h5 class="text-white fw-bold mb-4">Edit Profile</h5>

            <div v-if="profileError" class="alert alert-danger py-2">{{ profileError }}</div>
            <div v-if="profileSuccess" class="alert alert-success py-2">{{ profileSuccess }}</div>

            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label text-light">Full Name</label>
                <input v-model="profile.full_name" type="text" class="form-control custom-input" />
              </div>
              <div class="col-md-6">
                <label class="form-label text-light">Phone</label>
                <input v-model="profile.phone" type="text" class="form-control custom-input" />
              </div>
              <div class="col-md-4">
                <label class="form-label text-light">Branch</label>
                <input v-model="profile.branch" type="text" class="form-control custom-input" />
              </div>
              <div class="col-md-4">
                <label class="form-label text-light">Year</label>
                <input v-model="profile.year" type="number" class="form-control custom-input" />
              </div>
              <div class="col-md-4">
                <label class="form-label text-light">CGPA</label>
                <input v-model="profile.cgpa" type="number" step="0.1" class="form-control custom-input" />
              </div>
              <div class="col-12">
                <label class="form-label text-light">Skills</label>
                <input v-model="profile.skills" type="text" class="form-control custom-input" placeholder="e.g. Python, Vue, SQL" />
              </div>

              <!-- Resume Upload -->
              <div class="col-12">
                <label class="form-label text-light">Resume (PDF only)</label>
                <input type="file" accept=".pdf" @change="handleResumeFile" class="form-control custom-input" />
                <div v-if="profile.resume_path" class="mt-2">
                  <span class="text-success">Resume on file: {{ profile.resume_path }}</span>
                </div>
                <div v-if="resumeSuccess" class="alert alert-success py-2 mt-2">{{ resumeSuccess }}</div>
                <div v-if="resumeError" class="alert alert-danger py-2 mt-2">{{ resumeError }}</div>
              </div>
            </div>

            <div class="d-flex gap-3 mt-4">
              <button @click="updateProfile" class="btn btn-orange fw-bold px-5">
                Save Profile
              </button>
              <button @click="uploadResume" :disabled="!resumeFile" class="btn btn-outline-orange fw-bold px-4">
                Upload Resume
              </button>
            </div>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>

<script>
import axios from '../axios'

export default {
  data() {
    return {
      username: localStorage.getItem('username'),
      activeTab: 'drives',
      tabs: [
        { key: 'drives', label: 'Placement Drives' },
        { key: 'organizations', label: 'Organizations' },
        { key: 'applications', label: 'Applied Drives' },
        { key: 'profile', label: 'Profile' }
      ],
      dashboard: {},
      drives: [],
      organizations: [],
      applications: [],
      search: '',
      profile: {},
      profileError: '',
      profileSuccess: '',
      resumeFile: null,
      resumeSuccess: '',
      resumeError: '',

      // View state variables to match wireframe
      currentView: 'dashboard', // 'dashboard', 'history', 'company', 'drive', 'profile'
      selectedCompany: null,
      selectedDrive: null,
      previousView: 'dashboard'
    }
  },
  async mounted() {
    await this.loadDashboard()
    await this.loadOrganizations()
    await this.loadApplications()
    await this.loadProfile()
  },
  methods: {
    async loadDashboard() {
      const res = await axios.get('/student/dashboard')
      this.dashboard = res.data
      this.drives = res.data.drives
    },
    async loadOrganizations() {
      try {
        const res = await axios.get('/student/companies')
        this.organizations = res.data
      } catch (err) {
        console.error('Failed to load organizations', err)
      }
    },
    async loadApplications() {
      const res = await axios.get('/student/applications')
      this.applications = res.data
    },
    async loadProfile() {
      const res = await axios.get('/student/profile')
      this.profile = res.data
    },
    async searchDrives() {
      const res = await axios.get(`/student/drives/search?search=${this.search}`)
      this.drives = res.data
    },
    async setView(view, id = null) {
      this.profileError = ''
      this.profileSuccess = ''
      this.resumeSuccess = ''
      this.resumeError = ''

      if (view === 'dashboard') {
        this.currentView = 'dashboard'
        this.selectedCompany = null
        this.selectedDrive = null
      } else if (view === 'history') {
        this.currentView = 'history'
        await this.loadApplications()
      } else if (view === 'profile') {
        this.currentView = 'dashboard'
        this.activeTab = 'profile'
      } else if (view === 'company') {
        this.currentView = 'company'
        try {
          const res = await axios.get(`/student/companies/${id}`)
          this.selectedCompany = res.data
        } catch (err) {
          alert('Failed to load company details')
          this.setView('dashboard')
        }
      } else if (view === 'drive') {
        this.previousView = this.currentView
        this.currentView = 'drive'
        try {
          const res = await axios.get(`/student/drives/${id}`)
          this.selectedDrive = res.data
        } catch (err) {
          alert('Failed to load drive details')
          this.setView('dashboard')
        }
      }
    },
    goBackFromDrive() {
      if (this.previousView === 'company') {
        this.currentView = 'company'
      } else {
        this.setView('dashboard')
      }
    },
    async applyDrive(driveId) {
      try {
        await axios.post(`/student/apply/${driveId}`)
        await this.loadDashboard()
        await this.loadApplications()
        if (this.selectedDrive) {
          this.selectedDrive.already_applied = true
        }
        alert('Application submitted successfully!')
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to apply')
      }
    },
    async updateProfile() {
      this.profileError = ''
      this.profileSuccess = ''
      try {
        await axios.put('/student/profile', this.profile)
        this.profileSuccess = 'Profile updated successfully!'
        await this.loadDashboard()
      } catch (err) {
        this.profileError = err.response?.data?.message || 'Failed to update profile'
      }
    },
    handleResumeFile(event) {
      this.resumeFile = event.target.files[0]
    },
    async uploadResume() {
      this.resumeError = ''
      this.resumeSuccess = ''
      if (!this.resumeFile) {
        this.resumeError = 'Please select a PDF file'
        return
      }
      const formData = new FormData()
      formData.append('resume', this.resumeFile)
      try {
        const token = localStorage.getItem('token')
        const res = await fetch('http://localhost:5000/api/student/upload-resume', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        })
        const data = await res.json()
        if (res.ok) {
          this.resumeSuccess = 'Resume uploaded successfully!'
          await this.loadProfile()
        } else {
          this.resumeError = data.message || 'Upload failed'
        }
      } catch (err) {
        this.resumeError = 'Upload failed'
      }
    },
    async exportCSV() {
      try {
        await axios.post('/student/export-csv')
        alert('Export started! You will receive an email shortly.')
      } catch (err) {
        alert(err.response?.data?.message || 'Export failed')
      }
    },
    logout() {
      localStorage.clear()
      this.$router.push('/login')
    },
    formatDate(date) {
      if (!date) return '-'
      return new Date(date).toLocaleDateString()
    },
    formatWebsite(url) {
      if (!url) return '#'
      if (!/^https?:\/\//i.test(url)) {
        return `https://${url}`
      }
      return url
    }
  }
}
</script>

<style scoped>
.dashboard-bg { background: #0f0e17; }
.dashboard-nav { background: #1e1e2e; border-bottom: 1px solid #3a3a5c; }
.text-orange { color: #f97316; }
.student-header-card {
  background: #1e1e2e;
  border: 1px solid #3a3a5c;
  border-radius: 12px;
  padding: 24px;
}
.btn-orange { background: linear-gradient(135deg, #f97316, #ea580c); border: none; color: white; }
.btn-orange:hover { background: linear-gradient(135deg, #ea580c, #c2410c); color: white; }
.btn-outline-orange { border: 1px solid #f97316; color: #f97316; background: transparent; }
.btn-outline-orange:hover { background: #f97316; color: white; }
.tab-bar { display: flex; gap: 8px; border-bottom: 1px solid #3a3a5c; }
.tab-btn { background: none; border: none; color: #8888aa; padding: 10px 20px; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; }
.tab-active { color: #f97316; border-bottom: 2px solid #f97316; }
.drive-card { background: #1e1e2e; border: 1px solid #3a3a5c; border-radius: 12px; padding: 20px; height: 100%; }
.drive-meta { display: flex; flex-direction: column; gap: 4px; font-size: 13px; color: #aaaacc; }
.meta-label { color: #666688; }
.form-card { background: #1e1e2e; border: 1px solid #3a3a5c; border-radius: 12px; padding: 28px; }
.custom-input { background: #2a2a3e; border: 1px solid #3a3a5c; color: #ffffff; }
.custom-input:focus { background: #2a2a3e; border-color: #f97316; color: #ffffff; box-shadow: none; }
.table-wrapper { background: #1e1e2e; border: 1px solid #3a3a5c; border-radius: 12px; overflow: hidden; }
.custom-table { margin: 0; color: #e2e8f0; }
.custom-table thead th { background: #2a2a3e; color: #cbd5e1; border-color: #3a3a5c; font-size: 12px; text-transform: uppercase; padding: 14px 16px; }
.custom-table tbody td { border-color: #2a2a3e; padding: 14px 16px; vertical-align: middle; color: #f1f5f9; }
.custom-table tbody tr:hover { background: #252535; }
.status-badge { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: capitalize; }
.status-approved { background: rgba(34,197,94,0.15); color: #4ade80; }
.status-pending { background: rgba(249,115,22,0.15); color: #fb923c; }
.status-rejected { background: rgba(239,68,68,0.15); color: #f87171; }
.status-applied { background: rgba(59,130,246,0.15); color: #60a5fa; }
.status-shortlisted { background: rgba(249,115,22,0.15); color: #fb923c; }
.status-selected { background: rgba(34,197,94,0.15); color: #4ade80; }
.empty-state { text-align: center; padding: 60px; color: #94a3b8; }
.empty-icon { font-size: 48px; margin-bottom: 16px; }

/* Custom premium elements */
.hover-underline:hover { text-decoration: underline !important; }
.bg-dark-card { background: #151421; border: 1px solid #2a2a3e; color: #f1f5f9 !important; }
.bg-dark-card * { color: #f1f5f9 !important; }
.whitespace-pre { white-space: pre-wrap; }
.drive-meta-card { background: #1e1e2e; border: 1px solid #3a3a5c; color: #f1f5f9; }
.drive-meta-card strong { color: #f97316; }
.logo-placeholder {
  width: 64px;
  height: 64px;
  background: #f97316;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}
.student-meta {
  padding: 16px;
  background: #1a1a2e;
  border-radius: 8px;
  border: 1px solid #333355;
  color: #f1f5f9;
}
.text-muted { color: #94a3b8 !important; }
.text-light { color: #cbd5e1 !important; }
.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;  
  overflow: hidden;
}
.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>