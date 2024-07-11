import sqlite3

def fetch_records(table_name):
    conn = sqlite3.connect('C:/Users/kumar/Desktop/Capstone-Project-master/instance/database.db')  
    cursor = conn.cursor()
    
    try:
        cursor.execute(f'SELECT * FROM {table_name}')
        records = cursor.fetchall()
        for record in records:
            print(record)
    
    except sqlite3.Error as e:
        print("Error fetching records:", e)
    
    finally:
        
        cursor.close()
        conn.close()

fetch_records('client')