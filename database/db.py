import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("database/vbcua_history.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filename TEXT NOT NULL,
                concept_name TEXT NOT NULL,
                overall_score REAL NOT NULL,
                grade TEXT NOT NULL,
                semantic_score REAL NOT NULL,
                fluency_score REAL NOT NULL,
                communication_score REAL NOT NULL,
                transcript TEXT,
                filler_count INTEGER,
                pdf_report_path TEXT,
                meta_json TEXT
            )
        """)
        conn.commit()

def save_evaluation(filename, concept_name, overall_score, grade, semantic_score, 
                    fluency_score, communication_score, transcript, filler_count, pdf_report_path, meta_dict=None):
    init_db()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta_json = json.dumps(meta_dict) if meta_dict else "{}"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO evaluation_history (
                timestamp, filename, concept_name, overall_score, grade,
                semantic_score, fluency_score, communication_score, transcript,
                filler_count, pdf_report_path, meta_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, filename, concept_name, float(overall_score), grade,
            float(semantic_score), float(fluency_score), float(communication_score),
            transcript, int(filler_count), pdf_report_path, meta_json
        ))
        conn.commit()

def get_all_evaluations():
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM evaluation_history ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_evaluation_stats():
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_evaluations,
                AVG(overall_score) as avg_overall,
                AVG(semantic_score) as avg_semantic,
                AVG(fluency_score) as avg_fluency,
                AVG(communication_score) as avg_communication,
                SUM(filler_count) as total_fillers
            FROM evaluation_history
        """)
        row = cursor.fetchone()
        if not row or row["total_evaluations"] == 0:
            return {
                "total_evaluations": 0,
                "avg_overall": 0.0,
                "avg_semantic": 0.0,
                "avg_fluency": 0.0,
                "avg_communication": 0.0,
                "total_fillers": 0
            }
        return dict(row)

def delete_evaluation(eval_id):
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM evaluation_history WHERE id = ?", (eval_id,))
        conn.commit()

def clear_all_history():
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM evaluation_history")
        conn.commit()
