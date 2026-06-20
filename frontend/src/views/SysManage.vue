<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>业务系统管理</span>
          <el-button type="primary" @click="openAdd">新增系统</el-button>
        </div>
      </template>
      <div style="margin-bottom:12px;display:flex;gap:12px">
        <el-input v-model="filterName" placeholder="系统名称 / 编码" clearable style="width:200px" @change="fetch" />
        <el-input v-model="filterDev" placeholder="研发负责人" clearable style="width:150px" @change="fetch" />
        <el-input v-model="filterOps" placeholder="运维负责人" clearable style="width:150px" @change="fetch" />
      </div>
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="sys_code" label="系统编码" width="130" />
        <el-table-column prop="sys_name" label="系统名称" width="150" />
        <el-table-column prop="dev_owner" label="研发负责人" width="120" />
        <el-table-column prop="ops_owner" label="运维负责人" width="120" />
        <el-table-column prop="remark" label="系统描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="240">
          <template #default="{row}">
            <el-button size="small" type="primary" link @click="$router.push('/app?sys_id='+row.id)">下钻</el-button>
            <el-button size="small" link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="doRemove(row.id)">
              <template #reference>
                <el-button size="small" link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination style="margin-top:12px" v-model:current-page="page" :total="total" :page-size="size" @current-change="fetch" layout="total,prev,pager,next" />
    </el-card>

    <el-dialog :title="form.id?'编辑系统':'新增系统'" v-model="visible" width="650px">
      <el-form :model="form" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="系统编码" required><el-input v-model="form.sys_code" :disabled="!!form.id" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="系统名称" required><el-input v-model="form.sys_name" /></el-form-item></el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="研发负责人"><el-input v-model="form.dev_owner" placeholder="支持逗号分隔多账号" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="运维负责人"><el-input v-model="form.ops_owner" placeholder="支持逗号分隔多账号" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="系统描述"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="visible=false">取消</el-button><el-button type="primary" @click="doSave">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { sysApi } from '../api'

const items = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(20)
const loading = ref(false)
const visible = ref(false)
const filterName = ref('')
const filterDev = ref('')
const filterOps = ref('')

const emptyForm = () => ({ id: 0, sys_code: '', sys_name: '', dev_owner: '', ops_owner: '', remark: '' })
const form = reactive(emptyForm())

async function fetch() {
  loading.value = true
  const r = await sysApi.list({ page: page.value, size: size.value })
  let data = r.items
  if (filterName.value) data = data.filter(i => i.sys_code.includes(filterName.value) || i.sys_name.includes(filterName.value))
  if (filterDev.value) data = data.filter(i => i.dev_owner?.includes(filterDev.value))
  if (filterOps.value) data = data.filter(i => i.ops_owner?.includes(filterOps.value))
  items.value = data
  total.value = r.total
  loading.value = false
}

function openAdd() { Object.assign(form, emptyForm()); visible.value = true }
function openEdit(row) { Object.assign(form, row); visible.value = true }

async function doSave() {
  await sysApi.save(form)
  ElMessage.success('保存成功')
  visible.value = false; fetch()
}

async function doRemove(id) {
  await sysApi.remove(id)
  ElMessage.success('已删除')
  fetch()
}

onMounted(fetch)
</script>
