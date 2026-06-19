<template>
  <div style="display:flex;flex-direction:column;gap:16px">
    <el-card>
      <template #header><span>📦 发布基线历史</span></template>
      <div style="margin-bottom:12px;display:flex;gap:12px">
        <el-input v-model="filterEnv" placeholder="环境" clearable style="width:120px" @change="fetch" />
        <el-input v-model="filterApp" placeholder="应用" clearable style="width:120px" @change="fetch" />
      </div>
      <el-table :data="baselines" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="env_code" label="环境" width="70" />
        <el-table-column prop="app_code" label="应用" width="100" />
        <el-table-column prop="group_code" label="分组" width="120" />
        <el-table-column prop="build_no" label="构建编号" width="140" />
        <el-table-column prop="artifact_version" label="版本备注" width="180" show-overflow-tooltip />
        <el-table-column prop="release_user" label="操作人" width="100" />
        <el-table-column prop="release_time" label="发布时间" width="170" />
        <el-table-column prop="release_status" label="结果" width="100">
          <template #default="{row}">
            <el-tag :type="row.release_status==='success'?'success':row.release_status==='fail'?'danger':'warning'" size="small">
              {{ row.release_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_current" label="当前" width="80">
          <template #default="{row}">
            <el-tag v-if="row.is_current" type="success" size="small">生效中</el-tag>
            <span v-else style="color:#c0c4cc">—</span>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" v-model:current-page="page" :total="total" :page-size="size" @current-change="fetch" layout="total,prev,pager,next" />
    </el-card>

    <el-card>
      <template #header><span>📋 单机实例发布快照</span></template>
      <div style="margin-bottom:12px">
        <el-input v-model="filterInstId" placeholder="实例ID" @change="fetchSnaps" style="width:150px;margin-right:8px" />
        <el-button @click="fetchSnaps">查询</el-button>
      </div>
      <el-table :data="snaps" v-loading="snapLoading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="instance_id" label="实例ID" width="90" />
        <el-table-column prop="instance_ip" label="IP" width="150" />
        <el-table-column prop="cluster_release_id" label="基线ID" width="90" />
        <el-table-column prop="build_no" label="构建编号" width="140" />
        <el-table-column prop="current_version" label="版本" width="180" show-overflow-tooltip />
        <el-table-column prop="deploy_time" label="部署时间" width="170" />
        <el-table-column prop="deploy_result" label="结果" width="100">
          <template #default="{row}">
            <el-tag :type="row.deploy_result==='success'?'success':'danger'" size="small">{{ row.deploy_result }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" v-model:current-page="snapPage" :total="snapTotal" :page-size="20" @current-change="fetchSnaps" layout="total,prev,pager,next" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { releaseApi } from '../api'

const baselines = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const size = 20
const filterEnv = ref('')
const filterApp = ref('')

const snaps = ref([])
const snapLoading = ref(false)
const snapPage = ref(1)
const snapTotal = ref(0)
const filterInstId = ref(0)

async function fetch() {
  loading.value = true
  const res = await releaseApi.baseline({ page: page.value, size, env_code: filterEnv.value, app_code: filterApp.value })
  baselines.value = res.items
  total.value = res.total
  loading.value = false
}

async function fetchSnaps() {
  snapLoading.value = true
  const params = { page: snapPage.value, size: 20 }
  if (filterInstId.value) params.instance_id = filterInstId.value
  const res = await releaseApi.snaps(params)
  snaps.value = res.items
  snapTotal.value = res.total
  snapLoading.value = false
}

onMounted(() => { fetch(); fetchSnaps() })
</script>
