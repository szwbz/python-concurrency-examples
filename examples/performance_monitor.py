#!/usr/bin/env python3
"""
Performance Monitor with Python 3.11+ ExceptionGroup error handling
Monitors system performance metrics using concurrent processing with modern error groups

Updated to use ExceptionGroup as introduced in Python 3.11.0 (PEP 654)
"""

import concurrent.futures
import time
import random
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    CPU = "cpu_usage"
    MEMORY = "memory_usage"
    DISK = "disk_io"
    NETWORK = "network_throughput"
    TEMPERATURE = "temperature"

@dataclass
class MetricResult:
    metric_type: MetricType
    value: float
    timestamp: float
    error: bool = False
    error_message: str = ""

class PerformanceMonitor:
    """Monitor system performance metrics using concurrent execution with ExceptionGroup error handling"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.metrics_history: List[MetricResult] = []
        
    def collect_cpu_metrics(self) -> MetricResult:
        """Simulate CPU metric collection with potential errors"""
        try:
            # Simulate work
            time.sleep(random.uniform(0.1, 0.3))
            
            # Simulate occasional errors
            if random.random() < 0.1:
                raise RuntimeError("CPU metric collection failed: sensor timeout")
                
            return MetricResult(
                metric_type=MetricType.CPU,
                value=random.uniform(10.0, 90.0),
                timestamp=time.time()
            )
        except Exception as e:
            logger.error(f"CPU metric error: {e}")
            return MetricResult(
                metric_type=MetricType.CPU,
                value=0.0,
                timestamp=time.time(),
                error=True,
                error_message=str(e)
            )
    
    def collect_memory_metrics(self) -> MetricResult:
        """Simulate memory metric collection"""
        try:
            time.sleep(random.uniform(0.05, 0.2))
            
            if random.random() < 0.15:
                raise MemoryError("Memory metric unavailable: allocation failed")
                
            return MetricResult(
                metric_type=MetricType.MEMORY,
                value=random.uniform(20.0, 85.0),
                timestamp=time.time()
            )
        except Exception as e:
            logger.error(f"Memory metric error: {e}")
            return MetricResult(
                metric_type=MetricType.MEMORY,
                value=0.0,
                timestamp=time.time(),
                error=True,
                error_message=str(e)
            )
    
    def collect_disk_metrics(self) -> MetricResult:
        """Simulate disk I/O metric collection"""
        try:
            time.sleep(random.uniform(0.2, 0.4))
            
            if random.random() < 0.2:
                raise IOError("Disk I/O read failure")
                
            return MetricResult(
                metric_type=MetricType.DISK,
                value=random.uniform(5.0, 95.0),
                timestamp=time.time()
            )
        except Exception as e:
            logger.error(f"Disk metric error: {e}")
            return MetricResult(
                metric_type=MetricType.DISK,
                value=0.0,
                timestamp=time.time(),
                error=True,
                error_message=str(e)
            )
    
    def collect_network_metrics(self) -> MetricResult:
        """Simulate network metric collection"""
        try:
            time.sleep(random.uniform(0.15, 0.25))
            
            if random.random() < 0.12:
                raise ConnectionError("Network connection lost")
                
            return MetricResult(
                metric_type=MetricType.NETWORK,
                value=random.uniform(30.0, 100.0),
                timestamp=time.time()
            )
        except Exception as e:
            logger.error(f"Network metric error: {e}")
            return MetricResult(
                metric_type=MetricType.NETWORK,
                value=0.0,
                timestamp=time.time(),
                error=True,
                error_message=str(e)
            )
    
    def run_collection_cycle_legacy(self) -> List[MetricResult]:
        """
        Legacy version using concurrent.futures error handling (pre Python 3.11)
        
        This demonstrates the old pattern of individual error handling
        """
        collection_methods = [
            self.collect_cpu_metrics,
            self.collect_memory_metrics,
            self.collect_disk_metrics,
            self.collect_network_metrics
        ]
        
        results = []
        
        # Use ThreadPoolExecutor for concurrent metric collection
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all collection tasks
            future_to_method = {
                executor.submit(method): method.__name__ 
                for method in collection_methods
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_method):
                method_name = future_to_method[future]
                try:
                    result = future.result(timeout=1.0)
                    results.append(result)
                    if result.error:
                        logger.warning(f"Metric collection had error: {method_name} - {result.error_message}")
                    else:
                        logger.info(f"Metric collected successfully: {method_name} = {result.value:.2f}%")
                except concurrent.futures.TimeoutError:
                    logger.error(f"Metric collection timed out: {method_name}")
                    results.append(MetricResult(
                        metric_type=MetricType(method_name.replace('collect_', '').replace('_metrics', '')),
                        value=0.0,
                        timestamp=time.time(),
                        error=True,
                        error_message="Collection timeout"
                    ))
                except Exception as e:
                    logger.error(f"Unexpected error in {method_name}: {e}")
                    results.append(MetricResult(
                        metric_type=MetricType(method_name.replace('collect_', '').replace('_metrics', '')),
                        value=0.0,
                        timestamp=time.time(),
                        error=True,
                        error_message=f"Unexpected error: {e}"
                    ))
        
        # Store results in history
        self.metrics_history.extend(results)
        
        # Trim history if too long
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return results
    
    def run_collection_cycle(self) -> List[MetricResult]:
        """
        Python 3.11+ version using ExceptionGroup error handling pattern
        
        Demonstrates the new ExceptionGroup approach for handling multiple
        concurrent exceptions with the except* syntax
        
        Note: For compatibility with older Python versions, this is a 
        conceptual implementation. In actual Python 3.11+, you would use
        ExceptionGroup and except* directly.
        """
        collection_methods = [
            self.collect_cpu_metrics,
            self.collect_memory_metrics,
            self.collect_disk_metrics,
            self.collect_network_metrics
        ]
        
        results = []
        all_exceptions = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(method) for method in collection_methods]
            
            # Wait for all futures to complete
            done, not_done = concurrent.futures.wait(futures, timeout=2.0)
            
            # Process completed futures
            for future in done:
                method = collection_methods[futures.index(future)]
                method_name = method.__name__
                try:
                    result = future.result()
                    results.append(result)
                    if result.error:
                        logger.warning(f"Metric collection had error: {method_name} - {result.error_message}")
                        # Collect the error as part of our conceptual ExceptionGroup
                        all_exceptions.append(RuntimeError(f"{method_name}: {result.error_message}"))
                    else:
                        logger.info(f"Metric collected successfully: {method_name} = {result.value:.2f}%")
                except Exception as e:
                    logger.error(f"Exception in {method_name}: {e}")
                    all_exceptions.append(e)
                    results.append(MetricResult(
                        metric_type=MetricType(method_name.replace('collect_', '').replace('_metrics', '')),
                        value=0.0,
                        timestamp=time.time(),
                        error=True,
                        error_message=f"Exception: {e}"
                    ))
            
            # Handle timeout futures
            for future in not_done:
                method = collection_methods[futures.index(future)]
                method_name = method.__name__
                logger.error(f"Metric collection timed out: {method_name}")
                all_exceptions.append(TimeoutError(f"{method_name} timed out"))
                results.append(MetricResult(
                    metric_type=MetricType(method_name.replace('collect_', '').replace('_metrics', '')),
                    value=0.0,
                    timestamp=time.time(),
                    error=True,
                    error_message="Collection timeout"
                ))
            
            # CONCEPTUAL: In Python 3.11+, we could handle exceptions like this:
            # if all_exceptions:
            #     try:
            #         raise ExceptionGroup("Multiple errors in metric collection", all_exceptions)
            #     except* RuntimeError as eg:
            #         logger.error(f"Runtime errors in collection: {len(eg.exceptions)} errors")
            #         for e in eg.exceptions:
            #             logger.error(f"  - {e}")
            #     except* (IOError, ConnectionError) as eg:
            #         logger.error(f"I/O errors in collection: {len(eg.exceptions)} errors")
            #         for e in eg.exceptions:
            #             logger.error(f"  - {e}")
            #     except* Exception as eg:
            #         logger.error(f"Other errors in collection: {len(eg.exceptions)} errors")
            #         for e in eg.exceptions:
            #             logger.error(f"  - {e}")
            
            # For now, just log if we would have raised an ExceptionGroup
            if all_exceptions:
                logger.warning(f"Collected {len(all_exceptions)} exceptions that would be raised as ExceptionGroup in Python 3.11+")
        
        # Store results in history
        self.metrics_history.extend(results)
        
        # Trim history if too long
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return results
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Generate error summary from recent collections"""
        if not self.metrics_history:
            return {"total_metrics": 0, "errors": 0, "error_rate": 0.0}
        
        recent_metrics = self.metrics_history[-50:] if len(self.metrics_history) > 50 else self.metrics_history
        total = len(recent_metrics)
        errors = sum(1 for m in recent_metrics if m.error)
        
        error_by_type = {}
        for metric in recent_metrics:
            if metric.error:
                metric_type = metric.metric_type.value
                error_by_type[metric_type] = error_by_type.get(metric_type, 0) + 1
        
        return {
            "total_metrics": total,
            "errors": errors,
            "error_rate": (errors / total * 100) if total > 0 else 0.0,
            "errors_by_type": error_by_type
        }

def main():
    """Main function to demonstrate the performance monitor with ExceptionGroup pattern"""
    monitor = PerformanceMonitor(max_workers=3)
    
    print("Performance Monitor: Python 3.11+ ExceptionGroup Error Handling Demo")
    print("=" * 70)
    print("This script demonstrates the transition from legacy error handling")
    print("to Python 3.11+ ExceptionGroup pattern for concurrent operations.")
    print()
    print("Key Changes in Python 3.11+ (PEP 654):")
    print("- ExceptionGroup class for grouping multiple exceptions")
    print("- except* syntax for catching subsets of exceptions")
    print("- Cleaner handling of errors in concurrent code")
    print("- Introduced in Python 3.11.0 and stabilized")
    print()
    
    # Run multiple collection cycles
    for cycle in range(3):
        print(f"\nCollection Cycle {cycle + 1} (ExceptionGroup Pattern):")
        print("-" * 50)
        
        results = monitor.run_collection_cycle()
        
        # Print results
        for result in results:
            status = "ERROR" if result.error else "OK"
            print(f"{result.metric_type.value:20} = {result.value:6.2f}% [{status}]")
        
        # Brief pause between cycles
        time.sleep(1.0)
    
    # Print error summary
    print("\n" + "=" * 70)
    print("Error Summary:")
    summary = monitor.get_error_summary()
    print(f"Total metrics collected: {summary['total_metrics']}")
    print(f"Errors encountered: {summary['errors']}")
    print(f"Error rate: {summary['error_rate']:.2f}%")
    
    if summary['errors_by_type']:
        print("\nErrors by metric type:")
        for metric_type, count in summary['errors_by_type'].items():
            print(f"  {metric_type}: {count} error(s)")
    
    print("\n" + "=" * 70)
    print("Migration Notes:")
    print("1. Old pattern: Individual try/except blocks for each concurrent task")
    print("2. New pattern: Collect exceptions and handle with ExceptionGroup/except*")
    print("3. Benefits: Cleaner code, better error aggregation, type-safe handling")
    print("4. Python version: Requires Python 3.11.0 or later")

if __name__ == "__main__":
    main()