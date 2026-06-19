const BASE_URL = 'http://localhost:8000/api/contacts'
const AUTH_URL = 'http://localhost:8000/api/auth'

// ---------- TOKEN HELPERS ----------
function getToken() {
  return localStorage.getItem('access_token')
}

function setTokens(access_token, refresh_token) {
  localStorage.setItem('access_token', access_token)
  if (refresh_token) localStorage.setItem('refresh_token', refresh_token)
}

function clearTokens() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

function authHeaders() {
  const token = getToken()
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

// ---------- AUTH ----------
window.registerUser = async function (user) {
  const response = await fetch(`${AUTH_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  })
  if (!response.ok) {
    const err = await response.json()
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  return await response.json()
}

window.loginUser = async function (email, password) {
  // OAuth2PasswordRequestForm ожидает form-data, а не JSON
  const formData = new URLSearchParams()
  formData.append('username', email)
  formData.append('password', password)

  const response = await fetch(`${AUTH_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  })
  if (!response.ok) {
    const err = await response.json()
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  const data = await response.json()
  setTokens(data.access_token, data.refresh_token)
  return data
}

window.logoutUser = function () {
  clearTokens()
}

window.isLoggedIn = function () {
  return !!getToken()
}

// ---------- CONTACTS ----------
window.getContacts = async function () {
  const response = await fetch(`${BASE_URL}/`, {
    headers: { ...authHeaders() },
  })
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
  return await response.json()
}

window.createContact = async function (contact) {
  const response = await fetch(`${BASE_URL}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(contact),
  })
  if (!response.ok) {
    const err = await response.json()
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  return await response.json()
}

window.updateContact = async function (contact) {
  const response = await fetch(`${BASE_URL}/${contact.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(contact),
  })
  if (!response.ok) {
    const err = await response.json()
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  return await response.json()
}

window.deleteContact = async function (id) {
  const response = await fetch(`${BASE_URL}/${id}`, {
    method: 'DELETE',
    headers: { ...authHeaders() },
  })
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
}

window.searchContacts = async function (query) {
  const params = new URLSearchParams()
  if (query.first_name) params.append('first_name', query.first_name)
  if (query.last_name) params.append('last_name', query.last_name)
  if (query.email) params.append('email', query.email)
  const response = await fetch(`${BASE_URL}/search/?${params}`, {
    headers: { ...authHeaders() },
  })
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
  return await response.json()
}

window.getUpcomingBirthdays = async function () {
  const response = await fetch(`${BASE_URL}/birthdays/upcoming`, {
    headers: { ...authHeaders() },
  })
  if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
  return await response.json()
}