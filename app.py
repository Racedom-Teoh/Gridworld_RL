import random
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def is_valid_state(i, j, n, obstacles):
    """检查状态是否在网格内并且不是障碍物。"""
    return 0 <= i < n and 0 <= j < n and (i, j) not in obstacles

def value_iteration(n, start, goal, obstacles, gamma=0.9, theta=0.01):
    """执行价值迭代算法，计算价值矩阵和政策矩阵。"""
    V = np.zeros((n, n))   
    policy = np.full((n, n), ' ', dtype=object)   
    
    # 动作定义（上、下、左、右）
    actions = ['↑', '↓', '←', '→']
    action_delta = {
        '↑': (-1, 0),
        '↓': (1, 0),
        '←': (0, -1),
        '→': (0, 1)
    }
    
    # 奖励初始化
    rewards = np.full((n, n), -1)  
    rewards[goal] = 20   
    for obs in obstacles:
        rewards[obs] = -1   

    # 价值迭代
    delta = float('inf')
    while delta >= theta:
        delta = 0
        for i in range(n):
            for j in range(n):
                if (i, j) == goal or (i, j) in obstacles:
                    continue  # 跳过目标和障碍物格子
                
                old_v = V[i, j]
                max_value = float('-inf')
                best_actions = []

                
                for action, (di, dj) in action_delta.items():
                    ni, nj = i + di, j + dj
 
                    if is_valid_state(ni, nj, n, obstacles):
                        new_value = rewards[ni, nj] + gamma * V[ni, nj]
                        if new_value > max_value:
                            max_value = new_value
                            best_actions = [action]   
                        elif new_value == max_value:
                            best_actions.append(action)  

                V[i, j] = max_value
                policy[i, j] = "".join(best_actions)  
                delta = max(delta, abs(old_v - V[i, j]))   
    # 查找最佳路径（从起始点到目标点）
    path = []
    current = start
    while current != goal:
        path.append(current)
        i, j = current
        if not policy[i, j]:   
            break
        action = random.choice(policy[i, j])  
        di, dj = action_delta[action]
        current = (i + di, j + dj)
    path.append(goal)

    return V.tolist(), policy.tolist(), path

def generate_random_policy(n, start, goal, obstacles):
    """生成随机策略矩阵和随机价值矩阵"""
    policy = np.full((n, n), ' ', dtype=object)
    value_matrix = np.zeros((n, n))
    actions = ['↑', '↓', '←', '→']

    for i in range(n):
        for j in range(n):
            if (i, j) == start or (i, j) == goal or (i, j) in obstacles:
                continue
            policy[i, j] = random.choice(actions)  # 随机分配动作
            value_matrix[i, j] = round(random.uniform(-10, 10), 2)  # 随机赋值（范围可调）

    # 目标状态设定高值
    policy[goal] = 'G'  
    value_matrix[goal] = 20.0

    return policy.tolist(), value_matrix.tolist()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate_random_policy", methods=["POST"])
def random_policy():
    try:
        data = request.get_json()
        n = int(data["n"])
        start = tuple(map(int, data["start"].split(',')))
        goal = tuple(map(int, data["goal"].split(',')))
        obstacles = set(tuple(map(int, o.split(','))) for o in data["obstacles"])

        policy, value_matrix = generate_random_policy(n, start, goal, obstacles)
        return jsonify({"policy_matrix": policy, "value_matrix": value_matrix})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/run_value_iteration", methods=["POST"])
def run_value_iteration():
    try:
        data = request.get_json()
        n = int(data["n"])
        start = tuple(map(int, data["start"].split(',')))
        goal = tuple(map(int, data["goal"].split(',')))
        obstacles = set(tuple(map(int, o.split(','))) for o in data["obstacles"])

        value_matrix, policy_matrix, path = value_iteration(n, start, goal, obstacles)
        return jsonify({
            "value_matrix": value_matrix,
            "policy_matrix": policy_matrix,
            "path": path
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)