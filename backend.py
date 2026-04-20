import mysql.connector
from mysql.connector import Error, pooling
import hashlib

class ChatDatabase:
    """
    Handles all database interactions for the Chat Application.
    Implements a simple connection pooling pattern for scalability and efficiency.
    """

    def __init__(self, host, user, password, database):
        """Initializes connection pooling for secure, thread-safe database operations."""
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="chat_app_pool",
                pool_size=5,
                pool_reset_session=True,
                host=host,
                user=user,
                password=password,
                database=database
            )
            print("Database connection pool created successfully.")
        except Error as e:
            print(f"Database Initialization Error: {e}")
            self.pool = None

    def _hash_password(self, password):
        """Security Practice: Hashes user passwords using SHA-256 for secure storage."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, email, password):
        """Registers a user. Inserts secure credentials into the users table."""
        if not self.pool: 
            return False, "DB Pool missing. Cannot connect."
        
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            pwd_hash = self._hash_password(password)
            
            # Using parameterized query to prevent SQL injections
            query = "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)"
            cursor.execute(query, (username, email, pwd_hash))
            
            conn.commit()  # Explicitly commit data on success
            return True, "User registered successfully!"
        except Error as e:
            conn.rollback()  # Transaction rollback in case of issues (e.g. UNIQUE constraint fail)
            return False, f"Registration failed: {e.msg}"
        finally:
            cursor.close()
            conn.close()

    def login_user(self, username, password):
        """Authenticates user with username and password login."""
        if not self.pool: return None
        
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            pwd_hash = self._hash_password(password)
            
            query = "SELECT id, username FROM users WHERE username = %s AND password_hash = %s"
            cursor.execute(query, (username, pwd_hash))
            
            user = cursor.fetchone()
            return user
        except Error as e:
            print(f"Login database error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def get_user_chats(self, user_id):
        """Fetch basic chat records to see what chats the user is currently involved in."""
        if not self.pool: return []
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT c.id, c.is_group 
            FROM chats c
            JOIN chat_participants cp ON c.id = cp.chat_id
            WHERE cp.user_id = %s
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def send_message(self, chat_id, sender_id, text_content):
        """
        Sends a message into a chat. 
        Shows an example of safe transaction handling where message & status 
        need to be pushed together as a single atomic unit.
        """
        if not self.pool: return False
        
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            
            # Explicit transaction begins implicitly on first execute
            
            # 2. Insert the main message text
            cursor.execute(
                "INSERT INTO messages (chat_id, sender_id, message_type, content) VALUES (%s, %s, 'text', %s)",
                (chat_id, sender_id, text_content)
            )
            msg_id = cursor.lastrowid
            
            # 3. Create the corresponding default status indicator line (e.g. 'sent')
            cursor.execute(
                "INSERT INTO message_status (message_id, user_id, status) VALUES (%s, %s, 'sent')",
                (msg_id, sender_id)
            )
            
            # 4. Success -> Finalize and persist database edit actions
            conn.commit()
            return True
        except Error as e:
            # Revert any uncommitted inserts to keep consistent DB state if this failed
            conn.rollback()
            print(f"Send message failed - Internal rollback generated: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_chat_history(self, chat_id):
        """
        Fetches full message history using Common Table Expressions (CTEs)
        used mainly to elegantly assemble the username string next to the texts before finalizing SELECT.
        """
        if not self.pool: return []
        
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            
            # CTE querying allows making complex multi-joins easily structured 
            query = """
            WITH FormattedMessages AS (
                SELECT 
                    m.id,
                    m.content,
                    m.sent_at,
                    m.sender_id,
                    u.username AS sender_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.chat_id = %s
            )
            SELECT * FROM FormattedMessages ORDER BY sent_at ASC;
            """
            cursor.execute(query, (chat_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def get_recent_chats(self, user_id):
        """
        Fetch the single most recent message for all chats of this user. 
        Reads directly from the Advanced Window Function aggregate 'view_latest_messages' 
        """
        if not self.pool: return []
        
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            
            query = """
            SELECT v.chat_id, v.content, v.sent_at, u.username as sender_name
            FROM view_latest_messages v
            JOIN chat_participants cp ON v.chat_id = cp.chat_id
            JOIN users u ON v.sender_id = u.id
            WHERE cp.user_id = %s
            ORDER BY v.sent_at DESC
            """
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
            
    def setup_new_chat(self, user_id, other_username):
        """Shortcut method to launch a new chat."""
        if not self.pool: return False, "Database connection pool is offline."
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            # Find destination username target inside `users` 
            cursor.execute("SELECT id FROM users WHERE username = %s", (other_username.strip(),))
            other = cursor.fetchone()
            if not other: return False, f"The specific user '{other_username}' does not show in the system directory."
            
            other_id = other['id']
            
            cursor.execute("INSERT INTO chats (is_group) VALUES (0)")
            chat_id = cursor.lastrowid
            
            cursor.execute("INSERT INTO chat_participants (chat_id, user_id) VALUES (%s, %s)", (chat_id, user_id))
            cursor.execute("INSERT INTO chat_participants (chat_id, user_id) VALUES (%s, %s)", (chat_id, other_id))
            
            conn.commit()
            return True, chat_id
        except Error as e:
            conn.rollback()
            print(f"Failed to setup chat relation: {e}")
            return False, f"Database crashed during Chat Generation: {e}"
        finally:
            cursor.close()
            conn.close()
