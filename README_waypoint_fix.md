# Nav2 Waypoint Feedback 修復說明

## 問題描述

原始的 `waypoint_publisher_2.py` 有以下問題：

1. **沒有註冊 feedback callback**：在 `send_goal` 方法中，沒有將 `_feedback_cb` 註冊到 action client
2. **使用了錯誤的 feedback 結構**：`NavigateThroughPoses` 的 feedback 結構與 `FollowWaypoints` 不同
3. **代碼中有未使用的 client**：創建了 `FollowWaypoints` 的 client 但沒有使用

## 解決方案

### 1. 新檔案：`waypoint_publisher_fixed.py`

這個修復版本包含以下改進：

- **正確註冊 feedback callback**：在 `send_goal_async` 中添加了 `feedback_callback` 參數
- **支持兩種 action 類型**：
  - `FollowWaypoints`：提供 `current_waypoint` 索引
  - `NavigateThroughPoses`：提供 `current_pose` 和 `navigation_time`
- **改進的 feedback 處理**：根據不同的 action 類型處理不同的 feedback 結構

### 2. 測試檔案：`test_waypoint_action.py`

用於測試 action servers 是否正常工作，包括：
- 檢查 action servers 是否可用
- 測試 feedback 回調是否正常工作
- 觀察 feedback 數據結構

### 3. 測試 Launch 檔案：`test_waypoint_action.launch.py`

啟動完整的 nav2 系統並運行測試腳本。

## 使用方法

### 方法 1：使用修復後的導航腳本

```bash
# 啟動 nav2 系統
ros2 launch drone_in_warehouse rtab_slam3d.launch.py

# 在另一個終端運行修復後的導航腳本
ros2 run drone_in_warehouse waypoint_publisher_fixed.py
```

### 方法 2：使用測試腳本驗證

```bash
# 運行測試
ros2 launch drone_in_warehouse test_waypoint_action.launch.py
```

## 關鍵改進

### FollowWaypoints 提供路徑點索引：
```python
if hasattr(fb, 'current_waypoint'):
    self.current_waypoint_index = int(fb.current_waypoint)
    self.get_logger().info(f'Current waypoint index: {self.current_waypoint_index}')
```

### NavigateThroughPoses 提供位置信息：
```python
if hasattr(fb, 'current_pose'):
    current_pose = fb.current_pose
    self.get_logger().info(f'Current pose: x={current_pose.pose.position.x:.2f}, y={current_pose.pose.position.y:.2f}')
```

### 正確的 callback 註冊：
```python
send_goal_future = self._action_client.send_goal_async(
    goal_msg, feedback_callback=self._feedback_cb
)
```

## 配置說明

確保你的 `bringup_params.yaml` 或 `turtlebot3_params.yaml` 中包含 `waypoint_follower` 配置：

```yaml
waypoint_follower:
  ros__parameters:
    use_sim_time: true
    loop_rate: 20
    stop_on_failure: false
    action_server_result_timeout: 900.0
    waypoint_task_executor_plugin: "wait_at_waypoint"
    wait_at_waypoint:
      plugin: "nav2_waypoint_follower::WaitAtWaypoint"
      enabled: True
      waypoint_pause_duration: 200
```

## 切換 Action 類型

在 `waypoint_publisher_fixed.py` 中，你可以通過修改以下行來切換使用哪種 action：

```python
self.use_follow_waypoints = True   # 使用 FollowWaypoints (推薦，提供路徑點索引)
# 或
self.use_follow_waypoints = False  # 使用 NavigateThroughPoses
```

## 預期輸出

使用修復後的腳本，你應該能看到類似以下的輸出：

```
[INFO] [waypoint_navigator_client]: Current waypoint index: 0
[INFO] [waypoint_navigator_client]: Distance remaining: 2.34 meters
[INFO] [waypoint_navigator_client]: Current waypoint index: 1
[INFO] [waypoint_navigator_client]: Distance remaining: 1.12 meters
```

這表示你現在可以正確接收和處理 nav2 的 waypoint 狀態了！
