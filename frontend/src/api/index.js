import axios from 'axios'

const api = axios.create({ baseURL: '' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      if (location.pathname !== '/login') location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

// ---------- 鉴权 ----------
export const login = (username, password) =>
  api.post('/api/auth/login', { username, password }).then((r) => r.data)

export const me = () => api.get('/api/auth/me').then((r) => r.data)

// ---------- 内容发现（功能1）----------
export const listPlatforms = () => api.get('/api/content/platforms').then((r) => r.data)

export const searchContent = (payload) =>
  api.post('/api/content/search', payload).then((r) => r.data)

export const fetchTrending = (payload) =>
  api.post('/api/content/trending', payload).then((r) => r.data)

export const listContents = (params) =>
  api.get('/api/content/list', { params }).then((r) => r.data)

// ---------- 购物车 ----------
export const addToCart = (content_id) =>
  api.post('/api/cart/add', { content_id }).then((r) => r.data)

export const getCart = () => api.get('/api/cart').then((r) => r.data)
export const removeFromCart = (id) => api.delete(`/api/cart/${id}`).then((r) => r.data)
export const clearCart = () => api.delete('/api/cart').then((r) => r.data)

// ---------- 洗稿（功能2）----------
export const rewrite = (payload) => api.post('/api/rewrite', payload).then((r) => r.data)
export const listRewrites = () => api.get('/api/rewrite/list').then((r) => r.data)

// ---------- 图片（功能3）----------
export const extractPrompt = (image) =>
  api.post('/api/image/extract_prompt', { image }).then((r) => r.data)
export const generateImages = (payload) =>
  api.post('/api/image/generate', payload).then((r) => r.data)

// ---------- 发布（功能4，admin）----------
export const listAccounts = (platform) =>
  api.get('/api/publish/accounts', { params: platform ? { platform } : {} }).then((r) => r.data)
export const createAccount = (payload) =>
  api.post('/api/publish/accounts', payload).then((r) => r.data)
export const deleteAccount = (id) =>
  api.delete(`/api/publish/accounts/${id}`).then((r) => r.data)
export const publish = (payload) => api.post('/api/publish', payload).then((r) => r.data)
export const listPublishTasks = () =>
  api.get('/api/publish/tasks').then((r) => r.data)

// ---------- 评论（功能5，admin）----------
export const suggestComments = (payload) =>
  api.post('/api/comment/suggest', payload).then((r) => r.data)
