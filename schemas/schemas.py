def individual_data(task):
    return {
        "id": str(task.get("_id")),
        "title": task.get("title", "No Title"),
        "email": task.get("email", "No Email"),
        "description": task.get("description", ""),
        "status": task.get("status", "Unknown")
    }


def all_task(tasks):
    return [individual_data(task) for task in tasks]
