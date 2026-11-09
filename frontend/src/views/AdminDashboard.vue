<template>
  <div class="dashboard-bg min-vh-100">

    <!-- Navbar / Header (Aligned with wireframe) -->
    <nav class="navbar px-4 py-3 dashboard-nav flex-wrap gap-3">
      <span class="navbar-brand text-white fw-bold" @click="setView('dashboard')" style="cursor: pointer;">Placement Portal (Admin)</span>
      <div class="d-flex align-items-center gap-2">
        <input v-model="globalSearch" type="text" class="form-control custom-input form-control-sm" placeholder="search student, organizations..." />
        <button @click="performGlobalSearch" class="btn btn-sm btn-orange fw-bold">search</button>
      </div>
      <div class="d-flex align-items-center gap-3">
        <span class="text-muted">Welcome, <span class="text-orange fw-bold">{{ username }}</span></span>
        <button @click="logout" class="btn btn-sm btn-outline-danger">Logout</button>
      </div>
    </nav>

    <div class="container-fluid px-4 py-4">

      <!-- Stats Cards -->
      <div class="row g-3 mb-4" v-if="!selectedDrive && !selectedApp && !selectedCompany">
        <div class="col-md-3 col-6">
          <div class="stat-card">
            <div class="stat-number">{{ stats.total_students }}</div>
            <div class="stat-label">Students</div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="stat-card">
            <div class="stat-number">{{ stats.total_companies }}</div>
            <div class="stat-label">Companies</div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="stat-card">
            <div class="stat-number">{{ stats.total_drives }}</div>
            <div class="stat-label">Drives</div>
          </div>
        </div>
        <div class="col-md-3 col-6">
          <div class="stat-card">
            <div class="stat-number">{{ stats.total_applications }}</div>
            <div class="stat-label">Applications</div>
          </div>
        </div>
      </div>

      <!-- Detail View: Drive details -->
      <div v-if="selectedDrive" class="fade-in">
        <div class="form-card mb-4">
          <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
              <h3 class="text-white fw-bold mb-1">{{ selectedDrive.job_title }}</h3>
              <p class="text-orange fw-bold mb-0">{{ selectedDrive.company_name }} ({{ selectedDrive.drive_name }})</p>
            </div>
            <button @click="selectedDrive = null" class="btn btn-outline-orange btn-sm fw-bold px-4">Go Back</button>
          </div>

          <div class="row g-4">
            <div class="col-md-8">
              <div class="mb-4">
                <h5 class="text-orange fw-bold mb-2">Job Description</h5>
                <div class="p-3 bg-dark-card rounded text-muted whitespace-pre">
                  {{ selectedDrive.job_description || 'No description provided.' }}
                </div>
              </div>
              <div class="mb-4">
                <h5 class="text-orange fw-bold mb-2">Eligibility</h5>
                <div class="p-3 bg-dark-card rounded text-muted">
                  <p class="mb-1"><strong>Eligible Branches:</strong> {{ selectedDrive.eligibility_branch || 'All' }}</p>
                  <p class="mb-1"><strong>Minimum CGPA:</strong> {{ selectedDrive.eligibility_cgpa }}</p>
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="drive-meta-card p-3 rounded">
                <p class="mb-2 text-light"><strong>Location:</strong> {{ selectedDrive.location || 'N/A' }}</p>
                <p class="mb-2 text-light"><strong>Salary:</strong> {{ selectedDrive.salary || 'N/A' }}</p>
                <p class="mb-2 text-light"><strong>Deadline:</strong> {{ formatDate(selectedDrive.application_deadline) }}</p>
                <p class="mb-2 text-light" v-if="selectedDrive.status === 'closed'">
                  <strong>Applied Students:</strong> {{ selectedDrive.applied_count || 0 }}
                </p>
                <p class="mb-0 text-light">
                  Status: <span :class="['status-badge', `status-${selectedDrive.status}`]">{{ selectedDrive.status }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detail View: Company details -->
      <div v-else-if="selectedCompany" class="fade-in">
        <div class="form-card mb-4">
          <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
              <h3 class="text-white fw-bold mb-1">{{ selectedCompany.company_name }}</h3>
              <p class="text-orange fw-bold mb-0">{{ selectedCompany.industry }} · {{ selectedCompany.location }}</p>
            </div>
            <button @click="selectedCompany = null" class="btn btn-outline-orange btn-sm fw-bold px-4">Go Back</button>
          </div>

          <div class="row g-4">
            <div class="col-md-8">
              <div class="mb-4">
                <h5 class="text-orange fw-bold mb-2">Company Overview</h5>
                <div class="p-3 bg-dark-card rounded text-muted whitespace-pre">
                  {{ selectedCompany.description || 'No overview provided.' }}
                </div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="drive-meta-card p-3 rounded">
                <p class="mb-2 text-light"><strong>Website:</strong> <a :href="formatWebsite(selectedCompany.website)" target="_blank" class="text-orange text-decoration-none fw-bold hover-underline">{{ selectedCompany.website || 'N/A' }}</a></p>
                <p class="mb-2 text-light"><strong>HR Contact:</strong> {{ selectedCompany.hr_contact || 'N/A' }}</p>
                <p class="mb-0 text-light">
                  Approval Status: <span :class="['status-badge', `status-${selectedCompany.approval_status}`]">{{ selectedCompany.approval_status }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detail View: Student Application details -->
      <div v-else-if="selectedApp" class="fade-in">
        <div class="form-card mb-4">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="text-white fw-bold mb-0">Student Application Details</h4>
            <button @click="selectedApp = null" class="btn btn-outline-orange btn-sm fw-bold px-4">Back</button>
          </div>

          <div class="row g-4">
            <div class="col-md-6">
              <div class="p-3 bg-dark-card rounded mb-4">
                <p class="text-light mb-2"><strong>Student Name:</strong> {{ selectedApp.student_name }}</p>
                <p class="text-light mb-2"><strong>Department:</strong> {{ selectedApp.branch || 'Computer Science' }}</p>
                <p class="text-light mb-2"><strong>Drive:</strong> {{ selectedApp.drive_name }}</p>
                <p class="text-light mb-2"><strong>Job Title:</strong> {{ selectedApp.job_title }}</p>
                <p class="text-light mb-0"><strong>Status:</strong> <span :class="['status-badge', `status-${selectedApp.status}`]">{{ selectedApp.status }}</span></p>
              </div>
              <button @click="downloadResume(selectedApp.student_id)" class="btn btn-orange fw-bold px-4">
                View Resume
              </button>
            </div>
            <div class="col-md-6 text-center d-flex flex-column justify-content-center align-items-center">
              <div class="avatar-placeholder mb-3">S</div>
              <h5 class="text-white mb-2">{{ selectedApp.student_name }}</h5>
              <p class="text-muted mb-0">Applied On: {{ formatDate(selectedApp.application_date) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Standard Tabbed Views -->
      <div v-else class="fade-in">
        <!-- Tabs -->
        <div class="tab-bar mb-4">
          <button v-for="tab in tabs" :key="tab.key"
            @click="activeTab = tab.key"
            :class="['tab-btn', activeTab === tab.key ? 'tab-active' : '']">
            {{ tab.label }}
            <span v-if="tab.key === 'companies' && pendingCompanies.length > 0" class="badge-pending">{{ pendingCompanies.length }}</span>
            <span v-if="tab.key === 'drives' && pendingDrives.length > 0" class="badge-pending">{{ pendingDrives.length }}</span>
          </button>
        </div>

        <!-- Companies & Applications Tab -->
        <div v-if="activeTab === 'companies'">
          <!-- Company Applications (Pending) -->
          <div class="form-card mb-4" v-if="pendingCompanies.length > 0">
            <h5 class="text-orange fw-bold mb-3">Company Applications (Pending Approval)</h5>
            <div class="table-wrapper">
              <table class="table custom-table">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Industry</th>
                    <th>Location</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="company in pendingCompanies" :key="company.id">
                    <td class="text-muted fw-bold">{{ company.company_name }}</td>
                    <td class="text-muted">{{ company.industry }}</td>
                    <td class="text-muted">{{ company.location }}</td>
                    <td>
                      <div class="d-flex gap-2">
                        <button @click="viewCompanyDetails(company)" class="btn btn-sm btn-outline-orange fw-bold">view details</button>
                        <button @click="updateCompany(company.id, 'approved')" class="btn btn-sm btn-success fw-bold">Approve</button>
                        <button @click="updateCompany(company.id, 'rejected')" class="btn btn-sm btn-danger fw-bold">Reject</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Registered Companies -->
          <div class="form-card">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="text-white mb-0">Registered Companies</h5>
              <input v-model="companySearch" @input="searchCompanies" type="text"
                class="form-control custom-input w-25" placeholder="Search companies..." />
            </div>
            <div class="table-wrapper">
              <table class="table custom-table">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Industry</th>
                    <th>Location</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="company in approvedCompanies" :key="company.id">
                    <td>
                      <div class="fw-bold text-muted">{{ company.company_name }}</div>
                      <div class="text-muted small">{{ company.email }}</div>
                    </td>
                    <td class="text-muted">{{ company.industry }}</td>
                    <td class="text-muted">{{ company.location }}</td>
                    <td>
                      <div class="d-flex gap-2">
                        <button @click="viewCompanyDetails(company)" class="btn btn-sm btn-outline-orange fw-bold">
                          view details
                        </button>
                        <button @click="blacklistCompany(company.id)"
                          :class="['btn btn-sm fw-bold', company.is_blacklisted ? 'btn-warning' : 'btn-outline-warning']">
                          {{ company.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                        </button>
                        <button @click="deleteCompany(company.id)" class="btn btn-sm btn-danger fw-bold">
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Registered Students Tab -->
        <div v-if="activeTab === 'students'">
          <div class="form-card">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="text-white mb-0">Registered Students</h5>
              <input v-model="studentSearch" @input="searchStudents" type="text"
                class="form-control custom-input w-25" placeholder="Search students..." />
            </div>
            <div class="table-wrapper">
              <table class="table custom-table">
                <thead>
                  <tr>
                    <th>Student Name</th>
                    <th>Branch</th>
                    <th>CGPA</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="student in students" :key="student.id">
                    <td>
                      <div class="fw-bold text-muted">{{ student.full_name }}</div>
                      <div class="text-muted small">{{ student.email }}</div>
                    </td>
                    <td class="text-muted">{{ student.branch }}</td>
                    <td class="text-muted">{{ student.cgpa }}</td>
                    <td>
                      <button @click="blacklistStudent(student.id)"
                        :class="['btn btn-sm fw-bold', student.is_blacklisted ? 'btn-warning' : 'btn-outline-warning']">
                        {{ student.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Drives Tab (Aligned to Ongoing Drives) -->
        <div v-if="activeTab === 'drives'">
          <!-- Pending Drives waiting for approval -->
          <div class="form-card mb-4" v-if="pendingDrives.length > 0">
            <h5 class="text-orange fw-bold mb-3">Placement Drive Applications (Pending)</h5>
            <div class="table-wrapper">
              <table class="table custom-table">
                <thead>
                  <tr>
                    <th>Drive</th>
                    <th>Company</th>
                    <th>Job Title</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="drive in pendingDrives" :key="drive.id">
                    <td class="text-muted">{{ drive.drive_name }}</td>
                    <td class="text-muted">{{ drive.company_name }}</td>
                    <td class="text-muted">{{ drive.job_title }}</td>
                    <td>
                      <div class="d-flex gap-2">
                        <button @click="viewDriveDetails(drive)" class="btn btn-sm btn-outline-orange fw-bold">view details</button>
                        <button @click="updateDrive(drive.id, 'approved')" class="btn btn-sm btn-success fw-bold">Approve</button>
                        <button @click="updateDrive(drive.id, 'rejected')" class="btn btn-sm btn-danger fw-bold">Reject</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Ongoing/Approved Drives -->
          <div class="form-card mb-4">
            <h5 class="text-white fw-bold mb-3">Ongoing Drives</h5>
            <div class="table-wrapper">
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
                  <tr v-for="(drive, idx) in approvedDrives" :key="drive.id">
                    <td class="text-muted fw-bold">{{ idx + 1 }}</td>
                    <td class="text-muted">{{ drive.drive_name }}</td>
                    <td class="text-muted">{{ drive.job_title }}</td>
                    <td>
                      <div class="d-flex gap-2">
                        <button @click="viewDriveDetails(drive)" class="btn btn-sm btn-outline-orange fw-bold">
                          view details
                        </button>
                        <button @click="updateDrive(drive.id, 'closed')" class="btn btn-sm btn-success fw-bold">
                          mark as complete
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Closed Drives -->
          <div class="form-card">
            <h5 class="text-white fw-bold mb-3">Closed Drives</h5>
            <div class="table-wrapper" v-if="closedDrives.length > 0">
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
                  <tr v-for="(drive, idx) in closedDrives" :key="drive.id">
                    <td class="text-muted fw-bold">{{ idx + 1 }}</td>
                    <td class="text-muted">{{ drive.drive_name }}</td>
                    <td class="text-muted">{{ drive.job_title }}</td>
                    <td>
                      <div class="d-flex gap-2">
                        <button @click="viewDriveDetails(drive)" class="btn btn-sm btn-outline-orange fw-bold">
                          view details
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-muted text-center py-3">
              No closed drives.
            </div>
          </div>
        </div>

        <!-- Student Applications Tab -->
        <div v-if="activeTab === 'applications'">
          <div class="form-card">
            <h5 class="text-white fw-bold mb-3">Student Applications</h5>
            <div class="table-wrapper">
              <table class="table custom-table">
                <thead>
                  <tr>
                    <th>Sr No.</th>
                    <th>Name</th>
                    <th>Drive</th>
                    <th>Company</th>
                    <th>Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(app, idx) in applications" :key="app.id">
                    <td class="text-muted fw-bold">{{ idx + 1 }}</td>
                    <td class="text-muted fw-bold">{{ app.student_name }}</td>
                    <td class="text-muted">{{ app.drive_name }}</td>
                    <td class="text-muted">{{ app.company_name }}</td>
                    <td class="text-muted">{{ formatDate(app.application_date) }}</td>
                    <td>
                      <button @click="viewAppDetails(app)" class="btn btn-sm btn-orange fw-bold">
                        view
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Reports Tab -->
        <div v-if="activeTab === 'reports'">
          <div class="row g-4 mb-4">
            <!-- Numerical metrics -->
            <div class="col-md-6">
              <div class="form-card h-100">
                <h5 class="text-white fw-bold mb-4">Key Performance Indicators</h5>
                <div class="d-flex flex-column gap-3">
                  <div class="d-flex justify-content-between text-light border-bottom border-secondary pb-2">
                    <span>Total Students:</span>
                    <span class="fw-bold text-orange">{{ reports.total_students || 0 }}</span>
                  </div>
                  <div class="d-flex justify-content-between text-light border-bottom border-secondary pb-2">
                    <span>Registered Companies:</span>
                    <span class="fw-bold text-orange">{{ reports.total_companies || 0 }}</span>
                  </div>
                  <div class="d-flex justify-content-between text-light border-bottom border-secondary pb-2">
                    <span>Total Drives Conducted:</span>
                    <span class="fw-bold text-orange">{{ reports.total_drives || 0 }}</span>
                  </div>
                  <div class="d-flex justify-content-between text-light border-bottom border-secondary pb-2">
                    <span>Total Applications:</span>
                    <span class="fw-bold text-orange">{{ reports.total_applications || 0 }}</span>
                  </div>
                  <div class="d-flex justify-content-between text-light pb-1">
                    <span>Overall Placement Rate:</span>
                    <span class="fw-bold text-success">{{ reports.placement_rate || 0 }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Status Breakdown chart-like representation -->
            <div class="col-md-6">
              <div class="form-card h-100">
                <h5 class="text-white fw-bold mb-4">Application Breakdown</h5>
                <div class="d-flex flex-column gap-3">
                  <div class="breakdown-item d-flex justify-content-between align-items-center w-100">
                    <span class="breakdown-label">Selected</span>
                    <span class="breakdown-count">{{ reports.total_selected || 0 }}</span>
                  </div>
                  <div class="breakdown-item d-flex justify-content-between align-items-center w-100">
                    <span class="breakdown-label">Shortlisted</span>
                    <span class="breakdown-count">{{ reports.total_shortlisted || 0 }}</span>
                  </div>
                  <div class="breakdown-item d-flex justify-content-between align-items-center w-100">
                    <span class="breakdown-label">Rejected</span>
                    <span class="breakdown-count">{{ reports.total_rejected || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Drive wise stats -->
          <div class="form-card">
            <h5 class="text-white fw-bold mb-3">Drive-wise Application Metrics</h5>
            <div class="table-wrapper">
              <table class="table custom-table">
                <thead>
                  <tr>
                    <th>Drive</th>
                    <th>Company</th>
                    <th>Job Title</th>
                    <th>Total Applications</th>
                    <th>Selected</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(drive, index) in reports.drive_stats" :key="index">
                    <td class="text-muted">{{ drive.drive_name }}</td>
                    <td class="text-muted">{{ drive.company_name }}</td>
                    <td class="text-muted">{{ drive.job_title }}</td>
                    <td class="text-muted">{{ drive.total_applications }}</td>
                    <td class="text-muted">{{ drive.selected }}</td>
                    <td>
                      <span :class="['status-badge', `status-${drive.status}`]">{{ drive.status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
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
      activeTab: 'companies',
      tabs: [
        { key: 'companies', label: 'Companies' },
        { key: 'students', label: 'Students' },
        { key: 'drives', label: 'Drives' },
        { key: 'applications', label: 'Student Applications' },
        { key: 'reports', label: 'Reports' }
      ],
      stats: {},
      companies: [],
      drives: [],
      students: [],
      applications: [],
      companySearch: '',
      studentSearch: '',
      globalSearch: '', // Global wireframe search input
      reports: {
        total_selected: 0,
        placement_rate: 0,
        total_shortlisted: 0,
        total_rejected: 0,
        total_applied: 0,
        total_applications: 0,
        drive_stats: []
      },

      // Detail view states to match wireframe
      selectedDrive: null,
      selectedApp: null,
      selectedCompany: null
    }
  },
  computed: {
    pendingCompanies() {
      return this.companies.filter(c => c.approval_status === 'pending')
    },
    approvedCompanies() {
      return this.companies.filter(c => c.approval_status !== 'pending')
    },
    pendingDrives() {
      return this.drives.filter(d => d.status === 'pending')
    },
    approvedDrives() {
      return this.drives.filter(d => d.status === 'approved')
    },
    closedDrives() {
      return this.drives.filter(d => d.status === 'closed')
    }
  },
  async mounted() {
    await this.loadDashboard()
    await this.loadCompanies()
    await this.loadDrives()
    await this.loadStudents()
    await this.loadApplications()
    await this.loadReports()
  },
  watch: {
    activeTab(newTab) {
      if (newTab === 'reports') {
        this.loadReports()
      }
    }
  },
  methods: {
    async loadDashboard() {
      const res = await axios.get('/admin/dashboard')
      this.stats = res.data
    },
    async loadCompanies() {
      const res = await axios.get('/admin/companies')
      this.companies = res.data
    },
    async loadDrives() {
      const res = await axios.get('/admin/drives')
      this.drives = res.data
    },
    async loadStudents() {
      const res = await axios.get('/admin/students')
      this.students = res.data
    },
    async loadApplications() {
      const res = await axios.get('/admin/applications')
      this.applications = res.data
    },
    async searchCompanies() {
      const res = await axios.get(`/admin/companies?search=${this.companySearch}`)
      this.companies = res.data
    },
    async searchStudents() {
      const res = await axios.get(`/admin/students?search=${this.studentSearch}`)
      this.students = res.data
    },
    async performGlobalSearch() {
      // Searches both student and company models based on the wireframe design
      this.companySearch = this.globalSearch
      this.studentSearch = this.globalSearch
      await this.searchCompanies()
      await this.searchStudents()
    },
    async updateCompany(id, status) {
      try {
        await axios.put(`/admin/companies/${id}/approval`, { status })
        await this.loadCompanies()
        await this.loadDashboard()
      } catch (err) {
        alert('Failed to update company status')
      }
    },
    async blacklistCompany(id) {
      try {
        await axios.put(`/admin/companies/${id}/blacklist`)
        await this.loadCompanies()
        await this.loadDrives()
        await this.loadDashboard()
      } catch (err) {
        alert('Failed to blacklist company')
      }
    },
    async updateDrive(id, status) {
      try {
        await axios.put(`/admin/drives/${id}/approval`, { status })
        await this.loadDrives()
        await this.loadDashboard()
        if (this.selectedDrive && this.selectedDrive.id === id) {
          this.selectedDrive.status = status
        }
      } catch (err) {
        alert('Failed to update drive status')
      }
    },
    async blacklistStudent(id) {
      try {
        await axios.put(`/admin/students/${id}/blacklist`)
        await this.loadStudents()
      } catch (err) {
        alert('Failed to blacklist student')
      }
    },
    async deleteCompany(id) {
      if (!confirm('Are you sure? This will delete the company and ALL their drives and applications!')) return
      try {
        await axios.delete(`/admin/companies/${id}`)
        await this.loadCompanies()
        await this.loadDashboard()
        await this.loadReports()
      } catch (err) {
        alert('Failed to delete company')
      }
    },
    async loadReports() {
      const res = await axios.get('/admin/reports')
      this.reports = res.data
    },
    setView(view) {
      if (view === 'dashboard') {
        this.selectedDrive = null
        this.selectedApp = null
        this.selectedCompany = null
      }
    },
    viewDriveDetails(drive) {
      this.selectedDrive = drive
    },
    viewCompanyDetails(company) {
      this.selectedCompany = company
    },
    viewAppDetails(app) {
      this.selectedApp = app
    },
    async downloadResume(studentId) {
      if (!studentId) {
        alert('Resume not found or student ID missing.')
        return
      }
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
.dashboard-nav {
  background: #1e1e2e;
  border-bottom: 1px solid #3a3a5c;
}
.text-orange { color: #f97316; }
.stat-card {
  background: #1e1e2e;
  border: 1px solid #3a3a5c;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}
.stat-icon { font-size: 28px; margin-bottom: 8px; }
.stat-number { font-size: 32px; font-weight: 700; color: #f97316; }
.stat-label { color: #8888aa; font-size: 13px; font-weight: 600; text-transform: uppercase; }
.btn-orange { background: linear-gradient(135deg, #f97316, #ea580c); border: none; color: white; }
.btn-orange:hover { background: linear-gradient(135deg, #ea580c, #c2410c); color: white; }
.btn-outline-orange { border: 1px solid #f97316; color: #f97316; background: transparent; }
.btn-outline-orange:hover { background: #f97316; color: white; }
.tab-bar { display: flex; gap: 8px; border-bottom: 1px solid #3a3a5c; }
.tab-btn { background: none; border: none; color: #8888aa; padding: 10px 20px; font-weight: 600; cursor: pointer; border-bottom: 2px solid transparent; position: relative; }
.tab-active { color: #f97316; border-bottom: 2px solid #f97316; }
.badge-pending { position: absolute; top: 0; right: 0; background: #ef4444; color: white; border-radius: 50%; width: 18px; height: 18px; font-size: 10px; display: flex; align-items: center; justify-content: center; transform: translate(50%, -20%); }
.table-wrapper { background: #1e1e2e; border: 1px solid #3a3a5c; border-radius: 12px; overflow: hidden; }
.custom-table { margin: 0; color: #e2e8f0; }
.custom-table thead th { background: #2a2a3e; color: #cbd5e1; border-color: #3a3a5c; font-size: 12px; text-transform: uppercase; padding: 14px 16px; }
.custom-table tbody td { border-color: #2a2a3e; padding: 14px 16px; vertical-align: middle; color: #f1f5f9; }
.custom-table tbody tr:hover { background: #252535; }
.status-badge { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; text-transform: capitalize; }
.status-approved { background: rgba(34,197,94,0.15); color: #4ade80; }
.status-pending { background: rgba(249,115,22,0.15); color: #fb923c; }
.status-rejected { background: rgba(239,68,68,0.15); color: #f87171; }
.status-closed { background: rgba(148,163,184,0.15); color: #94a3b8; }
.status-selected { background: rgba(34,197,94,0.15); color: #4ade80; }
.status-shortlisted { background: rgba(249,115,22,0.15); color: #fb923c; }
.status-applied { background: rgba(59,130,246,0.15); color: #60a5fa; }
.custom-input { background: #2a2a3e; border: 1px solid #3a3a5c; color: #ffffff; }
.custom-input:focus { background: #2a2a3e; border-color: #f97316; color: #ffffff; box-shadow: none; }
.form-card { background: #1e1e2e; border: 1px solid #3a3a5c; border-radius: 12px; padding: 28px; }
.bg-dark-card { background: #151421; border: 1px solid #2a2a3e; color: #f1f5f9 !important; }
.bg-dark-card * { color: #f1f5f9 !important; }
.whitespace-pre { white-space: pre-wrap; }
.drive-meta-card { background: #1e1e2e; border: 1px solid #3a3a5c; color: #f1f5f9; }
.drive-meta-card strong { color: #f97316; }
.text-muted { color: #94a3b8 !important; }
.text-light { color: #cbd5e1 !important; }
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
.empty-state { text-align: center; padding: 40px; color: #94a3b8; }

/* Reports visual elements */
.breakdown-item { display: flex; align-items: center; gap: 12px; color: #ccccdd; }
.breakdown-label { width: 100px; font-size: 14px; font-weight: 500; }
.breakdown-bar { flex-grow: 1; height: 10px; background: #2a2a3e; border-radius: 5px; overflow: hidden; }
.breakdown-fill { height: 100%; border-radius: 5px; }
.status-selected-fill { background: #22c55e; }
.status-shortlisted-fill { background: #eab308; }
.status-rejected-fill { background: #ef4444; }
.breakdown-count { width: 40px; text-align: right; font-weight: bold; }

.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>