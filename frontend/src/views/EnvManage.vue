<template>
  <div>
    <el-card>
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>环境管理</span>
          <el-button type="primary" @click="openDialog()">新增环境</el-button>
        </div>
      </template>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="env_code" label="环境编码" />
        <el-table-column prop="env_name" label="环境名称" />
        <el-table-column prop="env_tags" label="权限标签" />
        <el-table-column label="操作" width="200">
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

    <el-dialog :title="form.id?'编辑环境':'新增环境'" v-model="visible" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="环境编码" required>
          <el-input v-model="form.env_code" placeholder="prod/test/dev/staging" />
        </el-form-item>
        <el-form-item label="环境名称" required>
          <el-input v-model="form.env_name" placeholder="生产环境" />
        </el-form-item>
        <el-form-item label="权限标签">
          <el-input v-model="form.env_tags" placeholder="admin,ops" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" @click="doSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { envApi } from '../api'

const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const size = 20
const visible = ref(false)
const form = ref({})

function openDialog(row) {
  form.value = row ? { ...row } : { env_code: '', env_name: '', env_tags: '' }
  visible.value = true
}

async function fetch() {
  loading.value = true
  const res = await envApi.list({ page: page.value, size })
  tableData.value = res.items
  total.value = res.total
  loading.value = false
}

async function doSave() {
  await envApi.save(form.value)
  ElMessage.success('保存成功')
  visible.value = false
  fetch()
}

async function doRemove(id) {
  await envApi.remove(id)
  ElMessage.success('已删除')
  fetch()
}

onMounted(fetch)
</script>
