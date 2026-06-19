<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>📝 全量操作审计日志（永久留存）</span>
          <div style="display:flex;gap:8px">
            <el-input v-model="filterOperator" placeholder="操作人" clearable style="width:140px" @change="fetch" />
            <el-select v-model="filterOperation" placeholder="操作类型" clearable style="width:160px" @change="fetch">
              <el-option label="发布前置" value="PUBLISH_BEFORE" />
              <el-option label="发布后置" value="PUBLISH_AFTER" />
              <el-option label="新增" value="INSERT" />
              <el-option label="更新" value="UPDATE" />
              <el-option label="删除" value="DELETE" />
              <el-option label="同步" value="SYNC" />
              <el-option label="密钥查看" value="SECRET_QUERY" />
            </el-select>
          </div>
        </div>
      </template>
      <el-table :data="tableData" v-loading="loading" stripe max-height="600">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column prop="operation" label="操作类型" width="140">
          <template #default="{row}">
            <el-tag :type="row.operation==='PUBLISH_BEFORE'?'warning':row.operation==='PUBLISH_AFTER'?'success':row.operation==='DELETE'?'danger':''" size="small">
              {{ row.operation }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_table" label="目标表" width="180" />
        <el-table-column prop="target_biz_key" label="业务标识" width="180" show-overflow-tooltip />
        <el-table-column prop="trace_id" label="Trace ID" width="200" show-overflow-tooltip />
        <el-table-column prop="create_time" label="时间" width="170" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{row}">
            <el-button size="small" link @click="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" v-model:current-page="page" :total="total" :page-size="size" @current-change="fetch" layout="total,prev,pager,next" />
    </el-card>

    <el-dialog title="审计详情" v-model="detailVisible" width="700px">
      <el-descriptions :column="2" border v-if="detailRow">
        <el-descriptions-item label="操作人">{{ detailRow.operator }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">{{ detailRow.operation }}</el-descriptions-item>
        <el-descriptions-item label="目标表">{{ detailRow.target_table }}</el-descriptions-item>
        <el-descriptions-item label="业务标识">{{ detailRow.target_biz_key }}</el-descriptions-item>
        <el-descriptions-item label="Trace ID">{{ detailRow.trace_id }}</el-descriptions-item>
        <el-descriptions-item label="请求IP">{{ detailRow.request_ip || '-' }}</el-descriptions-item>
        <el-descriptions-item label="时间" :span="2">{{ detailRow.create_time }}</el-descriptions-item>
      </el-descriptions>
      <div v-if="detailRow" style="margin-top:16px;display:flex;gap:16px">
        <div style="flex:1">
          <el-divider content-position="left">变更前</el-divider>
          <pre style="background:#f5f7fa;padding:12px;border-radius:4px;max-height:300px;overflow:auto;font-size:12px">{{ JSON.stringify(detailRow.old_data, null, 2) || 'null' }}</pre>
        </div>
        <div style="flex:1">
          <el-divider content-position="left">变更后</el-divider>
          <pre style="background:#f5f7fa;padding:12px;border-radius:4px;max-height:300px;overflow:auto;font-size:12px">{{ JSON.stringify(detailRow.new_data, null, 2) || 'null' }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { auditApi } from '../api'

const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const size = 20
const filterOperator = ref('')
const filterOperation = ref('')
const detailVisible = ref(false)
const detailRow = ref(null)

async function fetch() {
  loading.value = true
  const res = await auditApi.list({ page: page.value, size, operator: filterOperator.value, operation: filterOperation.value })
  tableData.value = res.items
  total.value = res.total
  loading.value = false
}

function showDetail(row) {
  detailRow.value = row
  detailVisible.value = true
}

onMounted(fetch)
</script>
