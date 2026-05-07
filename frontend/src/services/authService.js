import api from './api'

export async function registerUser(name, email, password) {
  const { data } = await api.post('/register', { name, email, password })
  return data
}

export async function loginUser(email, password) {
  const { data } = await api.post('/login', { email, password })
  return data
}
