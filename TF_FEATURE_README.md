# ArUco Marker TF (Transform) Framework Feature

## 功能概述
已在 `multi_marker_landing.py` 中新增 TF (Transform) 發佈功能，以 4 個 ArUco 標記的幾何中心為原點建立座標系框架。

## TF 框架結構

```
camera_link (相機座標系)
    └── aruco_origin (4 個 marker 幾何中心)
            ├── marker_0
            ├── marker_1
            ├── marker_2
            └── marker_3
```

## 新增代碼

### 1. 導入模塊 (第 7, 12 行)
```python
from geometry_msgs.msg import PoseStamped, Twist, TransformStamped
from tf2_ros import TransformBroadcaster
```

### 2. 初始化 TF 廣播器 (第 53 行)
```python
self.tf_broadcaster = TransformBroadcaster(self)
```

### 3. 在 markers_callback 中調用 TF 發佈 (第 133 行)
```python
# 發佈 TF 框架
self.publish_marker_transforms()
```

### 4. publish_marker_transforms() 函數 (第 202-253 行)
- **作用**：計算並發佈所有 TF 變換
- **發佈內容**：
  - `aruco_origin`：4 個 marker 幾何中心的位置和旋轉
  - `marker_0`, `marker_1`, `marker_2`, `marker_3`：每個 marker 相對於 `aruco_origin` 的位置

## 使用場景

### 查看 TF 框架
```bash
# 在另一個終端運行
ros2 run tf2_tools view_frames
# 然後查看 /tmp/frames.pdf
```

### 訂閱 TF 資訊
```bash
# 查看所有發佈的 transform
ros2 topic echo /tf

# 查看特定 marker 的位置（相對於 aruco_origin）
ros2 tf2_tools view_frames
```

### 在其他節點中查詢 marker 位置
```python
from tf2_ros import TransformListener, Buffer

# 初始化
tf_buffer = Buffer()
tf_listener = TransformListener(tf_buffer)

# 查詢 marker_0 相對於 aruco_origin 的位置
try:
    transform = tf_buffer.lookup_transform('aruco_origin', 'marker_0', rclpy.time.Time())
    print(f"marker_0 position: {transform.transform.translation}")
except Exception as e:
    print(f"Error: {e}")
```

## 座標系說明

| 框架名稱 | 父框架 | 說明 |
|---------|------|------|
| `camera_link` | - | 相機座標系（固定） |
| `aruco_origin` | `camera_link` | 4 個 marker 幾何中心，作為參考原點 |
| `marker_0/1/2/3` | `aruco_origin` | 各個 marker 相對於幾何中心的位置 |

## 主要優點

1. **模塊化設計**：其他 ROS 節點可以通過 TF 查詢 marker 位置，無需硬編碼計算
2. **RViz 可視化**：可在 RViz 中視覺化所有框架和相對位置
3. **標準化接口**：遵循 ROS TF 框架標準，便於與其他系統集成
4. **動態更新**：每次偵測到 marker 時自動更新 TF

## 驗證功能

編譯並運行節點：
```bash
cd ~/ros2_ws
colcon build --packages-select drone_in_warehouse
source install/setup.bash
ros2 run drone_in_warehouse multi_marker_landing
```

在另一個終端查看 TF：
```bash
ros2 topic echo /tf
```

應該看到類似的輸出：
```
transforms:
- header:
    stamp:
      sec: <timestamp>
      nsec: <nanoseconds>
    frame_id: camera_link
  child_frame_id: aruco_origin
  transform:
    translation:
      x: <avg_x>
      y: <avg_y>
      z: <avg_z>
    rotation:
      x: <qx>
      y: <qy>
      z: <qz>
      w: <qw>
```

## 技術細節

- **更新頻率**：每次收到 marker 消息時更新（`/marker_publisher/markers` 話題）
- **座標系轉換**：使用 scipy 的 `Rotation.from_euler()` 從 yaw 角度轉換為四元數
- **相對位置計算**：marker 位置 - 幾何中心位置
- **時間戳記**：使用 `self.get_clock().now()` 獲取節點時鐘時間

## 後續可能的擴展

1. 發佈 drone 本身的位置相對於 `aruco_origin`
2. 在其他控制節點（如 `attitude_control.py`）中使用這些 TF 資訊
3. 與 SLAM 算法集成，建立全局地圖
4. 支持動態 marker 添加/移除
