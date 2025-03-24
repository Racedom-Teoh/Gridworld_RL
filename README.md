# 強化學習報告 - HW1-1

# 1. 設計概念

HW1-1 的目標是透過 Flask 架構建立一個 **n x n** 的互動式格子地圖，具體目標包括：

- **格子地圖生成**：使用者可以指定地圖的大小 (3 ≤ n ≤ 7)，生成對應的 n x n 網格。
- **用戶交互**：
    - 點擊格子設置 **起始點**（綠色顯示）。
    - 點擊格子設置 **終點**（紅色顯示）。
    - 允許用戶設置 **障礙物**（灰色顯示），最多可設置 n-2 個。
- **動態更新**：用戶透過按鈕和互動操作，將網格狀態同步到後端。

此功能作為強化學習環境的基礎，提供政策與價值迭代的視覺化展示，方便用戶直觀理解強化學習算法的行為。

## 2. ChatGPT Prompt 範例

> "我需要建立一個使用 Flask 框架的 Web 應用，實現一個互動式的 n x n 格子地圖 (n 的範圍為 3 到 7)。用戶能夠透過點擊網格來設置：
> 
> - **起始點**（綠色標示）。
> - **終點**（紅色標示）。
> - **障礙物**（灰色標示，最多 n-2 個）。
> 
> 當用戶輸入網格大小時，系統應動態生成對應的網格。每個格子需要支援用戶點擊操作，根據點擊次數依序標記起點、終點和障礙物。
> 
> 請幫我撰寫 Flask 程式碼，並確保前端使用 HTML + CSS + JavaScript，以 AJAX 方式與後端溝通，實現格子狀態的即時更新與顯示。"
> 

## 3. 相關 Code（含註解）

### **(A) 前端：index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>GridWorld - Value Iteration</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
    <h1>GridWorld with Value Iteration</h1>

    <!-- 設定網格大小並生成網格的按鈕 -->
    <label>Grid Size (3-9): <input type="number" id="grid-size" min="3" max="9" value="5"></label>
    <button onclick="generateGrid()">Generate Grid</button>

    <p>Click cells to set: Start (Green) → Goal (Red) → Obstacles (Gray)</p>

    <!-- 網格容器 -->
    <div class="grid-container">
        <div id="grid" class="grid"></div>
    </div>

    <script>
        // 初始化變量
        let n = 5, start = null, goal = null, obstacles = new Set(), maxObstacles = n - 2;

        // 生成 n x n 網格
        function generateGrid() {
            n = parseInt(document.getElementById("grid-size").value);
            start = goal = null;
            obstacles.clear();
            maxObstacles = n - 2;

            const grid = document.getElementById("grid");
            grid.innerHTML = "";
            grid.style.gridTemplateColumns = `repeat(${n}, 50px)`;

            for (let i = 0; i < n; i++) {
                for (let j = 0; j < n; j++) {
                    const cell = document.createElement("div");
                    cell.classList.add("cell");
                    cell.dataset.row = i;
                    cell.dataset.col = j;
                    cell.onclick = () => handleCellClick(cell, i, j);
                    grid.appendChild(cell);
                }
            }
        }

        // 處理格子點擊事件
        function handleCellClick(cell, i, j) {
            const id = `${i},${j}`;

            if (!start) {
                // 設置起始點
                start = id;
                cell.classList.add("start");
            } else if (!goal) {
                // 設置終點
                goal = id;
                cell.classList.add("goal");
            } else if (obstacles.size < maxObstacles && !obstacles.has(id)) {
                // 設置障礙物
                obstacles.add(id);
                cell.classList.add("obstacle");
            }
        }

        // 初始化生成網格
        generateGrid();
    </script>

    <style>
        body {
            font-family: 'Orbitron', sans-serif;
            text-align: center;
            background: #1a1a3b;
            color: white;
        }
        .grid-container {
            display: flex;
            justify-content: center;
            margin-top: 30px;
        }
        .grid {
            display: grid;
            gap: 5px;
        }
        .cell {
            width: 50px;
            height: 50px;
            border: solid 1px #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .start { background: #00ff00; }
        .goal { background: #ff0000; }
        .obstacle { background: #808080; }
    </style>
</body>
</html>

```

### **(B) 後端：app.py**

```python
from flask import Flask, render_template

# 初始化 Flask 應用
app = Flask(__name__)

# 主頁路由，渲染 index.html
@app.route("/")
def index():
    return render_template("index.html")

# 啟動 Flask 應用
if __name__ == "__main__":
    app.run(debug=True)

```

# **強化學習報告 - HW1-2**

## 1. 設計概念

HW1-2 的目標是透過 Flask Web 應用，針對格子地圖環境實現隨機政策生成與政策評估。具體目標包括：

- **隨機政策生成**：
    - 為每個格子隨機生成一個行動（↑、↓、←、→）。
    - 目標格子以 "G" 表示。
- **政策評估**：
    - 使用 Bellman 方程計算每個狀態的價值函數 V(s)。
    - 依據隨機政策，計算各格子的期望回報。
- **視覺化展示**：
    - 顯示隨機政策矩陣，呈現每個格子建議的移動方向。
    - 顯示價值函數矩陣，展示各格子的預期回報值。

此部分為強化學習中政策評估過程的核心，幫助理解在隨機行動策略下，環境中各個狀態的價值。

## 2. ChatGPT Prompt 範例

> "我正在開發一個基於 Flask 的強化學習應用，目的是在一個 n x n 的格子地圖中實現 隨機政策生成 與 政策評估。
> 
> 1. **隨機政策生成**
>     - 每個格子應隨機選擇一個行動（↑、↓、←、→）。
>     - 目標格子以 "G" 標示，障礙物不可選擇行動。
> 2. **政策評估**
>     - 根據 Bellman 方程對當前政策進行價值計算，估算每個格子的期望回報。
> 
> 請生成 Flask 程式碼，確保政策與價值矩陣能透過前端頁面動態呈現，並支援用戶一鍵觸發政策評估與結果顯示。"
> 

## 3. 相關 Code（含註解）

### **(A) 前端：index.html**

此部分擴展 HW1-1，增加了兩個新按鈕，分別用於生成隨機政策與執行政策評估。

```html
<button onclick="generateRandomPolicy()">Generate Random Policy</button>
<button onclick="runPolicyEvaluation()">Run Policy Evaluation</button>

<script>
    // 發送請求生成隨機政策
    function generateRandomPolicy() {
        fetch("/generate_random_policy", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ n, start, goal, obstacles: Array.from(obstacles) })
        })
        .then(response => response.json())
        .then(data => {
            displayMatrix("policy-matrix", data.policy_matrix, true);
            displayMatrix("value-matrix", data.value_matrix, false);
        });
    }

    // 發送請求執行政策評估
    function runPolicyEvaluation() {
        fetch("/run_policy_evaluation", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ n, start, goal, obstacles: Array.from(obstacles) })
        })
        .then(response => response.json())
        .then(data => {
            displayMatrix("value-matrix", data.value_matrix);
        });
    }

    // 顯示矩陣 (政策或價值)
    function displayMatrix(elementId, matrix, isPolicy = false) {
        const container = document.getElementById(elementId);
        container.innerHTML = "";

        for (let i = 0; i < n; i++) {
            const rowDiv = document.createElement("div");
            rowDiv.classList.add("matrix-row");
            rowDiv.style.display = "flex";

            for (let j = 0; j < n; j++) {
                const cellDiv = document.createElement("div");
                cellDiv.classList.add("matrix-cell");
                cellDiv.style.margin = "5px";

                // 根據矩陣類型設置值
                if (isPolicy) {
                    cellDiv.textContent = matrix[i][j];  // 顯示政策
                } else {
                    cellDiv.textContent = matrix[i][j].toFixed(2);  // 顯示價值
                }

                rowDiv.appendChild(cellDiv);
            }
            container.appendChild(rowDiv);
        }
    }
</script>

```

### **(B) 後端：app.py**

1. **隨機政策生成**

```python
import numpy as np
import random

def generate_random_policy(n, start, goal, obstacles):
    actions = ['↑', '↓', '←', '→']
    policy = np.full((n, n), ' ', dtype=object)
    value_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if (i, j) == start or (i, j) == goal or (i, j) in obstacles:
                continue
            policy[i, j] = random.choice(actions)
            value_matrix[i, j] = round(random.uniform(-10, 10), 2)

    policy[goal] = 'G'
    value_matrix[goal] = 20.0

    return policy.tolist(), value_matrix.tolist()

```

1. **政策評估**

```python
def policy_evaluation(n, start, goal, obstacles, policy, gamma=0.9, theta=0.01):
    V = np.zeros((n, n))
    actions = {'↑': (-1, 0), '↓': (1, 0), '←': (0, -1), '→': (0, 1)}

    while True:
        delta = 0
        for i in range(n):
            for j in range(n):
                if (i, j) == goal or (i, j) in obstacles:
                    continue

                old_value = V[i, j]
                action = policy[i][j]
                di, dj = actions[action]

                if 0 <= i + di < n and 0 <= j + dj < n:
                    V[i, j] = -1 + gamma * V[i + di, j + dj]
                else:
                    V[i, j] = -1

                delta = max(delta, abs(old_value - V[i, j]))

        if delta < theta:
            break

    return V.tolist()

```

1. **Flask 路由**

```python
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/generate_random_policy", methods=["POST"])
def random_policy():
    data = request.get_json()
    n = int(data["n"])
    start = tuple(map(int, data["start"].split(',')))
    goal = tuple(map(int, data["goal"].split(',')))
    obstacles = set(tuple(map(int, o.split(','))) for o in data["obstacles"])

    policy, value_matrix = generate_random_policy(n, start, goal, obstacles)
    return jsonify({"policy_matrix": policy, "value_matrix": value_matrix})

@app.route("/run_policy_evaluation", methods=["POST"])
def evaluate_policy():
    data = request.get_json()
    n = data["n"]
    start = tuple(map(int, data["start"].split(',')))
    goal = tuple(map(int, data["goal"].split(',')))
    obstacles = set(tuple(map(int, o.split(','))) for o in data["obstacles"])

    policy = data["policy_matrix"]
    value_matrix = policy_evaluation(n, start, goal, obstacles, policy)

    return jsonify({"value_matrix": value_matrix})

if __name__ == "__main__":
    app.run(debug=True)

```

##
