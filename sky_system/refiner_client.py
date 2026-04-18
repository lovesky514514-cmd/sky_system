import json
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REFINER_EXE = os.path.join(BASE_DIR, "refiner", "refiner.exe")


def local_reply(message):
    text = message.strip()
    if not text:
        return "你刚刚没有输入内容。"
    if "你好" in text or "嗨" in text:
        return "你好呀，很高兴再次和你聊天。"
    if "难过" in text or "伤心" in text:
        return "我能感觉到你现在情绪不太好，可以慢慢和我说。"
    if "开心" in text or "高兴" in text:
        return "听起来这是件让你开心的事情，我愿意继续听你说。"
    if "喜欢" in text:
        return "我会记住你提到的喜好，这样以后会更懂你。"
    return f"我收到了你说的“{text}”。"


def fallback_refine(message):
    keywords = ["喜欢", "讨厌", "生日", "家人", "朋友", "学校", "专业", "压力", "失眠", "开心", "难过", "目标"]
    hit = [word for word in keywords if word in message]
    if hit:
        return {
            "is_memory": True,
            "memory_type": "general_memory",
            "importance_score": 70,
            "summary": message[:60],
            "keywords": hit,
            "suggested_layer": "long_term",
            "refine_source": "python_fallback"
        }
    return {
        "is_memory": False,
        "memory_type": "general_chat",
        "importance_score": 20,
        "summary": message[:60],
        "keywords": [],
        "suggested_layer": "working_memory",
        "refine_source": "python_fallback"
    }


def call_refiner(username, message):
    if not os.path.exists(REFINER_EXE):
        return fallback_refine(message)

    payload = {
        "username": username,
        "message": message
    }

    try:
        result = subprocess.run(
            [REFINER_EXE],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            capture_output=True,
            encoding="utf-8",
            cwd=os.path.join(BASE_DIR, "refiner")
        )

        if result.returncode != 0:
            return fallback_refine(message)

        output = result.stdout.strip()
        if not output:
            return fallback_refine(message)

        parsed = json.loads(output)

        normalized = {
            "is_memory": bool(parsed.get("is_memory", False)),
            "memory_type": str(parsed.get("memory_type", "general_chat")),
            "importance_score": int(parsed.get("importance_score", 0)),
            "summary": str(parsed.get("summary", message[:60])),
            "keywords": parsed.get("keywords", []),
            "suggested_layer": str(parsed.get("suggested_layer", "working_memory")),
            "refine_source": str(parsed.get("refine_source", "refiner"))
        }

        if not isinstance(normalized["keywords"], list):
            normalized["keywords"] = []

        if normalized["importance_score"] < 0:
            normalized["importance_score"] = 0
        if normalized["importance_score"] > 100:
            normalized["importance_score"] = 100

        if normalized["memory_type"] == "emotion_event" and normalized["suggested_layer"] == "long_term":
            normalized["suggested_layer"] = "transition_memory"

        return normalized

    except Exception:
        return fallback_refine(message)


def should_save_memory(refine_result, user_type="normal"):
    threshold = 60 if user_type == "normal" else 45

    if not refine_result["is_memory"]:
        return False
    if refine_result["importance_score"] < threshold:
        return False
    if refine_result["memory_type"] == "general_chat":
        return False

    return True


def get_memory_display_limit(user_type="normal"):
    return 8 if user_type == "normal" else 16