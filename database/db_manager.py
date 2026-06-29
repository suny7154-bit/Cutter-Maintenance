import os
import sys
import sqlite3

# 1. USB/실행 경로 친화적 DB 경로 설정
if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(current_dir, "parts_management.db")

def init_db():
    """데이터베이스 및 테이블 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 외래키 제약조건 활성화
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 부품 마스터 테이블 (ID 변경 시 이력도 같이 바뀌도록 ON UPDATE CASCADE 설정)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS components (
            comp_id TEXT PRIMARY KEY,
            name TEXT NOT EXISTS DEFAULT '부품',
            manufacturer TEXT,
            comp_type TEXT,
            status TEXT DEFAULT 'Storage',
            regrid_count INTEGER DEFAULT 0,
            max_regrid INTEGER DEFAULT 15
        )
    """)
    
    # 작업 이력 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            comp_id TEXT,
            action_type TEXT,
            action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            detail TEXT,
            FOREIGN KEY(comp_id) REFERENCES components(comp_id) ON UPDATE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_PATH)
