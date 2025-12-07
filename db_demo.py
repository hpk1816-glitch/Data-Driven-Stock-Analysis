import mysql.connector
from mysql.connector import Error

# ==== CHANGE ONLY IF YOUR PASSWORD / USER IS DIFFERENT ====
DB_HOST = "localhost"
DB_USER = "root"               # MySQL username
DB_PASSWORD = "Prakash@2025"   # Your MySQL password
DB_NAME = "stock_analysis"     # Database created by final_sql.sql
# ===========================================================

def main():
    """Small demo: connect to MySQL and read a bit of data."""
    conn = None
    cursor = None

    try:
        # 1) Connect to MySQL
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )

        if conn.is_connected():
            print(f"✅ Connected to MySQL database: {DB_NAME}")

            cursor = conn.cursor()

            # 2) Get total rows in stocks table
            cursor.execute("SELECT COUNT(*) FROM stocks;")
            total_rows = cursor.fetchone()[0]
            print(f"Total rows in stocks table: {total_rows}")

            # 3) Get a small sample of data
            cursor.execute(
                """
                SELECT date, ticker, open, high, low, close, volume
                FROM stocks
                ORDER BY date ASC
                LIMIT 5;
                """
            )
            rows = cursor.fetchall()

            print("\nSample data from stocks table:")
            for row in rows:
                print(row)

    except Error as e:
        print("\n❌ Error while connecting / querying MySQL:")
        print(e)

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()
            print("\nMySQL connection is closed.")

if __name__ == "__main__":
    main()
