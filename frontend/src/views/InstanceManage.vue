<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>主机实例管理</span>
          <div style="display:flex;gap:8px">
            <el-input v-model="filterGroupId" placeholder="部署组ID" clearable style="width:130px" @change="fetch" />
            <el-button type="primary" @click="openDialog()">新增主机</el-button>
            <el-button @click="batchBindVisible=true">批量绑定部署组</el-button>
          </div>
        </div>
      </template>
      <el-table :data="tableData" v-loading="loading" stripe @selection-change="onSelect">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="deploy_group_id" label="部署组" width="90" />
        <el-table-column prop="instance_ip" label="内网IP" width="150" />
        <el-table-column prop="bk_host_id" label="蓝鲸主机ID" width="120" />
        <el-table-column prop="bk_cloud_id" label="云区域" width="80" />
        <el-table-column prop="bk_inner_ip" label="蓝鲸IP" width="150" />
        <el-table-column prop="instance_tags" label="标签" width="120" />
        <el-table-column prop="instance_status" label="状态" width="100">
          <template #default="{row}">
            <el-switch :model-value="row.instance_status===1" @change="(v)=>toggleStatus(row.id, v?1:0)"
              inline-prompt active-text="正常" inactive-text="维护" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{row}">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" v-model:current-page="page" :total="total" :page-size="size" @current-change="fetch" layout="total,prev,pager,next" />
    </el-card>

    <el-dialog :title="form.id?'编辑主机':'新增主机'" v-model="visible" width="700px">
      <el-form :model="form" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="部署组ID"><el-input v-model="form.deploy_group_id" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="内网IP" required><el-input v-model="form.instance_ip" /></el-form-item></el-col>
        </el-row>
        <el-divider content-position="left">蓝鲸五元组</el-divider>
        <el-row :gutter="16">
          <el-col :span="8"><el-form-item label="业务ID"><el-input v-model="form.bk_biz_id" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="主机ID"><el-input v-model="form.bk_host_id" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="云区域ID"><el-input v-model="form.bk_cloud_id" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="模块ID"><el-input v-model="form.bk_module_id" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="蓝鲸IP"><el-input v-model="form.bk_inner_ip" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="标签"><el-input v-model="form.instance_tags" placeholder="group-a" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" @click="doSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog title="批量绑定部署组" v-model="batchBindVisible" width="400px">
      <el-form label-width="100px">
        <el-form-item label="目标部署组ID">
          <el-input v-model="batchGroupId" />
        </el-form-item>
        <el-form-item>
          <span style="color:#909399">已选 {{ selectedIds.length }} 台主机</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchBindVisible=false">取消</el-button>
        <el-button type="primary" @click="doBatchBind">绑定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { instanceApi } from '../api'

const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const size = 50
const visible = ref(false)
const emptyForm = () => ({ deploy_group_id: 0, instance_ip: '', bk_biz_id: 0, bk_host_id: 0, bk_cloud_id: 0, bk_module_id: 0, bk_inner_ip: '', instance_tags: '' })
const form = reactive(emptyForm())
const filterGroupId = ref('')
const selectedIds = ref([])
const batchBindVisible = ref(false)
const batchGroupId = ref(0)

function openDialog(row) {
  Object.assign(form, row ? { ...row } : emptyForm())
  visible.value = true
}

function onSelect(rows) {
  selectedIds.value = rows.map(r => r.id)
}

async function fetch() {
  loading.value = true
  const params = { page: page.value, size }
  if (filterGroupId.value) params.group_id = filterGroupId.value
  const res = await instanceApi.list(params)
  tableData.value = res.items
  total.value = res.total
  loading.value = false
}

async function doSave() {
  form.deploy_group_id = Number(form.deploy_group_id) || 0
  form.ssh_port = Number(form.ssh_port) || 22
  form.bk_biz_id = Number(form.bk_biz_id) || 0
  form.bk_host_id = Number(form.bk_host_id) || 0
  form.bk_cloud_id = Number(form.bk_cloud_id) || 0
  form.bk_module_id = Number(form.bk_module_id) || 0
  form.instance_status = Number(form.instance_status)
  await instanceApi.save(form)
  ElMessage.success('保存成功')
  visible.value = false
  fetch()
}

async function toggleStatus(id, status) {
  await instanceApi.status(id, status)
  fetch()
}

async function doBatchBind() {
  if (!selectedIds.value.length) return ElMessage.warning('请选择主机')
  await instanceApi.bindGroup(selectedIds.value, Number(batchGroupId.value) || 0)
  ElMessage.success('绑定完成')
  batchBindVisible.value = false
  fetch()
}

onMounted(fetch)
</script>
