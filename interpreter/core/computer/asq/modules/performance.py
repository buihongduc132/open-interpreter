"""
Performance optimization module for ASQ integration.
Provides caching, lazy loading, and performance monitoring.
"""

import time
import weakref
from typing import Any, Dict, List, Optional, Callable, Tuple
from functools import wraps, lru_cache
from threading import Lock


class ElementCache:
    """Cache for GUI elements to improve performance."""
    
    def __init__(self, max_size: int = 100, ttl: float = 30.0):
        """Initialize element cache.
        
        Args:
            max_size: Maximum number of cached elements
            ttl: Time-to-live for cached elements in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache = {}
        self._timestamps = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get element from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached element or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            # Check if expired
            if time.time() - self._timestamps[key] > self.ttl:
                del self._cache[key]
                del self._timestamps[key]
                return None
            
            return self._cache[key]
    
    def set(self, key: str, element: Any) -> None:
        """Store element in cache.
        
        Args:
            key: Cache key
            element: Element to cache
        """
        with self._lock:
            # Remove oldest entries if cache is full
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._timestamps.keys(), key=self._timestamps.get)
                del self._cache[oldest_key]
                del self._timestamps[oldest_key]
            
            self._cache[key] = element
            self._timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cached elements."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed items."""
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, timestamp in self._timestamps.items():
                if current_time - timestamp > self.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                del self._timestamps[key]
        
        return len(expired_keys)


class PerformanceMonitor:
    """Monitor and track ASQ performance metrics."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.operation_times = {}
        self.operation_counts = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self._lock = Lock()
    
    def record_operation(self, operation: str, duration: float) -> None:
        """Record operation timing.
        
        Args:
            operation: Name of the operation
            duration: Time taken in seconds
        """
        with self._lock:
            if operation not in self.operation_times:
                self.operation_times[operation] = []
                self.operation_counts[operation] = 0
            
            self.operation_times[operation].append(duration)
            self.operation_counts[operation] += 1
            
            # Keep only last 100 measurements
            if len(self.operation_times[operation]) > 100:
                self.operation_times[operation] = self.operation_times[operation][-100:]
    
    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        with self._lock:
            self.cache_hits += 1
    
    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        with self._lock:
            self.cache_misses += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        with self._lock:
            stats = {
                'operations': {},
                'cache': {
                    'hits': self.cache_hits,
                    'misses': self.cache_misses,
                    'hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
                }
            }
            
            for operation, times in self.operation_times.items():
                if times:
                    stats['operations'][operation] = {
                        'count': self.operation_counts[operation],
                        'avg_time': sum(times) / len(times),
                        'min_time': min(times),
                        'max_time': max(times),
                        'total_time': sum(times)
                    }
            
            return stats
    
    def clear_stats(self) -> None:
        """Clear all performance statistics."""
        with self._lock:
            self.operation_times.clear()
            self.operation_counts.clear()
            self.cache_hits = 0
            self.cache_misses = 0


class LazyLoader:
    """Lazy loading for expensive ASQ operations."""
    
    def __init__(self):
        """Initialize lazy loader."""
        self._loaded_modules = {}
        self._loading_lock = Lock()
    
    def load_module(self, module_name: str, loader_func: Callable) -> Any:
        """Lazily load a module.
        
        Args:
            module_name: Name of the module
            loader_func: Function to load the module
            
        Returns:
            Loaded module
        """
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]
        
        with self._loading_lock:
            # Double-check pattern
            if module_name in self._loaded_modules:
                return self._loaded_modules[module_name]
            
            module = loader_func()
            self._loaded_modules[module_name] = module
            return module
    
    def is_loaded(self, module_name: str) -> bool:
        """Check if module is loaded.
        
        Args:
            module_name: Name of the module
            
        Returns:
            True if module is loaded
        """
        return module_name in self._loaded_modules
    
    def unload_module(self, module_name: str) -> None:
        """Unload a module.
        
        Args:
            module_name: Name of the module to unload
        """
        with self._loading_lock:
            if module_name in self._loaded_modules:
                del self._loaded_modules[module_name]


# Global instances
element_cache = ElementCache()
performance_monitor = PerformanceMonitor()
lazy_loader = LazyLoader()


def cached(cache_key_func: Optional[Callable] = None, ttl: float = 30.0):
    """Decorator to cache function results.
    
    Args:
        cache_key_func: Function to generate cache key
        ttl: Time-to-live for cached results
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = element_cache.get(cache_key)
            if cached_result is not None:
                performance_monitor.record_cache_hit()
                return cached_result
            
            # Execute function and cache result
            performance_monitor.record_cache_miss()
            result = func(*args, **kwargs)
            element_cache.set(cache_key, result)
            return result
        
        return wrapper
    return decorator


def timed(func: Callable) -> Callable:
    """Decorator to time function execution.
    
    Args:
        func: Function to time
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            performance_monitor.record_operation(func.__name__, duration)
    
    return wrapper


def optimized(cache_ttl: float = 30.0):
    """Decorator combining caching and timing.
    
    Args:
        cache_ttl: Cache time-to-live in seconds
    """
    def decorator(func: Callable) -> Callable:
        return timed(cached(ttl=cache_ttl)(func))
    return decorator


class ConnectionPool:
    """Pool for AT-SPI connections to improve performance."""
    
    def __init__(self, max_connections: int = 5):
        """Initialize connection pool.
        
        Args:
            max_connections: Maximum number of connections
        """
        self.max_connections = max_connections
        self._connections = []
        self._in_use = set()
        self._lock = Lock()
    
    def get_connection(self) -> Any:
        """Get a connection from the pool.
        
        Returns:
            AT-SPI connection
        """
        with self._lock:
            # Try to reuse existing connection
            for conn in self._connections:
                if conn not in self._in_use:
                    self._in_use.add(conn)
                    return conn
            
            # Create new connection if under limit
            if len(self._connections) < self.max_connections:
                conn = self._create_connection()
                if conn:
                    self._connections.append(conn)
                    self._in_use.add(conn)
                    return conn
            
            # Wait for connection to become available
            # In a real implementation, this would use proper waiting
            return None
    
    def release_connection(self, connection: Any) -> None:
        """Release a connection back to the pool.
        
        Args:
            connection: Connection to release
        """
        with self._lock:
            if connection in self._in_use:
                self._in_use.remove(connection)
    
    def close_all(self) -> None:
        """Close all connections in the pool."""
        with self._lock:
            for conn in self._connections:
                try:
                    if hasattr(conn, 'close'):
                        conn.close()
                except:
                    pass
            self._connections.clear()
            self._in_use.clear()
    
    def _create_connection(self) -> Optional[Any]:
        """Create a new AT-SPI connection.
        
        Returns:
            New connection or None if failed
        """
        try:
            # This would create actual AT-SPI connection
            # For now, return a placeholder
            return object()
        except Exception:
            return None


# Global connection pool
connection_pool = ConnectionPool()


def get_performance_report() -> str:
    """Generate a performance report.
    
    Returns:
        Formatted performance report
    """
    stats = performance_monitor.get_stats()
    
    report = ["ASQ Performance Report", "=" * 30]
    
    # Cache statistics
    cache_stats = stats['cache']
    report.append(f"Cache Hit Rate: {cache_stats['hit_rate']:.2%}")
    report.append(f"Cache Hits: {cache_stats['hits']}")
    report.append(f"Cache Misses: {cache_stats['misses']}")
    report.append(f"Cache Size: {element_cache.size()}")
    report.append("")
    
    # Operation statistics
    report.append("Operation Performance:")
    for operation, op_stats in stats['operations'].items():
        report.append(f"  {operation}:")
        report.append(f"    Count: {op_stats['count']}")
        report.append(f"    Avg Time: {op_stats['avg_time']:.3f}s")
        report.append(f"    Min Time: {op_stats['min_time']:.3f}s")
        report.append(f"    Max Time: {op_stats['max_time']:.3f}s")
        report.append(f"    Total Time: {op_stats['total_time']:.3f}s")
    
    return "\n".join(report)


def cleanup_performance_data() -> None:
    """Clean up performance data and expired cache entries."""
    expired_count = element_cache.cleanup_expired()
    performance_monitor.clear_stats()
    
    if expired_count > 0:
        print(f"Cleaned up {expired_count} expired cache entries")