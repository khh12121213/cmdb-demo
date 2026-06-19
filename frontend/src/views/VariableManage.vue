<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>多级变量配置</span>
          <div style="display:flex;gap:8px">
            <el-input v-model="filterEnv" placeholder="环境" clearable style="width:120px" @change="fetch" />
            <el-input v-model="filterApp" placeholder="应用" clearable style="width:120px" @change="fetch" />
            <el-button type="primary" @click="openDialog()">新增变量</el-button>
          </div>
        </div>
      </template>
      <el-alert title="变量优先级：应用级 → 集群级 → 部署组级 → 主机实例级（逐级覆盖）" type="info" :closable="false" style="margin-bottom:12px" />
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="env_code" label="环境" width="80" />
        <el-table-column prop="app_code" label="应用" width="110" />
        <el-table-column prop="var_key" label="变量名" width="160" />
        <el-table-column prop="var_value" label="变量值" min-width="200" show-overflow-tooltip />
        <el-table-column label="层级" width="120">
          <template #default="{row}">
            <el-tag v-if="row.group_code" type="warning" size="small">部署组级</el-tag>
            <el-tag v-else-if="row.cluster_code" type="primary" size="small">集群级</el-tag>
            <el-tag v-else-if="row.instance_id>0" type="danger" size="small">主机级</el-tag>
            <el-tag v-else size="small">应用级</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
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
    </el-card>

    <el-dialog :title="form.id?'编辑变量':'新增变量'" v-model="visible" width="550px">
      <el-form :model="form" label-width="110px">
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="环境" required><el-input v-model="form.env_code" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="应用" required><el-input v-model="form.app_code" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="主机ID"><el-input v-model="form.instance_id" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="集群编码"><el-input v-model="form.cluster_code" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="分组编码"><el-input v-model="form.group_code" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="主机ID"><el-input v-model="form.instance_id" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="变量名" required><el-input v-model="form.var_key" placeholder="DB_URL / APP_ENV / ..." /></el-form-item>
        <el-form-item label="变量值" required>
          <el-input v-model="form.var_value" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" /></el-form-item>
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
import { variableApi } from '../api'

const tableData = ref([])
const loading = ref(false)
const visible = ref(false)
const emptyForm = () => ({ env_code: '', app_code: '', cluster_code: '', group_code: '', instance_id: 0, var_key: '', var_value: '', remark: '' })
const form = reactive(emptyForm())
const filterEnv = ref('')
const filterApp = ref('')

function openDialog(row) {
  Object.assign(form, row ? { ...row } : emptyForm())
  visible.value = true
}

async function fetch() {
  loading.value = true
  const res = await variableApi.list({ env_code: filterEnv.value, app_code: filterApp.value })
  tableData.value = res.items
  loading.value = false
}

async function doSave() {
  form.instance_id = Number(form.instance_id) || 0
  await variableApi.save(form)
  ElMessage.success('保存成功')
  visible.value = false
  fetch()
}

async function doRemove(id) {
  await variableApi.remove(id)
  ElMessage.success('已删除')
  fetch()
}

onMounted(fetch)
</script>
