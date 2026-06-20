import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

api.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err.response?.data?.detail || err.message || '请求失败'
    ElMessage.error(msg)
    return Promise.reject(err)
  }
)

// ===== 环境 =====
export const envApi = {
  list: (params) => api.get('/admin/env/list', { params }),
  all: () => api.get('/admin/env/all'),
  save: (data) => api.post('/admin/env/save', data),
  remove: (id) => api.put('/admin/env/remove', { id }),
}

// ===== 系统 =====
export const sysApi = {
  list: (params) => api.get('/admin/sys/list', { params }),
  save: (data) => api.post('/admin/sys/save', data),
  remove: (id) => api.put('/admin/sys/remove', { id }),
}

// ===== 应用 =====
export const appApi = {
  list: (params) => api.get('/admin/app/list', { params }),
  all: () => api.get('/admin/app/all'),
  save: (data) => api.post('/admin/app/save', data),
  detail: (id) => api.get('/admin/app/detail', { params: { id } }),
  remove: (id) => api.put('/admin/app/remove', { id }),
}

// ===== 集群 =====
export const clusterApi = {
  list: (params) => api.get('/admin/cluster/list', { params }),
  save: (data) => api.post('/admin/cluster/save', data),
  status: (id, status) => api.put('/admin/cluster/status', { id, status }),
  remove: (id) => api.put('/admin/cluster/remove', { id }),
}

// ===== 部署组 =====
export const groupApi = {
  list: (params) => api.get('/admin/group/list', { params }),
  save: (data) => api.post('/admin/group/save', data),
  remove: (id) => api.put('/admin/group/remove', { id }),
}

// ===== 主机 =====
export const instanceApi = {
  list: (params) => api.get('/admin/instance/list', { params }),
  save: (data) => api.post('/admin/instance/save', data),
  status: (id, status) => api.put('/admin/instance/status', { id, status }),
  bindGroup: (ids, group_id) => api.put('/admin/instance/bind-group', { ids, group_id }),
}

// ===== 变量 =====
export const variableApi = {
  list: (params) => api.get('/admin/variable/list', { params }),
  save: (data) => api.post('/admin/variable/save', data),
  remove: (id) => api.delete('/admin/variable/remove', { params: { id } }),
}

// ===== 发布基线 / 快照 / 审计 =====
export const releaseApi = {
  baseline: (params) => api.get('/admin/release/baseline', { params }),
  snaps: (params) => api.get('/admin/release/instance-snaps', { params }),
}

export const auditApi = {
  list: (params) => api.get('/admin/audit/list', { params }),
}

export const enumsApi = {
  get: () => api.get('/admin/enums'),
}

export default api
