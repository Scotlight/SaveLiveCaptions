# 更新日志 (自 2025-11-29 19:32:52 以来)

基准提交: `6917d9b` (2025-11-29 19:34:18)

---

## 功能增强

### 分段录制和增强字幕处理 (`9db0ef0`)
**日期**: 2025-11-29 19:39:43

主要改进:
- 添加暂停/继续功能，无需重启应用程序
- 实现智能句子提取和去重
- 添加暂停时的文件预览功能
- 改进文本处理，更好的句子分割
- 修复连续句子捕获和缓冲区管理
- 添加对原项目 M-T-Arden 的署名

**涉及文件**:
- `src/function/save.py` - 保存功能增强
- `src/function/texthook.py` - 文本钩子改进
- `src/main.py` - 主程序更新

---

## Bug 修复

### 修复 Live Captions 检测失败问题 (`4393013`)
**日期**: 2025-11-30 11:47:34

- 删除重复的 `lc_detect` 函数定义（第243-250行）
- 重复的函数定义导致第二个函数覆盖第一个，引起导入冲突
- 现在 Live Captions 检测正常工作
- 应用程序启动不再有内部错误，功能完全恢复

### 修复事件循环错误和异步任务处理 (`b1bffb2`)
**日期**: 2025-11-30 10:54:21

- 添加 `pending_tasks` 队列系统处理异步任务
- 修复 "no running event loop" 错误
- 创建 `process_pending_tasks` 函数在正确的事件循环中执行异步操作
- 修改 `poll_loop` 正确处理异步任务队列

### 修复 hook 函数导入错误 (`0042864`)
**日期**: 2025-11-30 10:48:44

- 修复 `start_new_recording` 中错误的 hook 导入
- hook 函数应该从 `function.texthook` 导入，不是 `function.save`
- 修复 `resume_recording` 中的 hook 调用语法
- 修复全局变量声明 (添加 `hook_task`)
- 按钮点击不再出现 ImportError

### 修复 hook_task 未定义错误和缺失函数 (`d3f62db`)
**日期**: 2025-11-30 10:41:46

- 添加缺失的全局变量声明 (`hook_task`, `current_state`)
- 修复 `start_new_recording` 函数中的错误代码
- 添加缺失的 `update_ui_state` 函数
- 添加缺失的 `open_current_caption` 函数
- 添加缺失的 `close_all` 函数
- 修复所有按钮点击回调错误

### 修复语法错误并完成增强版本构建 (`1a622e8`)
**日期**: 2025-11-30 10:28:57

- 修复了 `main_simple_clean.py` 中的多个语法错误
- 添加了 UTF-8 编码声明
- 修复了 async/await 函数结构问题
- 成功构建了 `SaveLiveCaptions_Enhanced.exe`

---

## 代码清理

### 清理不需要的文件 (`063471f`)
**日期**: 2025-11-30 11:04:21

- 删除所有测试文件 (`test_*.py`)
- 删除旧版本文件 (`main_enhanced*.py`, `main_simple_test.py`)
- 删除构建文件和临时文件
- 保留核心功能文件:
  - `src/main.py` (原版)
  - `src/main_simple_clean.py` (最终增强版)
  - `src/function/*` (核心功能模块)

### 替换 main.py 为清理简化版本 (`1e78aae`)
**日期**: 2025-11-30 09:55:56

- 用清理和简化的版本替换 main.py

---

## CI/CD 改进

### 修复 GitHub Actions 工作流拼写错误 (`9e01db8`)
**日期**: 2025-11-29 20:19:08

- 修复工作流名称中 "Artifacts" 拼写
- 修复 "softprops" action 名称拼写
- 确保一致的 exe 命名 (`SaveLiveCaptions`)
- 改进构建和发布流程可靠性

---

## 文件变更统计

| 文件 | 变更 |
|------|------|
| `.github/workflows/deploy.yml` | +6/-1 |
| `src/function/save.py` | +90 行改进 |
| `src/function/texthook.py` | +144 行改进 |
| `src/main.py` | +221 行改进 |
| `src/main_simple_clean.py` | +344 行 (新增) |
