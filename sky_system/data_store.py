import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")


QUESTION_ITEMS = [
    {"id": 1, "text": "富有想象力，喜欢抽象思维", "dim": "O", "reverse": False},
    {"id": 2, "text": "做事有条理，遵守计划", "dim": "C", "reverse": False},
    {"id": 3, "text": "在紧急户外是活跃分子", "dim": "E", "reverse": False},
    {"id": 4, "text": "愿意相信他人，认为人性本善", "dim": "A", "reverse": False},
    {"id": 5, "text": "经常感到焦虑或担忧", "dim": "N", "reverse": False},
    {"id": 6, "text": "对艺术和美学有浓厚兴趣", "dim": "O", "reverse": False},
    {"id": 7, "text": "工作勤奋，有始有终", "dim": "C", "reverse": False},
    {"id": 8, "text": "喜欢结识新朋友", "dim": "E", "reverse": False},
    {"id": 9, "text": "通常优先考虑他人需求", "dim": "A", "reverse": False},
    {"id": 10, "text": "情绪容易起伏波动", "dim": "N", "reverse": False},
    {"id": 11, "text": "喜欢思考复杂的理论问题", "dim": "O", "reverse": False},
    {"id": 12, "text": "在人群中感到精力充沛", "dim": "E", "reverse": False},
    {"id": 13, "text": "保持环境整洁有序", "dim": "C", "reverse": False},
    {"id": 14, "text": "通常会避免与他人冲突", "dim": "A", "reverse": False},
    {"id": 15, "text": "能很好地应对压力", "dim": "N", "reverse": True}
]


def load_json(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default_data


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_users():
    users = load_json(USERS_FILE, {})
    changed = False

    for username, user in users.items():
        if "user_type" not in user:
            user["user_type"] = "normal"
            changed = True
        if "questionnaire_completed" not in user:
            user["questionnaire_completed"] = False
            changed = True
        if "questionnaire_answers" not in user:
            user["questionnaire_answers"] = {}
            changed = True
        if "personality_scores" not in user:
            user["personality_scores"] = {
                "O": 0.0,
                "C": 0.0,
                "E": 0.0,
                "A": 0.0,
                "N": 0.0
            }
            changed = True
        if "personality_summary" not in user:
            user["personality_summary"] = "尚未生成人格画像。"
            changed = True
        if "personality_tags" not in user:
            user["personality_tags"] = []
            changed = True
        if "personality" not in user:
            user["personality"] = {
                "openness": 50,
                "conscientiousness": 50,
                "extraversion": 50,
                "agreeableness": 50,
                "neuroticism": 50
            }
            changed = True

    if changed:
        save_json(USERS_FILE, users)

    return users


def save_users(users):
    save_json(USERS_FILE, users)


def get_memories():
    return load_json(MEMORY_FILE, {})


def save_memories(memories):
    save_json(MEMORY_FILE, memories)


def register_user(username, password, nickname):
    users = get_users()

    if not username or not password or not nickname:
        return False, "请完整填写用户名、密码和昵称。"

    if username in users:
        return False, "该用户名已存在。"

    users[username] = {
        "password": password,
        "nickname": nickname,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_type": "normal",
        "questionnaire_completed": False,
        "questionnaire_answers": {},
        "personality_scores": {
            "O": 0.0,
            "C": 0.0,
            "E": 0.0,
            "A": 0.0,
            "N": 0.0
        },
        "personality_summary": "尚未生成人格画像。",
        "personality_tags": [],
        "personality": {
            "openness": 50,
            "conscientiousness": 50,
            "extraversion": 50,
            "agreeableness": 50,
            "neuroticism": 50
        }
    }

    save_users(users)

    memories = get_memories()
    if username not in memories:
        memories[username] = []
        save_memories(memories)

    return True, "注册成功。"


def login_user(username, password):
    users = get_users()

    if username not in users:
        return False, "用户名不存在。", None

    if users[username]["password"] != password:
        return False, "密码错误。", None

    return True, "登录成功。", users[username]


def get_user_memories(username):
    memories = get_memories()
    return memories.get(username, [])


def save_memory(username, raw_message, refine_result):
    memories = get_memories()

    if username not in memories:
        memories[username] = []

    memories[username].append({
        "content": raw_message,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": refine_result["summary"],
        "memory_type": refine_result["memory_type"],
        "importance_score": refine_result["importance_score"],
        "keywords": refine_result["keywords"],
        "suggested_layer": refine_result["suggested_layer"],
        "refine_source": refine_result["refine_source"]
    })

    save_memories(memories)


def score_to_percent(avg_score):
    return round((avg_score - 1) / 4 * 100, 1)


def generate_tags(scores):
    tags = []

    if scores["O"] >= 70:
        tags.append("开放探索")
    elif scores["O"] <= 35:
        tags.append("偏向务实")

    if scores["C"] >= 70:
        tags.append("自律有序")
    elif scores["C"] <= 35:
        tags.append("灵活随性")

    if scores["E"] >= 70:
        tags.append("外向主动")
    elif scores["E"] <= 35:
        tags.append("偏安静内敛")

    if scores["A"] >= 70:
        tags.append("温和体贴")
    elif scores["A"] <= 35:
        tags.append("更重自我边界")

    if scores["N"] >= 70:
        tags.append("情绪敏感")
    elif scores["N"] <= 35:
        tags.append("抗压稳定")

    if not tags:
        tags.append("整体均衡")

    return tags


def generate_summary(scores):
    o = scores["O"]
    c = scores["C"]
    e = scores["E"]
    a = scores["A"]
    n = scores["N"]

    parts = []

    if o >= 70:
        parts.append("你对新事物、抽象问题和美学体验有较强兴趣，整体更偏开放探索型。")
    elif o <= 35:
        parts.append("你更偏向务实稳定，对具体、明确的事务会更有掌控感。")
    else:
        parts.append("你在开放性上处于中间水平，既能接受新想法，也重视现实可行性。")

    if c >= 70:
        parts.append("你做事更讲计划和秩序，执行力与责任感较强。")
    elif c <= 35:
        parts.append("你更灵活随性，不太喜欢被过多规则束缚。")
    else:
        parts.append("你在秩序感和灵活性之间较为平衡。")

    if e >= 70:
        parts.append("你在人际互动中更主动，容易从交流中获得能量。")
    elif e <= 35:
        parts.append("你更偏安静和内敛，更适合稳定、低刺激的交流节奏。")
    else:
        parts.append("你在社交活跃度上较为适中，会根据场景调整状态。")

    if a >= 70:
        parts.append("你更体贴、温和，倾向于优先考虑他人感受。")
    elif a <= 35:
        parts.append("你更强调原则和边界，在关系中较少一味迁就。")
    else:
        parts.append("你在人际关系中既能共情他人，也能保持自己的判断。")

    if n >= 70:
        parts.append("你对压力和情绪波动更敏感，系统后续更适合采用温和、稳定的陪伴方式。")
    elif n <= 35:
        parts.append("你整体抗压能力较强，情绪相对稳定。")
    else:
        parts.append("你在情绪敏感度上处于中等水平，面对压力时具有一定调节能力。")

    return "".join(parts)


def build_legacy_personality(scores):
    return {
        "openness": int(round(scores["O"])),
        "conscientiousness": int(round(scores["C"])),
        "extraversion": int(round(scores["E"])),
        "agreeableness": int(round(scores["A"])),
        "neuroticism": int(round(scores["N"]))
    }


def calculate_questionnaire_profile(answer_map):
    dim_scores = {
        "O": [],
        "C": [],
        "E": [],
        "A": [],
        "N": []
    }

    normalized_answers = {}

    for item in QUESTION_ITEMS:
        qid = str(item["id"])
        raw_score = int(answer_map.get(qid, 3))
        if raw_score < 1:
            raw_score = 1
        if raw_score > 5:
            raw_score = 5

        score = 6 - raw_score if item["reverse"] else raw_score
        dim_scores[item["dim"]].append(score)
        normalized_answers[qid] = raw_score

    avg_scores = {}
    for dim, values in dim_scores.items():
        avg_score = sum(values) / len(values)
        avg_scores[dim] = score_to_percent(avg_score)

    tags = generate_tags(avg_scores)
    summary = generate_summary(avg_scores)
    legacy = build_legacy_personality(avg_scores)

    return {
        "answers": normalized_answers,
        "scores": avg_scores,
        "tags": tags,
        "summary": summary,
        "legacy_personality": legacy
    }


def update_user_profile(username, answer_map):
    users = get_users()
    if username not in users:
        return False

    result = calculate_questionnaire_profile(answer_map)

    users[username]["questionnaire_completed"] = True
    users[username]["questionnaire_answers"] = result["answers"]
    users[username]["personality_scores"] = result["scores"]
    users[username]["personality_summary"] = result["summary"]
    users[username]["personality_tags"] = result["tags"]
    users[username]["personality"] = result["legacy_personality"]

    save_users(users)
    return True


def update_user_type(username, user_type):
    users = get_users()
    if username not in users:
        return False

    if user_type not in ["normal", "vip"]:
        return False

    users[username]["user_type"] = user_type
    save_users(users)
    return True


def refresh_user(username):
    users = get_users()
    return users.get(username)