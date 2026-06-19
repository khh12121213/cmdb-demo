<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>集群管理</span>
          <el-button type="primary" @click="openDialog()">新增集群</el-button>
        </div>
      </template>
      <div style="margin-bottom:12px;display:flex;gap:12px">
        <el-input v-model="filterEnv" placeholder="环境编码" clearable style="width:150px" @change="fetch" />
        <el-input v-model="filterApp" placeholder="应用编码" clearable style="width:150px" @change="fetch" />
      </div>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="env_code" label="环境" width="100" />
        <el-table-column prop="app_code" label="应用" width="120" />
        <el-table-column prop="cluster_code" label="集群编码" width="140" />
        <el-table-column prop="cluster_name" label="集群名称" width="140" />
        <el-table-column prop="deploy_mode" label="部署模式" width="100">
          <template #default="{row}">
            <el-tag :type="row.deploy_mode==='fixed'?'info':'success'">{{ row.deploy_mode }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{row}">
            <el-switch :model-value="row.status===1" @change="(v)=>toggleStatus(row.id, v?1:0)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{row}">
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

    <el-dialog :title="form.id?'编辑集群':'新增集群'" v-model="visible" width="550px">
      <el-form :model="form" label-width="110px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="环境" required>
              <el-input v-model="form.env_code" placeholder="prod" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="应用" required>
              <el-input v-model="form.app_code" placeholder="loan-core" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="集群编码" required><el-input v-model="form.cluster_code" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="集群名称" required><el-input v-model="form.cluster_name" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="部署模式" required>
          <el-radio-group v-model="form.deploy_mode">
            <el-radio value="fixed">固定主机(fixed)</el-radio>
            <el-radio value="elastic">TSF弹性容器(elastic)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.deploy_mode==='elastic'" label="TSF集群ID"><el-input v-model="form.tsf_cluster_id" /></el-form-item>
        <el-form-item v-if="form.deploy_mode==='elastic'" label="命名空间"><el-input v-model="form.namespace" /></el-form-item>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { clusterApi } from '../api'

const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const size = 20
const visible = ref(false)
const emptyForm = () => ({ env_code: '', app_code: '', cluster_code: '', cluster_name: '', deploy_mode: 'fixed', tsf_cluster_id: '', namespace: '', labels: '', status: 1 })
const form = reactive(emptyForm())
const filterEnv = ref('')
const filterApp = ref('')

function openDialog(row) {
  Object.assign(form, row ? { ...row } : emptyForm())
  visible.value = true
}

async function fetch() {
  loading.value = true
  const res = await clusterApi.list({ page: page.value, size, env_code: filterEnv.value, app_code: filterApp.value })
  tableData.value = res.items
  total.value = res.total
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

onMounted(fetch)
</script>
