
<video width="600" autoplay loop muted>
  <source src="Gridworld - Value Iteration.mp4" type="video/mp4">
  您的瀏覽器不支援影片播放。
</video>

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

# 強化學習報告 - HW2

## 1. 設計概念

HW2 的目標是使用 **價值迭代 (Value Iteration)** 算法，針對格子地圖環境推導出最佳政策。具體目標包括：

- **價值迭代算法**：
    - 透過 Bellman 最優方程反覆更新每個格子的價值，直到收斂。
    - 根據更新後的價值函數，選擇每個格子最佳行動。
- **最佳政策生成**：
    - 使用價值迭代計算最佳政策，為每個狀態決定最佳行動。
- **視覺化展示**：
    - 顯示最佳政策矩陣，呈現每個格子的最佳行動。
    - 顯示價值函數矩陣，展示每個格子的最優期望回報。

此部分展示了強化學習中 **動態規劃** 方法的一個核心過程，能夠找出長期回報最大的策略。

## 2. ChatGPT Prompt 範例

> "我想實現一個基於 Flask 的 Web 應用，目的是使用 價值迭代算法 (Value Iteration) 來推導出格子地圖中每個狀態的最佳政策。
> 
> 
> 需求如下：
> 
> 1. **算法邏輯**
>     - 使用 Bellman 最優方程，根據折扣因子 γ 和收斂閾值 θ，計算每個格子的最佳價值。
>     - 針對每個格子，根據價值選擇最佳行動 (↑、↓、←、→)。
> 2. **視覺化呈現**
>     - 顯示價值矩陣，標示每個格子的期望回報。
>     - 顯示政策矩陣，呈現每個格子的最佳行動。
> 
> 請提供完整的 Flask 程式碼，包含前端 (HTML + CSS + JavaScript) 及後端邏輯，確保能動態執行價值迭代並將結果視覺化展示於網頁。"
> 

## 3. 相關 Code（含註解）

### **(A) 前端：index.html**

此部分擴展 HW1-2，新增按鈕來執行價值迭代，並顯示最佳政策與價值矩陣。

```html
<button onclick="runValueIteration()">Run Value Iteration</button>

<script>
    // 發送請求執行價值迭代
    function runValueIteration() {
        fetch("/run_value_iteration", {
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

                if (isPolicy) {
                    cellDiv.textContent = matrix[i][j];
                } else {
                    cellDiv.textContent = matrix[i][j].toFixed(2);
                }

                rowDiv.appendChild(cellDiv);
            }
            container.appendChild(rowDiv);
        }
    }
</script>

```

### **(B) 後端：app.py**

1. **價值迭代算法**

```python
import numpy as np

def value_iteration(n, start, goal, obstacles, gamma=0.9, theta=0.01):
    V = np.zeros((n, n))
    policy = np.full((n, n), ' ')

    actions = {'↑': (-1, 0), '↓': (1, 0), '←': (0, -1), '→': (0, 1)}

    def is_valid(i, j):
        return 0 <= i < n and 0 <= j < n and (i, j) not in obstacles

    while True:
        delta = 0
        for i in range(n):
            for j in range(n):
                if (i, j) == goal or (i, j) in obstacles:
                    continue

                old_value = V[i, j]
                best_value = float('-inf')
                best_action = ''

                for action, (di, dj) in actions.items():
                    ni, nj = i + di, j + dj
                    if is_valid(ni, nj):
                        reward = 20 if (ni, nj) == goal else -1
                        value = reward + gamma * V[ni, nj]

                        if value > best_value:
                            best_value = value
                            best_action = action

                V[i, j] = best_value
                policy[i, j] = best_action
                delta = max(delta, abs(old_value - V[i, j]))

        if delta < theta:
            break

    return V.tolist(), policy.tolist()

```

1. **Flask 路由**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/run_value_iteration", methods=["POST"])
def run_value_iteration():
    data = request.get_json()

    n = data["n"]
    start = tuple(map(int, data["start"].split(',')))
    goal = tuple(map(int, data["goal"].split(',')))
    obstacles = set(tuple(map(int, o.split(','))) for o in data["obstacles"])

    value_matrix, policy_matrix = value_iteration(n, start, goal, obstacles)

    return jsonify({"value_matrix": value_matrix, "policy_matrix": policy_matrix})

if __name__ == "__main__":
    app.run(debug=True)

```

## 5. 網頁美化設計

### **1. 整體視覺風格**

- **背景設計**：
    - 使用多重漸變背景 (`background: linear-gradient`)，以深色系 (#0f0c29, #302b63, #24243e, #1a1a3b) 為主，營造科技感和未來感。
- **字體樣式**：
    - 採用 **Orbitron 字體**，強調數位與未來感，搭配白色字體 (`color: #fff`) 提升可讀性。

### **2. 互動元素設計**

- **按鈕設計**：
    - 使用漸變色背景 (`linear-gradient(45deg, #ff00ff, #00ffff)`)，提供亮眼的霓虹效果。
    - 加入懸停效果 (`button:hover`)，透過放大與發光動畫 (`transform: scale(1.1)`) 增強互動性。
- **網格與格子設計**：
    - 每個網格使用 **Flexbox** 布局，確保適配各種螢幕尺寸。
    - **cell (格子)** 有柔和的圓角 (`border-radius: 5px`) 和動態過渡效果 (`transition: all 0.3s ease`)，提升視覺效果。

### **3. 狀態標識設計**

- **起始點 (Start)**：
    - 使用綠色的環形漸變 (`radial-gradient(circle, #0f0, #0a0)`)，表示算法的起點。
- **終點 (Goal)**：
    - 使用紅色的環形漸變 (`radial-gradient(circle, #f00, #a00)`)，明確指示目標位置。
- **障礙物 (Obstacle)**：
    - 以黑色 (`background: #000000`) 為主，並搭配白色邊框強調其不可通行的特性。

### **4. 值與政策矩陣視覺化**

- **政策矩陣 (Policy Matrix)**：
    - 每個格子以漸變藍色背景 (`linear-gradient(90deg, #00a2ff46, #00d9ffe7)`) 表示，突顯政策方向。
- **價值矩陣 (Value Matrix)**：
    - 使用橘色系背景 (`linear-gradient(90deg, #ff9100a6, #eb7f04d8)`)，直觀表達每個狀態的價值。

### **5. 動畫與特效設計**

- **路徑動畫 (Path Animation)**：
    - 定義 `@keyframes futuristic-glow` 動畫，呈現從淡藍到紫色的光暈效果，強調演算法計算出的最佳路徑。
- **懸浮特效**：
    - 在 `.matrix:hover` 中，加入發光與邊框顏色變化，強調使用者互動。

### **6. 佈局與響應式設計**

- **Flexbox 佈局**：
    - 使用 Flexbox 進行網格與矩陣的對齊與布局，確保各種解析度下的顯示效果。
- **間距與邊距**：
    - 透過 `margin-top` 與 `gap` 控制元素間距，提升網頁整體的閱讀性與空間感。

此設計不僅強調 **未來感與科技感**，還提升了使用者與演算法的 **互動體驗**，提供直觀且具吸引力的視覺呈現。

```html
    <style>
        body {
            font-family: 'Orbitron', sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e, #1a1a3b);
            color: #fff;
            text-align: center;
            margin: 20px;
        }
        h1 {
            font-size: 3em;
            text-shadow: 3px 3px 15px rgba(0, 255, 255, 0.8), 0 0 30px rgba(0, 255, 255, 1);
        }
        p {
            font-size: 1.2em;
            line-height: 1.5;
        }
        button {
            margin-left: 5px;
            margin-top: 30px;
            padding: 12px 30px;
            font-size: 18px;
            background: linear-gradient(45deg, #ff00ff, #00ffff);
            border: none;
            border-radius: 12px;
            cursor: pointer;
            color: white;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
            transition: all 0.3s ease-in-out;
        }
        button:hover {
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.8);
            transform: scale(1.1);
        }
        .grid-container {
            display: flex;
            justify-content: center;
            margin-top: 30px;
        }
        .grid {
            display: grid;
            gap: 5px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
            transition: all 0.3s ease-in-out;
        }
        .cell {
            border: solid #fddd4f;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .start { background: radial-gradient(circle, #0f0, #0a0); }
        .goal { background: radial-gradient(circle, #f00, #a00); }
        .obstacle { background: #000000; }
        .matrix-container {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 40px;
        }
        .matrix {
            padding: 20px;
            border-radius: 15px;
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(85, 0, 255, 0.2));
            backdrop-filter: blur(15px);
            box-shadow: 0 0 25px rgba(0, 255, 255, 0.5), 0 0 40px rgba(85, 0, 255, 0.5);
            border: 3px solid rgba(0, 255, 255, 0.6);
            transition: all 0.3s ease-in-out;
            position: relative;
            overflow: hidden;
        }
        .matrix::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.2), transparent);
            transform: rotate(45deg);
            opacity: 0.2;
        }
        .matrix:hover {
            box-shadow: 0 0 40px rgba(0, 255, 255, 0.8), 0 0 60px rgba(85, 0, 255, 0.8);
            border-color: rgba(85, 0, 255, 0.8);
        }
        .matrix-row {
            display: flex;
            justify-content: center;
        }
        .matrix-cell {
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            border-radius: 5px;
            transition: all 0.3s ease;
        }
        .value-matrix .matrix-cell {
            background: linear-gradient(90deg, #ff9100a6, #eb7f04d8);
        }
        .policy-matrix .matrix-cell {
            background: linear-gradient(90deg, #00a2ff46, #00d9ffe7);
        }
        @keyframes futuristic-glow {
            0% { background: rgba(0, 255, 255, 0.2); box-shadow: 0 0 5px rgba(0, 255, 255, 0.5); }
            50% { background: rgba(85, 0, 255, 0.5); box-shadow: 0 0 15px rgba(85, 0, 255, 1); }
            100% { background: rgba(170, 0, 255, 0.8); box-shadow: 0 0 20px rgba(170, 0, 255, 1); }
        }
        .path {
            animation: futuristic-glow 0.6s ease-in-out forwards;
            color: white;
            font-weight: bold;
            text-shadow: 0 0 5px rgba(255, 255, 255, 0.8);
        }

        .obstacle {
            background: #000000; 
            border: solid 2px #ffffff; 
            color: white; 
            font-weight: bold; 
        }
    </style>
```
