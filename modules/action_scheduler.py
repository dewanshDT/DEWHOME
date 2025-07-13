import time
import threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from modules import db_operations, gpio_control


class ActionScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler(daemon=True)
        self.scheduler.add_listener(
            self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )
        self.running = False

    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.scheduler.start()
            self.running = True
            self._load_actions()
            print("Action scheduler started")

    def stop(self):
        """Stop the scheduler"""
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            print("Action scheduler stopped")

    def _load_actions(self):
        """Load all enabled actions from database and schedule them"""
        try:
            actions = db_operations.get_enabled_actions()

            for action in actions:
                self._schedule_action(action)

        except Exception as e:
            print(f"Error loading actions: {e}")

    def _schedule_action(self, action):
        """Schedule a single action"""
        try:
            action_id = action["id"]
            action_type = action["type"]
            schedule = action["schedule"]

            # Remove existing job if it exists
            try:
                self.scheduler.remove_job(f"action_{action_id}")
            except:
                pass  # Job doesn't exist, that's fine

            # Schedule based on action type
            if action_type == "timer":
                self._schedule_timer_action(action_id, schedule)
            elif action_type == "countdown":
                self._schedule_countdown_action(action_id, schedule)
            elif action_type == "interval":
                self._schedule_interval_action(action_id, schedule)
            else:
                print(f"Unsupported action type: {action_type}")

        except Exception as e:
            print(f"Error scheduling action {action['id']}: {e}")

    def _schedule_timer_action(self, action_id, schedule):
        """Schedule a cron-based timer action"""
        try:
            # Parse cron schedule: "minute hour day month day_of_week"
            # Example: "30 7 * * 1-5" = 7:30 AM Monday to Friday
            parts = schedule.split()
            if len(parts) != 5:
                raise ValueError("Invalid cron schedule format")

            minute, hour, day, month, day_of_week = parts

            trigger = CronTrigger(
                minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week
            )

            self.scheduler.add_job(
                func=self._execute_action,
                trigger=trigger,
                args=[action_id],
                id=f"action_{action_id}",
                name=f"Action {action_id}",
                misfire_grace_time=30,
            )

            print(f"Scheduled timer action {action_id} with cron: {schedule}")

        except Exception as e:
            print(f"Error scheduling timer action {action_id}: {e}")

    def _schedule_countdown_action(self, action_id, schedule):
        """Schedule a one-time countdown action"""
        try:
            # Parse countdown schedule: "30m", "2h", "1d"
            if schedule.endswith("m"):
                minutes = int(schedule[:-1])
                run_date = datetime.now().replace(second=0, microsecond=0)
                run_date = run_date.replace(minute=run_date.minute + minutes)
            elif schedule.endswith("h"):
                hours = int(schedule[:-1])
                run_date = datetime.now().replace(second=0, microsecond=0)
                run_date = run_date.replace(hour=run_date.hour + hours)
            elif schedule.endswith("d"):
                days = int(schedule[:-1])
                run_date = datetime.now().replace(second=0, microsecond=0)
                run_date = run_date.replace(day=run_date.day + days)
            else:
                raise ValueError("Invalid countdown format")

            trigger = DateTrigger(run_date=run_date)

            self.scheduler.add_job(
                func=self._execute_action,
                trigger=trigger,
                args=[action_id],
                id=f"action_{action_id}",
                name=f"Action {action_id}",
                misfire_grace_time=30,
            )

            print(f"Scheduled countdown action {action_id} for {run_date}")

        except Exception as e:
            print(f"Error scheduling countdown action {action_id}: {e}")

    def _schedule_interval_action(self, action_id, schedule):
        """Schedule a recurring interval action"""
        try:
            # Parse interval schedule: "30s", "5m", "1h"
            if schedule.endswith("s"):
                seconds = int(schedule[:-1])
                trigger = IntervalTrigger(seconds=seconds)
            elif schedule.endswith("m"):
                minutes = int(schedule[:-1])
                trigger = IntervalTrigger(minutes=minutes)
            elif schedule.endswith("h"):
                hours = int(schedule[:-1])
                trigger = IntervalTrigger(hours=hours)
            else:
                raise ValueError("Invalid interval format")

            self.scheduler.add_job(
                func=self._execute_action,
                trigger=trigger,
                args=[action_id],
                id=f"action_{action_id}",
                name=f"Action {action_id}",
                misfire_grace_time=30,
            )

            print(f"Scheduled interval action {action_id} with interval: {schedule}")

        except Exception as e:
            print(f"Error scheduling interval action {action_id}: {e}")

    def _execute_action(self, action_id):
        """Execute an action"""
        try:
            print(f"Executing action {action_id}")

            # Get action details
            action = db_operations.get_action_by_id(action_id)
            if not action:
                print(f"Action {action_id} not found")
                return

            if not action["enabled"]:
                print(f"Action {action_id} is disabled")
                return

            # Execute devices in sequence with delays
            for device_action in action["devices"]:
                device_id = device_action["device_id"]
                action_type = device_action["action_type"]
                delay_seconds = device_action["delay_seconds"]

                # Apply delay if specified
                if delay_seconds > 0:
                    time.sleep(delay_seconds)

                # Execute device action
                try:
                    if action_type == "toggle":
                        # Get current state and toggle
                        devices = db_operations.get_all_devices()
                        current_device = next(
                            (d for d in devices if d["id"] == device_id), None
                        )
                        if current_device:
                            new_state = (
                                "low" if current_device["state"] == "high" else "high"
                            )
                            gpio_control.control_device(device_id, new_state)
                            db_operations.update_device_state(device_id, new_state)
                    elif action_type in ["high", "low"]:
                        # Set specific state
                        gpio_control.control_device(device_id, action_type)
                        db_operations.update_device_state(device_id, action_type)
                    else:
                        print(f"Unknown action type: {action_type}")

                except Exception as e:
                    print(f"Error executing device action for device {device_id}: {e}")

            # Log successful execution
            db_operations.log_action_execution(
                action_id, "success", "Action executed successfully"
            )
            print(f"Action {action_id} executed successfully")

        except Exception as e:
            error_msg = f"Error executing action {action_id}: {str(e)}"
            print(error_msg)
            db_operations.log_action_execution(action_id, "error", error_msg)

    def _job_listener(self, event):
        """Listen for job execution events"""
        if event.exception:
            print(f"Job {event.job_id} crashed: {event.exception}")
        else:
            print(f"Job {event.job_id} executed successfully")

    def add_action(self, action):
        """Add and schedule a new action"""
        try:
            self._schedule_action(action)
        except Exception as e:
            print(f"Error adding action: {e}")

    def remove_action(self, action_id):
        """Remove an action from scheduler"""
        try:
            self.scheduler.remove_job(f"action_{action_id}")
            print(f"Removed action {action_id} from scheduler")
        except Exception as e:
            print(f"Error removing action {action_id}: {e}")

    def update_action(self, action):
        """Update an existing action"""
        try:
            # Remove old job and add new one
            self.remove_action(action["id"])
            self._schedule_action(action)
        except Exception as e:
            print(f"Error updating action: {e}")

    def get_jobs(self):
        """Get all scheduled jobs"""
        return self.scheduler.get_jobs()

    def execute_action_now(self, action_id):
        """Execute an action immediately"""
        try:
            self._execute_action(action_id)
        except Exception as e:
            print(f"Error executing action immediately: {e}")


# Global scheduler instance
scheduler = ActionScheduler()


def start_scheduler():
    """Start the global scheduler"""
    scheduler.start()


def stop_scheduler():
    """Stop the global scheduler"""
    scheduler.stop()


def get_scheduler():
    """Get the global scheduler instance"""
    return scheduler
