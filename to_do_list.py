def load_tasks():
    try:
        with open('tasks.txt', 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open('tasks.txt', 'w') as file:
        for task in tasks:
            file.write(task + '\n')

def add_task(tasks, task):
    tasks.append(task)
    save_tasks(tasks)
    print(f"Task '{task}' added successfully.")

def remove_task(tasks, index):
    try:
        task = tasks.pop(index - 1)
        save_tasks(tasks)
        print(f"Task '{task}' removed successfully.")
    except IndexError:
        print("Invalid task number.")

def view_tasks(tasks):
    if not tasks:
        print("No tasks in the list.")
    else:
        print("\nYour To-Do List:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")

def main():
    tasks = load_tasks()
    while True:
        print("\nTo-Do List Manager")
        print("1. View tasks")
        print("2. Add task")
        print("3. Remove task")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            view_tasks(tasks)
        elif choice == '2':
            task = input("Enter task: ")
            if task.strip():
                add_task(tasks, task.strip())
            else:
                print("Task cannot be empty.")
        elif choice == '3':
            view_tasks(tasks)
            if tasks:
                try:
                    index = int(input("Enter task number to remove: "))
                    remove_task(tasks, index)
                except ValueError:
                    print("Please enter a valid number.")
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()