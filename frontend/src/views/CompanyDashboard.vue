<template>
  <div class="dashboard-bg min-vh-100">

    <!-- Navbar / Header -->
    <nav class="navbar px-4 py-3 dashboard-nav">
      <span class="navbar-brand text-white fw-bold" @click="setView('dashboard')" style="cursor: pointer;">Placement Portal</span>
      <div class="d-flex align-items-center gap-3">
        <span class="text-muted">Welcome, <span class="text-orange fw-bold">{{ username }}</span></span>
        <button @click="logout" class="btn btn-sm btn-outline-danger">Logout</button>
      </div>
    </nav>

    <div class="container-fluid px-4 py-4">

      <!-- Company Info Header Card -->
      <div class="company-header-card mb-4" v-if="currentView === 'dashboard'">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
          <div>
            <h4 class="text-white fw-bold mb-1">{{ dashboard.company_name }}</h4>
            <span class="text-muted">{{ dashboard.industry }} · {{ dashboard.location }}</span>
          </div>
          <button @click="setView('create')" class="btn btn-orange fw-bold px-4">
            + Create Drive
          </button>
        </div>
      </div>

      <!-- View: Create Drive Form -->
      <div v-if="currentView === 'create'" class="fade-in">
        <div class="form-card">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="text-white fw-bold mb-0">Create New Drive</h5>
            <button @click="setView('dashboard')" class="btn btn-outline-orange btn-sm fw-bold px-4">← Back</button>
          </div>

          <div v-if="createError" class="alert alert-danger py-2">{{ createError }}</div>
          <div v-if="createSuccess" class="alert alert-success py-2">{{ createSuccess }}</div>

          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label text-light">Drive Name</label>
              <input v-model="newDrive.drive_name" type="text" class="form-control custom-input" placeholder="e.g. Tech Corp Drive 2026" />
            </div>
            <div class="col-md-6">
              <label class="form-label text-light">Job Title</label>
              <input v-model="newDrive.job_title" type="text" class="form-control custom-input" placeholder="e.g. Software Engineer" />
            </div>
            <div class="col-12">
              <label class="form-label text-light">Job Description</label>
              <textarea v-model="newDrive.job_description" class="form-control custom-input" rows="3" placeholder="Describe the role..."></textarea>
            </div>
            <div class="col-12">
              <label class="form-label text-light d-block">Eligible Branches</label>
              <div class="d-flex flex-wrap gap-3 p-3 bg-dark-card rounded mb-2">
                <div class="form-check" v-for="branch in branchOptions" :key="branch">
                  <input class="form-check-input" type="checkbox" :id="'branch-' + branch" :value="branch" v-model="selectedBranches" />
                  <label class="form-check-label text-light" :for="'branch-' + branch">
                    {{ branch }}
                  </label>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <label class="form-label text-light">Minimum CGPA</label>
              <input v-model="newDrive.eligibility_cgpa" type="number" step="0.1" class="form-control custom-input" placeholder="e.g. 7.0" />
            </div>
            <div class="col-md-4">
              <label class="form-label text-light">Year</label>
              <input v-model="newDrive.eligibility_year" type="number" class="form-control custom-input" placeholder="e.g. 3" />
            </div>
            <div class="col-md-4">
              <label class="form-label text-light">Salary</label>
              <input v-model="newDrive.salary" type="text" class="form-control custom-input" placeholder="e.g. 600000" />
            </div>
            <div class="col-md-4">
              <label class="form-label text-light">Location</label>
              <input v-model="newDrive.location" type="text" class="form-control custom-input" placeholder="e.g. Chennai" />
            </div>
            <div class="col-md-4">
              <label class="form-label text-light">Application Deadline</label>
              <input v-model="newDrive.application_deadline" type="date" class="form-control custom-input" />
            </div>
          </div>

          <button @click="createDrive" :disabled="createLoading" class="btn btn-orange fw-bold px-5 mt-4">
            {{ createLoading ? 'Creating...' : 'Create Drive' }}
          </button>
        </div>
      </div>

      <!-- View: Update Applications for the Drive (Applicants List) -->
      <div v-else-if="currentView === 'applications'" class="fade-in">
        <div class="form-card mb-4" v-if="selectedDrive">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h4 class="text-white fw-bold mb-1">Update Applications for the Drive</h4>
              <p class="text-orange mb-0">Job Title: {{ selectedDrive.job_title }} ({{ selectedDrive.drive_name }})</p>
            </div>
            <button @click="setView('dashboard')" class="btn btn-outline-orange btn-sm fw-bold px-4">← Back</button>
          </div>

          <h5 class="text-light mb-3">Received Applications</h5>
          <div v-if="applications.length === 0" class="empty-state">
            <p>No applications yet for this drive.</p>
          </div>

          <div class="table-wrapper mb-4" v-else>
            <table class="table custom-table">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Branch</th>
                  <th>CGPA</th>
                  <th>Current Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applications" :key="app.application_id">
                  <td class="text-muted">{{ app.student_name }}</td>
                  <td class="text-muted">{{ app.branch }}</td>
                  <td class="text-muted">{{ app.cgpa }}</td>
                  <td>
                    <span :class="['status-badge', `status-${app.status}`]">{{ app.status }}</span>
                  </td>
                  <td>
                    <button @click="reviewApplication(app)" class="btn btn-sm btn-orange fw-bold">
                      review application
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="d-flex justify-content-end">
            <button @click="saveAllApplications" class="btn btn-orange fw-bold px-5">Save & Finish</button>
          </div>
        </div>
      </div>

      <!-- View: Review Candidate Application Details -->
      <div v-else-if="currentView === 'review'" class="fade-in">
        <div class="form-card mb-4" v-if="currentApp">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="text-white fw-bold mb-0">Student Application Details</h4>
            <button @click="setView('applications', selectedDrive.id)" class="btn btn-outline-orange btn-sm fw-bold px-4">← Back</button>
          </div>

          <div class="row g-4">
            <div class="col-md-6">
              <div class="p-3 bg-dark-card rounded mb-4">
                <p class="text-light mb-2"><strong>Student Name:</strong> {{ currentApp.student_name }}</p>
                <p class="text-light mb-2"><strong>Department:</strong> {{ currentApp.branch }}</p>
                <p class="text-light mb-2"><strong>Drive:</strong> {{ selectedDrive.drive_name }}</p>
                <p class="text-light mb-0"><strong>Job Title:</strong> {{ selectedDrive.job_title }}</p>
              </div>

              <div class="mb-3">
                <label class="form-label text-light"><strong>Application Status</strong></label>
                <select v-model="currentApp.status" class="form-select custom-input">
                  <option value="applied">Applied (Pending)</option>
                  <option value="shortlisted">Shortlist</option>
                  <option value="selected">Select</option>
                  <option value="rejected">Reject</option>
                </select>
              </div>



              <div class="mb-3">
                <label class="form-label text-light"><strong>Feedback / Remark (Optional)</strong></label>
                <textarea v-model="currentApp.feedback" class="form-control custom-input" rows="3" placeholder="Write feedback details..."></textarea>
              </div>

              <button @click="submitApplicationReview" class="btn btn-orange fw-bold px-4 mt-2">
                Save Review
              </button>
            </div>

            <div class="col-md-6 text-center d-flex flex-column justify-content-center align-items-center">
              <div class="avatar-placeholder mb-3">S</div>
              <h5 class="text-white mb-2">{{ currentApp.student_name }}</h5>
              <p class="text-muted mb-4">CGPA: {{ currentApp.cgpa }} · {{ currentApp.branch }}</p>
              <button @click="downloadResume(currentApp.student_id)" class="btn btn-outline-orange fw-bold px-4">
                View Resume (Download PDF)
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- View: Dashboard Standard tables -->
      <div v-else class="fade-in">
        <!-- Upcoming drives -->
        <div class="form-card mb-4">
          <h5 class="text-orange fw-bold mb-3">Upcoming Drives</h5>
          <div v-if="upcomingDrives.length === 0" class="empty-state">
            <p class="mb-0">No upcoming drives. Click "Create Drive" above to create one!</p>
          </div>
          <div class="table-wrapper" v-else>
            <table class="table custom-table">
              <thead>
                <tr>
                  <th>Sr No.</th>
                  <th>Drive Name</th>
                  <th>Job Title</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(drive, index) in upcomingDrives" :key="drive.id">
                  <td class="text-muted fw-bold">{{ index + 1 }}</td>
                  <td class="text-muted">{{ drive.drive_name }}</td>
                  <td class="text-muted">{{ drive.job_title }}</td>
                  <td>
                    <span :class="['status-badge', `status-${drive.status}`]">{{ drive.status }}</span>
                  </td>
                  <td>
                    <div class="d-flex gap-2">
                      <button @click="setView('applications', drive.id)" class="btn btn-sm btn-outline-orange fw-bold">
                        view details
                      </button>
                      <button @click="markDriveComplete(drive.id)" class="btn btn-sm btn-success fw-bold">
                        mark as complete
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Closed drives -->
        <div class="form-card mb-4">
          <h5 class="text-muted fw-bold mb-3">Closed Drives</h5>
          <div v-if="closedDrives.length === 0" class="empty-state py-4">
            <p class="mb-0">No closed drives yet.</p>
          </div>
          <div class="table-wrapper" v-else>
            <table class="table custom-table">
              <thead>
                <tr>
                  <th>Sr No.</th>
                  <th>Drive Name</th>
                  <th>Job Title</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(drive, index) in closedDrives" :key="drive.id">
                  <td class="text-muted fw-bold">{{ index + 1 }}</td>
                  <td class="text-muted">{{ drive.drive_name }}</td>
                  <td class="text-muted">{{ drive.job_title }}</td>
                  <td>
                    <button @click="setView('applications', drive.id)" class="btn btn-sm btn-outline-secondary fw-bold">
                      update
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
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
      currentView: 'dashboard', // 'dashboard', 'create', 'applications', 'review'
      dashboard: {},
      applications: [],
      selectedDrive: null,
      currentApp: null,

      createError: '',
      createSuccess: '',
      createLoading: false,
      branchOptions: [
        'Computer Science',
        'Electronics',
        'Electrical',
        'Mechanical',
        'Civil',
        'Chemical',
        'Biotechnology'
      ],
      selectedBranches: [],
      newDrive: {
        drive_name: '',
        job_title: '',
        job_description: '',
        eligibility_branch: '',
        eligibility_cgpa: '',
        eligibility_year: '',
        salary: '',
        location: '',
        application_deadline: ''
      }
    }
  },
  computed: {
    upcomingDrives() {
      if (!this.dashboard.drives) return []
      return this.dashboard.drives.filter(d => d.status !== 'closed')
    },
    closedDrives() {
      if (!this.dashboard.drives) return []
      return this.dashboard.drives.filter(d => d.status === 'closed')
    }
  },
  async mounted() {
    await this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      const res = await axios.get('/company/dashboard')
      this.dashboard = res.data
    },
    async setView(view, id = null) {
      this.createError = ''
      this.createSuccess = ''
      this.createLoading = false

      if (view === 'dashboard') {
        this.currentView = 'dashboard'
        this.selectedDrive = null
        this.applications = []
        await this.loadDashboard()
      } else if (view === 'create') {
        this.currentView = 'create'
        this.selectedBranches = []
      } else if (view === 'applications') {
        this.currentView = 'applications'
        // Find the selected drive
        this.selectedDrive = this.dashboard.drives.find(d => d.id === id)
        await this.loadApplications(id)
      }
    },
    async loadApplications(driveId) {
      try {
        const res = await axios.get(`/company/drives/${driveId}/applications`)
        this.applications = res.data
      } catch (err) {
        alert('Failed to load applications.')
      }
    },
    async createDrive() {
      this.createError = ''
      this.createSuccess = ''
      this.createLoading = true
      try {
        const payload = {
          ...this.newDrive,
          eligibility_branch: this.selectedBranches.join(', ')
        }
        await axios.post('/company/drives', payload)
        this.createSuccess = 'Drive created successfully! Waiting for admin approval.'
        this.newDrive = {
          drive_name: '',
          job_title: '',
          job_description: '',
          eligibility_branch: '',
          eligibility_cgpa: '',
          eligibility_year: '',
          salary: '',
          location: '',
          application_deadline: ''
        }
        this.selectedBranches = []
        await this.loadDashboard()
      } catch (err) {
        this.createError = err.response?.data?.message || 'Failed to create drive'
      } finally {
        this.createLoading = false
      }
    },
    async markDriveComplete(driveId) {
      if (!confirm('Are you sure you want to mark this drive as complete (closed)?')) return
      try {
        await axios.put(`/company/drives/${driveId}/close`)
        await this.loadDashboard()
        alert('Drive marked as complete successfully!')
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to close drive')
      }
    },
    reviewApplication(app) {
      this.currentApp = {
        ...app
      }
      this.currentView = 'review'
    },
    async submitApplicationReview() {
      try {
        const payload = {
          status: this.currentApp.status,
          feedback: this.currentApp.feedback
        }
        await axios.put(`/company/applications/${this.currentApp.application_id}`, payload)
        alert('Application review saved successfully!')
        await this.loadApplications(this.selectedDrive.id)
        this.setView('applications', this.selectedDrive.id)
      } catch (err) {
        alert('Failed to save application review')
      }
    },
    async saveAllApplications() {
      alert('All changes saved! Drive applications list finalized.')
      this.setView('dashboard')
    },
    async downloadResume(studentId) {
      try {
        const res = await axios.get(`/student/resume/${studentId}`, { responseType: 'blob' })
        const file = new Blob([res.data], { type: 'application/pdf' })
        const fileURL = URL.createObjectURL(file)
        window.open(fileURL)
      } catch (err) {
        alert('Resume PDF is not uploaded by the student yet.')
      }
    },
    logout() {
      localStorage.clear()
      this.$router.push('/login')
    },
    formatDate(date) {
      if (!date) return '-'
      return new Date(date).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.dashboard-bg { background: #0f0e17; }
.dashboard-nav { background: #1e1e2e; border-bottom: 1px solid #3a3a5c; }
.text-orange { color: #f97316; }
.company-header-card {
  background: #1e1e2e;
  border: 1px solid #3a3a5c;
  border-radius: 12px;
  padding: 24px;
}
.btn-orange { background: linear-gradient(135deg, #f97316, #ea580c); border: none; color: white; }
.btn-orange:hover { background: linear-gradient(135deg, #ea580c, #c2410c); color: white; }
.btn-outline-orange { border: 1px solid #f97316; color: #f97316; background: transparent; }
.btn-outline-orange:hover { background: #f97316; color: white; }
.form-card { background: #1e1e2e; border: 1px solid #3a3a5c; border-radius: 12px; padding: 28px; }
.custom-input { background: #2a2a3e; border: 1px solid #3a3a5c; color: #ffffff; }
.custom-input:focus { background: #2a2a3e; border-color: #f97316; color: #ffffff; box-shadow: none; }
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
.status-closed { background: rgba(100,116,139,0.15); color: #94a3b8; }
.empty-state { text-align: center; padding: 40px; color: #94a3b8; }

.bg-dark-card { background: #151421; border: 1px solid #2a2a3e; color: #f1f5f9 !important; }
.bg-dark-card * { color: #f1f5f9 !important; }
.text-muted { color: #94a3b8 !important; }
.text-light { color: #cbd5e1 !important; }
.form-label { color: #e2e8f0 !important; }
.avatar-placeholder {
  width: 96px;
  height: 96px;
  background: #f97316;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
}
.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>