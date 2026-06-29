import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QListWidget, QStackedWidget, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QComboBox, QFormLayout)
from database.db_manager import init_db, get_db_connection

class PartsManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("부품 생애주기 관리 시스템 (오프라인 USB 버전)")
        self.setGeometry(100, 100, 850, 550)
        
        # DB 초기화
        init_db()
        
        # 메인 레이아웃 구성 (좌측 메뉴 바 - 우측 메인 화면)
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # 좌측 메뉴 리스트
        self.menu_list = QListWidget()
        self.menu_list.setFixedWidth(180)
        self.menu_list.addItems([
            "0. Home",
            "1. 신규 부품 등록",
            "2. 장비 장착/탈거",
            "3. 연마 출하",
            "4. 연마 입고",
            "5. 부품 ID 변경"
        ])
        self.menu_list.currentRowChanged.connect(self.display_page)
        
        # 우측 뷰 스택 (Stacked Widget으로 6개 페이지 관리)
        self.pages_widget = QStackedWidget()
        self.init_pages()
        
        main_layout.addWidget(self.menu_list)
        main_layout.addWidget(self.pages_widget)
        self.setCentralWidget(main_widget)
        
        # 기본 페이지 로드 (Home)
        self.menu_list.setCurrentRow(0)

    def init_pages(self):
        """6개의 메뉴 페이지 생성 및 스택 추가"""
        # Page 0: Home
        self.page_home = QWidget()
        layout0 = QVBoxLayout(self.page_home)
        self.home_summary = QLabel("현재 부품 수량 통계 데이터를 불러오는 중입니다...")
        layout0.addWidget(QLabel("### 0. Home - 부품 재고 통계 Summary"))
        layout0.addWidget(self.home_summary)
        self.pages_widget.addWidget(self.page_home)
        
        # Page 1: 신규 부품 등록
        self.page_register = QWidget()
        layout1 = QFormLayout(self.page_register)
        self.reg_id = QLineEdit()
        self.reg_manuf = QComboBox()
        self.reg_manuf.addItems(["제작사A", "제작사B", "제작사C"])
        self.reg_type = QComboBox()
        self.reg_type.addItems(["상도 커터", "하도 커터"])
        self.reg_max_regrid = QLineEdit("15")
        btn_reg = QPushButton("부품 신규 등록")
        btn_reg.clicked.connect(self.register_component)
        
        layout1.addRow("### 1. 신규 부품의 등록 페이지", QLabel(""))
        layout1.addRow("부품 고유 일련번호(ID):", self.reg_id)
        layout1.addRow("제작사 선택:", self.reg_manuf)
        layout1.addRow("부품 종류 선택:", self.reg_type)
        layout1.addRow("초기 연마 가능 횟수:", self.reg_max_regrid)
        layout1.addRow(btn_reg)
        self.pages_widget.addWidget(self.page_register)
        
        # Page 2: 장비 장착/탈거 (인터락 적용 구역)
        self.page_equip = QWidget()
        layout2 = QFormLayout(self.page_equip)
        self.eq_id = QLineEdit()
        btn_mount = QPushButton("장비 장착 (Storage 상태만 가능)")
        btn_demount = QPushButton("장비 탈거 (Using 상태만 가능)")
        btn_mount.clicked.connect(self.mount_component)
        btn_demount.clicked.connect(self.demount_component)
        
        layout2.addRow("### 2. 부품의 장비 장착/탈거 페이지", QLabel(""))
        layout2.addRow("조회할 부품 ID:", self.eq_id)
        layout2.addRow(btn_mount)
        layout2.addRow(btn_demount)
        self.pages_widget.addWidget(self.page_equip)
        
        # Page 3: 연ma 출하
        self.page_regrid_out = QWidget()
        layout3 = QFormLayout(self.page_regrid_out)
        self.rout_id = QLineEdit()
        btn_rout = QPushButton("가공업체 연마 출하 처리")
        btn_rout.clicked.connect(self.ship_to_regrid)
        layout3.addRow("### 3. 부품의 연마 출하 페이지", QLabel(""))
        layout3.addRow("출하할 부품 ID:", self.rout_id)
        layout3.addRow(btn_rout)
        self.pages_widget.addWidget(self.page_regrid_out)
        
        # Page 4: 연ma 입고
        self.page_regrid_in = QWidget()
        layout4 = QFormLayout(self.page_regrid_in)
        self.rin_id = QLineEdit()
        self.rin_count = QLineEdit()
        btn_rin = QPushButton("성적서 기준 연마 가능 횟수 업데이트 및 입고")
        btn_rin.clicked.connect(self.receive_from_regrid)
        layout4.addRow("### 4. 부품의 연마 입고 페이지", QLabel(""))
        layout4.addRow("입고할 부품 ID:", self.rin_id)
        layout4.addRow("성적서 기재 잔여 연마가능 횟수:", self.rin_count)
        layout4.addRow(btn_rin)
        self.pages_widget.addWidget(self.page_regrid_in)
        
        # Page 5: 부품 ID 변경
        self.page_id_change = QWidget()
        layout5 = QFormLayout(self.page_id_change)
        self.old_id = QLineEdit()
        self.new_id = QLineEdit()
        btn_change_id = QPushButton("부품 일련번호(ID) 변경 실행")
        btn_change_id.clicked.connect(self.change_component_id)
        layout5.addRow("### 5. 부품의 ID 변경 페이지", QLabel(""))
        layout5.addRow("기존 부품 ID:", self.old_id)
        layout5.addRow("새로운 부품 ID:", self.new_id)
        layout5.addRow(btn_change_id)
        self.pages_widget.addWidget(self.page_id_change)

    def display_page(self, index):
        """메뉴 바 클릭 시 화면 전환 및 데이터 새로고침"""
        self.pages_widget.setCurrentIndex(index)
        if index == 0:
            self.refresh_home_summary()

    def refresh_home_summary(self):
        """Home 화면의 상태별 통계 Summary 업데이트"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, COUNT(*) FROM components GROUP BY status")
        rows = cursor.fetchall()
        conn.close()
        
        summary_text = "■ 현재 부품 보유 현황 Summary\n\n"
        if not rows:
            summary_text += "등록된 부품 데이터가 없습니다."
        for status, count in rows:
            summary_text += f" - {status}: {count} 개\n"
        self.home_summary.setText(summary_text)

    # --- 기능 로직 및 인터락 제어부 ---
    
    def register_component(self):
        comp_id = self.reg_id.text().strip()
        if not comp_id:
            return QMessageBox.warning(self, "경고", "일련번호를 입력해 주세요.")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO components (comp_id, manufacturer, comp_type, max_regrid) VALUES (?, ?, ?, ?)",
                           (comp_id, self.reg_manuf.currentText(), self.reg_type.currentText(), int(self.reg_max_regrid.text())))
            cursor.execute("INSERT INTO history_log (comp_id, action_type, detail) VALUES (?, 'Register', '최초 등록')", (comp_id,))
            conn.commit()
            QMessageBox.information(self, "성공", f"부품 [{comp_id}]이 정상 등록되었습니다.")
            self.reg_id.clear()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "오류", "이미 존재하는 부품 일련번호입니다.")
        finally:
            conn.close()

    def mount_component(self):
        """인터락: Storage 상태의 부품만 장착 가능"""
        comp_id = self.eq_id.text().strip()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM components WHERE comp_id = ?", (comp_id,))
        res = cursor.fetchone()
        
        if not res:
            return QMessageBox.warning(self, "오류", "존재하지 않는 부품 ID입니다.")
        
        current_status = res[0]
        if current_status != "Storage":
            # ★ 인터락 동작: 연마 대기 상태(Waiting) 등이면 장착 전면 차단
            return QMessageBox.critical(self, "인터락 해제 불가", f"해당 부품은 현재 [{current_status}] 상태입니다.\n연마 완료 후 'Storage' 상태인 부품만 장착할 수 있습니다.")
        
        cursor.execute("UPDATE components SET status = 'Using' WHERE comp_id = ?", (comp_id,))
        cursor.execute("INSERT INTO history_log (comp_id, action_type, detail) VALUES (?, 'Mount', '설비 장착 완료')", (comp_id,))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "완료", "장비 장착 처리가 완료되었습니다 (Using 상태 전환).")

    def demount_component(self):
        """탈거 처리 -> Waiting 상태 전환"""
        comp_id = self.eq_id.text().strip()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM components WHERE comp_id = ?", (comp_id,))
        res = cursor.fetchone()
        
        if not res or res[0] != "Using":
            return QMessageBox.warning(self, "오류", "현재 사용 중(Using) 상태인 부품만 탈거할 수 있습니다.")
        
        cursor.execute("UPDATE components SET status = 'Waiting' WHERE comp_id = ?", (comp_id,))
        cursor.execute("INSERT INTO history_log (comp_id, action_type, detail) VALUES (?, 'Demount', '설비 탈거 완료 (연마 대기)')", (comp_id,))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "완료", "장비 탈거 처리가 완료되었습니다 (Waiting 상태 전환).")

    def ship_to_regrid(self):
        """연마 출하 -> Regrid 상태 전환"""
        comp_id = self.rout_id.text().strip()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM components WHERE comp_id = ?", (comp_id,))
        res = cursor.fetchone()
        
        if not res or res[0] != "Waiting":
            return QMessageBox.warning(self, "오류", "연마 대기(Waiting) 상태인 부품만 출하할 수 있습니다.")
            
        cursor.execute("UPDATE components SET status = 'Regrid' WHERE comp_id = ?", (comp_id,))
        cursor.execute("INSERT INTO history_log (comp_id, action_type, detail) VALUES (?, 'Ship_Regrid', '가공업체 출하')", (comp_id,))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "완료", "연마 출하 처리가 완료되었습니다 (Regrid 상태 전환).")

    def receive_from_regrid(self):
        """연마 입고 -> 성적서 기준 업데이트 -> Storage 상태 전환"""
        comp_id = self.rin_id.text().strip()
        new_max = self.rin_count.text().strip()
        
        if not new_max.isdigit():
            return QMessageBox.warning(self, "오류", "연마 가능 횟수는 숫자만 입력 가능합니다.")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, regrid_count FROM components WHERE comp_id = ?", (comp_id,))
        res = cursor.fetchone()
        
        if not res or res[0] != "Regrid":
            return QMessageBox.warning(self, "오류", "현재 외주 연마 중(Regrid) 상태인 부품만 입고 가능합니다.")
        
        next_regrid_count = res[1] + 1
        cursor.execute("""
            UPDATE components 
            SET status = 'Storage', regrid_count = ?, max_regrid = ? 
            WHERE comp_id = ?
        """, (next_regrid_count, int(new_max), comp_id))
        
        cursor.execute("INSERT INTO history_log (comp_id, action_type, detail) VALUES (?, 'Receive_Regrid', ?)", 
                       (comp_id, f"연마 입고 완료 (누적 {next_regrid_count}회 / 잔여 {new_max}회)"))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "완료", "연마 입고 및 성적서 데이터 업데이트가 완료되었습니다.")
        self.rin_id.clear()
        self.rin_count.clear()

    def change_component_id(self):
        """기존 부품 ID를 새 고유 ID로 변경 (CASCADE 옵션으로 이력 데이터도 자동 연동됨)"""
        old_id = self.old_id.text().strip()
        new_id = self.new_id.text().strip()
        
        if not old_id or not new_id:
            return QMessageBox.warning(self, "경고", "기존 ID와 신규 ID를 모두 입력해 주세요.")
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT comp_id FROM components WHERE comp_id = ?", (old_id,))
        if not cursor.fetchone():
            return QMessageBox.warning(self, "오류", "존재하지 않는 기존 부품 ID입니다.")
            
        try:
            cursor.execute("UPDATE components SET comp_id = ? WHERE comp_id = ?", (new_id, old_id))
            cursor.execute("INSERT INTO history_log (comp_id, action_type, detail) VALUES (?, 'ID_Change', ?)", 
                           (new_id, f"기존 ID [{old_id}] 에서 변경됨"))
            conn.commit()
            QMessageBox.information(self, "성공", f"부품 ID가 [{old_id}] -> [{new_id}]로 변경되었습니다.")
            self.old_id.clear()
            self.new_id.clear()
        except sqlite3.IntegrityError:
            QMessageBox.critical(self, "오류", "새로 지정하려는 ID가 이미 데이터베이스에 존재합니다.")
        finally:
            conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PartsManagerApp()
    ex.show()
    sys.exit(app.exec())
