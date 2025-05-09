import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='conference.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Attendees Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                organization TEXT,
                position TEXT,
                bio TEXT,
                last_attended DATETIME
            )
        ''')
        
        # Conference Calls Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conference_calls (
                call_id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_topic TEXT NOT NULL,
                call_time DATETIME NOT NULL,
                host_id INTEGER,
                FOREIGN KEY(host_id) REFERENCES attendees(id)
            )
        ''')
        
        # Attendance Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id INTEGER,
                attendee_id INTEGER,
                FOREIGN KEY(call_id) REFERENCES conference_calls(call_id),
                FOREIGN KEY(attendee_id) REFERENCES attendees(id)
            )
        ''')
        self.conn.commit()
    
    # CRUD Operations for Attendees
    def add_attendee(self, data):
        sql = '''INSERT INTO attendees 
                 (first_name, last_name, email, phone, organization, position, bio, last_attended)
                 VALUES (?,?,?,?,?,?,?,?)'''
        cursor = self.conn.cursor()
        cursor.execute(sql, data)
        self.conn.commit()
        return cursor.lastrowid
    
    def get_attendees(self, search_term=None):
        sql = '''SELECT * FROM attendees'''
        params = ()
        if search_term:
            sql += ''' WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?'''
            params = (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%')
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    
    # Add other CRUD methods here (update, delete, etc.)

    def __del__(self):
        self.conn.close()
