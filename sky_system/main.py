import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QPushButton, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QMessageBox, QListWidget, QListWidgetItem,
    QStackedWidget, QFrame, QGridLayout, QTextBrowser, QGraphicsDropShadowEffect,
    QDialog, QComboBox, QFormLayout, QScrollArea, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient, QFont
from app_state import app_state
from data_store import (
    register_user, login_user, get_user_memories, save_memory,
    update_user_profile, update_user_type, refresh_user,
    QUESTION_ITEMS
)
from refiner_client import local_reply, call_refiner, should_save_memory, get_memory_display_limit
from theme import APP_STYLE


def add_shadow(widget, blur=36, x=0, y=10, alpha=55):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(x, y)
    shadow.setColor(Qt.black)
    c = shadow.color()
    c.setAlpha(alpha)
    shadow.setColor(c)
    widget.setGraphicsEffect(shadow)


class InfoTag(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setObjectName("TagLabel")
        self.setAlignment(Qt.AlignCenter)


class NavButton(QPushButton):
    def __init__(self, icon_text, label_text):
        super().__init__(f"{icon_text}  {label_text}")
        self.setMinimumHeight(46)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #ffffff,
                                            stop:1 #f4f9ff);
                border: 1px solid #d9e7f4;
                border-radius: 18px;
                padding: 12px 16px;
                color: #234;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #ffffff,
                                            stop:1 #eaf5ff);
                border: 1px solid #bcdcff;
            }
            QPushButton:pressed {
                background: #dceeff;
            }
        """)


class ScoreCircle(QWidget):
    def __init__(self, score=0):
        super().__init__()
        self.score = score
        self.setMinimumSize(150, 150)
        self.setMaximumSize(150, 150)

    def sizeHint(self):
        return QSize(150, 150)

    def set_score(self, score):
        self.score = max(0, min(100, int(score)))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -10)
        start_angle = 90 * 16
        span_angle = -int(360 * 16 * self.score / 100)

        base_pen = QPen(QColor("#e6f1fb"), 14)
        base_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(base_pen)
        painter.drawArc(rect, 0, 360 * 16)

        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, QColor("#78beff"))
        grad.setColorAt(0.5, QColor("#2f95ff"))
        grad.setColorAt(1.0, QColor("#1677d8"))

        progress_pen = QPen(grad, 14)
        progress_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(progress_pen)
        painter.drawArc(rect, start_angle, span_angle)

        painter.setPen(QColor("#123b63"))
        score_font = QFont("Microsoft YaHei", 26, QFont.Bold)
        painter.setFont(score_font)
        painter.drawText(self.rect().adjusted(0, -10, 0, 0), Qt.AlignCenter, str(self.score))

        painter.setPen(QColor("#6d8298"))
        label_font = QFont("Microsoft YaHei", 10, QFont.Medium)
        painter.setFont(label_font)
        painter.drawText(self.rect().adjusted(0, 42, 0, 0), Qt.AlignCenter, "重要度")


class GradientProgressBar(QWidget):
    def __init__(self, title, value=0):
        super().__init__()
        self.title = title
        self.value = value
        self.setMinimumHeight(54)

    def set_value(self, value):
        self.value = max(0, min(100, int(value)))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        full_rect = self.rect().adjusted(0, 18, 0, -8)
        bg_rect = QRect(full_rect.x(), full_rect.y() + 10, full_rect.width(), 14)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#e8f2fc"))
        painter.drawRoundedRect(bg_rect, 7, 7)

        fill_width = int(bg_rect.width() * self.value / 100)
        fill_rect = QRect(bg_rect.x(), bg_rect.y(), fill_width, bg_rect.height())

        grad = QLinearGradient(fill_rect.topLeft(), fill_rect.topRight())
        grad.setColorAt(0.0, QColor("#7bc1ff"))
        grad.setColorAt(0.5, QColor("#41a1ff"))
        grad.setColorAt(1.0, QColor("#1677d8"))
        painter.setBrush(grad)
        painter.drawRoundedRect(fill_rect, 7, 7)

        painter.setPen(QColor("#123b63"))
        title_font = QFont("Microsoft YaHei", 10, QFont.Bold)
        painter.setFont(title_font)
        painter.drawText(QRect(0, 0, self.width(), 18), Qt.AlignLeft | Qt.AlignVCenter, self.title)

        painter.setPen(QColor("#1677d8"))
        value_font = QFont("Microsoft YaHei", 10, QFont.Bold)
        painter.setFont(value_font)
        painter.drawText(QRect(0, 0, self.width(), 18), Qt.AlignRight | Qt.AlignVCenter, f"{self.value}")


class ChatView(QTextBrowser):
    def __init__(self):
        super().__init__()
        self.setOpenExternalLinks(False)
        self.setStyleSheet("""
            QTextBrowser {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #f6fbff,
                                            stop:1 #edf6ff);
                border: 1px solid #dbe8f5;
                border-radius: 24px;
                padding: 18px;
            }
        """)
        self.setHtml("<div style='color:#8aa0b5;font-size:14px;'>开始聊天吧～</div>")

    def append_message(self, text, is_user=False, is_notice=False):
        safe_text = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )

        if is_notice:
            html = f"""
            <div style="text-align:center; margin:12px 0;">
                <span style="
                    display:inline-block;
                    background:linear-gradient(135deg,#eef7ff,#dff0ff);
                    color:#145b96;
                    border:1px solid #cfe6fb;
                    padding:8px 14px;
                    border-radius:16px;
                    font-size:12px;
                    font-weight:700;
                ">
                    {safe_text}
                </span>
            </div>
            """
        elif is_user:
            html = f"""
            <div style="text-align:right; margin:12px 0;">
                <div style="
                    display:inline-block;
                    max-width:72%;
                    background:linear-gradient(135deg,#73bcff,#2f95ff 55%,#1677d8);
                    color:white;
                    padding:13px 17px;
                    border-radius:20px 20px 8px 20px;
                    font-size:14px;
                    line-height:1.65;
                ">
                    {safe_text}
                </div>
            </div>
            """
        else:
            html = f"""
            <div style="text-align:left; margin:12px 0;">
                <div style="
                    display:inline-block;
                    max-width:72%;
                    background:linear-gradient(135deg,#ffffff,#f6fbff);
                    color:#1f2d3d;
                    border:1px solid #dce8f5;
                    padding:13px 17px;
                    border-radius:20px 20px 20px 8px;
                    font-size:14px;
                    line-height:1.65;
                ">
                    {safe_text}
                </div>
            </div>
            """

        self.append(html)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class QuestionnaireDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("人格画像问卷")
        self.resize(780, 760)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        title = QLabel("请完成首次人格画像问卷")
        title.setObjectName("PageTitle")

        desc = QLabel("请根据你的真实感受作答：1=非常不同意，2=不同意，3=一般，4=同意，5=非常同意")
        desc.setWordWrap(True)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        form_layout = QFormLayout(content)
        form_layout.setSpacing(14)

        self.answer_boxes = {}

        options = [("1", 1), ("2", 2), ("3", 3), ("4", 4), ("5", 5)]

        for item in QUESTION_ITEMS:
            label = QLabel(f"{item['id']}. {item['text']}")
            label.setWordWrap(True)

            box = QComboBox()
            for text, value in options:
                box.addItem(text, value)
            box.setCurrentIndex(2)

            self.answer_boxes[str(item["id"])] = box
            form_layout.addRow(label, box)

        scroll.setWidget(content)

        btn_row = QHBoxLayout()
        submit_btn = QPushButton("提交问卷")
        submit_btn.setObjectName("PrimaryButton")
        submit_btn.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(submit_btn)

        main_layout.addWidget(title)
        main_layout.addWidget(desc)
        main_layout.addWidget(scroll)
        main_layout.addLayout(btn_row)

    def get_answers(self):
        result = {}
        for qid, box in self.answer_boxes.items():
            result[qid] = int(box.currentData())
        return result


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SKY蓝天陪伴系统 - 登录")
        self.setMinimumSize(420, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(16)

        title = QLabel("SKY蓝天陪伴系统")
        title.setObjectName("PageTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("登录")
        subtitle.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("登录")
        login_btn.setObjectName("PrimaryButton")
        login_btn.clicked.connect(self.handle_login)

        to_register_btn = QPushButton("没有账号？去注册")
        to_register_btn.clicked.connect(self.open_register)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_btn)
        layout.addWidget(to_register_btn)
        layout.addStretch()

        self.register_window = None
        self.main_window = None

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        ok, msg, user_data = login_user(username, password)
        if not ok:
            QMessageBox.warning(self, "登录失败", msg)
            return

        app_state.login(username, user_data)

        if not user_data.get("questionnaire_completed", False):
            dialog = QuestionnaireDialog(self)
            if dialog.exec():
                answers = dialog.get_answers()
                update_user_profile(username, answers)
                refreshed = refresh_user(username)
                app_state.login(username, refreshed)
            else:
                QMessageBox.information(self, "提示", "首次使用需要完成人格画像问卷。")
                return

        refreshed = refresh_user(username)
        app_state.login(username, refreshed)

        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SKY蓝天陪伴系统 - 注册")
        self.setMinimumSize(420, 560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(16)

        title = QLabel("SKY蓝天陪伴系统")
        title.setObjectName("PageTitle")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("注册")
        subtitle.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText("昵称")

        register_btn = QPushButton("注册")
        register_btn.setObjectName("PrimaryButton")
        register_btn.clicked.connect(self.handle_register)

        back_btn = QPushButton("返回登录")
        back_btn.clicked.connect(self.back_login)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.nickname_input)
        layout.addWidget(register_btn)
        layout.addWidget(back_btn)
        layout.addStretch()

        self.login_window = None

    def handle_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        nickname = self.nickname_input.text().strip()
        ok, msg = register_user(username, password, nickname)
        if not ok:
            QMessageBox.warning(self, "注册失败", msg)
            return
        QMessageBox.information(self, "注册成功", "注册成功，请登录。")
        self.back_login()

    def back_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SKY蓝天陪伴系统")
        self.resize(1400, 920)

        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(250)
        add_shadow(sidebar, blur=20, x=2, y=0, alpha=18)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 20, 18, 20)
        sidebar_layout.setSpacing(12)

        title = QLabel("SKY蓝天")
        title.setObjectName("SidebarTitle")

        self.btn_home = NavButton("🏠", "主页")
        self.btn_chat = NavButton("💬", "聊天")
        self.btn_memory = NavButton("🧠", "记忆库")
        self.btn_profile = NavButton("📊", "用户画像")
        self.btn_settings = NavButton("⚙", "设置")
        self.btn_logout = NavButton("↩", "退出登录")

        self.btn_home.clicked.connect(lambda: self.switch_page(0, self.btn_home))
        self.btn_chat.clicked.connect(lambda: self.switch_page(1, self.btn_chat))
        self.btn_memory.clicked.connect(lambda: self.switch_memory_page(self.btn_memory))
        self.btn_profile.clicked.connect(lambda: self.switch_profile_page(self.btn_profile))
        self.btn_settings.clicked.connect(lambda: self.switch_page(4, self.btn_settings))
        self.btn_logout.clicked.connect(self.logout)

        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(self.btn_home)
        sidebar_layout.addWidget(self.btn_chat)
        sidebar_layout.addWidget(self.btn_memory)
        sidebar_layout.addWidget(self.btn_profile)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.btn_logout)

        self.stack = QStackedWidget()

        self.home_page = self.build_home_page()
        self.chat_page = self.build_chat_page()
        self.memory_page = self.build_memory_page()
        self.profile_page = self.build_profile_page()
        self.settings_page = self.build_settings_page()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.chat_page)
        self.stack.addWidget(self.memory_page)
        self.stack.addWidget(self.profile_page)
        self.stack.addWidget(self.settings_page)

        self.page_effect = QGraphicsOpacityEffect()
        self.stack.setGraphicsEffect(self.page_effect)
        self.page_effect.setOpacity(1.0)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.stack)

        self.refresh_home_page()
        self.refresh_memory_page()
        self.refresh_profile_page()
        self.refresh_chat_memory_list()
        self.update_nav_styles(0)

    def build_page_wrapper(self, page_title):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel(page_title)
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        return page, layout

    def make_card(self):
        card = QFrame()
        card.setObjectName("Card")
        add_shadow(card, blur=28, x=0, y=10, alpha=26)
        return card

    def get_current_user_type(self):
        user = app_state.current_user or {}
        return user.get("user_type", "normal")

    def update_nav_styles(self, index):
        buttons = [self.btn_home, self.btn_chat, self.btn_memory, self.btn_profile, self.btn_settings]
        for i, btn in enumerate(buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                    stop:0 #78beff,
                                                    stop:0.5 #47a2ff,
                                                    stop:1 #1c84ea);
                        color: white;
                        border: none;
                        border-radius: 18px;
                        padding: 12px 16px;
                        font-weight: 800;
                        text-align: left;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                    stop:0 #ffffff,
                                                    stop:1 #f4f9ff);
                        border: 1px solid #d9e7f4;
                        border-radius: 18px;
                        padding: 12px 16px;
                        color: #234;
                        font-weight: 700;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                    stop:0 #ffffff,
                                                    stop:1 #eaf5ff);
                        border: 1px solid #bcdcff;
                    }
                """)

    def switch_page(self, index, button=None):
        self.update_nav_styles(index)
        if button is not None:
            self.sidebar_bounce(button)
        self.play_page_switch_animation(index)

    def play_page_switch_animation(self, index):
        fade_out = QPropertyAnimation(self.page_effect, b"opacity")
        fade_out.setDuration(120)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.25)
        fade_out.setEasingCurve(QEasingCurve.OutCubic)

        fade_in = QPropertyAnimation(self.page_effect, b"opacity")
        fade_in.setDuration(180)
        fade_in.setStartValue(0.25)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.OutCubic)

        def after_fade_out():
            self.stack.setCurrentIndex(index)
            fade_in.start()

        fade_out.finished.connect(after_fade_out)
        fade_out.start()
        self._fade_out_anim = fade_out
        self._fade_in_anim = fade_in

    def build_home_page(self):
        page, layout = self.build_page_wrapper("主页")

        top_card = self.make_card()
        top_layout = QVBoxLayout(top_card)
        top_layout.setContentsMargins(24, 24, 24, 24)

        self.welcome_label = QLabel("")
        self.meta_label = QLabel("")
        self.meta_label.setObjectName("Muted")

        self.user_type_tag = InfoTag("普通用户")
        self.questionnaire_tag = InfoTag("未完成画像")

        type_row = QHBoxLayout()
        type_row.addWidget(self.user_type_tag)
        type_row.addWidget(self.questionnaire_tag)
        type_row.addStretch()

        top_layout.addWidget(self.welcome_label)
        top_layout.addWidget(self.meta_label)
        top_layout.addLayout(type_row)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(18)

        self.stat_memories = self.make_card()
        stat_mem_layout = QVBoxLayout(self.stat_memories)
        stat_mem_layout.setContentsMargins(20, 20, 20, 20)
        stat_mem_title = QLabel("已保存记忆")
        self.stat_mem_value = QLabel("0")
        self.stat_mem_value.setObjectName("BigValue")
        stat_mem_layout.addWidget(stat_mem_title)
        stat_mem_layout.addWidget(self.stat_mem_value)

        self.stat_user = self.make_card()
        stat_user_layout = QVBoxLayout(self.stat_user)
        stat_user_layout.setContentsMargins(20, 20, 20, 20)
        stat_user_title = QLabel("当前用户")
        self.stat_user_value = QLabel("")
        self.stat_user_value.setObjectName("BigValue")
        stat_user_layout.addWidget(stat_user_title)
        stat_user_layout.addWidget(self.stat_user_value)

        stats_row.addWidget(self.stat_memories)
        stats_row.addWidget(self.stat_user)

        layout.addWidget(top_card)
        layout.addLayout(stats_row)

        recent_card = self.make_card()
        recent_layout = QVBoxLayout(recent_card)
        recent_layout.setContentsMargins(20, 20, 20, 20)
        recent_title = QLabel("最近记忆")
        self.home_memory_list = QListWidget()
        recent_layout.addWidget(recent_title)
        recent_layout.addWidget(self.home_memory_list)

        layout.addWidget(recent_card)
        return page

    def build_chat_page(self):
        page, layout = self.build_page_wrapper("聊天")

        main_row = QHBoxLayout()
        main_row.setSpacing(18)

        left_card = self.make_card()
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(14)

        left_title = QLabel("对话")
        left_title.setStyleSheet("font-size:18px;font-weight:700;color:#123b63;")

        self.chat_view = ChatView()

        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("请输入你想说的话...")
        self.chat_input.setFixedHeight(110)

        send_btn = QPushButton("✨ 发送")
        send_btn.setObjectName("PrimaryButton")
        send_btn.setFixedHeight(48)
        send_btn.clicked.connect(self.handle_send_message)
        self.send_btn = send_btn

        left_layout.addWidget(left_title)
        left_layout.addWidget(self.chat_view)
        left_layout.addWidget(self.chat_input)
        left_layout.addWidget(send_btn)

        right_column = QVBoxLayout()
        right_column.setSpacing(18)

        analysis_card = self.make_card()
        analysis_layout = QVBoxLayout(analysis_card)
        analysis_layout.setContentsMargins(20, 20, 20, 20)
        analysis_layout.setSpacing(14)

        analysis_title = QLabel("智能精炼分析")
        analysis_title.setStyleSheet("font-size:18px;font-weight:700;color:#123b63;")

        circle_row = QHBoxLayout()
        circle_row.setSpacing(18)

        self.score_circle = ScoreCircle(0)

        circle_info_col = QVBoxLayout()
        circle_info_col.setSpacing(10)

        self.refine_type = InfoTag("类型：--")
        self.refine_layer = InfoTag("层级：--")
        self.refine_source = QLabel("来源：--")
        self.refine_source.setObjectName("Muted")

        circle_info_col.addStretch()
        circle_info_col.addWidget(self.refine_type)
        circle_info_col.addWidget(self.refine_layer)
        circle_info_col.addWidget(self.refine_source)
        circle_info_col.addStretch()

        circle_row.addWidget(self.score_circle, 0, Qt.AlignCenter)
        circle_row.addLayout(circle_info_col, 1)

        progress_wrap = QFrame()
        progress_wrap.setStyleSheet("background: transparent;")
        progress_layout = QVBoxLayout(progress_wrap)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(10)

        self.progress_importance = GradientProgressBar("重要度", 0)
        self.progress_memory = GradientProgressBar("记忆倾向", 0)
        self.progress_layer = GradientProgressBar("长期保留倾向", 0)

        progress_layout.addWidget(self.progress_importance)
        progress_layout.addWidget(self.progress_memory)
        progress_layout.addWidget(self.progress_layer)

        summary_title = QLabel("精炼摘要")
        summary_title.setStyleSheet("font-size:15px;font-weight:700;color:#123b63;")

        self.refine_summary = QTextEdit()
        self.refine_summary.setReadOnly(True)
        self.refine_summary.setPlaceholderText("这里会显示精炼摘要...")
        self.refine_summary.setFixedHeight(110)

        keyword_title = QLabel("关键词")
        keyword_title.setStyleSheet("font-size:15px;font-weight:700;color:#123b63;")

        self.keyword_row = QHBoxLayout()
        self.keyword_row.setSpacing(8)

        keyword_wrap = QFrame()
        keyword_wrap_layout = QVBoxLayout(keyword_wrap)
        keyword_wrap_layout.setContentsMargins(0, 0, 0, 0)
        keyword_wrap_layout.addLayout(self.keyword_row)

        analysis_layout.addWidget(analysis_title)
        analysis_layout.addLayout(circle_row)
        analysis_layout.addWidget(progress_wrap)
        analysis_layout.addWidget(summary_title)
        analysis_layout.addWidget(self.refine_summary)
        analysis_layout.addWidget(keyword_title)
        analysis_layout.addWidget(keyword_wrap)

        self.analysis_card = analysis_card

        memory_card = self.make_card()
        memory_layout = QVBoxLayout(memory_card)
        memory_layout.setContentsMargins(20, 20, 20, 20)
        memory_title = QLabel("最近保存的记忆")
        memory_title.setStyleSheet("font-size:18px;font-weight:700;color:#123b63;")
        self.chat_memory_list = QListWidget()
        memory_layout.addWidget(memory_title)
        memory_layout.addWidget(self.chat_memory_list)

        right_column.addWidget(analysis_card, 3)
        right_column.addWidget(memory_card, 2)

        main_row.addWidget(left_card, 3)
        main_row.addLayout(right_column, 2)

        layout.addLayout(main_row)
        return page

    def build_memory_page(self):
        page, layout = self.build_page_wrapper("记忆库")

        card = self.make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        self.memory_list_widget = QListWidget()
        card_layout.addWidget(self.memory_list_widget)
        layout.addWidget(card)

        return page

    def build_profile_page(self):
        page, layout = self.build_page_wrapper("用户画像")

        top_row = QHBoxLayout()
        top_row.setSpacing(16)

        summary_card = self.make_card()
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(20, 20, 20, 20)

        summary_title = QLabel("人格画像总结")
        summary_title.setStyleSheet("font-size:18px;font-weight:700;color:#123b63;")
        self.profile_summary = QTextEdit()
        self.profile_summary.setReadOnly(True)
        self.profile_summary.setFixedHeight(180)

        self.profile_tag_row = QHBoxLayout()
        self.profile_tag_row.setSpacing(8)

        tag_wrap = QFrame()
        tag_wrap_layout = QVBoxLayout(tag_wrap)
        tag_wrap_layout.setContentsMargins(0, 0, 0, 0)
        tag_wrap_layout.addLayout(self.profile_tag_row)

        summary_layout.addWidget(summary_title)
        summary_layout.addWidget(self.profile_summary)
        summary_layout.addWidget(tag_wrap)

        top_row.addWidget(summary_card)

        layout.addLayout(top_row)

        grid = QGridLayout()
        grid.setSpacing(16)

        self.profile_cards = {}

        labels = [
            ("开放性 O", "O"),
            ("尽责性 C", "C"),
            ("外向性 E", "E"),
            ("宜人性 A", "A"),
            ("神经质 N", "N")
        ]

        for idx, (title, key) in enumerate(labels):
            card = self.make_card()
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 20, 20, 20)
            title_label = QLabel(title)
            value_label = QLabel("0")
            value_label.setObjectName("BigValue")
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            self.profile_cards[key] = value_label
            row = idx // 2
            col = idx % 2
            grid.addWidget(card, row, col)

        layout.addLayout(grid)
        return page

    def build_settings_page(self):
        page, layout = self.build_page_wrapper("设置")

        user_card = self.make_card()
        user_layout = QVBoxLayout(user_card)
        user_layout.setContentsMargins(20, 20, 20, 20)

        user_title = QLabel("用户类型")
        user_title.setStyleSheet("font-size:18px;font-weight:700;color:#123b63;")

        self.user_type_label = QLabel("当前：普通用户")
        self.user_type_label.setObjectName("Muted")

        btn_row = QHBoxLayout()
        normal_btn = QPushButton("🌤 切换为普通用户")
        vip_btn = QPushButton("💎 切换为 VIP 用户")
        normal_btn.clicked.connect(lambda: self.change_user_type("normal"))
        vip_btn.clicked.connect(lambda: self.change_user_type("vip"))

        btn_row.addWidget(normal_btn)
        btn_row.addWidget(vip_btn)

        user_layout.addWidget(user_title)
        user_layout.addWidget(self.user_type_label)
        user_layout.addLayout(btn_row)

        questionnaire_card = self.make_card()
        questionnaire_layout = QVBoxLayout(questionnaire_card)
        questionnaire_layout.setContentsMargins(20, 20, 20, 20)

        questionnaire_title = QLabel("人格问卷")
        questionnaire_title.setStyleSheet("font-size:18px;font-weight:700;color:#123b63;")

        retest_btn = QPushButton("📝 重新进行人格画像问卷")
        retest_btn.setObjectName("PrimaryButton")
        retest_btn.clicked.connect(self.retake_questionnaire)

        questionnaire_layout.addWidget(questionnaire_title)
        questionnaire_layout.addWidget(retest_btn)

        layout.addWidget(user_card)
        layout.addWidget(questionnaire_card)
        layout.addStretch()
        return page

    def refresh_home_page(self):
        user = app_state.current_user
        username = app_state.current_username
        memories = get_user_memories(username) if username else []
        user_type = user.get("user_type", "normal") if user else "normal"
        completed = user.get("questionnaire_completed", False) if user else False

        self.welcome_label.setText(f"欢迎你，{user['nickname']}" if user else "欢迎使用")
        self.meta_label.setText(f"用户名：{username}" if username else "")
        self.stat_mem_value.setText(str(len(memories)))
        self.stat_user_value.setText(user["nickname"] if user else "")
        self.user_type_tag.setText("VIP 用户" if user_type == "vip" else "普通用户")
        self.questionnaire_tag.setText("已完成人格画像" if completed else "未完成人格画像")

        self.home_memory_list.clear()
        limit = 6 if user_type == "normal" else 10
        for item in reversed(memories[-limit:]):
            text = f"{item['saved_at']}｜{item['summary']}｜{item['memory_type']}｜{item['importance_score']}"
            self.home_memory_list.addItem(QListWidgetItem(text))

        self.user_type_label.setText("当前：VIP 用户" if user_type == "vip" else "当前：普通用户")

    def refresh_memory_page(self):
        username = app_state.current_username
        memories = get_user_memories(username) if username else []

        self.memory_list_widget.clear()
        for item in reversed(memories):
            text = (
                f"时间：{item['saved_at']}\n"
                f"原始内容：{item['content']}\n"
                f"摘要：{item['summary']}\n"
                f"类型：{item['memory_type']}｜分数：{item['importance_score']}｜层级：{item['suggested_layer']}\n"
                f"关键词：{'、'.join(item['keywords']) if item['keywords'] else '无'}\n"
                f"来源：{item['refine_source']}"
            )
            self.memory_list_widget.addItem(QListWidgetItem(text))

    def clear_profile_tags(self):
        while self.profile_tag_row.count():
            item = self.profile_tag_row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_profile_page(self):
        user = app_state.current_user
        if not user:
            return

        scores = user.get("personality_scores", {"O": 0, "C": 0, "E": 0, "A": 0, "N": 0})
        summary = user.get("personality_summary", "尚未生成人格画像。")
        tags = user.get("personality_tags", [])

        self.profile_summary.setPlainText(summary)

        for key, label in self.profile_cards.items():
            label.setText(str(scores.get(key, 0)))

        self.clear_profile_tags()
        if tags:
            for tag in tags:
                self.profile_tag_row.addWidget(InfoTag(tag))
        else:
            self.profile_tag_row.addWidget(InfoTag("暂无标签"))

    def refresh_chat_memory_list(self):
        username = app_state.current_username
        memories = get_user_memories(username) if username else []
        user_type = self.get_current_user_type()
        limit = get_memory_display_limit(user_type)

        self.chat_memory_list.clear()
        for item in reversed(memories[-limit:]):
            text = (
                f"{item['saved_at']}｜{item['summary']}｜"
                f"{item['memory_type']}｜{item['importance_score']}｜{item['suggested_layer']}"
            )
            self.chat_memory_list.addItem(QListWidgetItem(text))

    def switch_memory_page(self, button=None):
        self.refresh_memory_page()
        self.switch_page(2, button)

    def switch_profile_page(self, button=None):
        self.refresh_profile_page()
        self.switch_page(3, button)

    def clear_keyword_row(self):
        while self.keyword_row.count():
            item = self.keyword_row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def bounce_widget(self, widget):
        geom = widget.geometry()
        anim = QPropertyAnimation(widget, b"geometry", self)
        anim.setDuration(260)
        anim.setStartValue(QRect(geom.x(), geom.y() + 10, geom.width(), geom.height()))
        anim.setEndValue(geom)
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.start()
        self._last_anim = anim

    def pulse_button(self, button):
        geom = button.geometry()
        anim = QPropertyAnimation(button, b"geometry", self)
        anim.setDuration(180)
        anim.setKeyValueAt(0.0, geom)
        anim.setKeyValueAt(0.5, QRect(geom.x() - 2, geom.y() - 2, geom.width() + 4, geom.height() + 4))
        anim.setKeyValueAt(1.0, geom)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._btn_anim = anim

    def sidebar_bounce(self, button):
        geom = button.geometry()
        anim = QPropertyAnimation(button, b"geometry", self)
        anim.setDuration(220)
        anim.setStartValue(geom)
        anim.setKeyValueAt(0.5, QRect(geom.x() + 4, geom.y(), geom.width(), geom.height()))
        anim.setEndValue(geom)
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.start()
        self._nav_anim = anim

    def update_refine_panel(self, refine_result):
        score = int(refine_result["importance_score"])
        self.score_circle.set_score(score)
        self.refine_type.setText(f"类型：{refine_result['memory_type']}")
        self.refine_layer.setText(f"层级：{refine_result['suggested_layer']}")
        self.refine_source.setText(f"来源：{refine_result['refine_source']}")
        self.refine_summary.setPlainText(refine_result["summary"])

        memory_tendency = 100 if refine_result["is_memory"] else 15

        layer_map = {
            "working_memory": 25,
            "transition_memory": 60,
            "long_term": 90
        }
        layer_score = layer_map.get(refine_result["suggested_layer"], 20)

        self.progress_importance.set_value(score)
        self.progress_memory.set_value(memory_tendency)
        self.progress_layer.set_value(layer_score)

        self.clear_keyword_row()
        if refine_result["keywords"]:
            for word in refine_result["keywords"]:
                self.keyword_row.addWidget(InfoTag(word))
        else:
            self.keyword_row.addWidget(InfoTag("无"))

        self.bounce_widget(self.analysis_card)

    def handle_send_message(self):
        message = self.chat_input.toPlainText().strip()
        if not message:
            QMessageBox.warning(self, "提示", "请输入内容。")
            return

        username = app_state.current_username
        user_type = self.get_current_user_type()

        ai_message = local_reply(message)
        refine_result = call_refiner(username, message)

        self.chat_view.append_message(message, is_user=True)
        self.chat_view.append_message(ai_message, is_user=False)
        self.update_refine_panel(refine_result)
        self.pulse_button(self.send_btn)

        if should_save_memory(refine_result, user_type):
            save_memory(username, message, refine_result)
            self.chat_view.append_message("本条内容已写入记忆库。", is_notice=True)
        else:
            self.chat_view.append_message("本条内容未进入长期记忆库。", is_notice=True)

        self.chat_input.clear()
        self.refresh_chat_memory_list()
        self.refresh_home_page()
        self.refresh_memory_page()

    def change_user_type(self, user_type):
        username = app_state.current_username
        ok = update_user_type(username, user_type)
        if ok:
            refreshed = refresh_user(username)
            app_state.login(username, refreshed)
            self.refresh_home_page()
            self.refresh_chat_memory_list()
            QMessageBox.information(self, "提示", "用户类型已更新。")

    def retake_questionnaire(self):
        username = app_state.current_username
        dialog = QuestionnaireDialog(self)
        if dialog.exec():
            answers = dialog.get_answers()
            update_user_profile(username, answers)
            refreshed = refresh_user(username)
            app_state.login(username, refreshed)
            self.refresh_home_page()
            self.refresh_profile_page()
            QMessageBox.information(self, "提示", "人格画像已更新。")

    def logout(self):
        app_state.logout()
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())