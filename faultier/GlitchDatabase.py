import sqlite3
import os
from typing import Optional, List, Tuple
import threading

class GlitchDatabase:
    """
    A simple Python library for managing voltage fault-injection testing results.
    
    Usage:
        gd = GlitchDatabase("measurements.db", "higher_temperatures")
        gd.addResult(delay=100, pulse=500, result="Glitched")
        gd.flush()  # Optional - results are auto-flushed
    """
    
    def __init__(self, db_path: str, identifier: str, auto_flush: bool = True, batch_size: int = 5):
        """
        Initialize the GlitchDatabase.
        
        Args:
            db_path (str): Path to the SQLite database file
            identifier (str): Identifier for this test run (e.g., "higher_temperatures")
            auto_flush (bool): Whether to automatically flush results to database
            batch_size (int): Number of results to batch before auto-flushing
        """
        self.db_path = db_path
        self.identifier = identifier
        self.auto_flush = auto_flush
        self.batch_size = batch_size
        self._pending_results = []
        self._lock = threading.Lock()
        
        # Create database and table if they don't exist
        self._initialize_database()
    
    def _initialize_database(self):
        """Create the database and table if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS measurements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        identifier TEXT,
                        pulse INTEGER,
                        delay INTEGER,
                        freetext_result TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to initialize database: {e}")
    
    def addResult(self, delay: int, pulse: int, result: str) -> None:
        """
        Add a measurement result to the database.
        
        Args:
            delay (int): Delay value for the measurement
            pulse (int): Pulse value for the measurement
            result (str): Result description (e.g., "Glitched", "Crashed", "Reset")
        """
        if not isinstance(delay, int) or not isinstance(pulse, int):
            raise ValueError("Delay and pulse must be integers")
        
        if not isinstance(result, str) or not result.strip():
            raise ValueError("Result must be a non-empty string")
        
        with self._lock:
            self._pending_results.append((self.identifier, pulse, delay, result.strip()))
            
            # Auto-flush if batch size is reached
            if self.auto_flush and len(self._pending_results) >= self.batch_size:
                self._flush_to_database()
    
    def _flush_to_database(self) -> int:
        """
        Internal method to flush pending results to the database.
        
        Returns:
            int: Number of results flushed
        """
        if not self._pending_results:
            return 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany(
                    'INSERT INTO measurements (identifier, pulse, delay, freetext_result) VALUES (?, ?, ?, ?)',
                    self._pending_results
                )
                conn.commit()
                
                count = len(self._pending_results)
                self._pending_results.clear()
                return count
                
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to flush results to database: {e}")
    
    def flush(self) -> int:
        """
        Manually flush all pending results to the database.
        
        Returns:
            int: Number of results flushed
        """
        with self._lock:
            return self._flush_to_database()
    
    def getPendingCount(self) -> int:
        """
        Get the number of pending results not yet flushed to the database.
        
        Returns:
            int: Number of pending results
        """
        with self._lock:
            return len(self._pending_results)
    
    def getResultCount(self, identifier: Optional[str] = None) -> int:
        """
        Get the total number of results in the database.
        
        Args:
            identifier (str, optional): If provided, count only results for this identifier
        
        Returns:
            int: Number of results in the database
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if identifier:
                    cursor.execute('SELECT COUNT(*) FROM measurements WHERE identifier = ?', (identifier,))
                else:
                    cursor.execute('SELECT COUNT(*) FROM measurements')
                
                return cursor.fetchone()[0]
                
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to query database: {e}")
    
    def getResults(self, identifier: Optional[str] = None, limit: Optional[int] = None) -> List[Tuple]:
        """
        Retrieve results from the database.
        
        Args:
            identifier (str, optional): If provided, get only results for this identifier
            limit (int, optional): Maximum number of results to return
        
        Returns:
            List[Tuple]: List of (id, identifier, pulse, delay, freetext_result) tuples
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = 'SELECT id, identifier, pulse, delay, freetext_result FROM measurements'
                params = []
                
                if identifier:
                    query += ' WHERE identifier = ?'
                    params.append(identifier)
                
                query += ' ORDER BY id DESC'
                
                if limit:
                    query += ' LIMIT ?'
                    params.append(limit)
                
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to query database: {e}")
    
    def clearResults(self, identifier: Optional[str] = None) -> int:
        """
        Clear results from the database.
        
        Args:
            identifier (str, optional): If provided, clear only results for this identifier.
                                      If None, clears ALL results (use with caution!)
        
        Returns:
            int: Number of results deleted
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if identifier:
                    cursor.execute('DELETE FROM measurements WHERE identifier = ?', (identifier,))
                else:
                    cursor.execute('DELETE FROM measurements')
                
                conn.commit()
                return cursor.rowcount
                
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to clear results: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures all results are flushed."""
        self.flush()
    
    def __del__(self):
        """Destructor - ensures all results are flushed."""
        try:
            self.flush()
        except:
            pass  # Ignore errors during cleanup 