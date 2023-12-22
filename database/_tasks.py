from . import db
import asyncpg
from config import logger
import pickle
from typing import List


async def db_add_scheduled_task(date: str, accounts: str, message: str, scheduler_object, timing: int, task_id) -> None:
    """
    Adds a scheduled task to the database.
    """
    try:
        # Сериализовать объект в байты с помощью pickle
        serialized_object = pickle.dumps(scheduler_object)

        query = """
            INSERT INTO scheduled_tasks (date, accounts, message, scheduler_object, timing, task_id)
            VALUES ($1, $2, $3, $4, $5, $6)
        """
        await db.execute_query(query, date, accounts, message, serialized_object, timing, task_id)
        logger.info("Scheduled task added to the database")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error adding scheduled task to the database: {error}")



async def db_get_all_scheduled_tasks() -> List[dict]:
    """
    Retrieves all scheduled tasks from the database.
    Returns a list of dictionaries representing each task.
    """
    try:
        query = """
            SELECT date, accounts, message, scheduler_object, timing, task_id
            FROM scheduled_tasks
        """
        results = await db.fetch_all(query)

        scheduled_tasks = []
        for row in results:
            date = row['date']
            accounts = row['accounts']
            message = row['message']
            scheduler_object = pickle.loads(row['scheduler_object'])
            timing = row['timing']
            task_id = row['task_id']

            task = {
                'date': date,
                'accounts': accounts,
                'message': message,
                'scheduler_object': scheduler_object,
                'timing': timing,
                'task_id': task_id

            }
            scheduled_tasks.append(task)

        logger.info("Retrieved all scheduled tasks from the database")
        return scheduled_tasks
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error retrieving scheduled tasks from the database: {error}")
        return []

async def db_get_all_executed_tasks() -> List[dict]:
    """
    Retrieves all scheduled tasks from the database.
    Returns a list of dictionaries representing each task.
    """
    try:
        query = """
            SELECT date, accounts, message, scheduler_object, timing, task_id
            FROM executed_tasks
        """
        results = await db.fetch_all(query)

        scheduled_tasks = []
        for row in results:
            date = row['date']
            accounts = row['accounts']
            message = row['message']
            scheduler_object = pickle.loads(row['scheduler_object'])
            timing = row['timing']
            task_id = row['task_id']

            task = {
                'date': date,
                'accounts': accounts,
                'message': message,
                'scheduler_object': scheduler_object,
                'timing': timing,
                'task_id': task_id

            }
            scheduled_tasks.append(task)

        logger.info("Retrieved all scheduled tasks from the database")
        return scheduled_tasks
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error retrieving scheduled tasks from the database: {error}")
        return []


async def db_execute_scheduled_task(task_id: int) -> None:
    """
    Moves a scheduled task to the executed_tasks table and deletes it from scheduled_tasks table.
    """
    try:
        # Retrieve the scheduled task from the scheduled_tasks table using task_id
        query_select = """
            SELECT date, accounts, message, scheduler_object, timing, task_id
            FROM scheduled_tasks
            WHERE task_id = $1
        """
        task = await db.fetch_row(query_select, task_id)

        if task:
            # Serialize the scheduler_object
            scheduler_object = pickle.loads(task['scheduler_object'])

            # Insert the task into the executed_tasks table
            query_insert = """
                INSERT INTO executed_tasks (date, accounts, message, scheduler_object, timing, task_id)
                VALUES ($1, $2, $3, $4, $5, $6)
            """
            await db.execute_query(query_insert, task['date'], task['accounts'], task['message'], pickle.dumps(scheduler_object), task['timing'], task['task_id'])

            # Delete the task from the scheduled_tasks table
            query_delete = """
                DELETE FROM scheduled_tasks
                WHERE task_id = $1
            """
            await db.execute_query(query_delete, task_id)

            logger.info(f"Scheduled task with task_id {task_id} moved to executed_tasks and deleted from scheduled_tasks")
        else:
            logger.warning(f"No scheduled task found with task_id {task_id}")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error executing scheduled task: {error}")


async def delete_scheduled_task(task_id: int) -> None:
    """
    Deletes a task from the scheduled_tasks table based on task_id.
    """
    try:
        query = """
            DELETE FROM scheduled_tasks
            WHERE task_id = $1
        """
        await db.execute_query(query, task_id)
        logger.info(f"Scheduled task with task_id {task_id} deleted from scheduled_tasks")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error deleting scheduled task: {error}")
