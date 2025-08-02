#!/usr/bin/env python3
"""
StepFlow Monitor - Stop on Error Example

This example demonstrates how to use the stop_on_error parameter
to control execution flow when steps fail.

Syntax: STEP_START:step_name[stop_on_error=true|false]
"""

import sys
import time
import random

def main():
    """Demo script showing stop_on_error functionality"""
    
    print("=== StepFlow Monitor - Stop on Error Demo ===")
    
    # Step 1: Environment setup (critical)
    print("STEP_START:environment_setup[stop_on_error=true]")
    print("Setting up environment...")
    time.sleep(1)
    
    # Simulate random failure for demo
    if len(sys.argv) > 1 and sys.argv[1] == "fail_critical":
        print("STEP_ERROR:Environment setup failed - missing dependencies")
        sys.exit(1)  # This will stop execution due to stop_on_error=true
    
    print("Environment setup completed successfully")
    print("STEP_COMPLETE:environment_setup")
    
    # Step 2: Database connection (critical)
    print("STEP_START:database_connection[stop_on_error=true]")
    print("Connecting to database...")
    time.sleep(1)
    print("Database connection established")
    print("STEP_COMPLETE:database_connection")
    
    # Step 3: Cache warming (optional)
    print("STEP_START:cache_warming[stop_on_error=false]")
    print("Warming up cache...")
    time.sleep(1)
    
    # Simulate optional failure
    if len(sys.argv) > 1 and sys.argv[1] == "fail_optional":
        print("STEP_ERROR:Cache warming failed - cache server unavailable")
        # Continue execution despite failure
    else:
        print("Cache warmed successfully")
        print("STEP_COMPLETE:cache_warming")
    
    # Step 4: Email notification (optional)
    print("STEP_START:email_notification[stop_on_error=false]")
    print("Sending notification email...")
    time.sleep(1)
    
    # Simulate another optional failure
    if random.choice([True, False]):
        print("STEP_ERROR:Email notification failed - SMTP server timeout")
    else:
        print("Notification email sent successfully")
        print("STEP_COMPLETE:email_notification")
    
    # Step 5: Final validation (critical)
    print("STEP_START:final_validation[stop_on_error=true]")
    print("Running final validation...")
    time.sleep(1)
    print("All validations passed")
    print("STEP_COMPLETE:final_validation")
    
    print("=== Demo completed successfully! ===")

if __name__ == "__main__":
    main()