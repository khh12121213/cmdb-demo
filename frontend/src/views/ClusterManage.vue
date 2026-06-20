<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>应用集群管理</span>
          <el-button type="primary" @click="openDialog()">新增集群</el-button>
        </div>
      </template>
      <div style="margin-bottom:12px;display:flex;gap:12px;flex-wrap:wrap">
        <el-select v-model="filterEnv" placeholder="环境" clearable style="width:120px" @change="fetch">
          <el-option v-for="e in envOptions" :key="e.env_code" :label="e.env_code" :value="e.env_code" />
        </el-select>
        <el-input v-model="filterApp" placeholder="应用编码" clearable style="width:150px" @change="fetch" />
        <el-select v-model="filterMode" placeholder="部署模式" clearable style="width:140px" @change="fetch">
          <el-option label="fixed - 虚拟机" value="fixed" />
          <el-option label="elastic - 容器" value="elastic" />
        </el-select>
        <el-select v-model="filterPlatform" placeholder="容器平台" clearable style="width:160px" @change="fetch">
          <el-option label="TSF容器" value="tsf" />
          <el-option label="TKE K8s" value="tke" />
          <el-option label="原生Docker" value="docker" />
        </el-select>
      </div>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="env_code" label="环境" width="80" />
        <el-table-column prop="app_code" label="应用" width="110" />
        <el-table-column prop="cluster_code" label="集群编码" width="130" />
        <el-table-column prop="cluster_name" label="集群名称" width="140" />
        <el-table-column prop="deploy_mode" label="部署模式" width="110">
          <template #default="{row}">
            <el-tag :type="row.deploy_mode==='fixed'?'info':'success'" size="small">{{ row.deploy_mode==='fixed'?'虚拟机':'容器' }}</el-tag>
          </template>
        </el-table-column>
        <!-- 容器平台列，fixed模式隐藏 -->
        <el-table-column prop="container_platform" label="容器平台" width="110">
          <template #default="{row}">
            <span v-if="row.deploy_mode==='elastic'">{{ row.container_platform || '-' }}</span>
            <span v-else style="color:#aaa">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="tsf_cluster_id" label="TSF集群ID" width="130" show-overflow-tooltip />
        <el-table-column prop="labels" label="灰度标签" width="140" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{row}">
            <el-switch :model-value="row.status===1" @change="(v)=>toggleStatus(row.id, v?1:0)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{row}">
            <el-button size="small" type="primary" link @click="$router.push('/group?env_code='+row.env_code+'&app_code='+row.app_code+'&cluster_id='+row.id)">下钻</el-button>
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="doRemove(row.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" v-model:current-page="page" :total="total" :page-size="size" @current-change="fetch" layout="total,prev,pager,next" />
    </el-card>

    <el-dialog :title="form.id?'编辑集群':'新增集群'" v-model="visible" width="600px">
      <el-form :model="form" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="环境" required>
              <el-select v-model="form.env_code" style="width:100%" filterable>
                <el-option v-for="e in envOptions" :key="e.env_code" :label="e.env_code + '-' + e.env_name" :value="e.env_code" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="应用" required>
              <el-select v-model="form.app_code" style="width:100%" filterable>
                <el-option v-for="a in appOptions" :key="a.app_code" :label="a.app_code + '-' + a.app_name" :value="a.app_code" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="集群编码" required><el-input v-model="form.cluster_code" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="集群名称" required><el-input v-model="form.cluster_name" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="部署模式" required>
          <el-radio-group v-model="form.deploy_mode">
            <el-radio value="fixed">虚拟机(fixed)</el-radio>
            <el-radio value="elastic">容器(elastic)</el-radio>
          </el-radio-group>
        </el-form-item>
        <!-- elastic 模式：容器平台下拉 + 容器字段 -->
        <template v-if="form.deploy_mode==='elastic'">
          <el-form-item label="容器平台" required>
            <el-select v-model="form.container_platform" style="width:100%">
              <el-option value="tsf" label="TSF容器" />
              <el-option value="tke" label="TKE K8s" />
              <el-option value="docker" label="原生Docker" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="form.container_platform==='tsf'" label="TSF集群ID"><el-input v-model="form.tsf_cluster_id" /></el-form-item>
          <el-form-item label="命名空间"><el-input v-model="form.namespace" /></el-form-item>
        </template>
        <!-- fixed 模式：置空容器平台，隐藏容器字段 -->
        <el-form-item label="灰度标签"><el-input v-model="form.labels" placeholder="group-a,group-b" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="允许发布" inactive-text="禁用" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" @click="doSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { clusterApi, envApi, appApi } from '../api'
import { useRoute } from 'vue-router'

const route = useRoute()
const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const size = 20
const visible = ref(false)
const envOptions = ref([])
const appOptions = ref([])
const emptyForm = () => ({ env_code: '', app_code: '', cluster_code: '', cluster_name: '', deploy_mode: 'fixed', container_platform: '', tsf_cluster_id: '', namespace: '', labels: '', status: 1 })
const form = reactive(emptyForm())
const filterEnv = ref(route.query.env_code || '')
const filterApp = ref(route.query.app_code || '')
const filterMode = ref('')
const filterPlatform = ref('')

// fixed模式自动清空container_platform
watch(() => form.deploy_mode, (v) => { if (v === 'fixed') form.container_platform = '' })

function openDialog(row) {
  Object.assign(form, row ? { ...row } : emptyForm())
  if (!row) form.deploy_mode = 'fixed' // default
  visible.value = true
}

async function fetchOptions() {
  envOptions.value = await envApi.all() || []
  const r = await appApi.list({ size: 1000 })
  appOptions.value = r.items || []
}

async function fetch() {
  loading.value = true
  const all = await clusterApi.list({ page: 1, size: 1000 })
  let data = all.items || []
  if (filterEnv.value) data = data.filter(i => i.env_code === filterEnv.value)
  if (filterApp.value) data = data.filter(i => i.app_code === filterApp.value)
  if (filterMode.value) data = data.filter(i => i.deploy_mode === filterMode.value)
  if (filterPlatform.value) data = data.filter(i => i.container_platform === filterPlatform.value)
  const start = (page.value - 1) * size
  tableData.value = data.slice(start, start + size)
  total.value = data.length
  loading.value = false
}

async function doSave() {
  form.status = Number(form.status)
  await clusterApi.save(form)
  ElMessage.success('保存成功')
  visible.value = false
  fetch()
}

async function doRemove(id) {
  await clusterApi.remove(id)
  ElMessage.success('已删除')
  fetch()
}

async function toggleStatus(id, status) {
  await clusterApi.status(id, status)
  fetch()
}

onMounted(() => { fetchOptions(); fetch() })
</script>
