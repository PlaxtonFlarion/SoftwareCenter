# 性能实战教学

README 只保留性能能力边界和入口说明；需要完整蓝本样例与典型跑法时，直接看这里。

## 阅读顺序
- 想看端到端体验：先看 `E2E / ASR / VAD / tokens/s`
- 想看资源趋势：再看 `Android 内存基线 / 内存泄漏 / 流畅度`
- 想做稳定性扰动：最后看 `Android Monkey`

## 能力速览
| 类型 | 入口 |
|------|------|
| 视觉真值 | Framix 帧分析与阶段报告 |
| 指标采样 | Memrix 内存 / 流畅度 / 趋势对比 |
| 稳定性扰动 | Monkey + logcat 异常留痕 |
| 典型跑法 | `mind --plan --code ...` 或 `mind --chat "..."` |

下面几个 `cfg` 蓝本示例默认都用同一条命令运行：
```bash
mind --plan --code example.md
```

## E2E 耗时、ASR 首字上屏、VAD 尾字上屏、流式 tokens/s
``````
```cfg
attempts: 3
stop_on_fail: false

item_prefix: |
  每轮任务开始前，先确认测试设备在线且目标应用可拉起。
```

# name: performance-001
录制一次完整交互流程，再生成 Framix 阶段报告。

steps = [
  {
    "tool": "scrcpy_record",
    "args": {
      "directory": "/tmp/mind_perf/e2e",
      "fps": 30
    }
  },
  {
    "tool": "app_foreground",
    "args": {
      "package": "com.example.app"
    }
  },
  {
    "tool": "wait_element",
    "args": {
      "by": "text",
      "value": "输入框",
      "timeout": 10,
      "state": "exists"
    }
  },
  {
    "tool": "click",
    "args": {
      "by": "text",
      "value": "输入框"
    }
  },
  {
    "tool": "input_text",
    "args": {
      "value": "你好"
    }
  },
  {
    "tool": "press_enter",
    "args": {}
  },
  {
    "tool": "wait_element",
    "args": {
      "by": "text",
      "value": "回复完成",
      "timeout": 20,
      "state": "exists"
    }
  },
  {
    "tool": "scrcpy_close",
    "args": {}
  },
  {
    "tool": "fx_frame_analyzer",
    "args": {
      "title": "performance_e2e",
      "scale": 0.4
    }
  },
  {
    "tool": "fx_frame_reporter",
    "args": {}
  }
]
---
`````` 

## Android 内存基线
``````
```cfg
repeat: 10

loop_suffix: |
  所有轮次结束后，统一生成分层内存报告。
```

# name: performance-001
对首页进入流程做重复采样，建立内存基线。

steps = [
  {
    "tool": "mx_sample_mem",
    "args": {
      "focus": "com.example.app",
      "title": "mem_baseline"
    }
  },
  {
    "tool": "app_foreground",
    "args": {
      "package": "com.example.app"
    }
  },
  {
    "tool": "wait_element",
    "args": {
      "by": "text",
      "value": "首页",
      "timeout": 10,
      "state": "exists"
    }
  },
  {
    "tool": "sleep",
    "args": {
      "delay": 5
    }
  },
  {
    "tool": "mx_task_final",
    "args": {}
  },
  {
    "tool": "mx_mem_reporter",
    "args": {
      "layer": true
    }
  }
]
---
`````` 

## Android 内存泄漏
``````
```cfg
loop_suffix: |
  所有轮次结束后，统一生成内存报告。
```

# name: performance-001
围绕同一业务流重复进出页面，观察内存是否持续抬升。

steps = [
  {
    "tool": "mx_sample_mem",
    "args": {
      "focus": "com.example.app",
      "title": "mem_leak"
    }
  },
  {
    "tool": "app_foreground",
    "args": {
      "package": "com.example.app"
    }
  },
  {
    "tool": "wait_element",
    "args": {
      "by": "text",
      "value": "首页",
      "timeout": 10,
      "state": "exists"
    }
  },
  {
    "tool": "scroll_into_view",
    "args": {
      "by": "text",
      "value": "详情",
      "direction": "down",
      "timeout": 10,
      "max_swipes": 6,
      "should_click": true
    }
  },
  {
    "tool": "go_back",
    "args": {}
  },
  {
    "tool": "sleep",
    "args": {
      "delay": 3
    }
  },
  {
    "tool": "mx_task_final",
    "args": {}
  },
  {
    "tool": "mx_mem_reporter",
    "args": {}
  }
]
---
`````` 

## Android 流畅度
``````
```cfg
loop_suffix: |
  所有轮次结束后，统一生成流畅度报告。
```

# name: performance-001
对典型页面滚动和进入流程做图形采样，输出流畅度报告。

steps = [
  {
    "tool": "mx_sample_gfx",
    "args": {
      "focus": "com.example.app",
      "title": "gfx_baseline"
    }
  },
  {
    "tool": "app_foreground",
    "args": {
      "package": "com.example.app"
    }
  },
  {
    "tool": "wait_element",
    "args": {
      "by": "text",
      "value": "首页",
      "timeout": 10,
      "state": "exists"
    }
  },
  {
    "tool": "scroll",
    "args": {
      "direction": "down",
      "x": 500,
      "y": 1200,
      "duration": 350
    }
  },
  {
    "tool": "scroll",
    "args": {
      "direction": "up",
      "x": 500,
      "y": 600,
      "duration": 350
    }
  },
  {
    "tool": "sleep",
    "args": {
      "delay": 3
    }
  },
  {
    "tool": "mx_task_final",
    "args": {}
  },
  {
    "tool": "mx_gfx_reporter",
    "args": {}
  }
]
---
`````` 

## Android Monkey
``````
# name: monkey-001
对目标应用执行一次固定参数的 Monkey 扰动，并保留日志证据。

steps = [
  {
    "tool": "file_logcat_clean",
    "args": {}
  },
  {
    "tool": "injection",
    "args": {
      "package": "com.example.app",
      "seed": 42,
      "throttle_ms": 150,
      "touch": 65,
      "motion": 20,
      "nav": 10,
      "events": 10000
    }
  },
  {
    "tool": "file_logcat_dump",
    "args": {
      "keywords": ["Crash", "ANR", "FATAL EXCEPTION"],
      "level": "W",
      "max_lines": 200,
      "saved": "/tmp/mind_perf/monkey_logcat"
    }
  }
]
---
`````` 

说明：
- 同类目标也可以用英文或日文描述，执行语义保持一致
- 如果更偏批跑回归，建议把 Monkey 任务写入 `--code` 蓝本统一管理
