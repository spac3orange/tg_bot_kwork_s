from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import logger
from database import _tasks
import datetime


class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.enabled = False

    async def start(self):
        self.scheduler.start()
        self.enabled = True
        logger.info('Scheduler started')
        try:
            # Получить все задачи из базы данных
            tasks = await _tasks.db_get_all_scheduled_tasks()
            # Добавить задачи в планировщик
            print(tasks)
            for task in tasks:
                date_str = task['date']
                accounts = task['accounts']
                user_message = task['message']
                scheduler_object = task['scheduler_object']
                timing = task['timing']

                # Преобразовать строку даты в объект datetime
                date_time = datetime.datetime.strptime(date_str, "%d/%m/%Y %H:%M")
                # Создать триггер на основе даты
                trigger = DateTrigger(run_date=date_time)

                # Добавить задачу в планировщик
                job = self.scheduler.add_job(scheduler_object.func, trigger=trigger, id=scheduler_object.id, args=(accounts, user_message, timing, scheduler_object.id))
                logger.info(f'Task {scheduler_object.id} added to the scheduler for {date_str}')

        except Exception as e:
            logger.error(f'Error loading scheduled tasks from the database: {e}')

    async def add_task(self, task_id: str, task_func, date_str: str, accounts: str, user_message: str, timing: int):
        if not self.enabled:
            logger.warning('Scheduler is not started. Task cannot be added.')
            return

        try:
            date_time = datetime.datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        except ValueError:
            logger.error('Invalid date format. Task cannot be added.')
            return

        trigger = DateTrigger(run_date=date_time)
        job = self.scheduler.add_job(task_func, trigger=trigger, id=task_id, args=(accounts, user_message, timing, task_id))
        logger.info(f'Task {task_id} added to the scheduler for {date_str}')
        return job

    async def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.scheduler.remove_all_jobs()
            self.enabled = False
            logger.info('Scheduler stopped and all jobs cleared')
        else:
            logger.warning('Scheduler is not running')

    async def get_status(self):
        return self.enabled

    async def toggle_status(self, status: bool):
        if self.enabled:
            if status:
                pass
            else:
                await self.stop()
        else:
            if status:
                await self.start()
                self.enabled = status
            else:
                pass
        logger.warning(f'Bot status toggled to {status}')

    async def get_scheduled_tasks(self):
        scheduled_tasks = []

        if self.enabled:
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                task_info = {
                    'id': job.id,
                    'next_run_time': job.next_run_time,
                    'func': job.func.__name__,
                    'args': job.args
                }
                scheduled_tasks.append(task_info)

        return scheduled_tasks

    async def remove_task(self, task_id: str) -> None:
        """
        Removes a task from the scheduler based on task_id.
        """
        if self.enabled:
            try:
                self.scheduler.remove_job(task_id)
                logger.info(f'Task {task_id} removed from the scheduler')
            except Exception as e:
                logger.error(f'Error removing task {task_id} from the scheduler: {e}')
        else:
            logger.warning('Scheduler is not started. Cannot remove task.')


main_scheduler = Scheduler()


