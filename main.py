
from dataclasses import dataclass
from drafter import *

set_website_title("Campus Study Planner")
set_site_information(
    author="Suhaib Ahmad",
    description="A website for keeping track of assignments and study goals.",
    sources="Drafter documentation and ChatGPT",
    planning="See the project planning documents in the repository.",
    links=["https://github.com/suhaib-lgtm/Cisc-108-deployment"]
)
hide_debug_information()
set_website_framed(False)


@dataclass
class Task:
    number: int
    name: str
    course: str
    minutes: int
    completed: bool


@dataclass
class State:
    tasks: list[Task]
    next_task_number: int
    selected_course: str
    daily_goal_minutes: int
    message: str


@route
def index(state: State, task_name: str = "",
          course_name: str = "", minutes_text: str = "",
          course_choice: str = "", goal_text: str = "") -> Page:
    """Show the home page."""
    return Page(state, [
        Header("Campus Study Planner"),
        Paragraph("Welcome to your study planner!"),
        Paragraph("Add assignments, mark them done, and set study goals."),
        Paragraph(state.message),
        Paragraph("Total assignments: " + str(len(state.tasks))),
        Button("Add Assignment", "add_task"),
        Button("View Assignments", "task_list"),
        Button("Choose a Class", "focus"),
        Button("Daily Study Goal", "goal"),
        Button("Progress Summary", "summary")
    ])


@route
def add_task(state: State) -> Page:
    """Show the add assignment page."""
    return Page(state, [
        Header("Add Assignment"),
        Paragraph(state.message),
        Paragraph("Assignment Name"),
        TextBox("task_name"),
        Paragraph("Choose a Class"),
        SelectBox("course_name", [
            "CISC108",
            "ENGL110",
            "EGGG101",
            "THEA241",
            "THEA242",
            "Other"
        ]),
        Paragraph("Estimated Minutes"),
        TextBox("minutes_text", "30"),
        Button("Save Assignment", "save_task"),
        Button("Home", "index")
    ])


@route
def save_task(state: State, task_name: str,
              course_name: str, minutes_text: str) -> Page:
    """Save a new assignment."""
    if task_name.strip() == "":
        state.message = "Please enter an assignment name."
        return add_task(state)

    if not minutes_text.isdigit():
        state.message = "Please enter a valid number of minutes."
        return add_task(state)

    if int(minutes_text) <= 0:
        state.message = "Minutes must be greater than zero."
        return add_task(state)

    new_task = Task(
        state.next_task_number,
        task_name.strip(),
        course_name,
        int(minutes_text),
        False
    )

    state.tasks.append(new_task)
    state.next_task_number = state.next_task_number + 1
    state.message = "Assignment added successfully!"

    return task_list(state)


@route
def task_list(state: State) -> Page:
    """Show all assignments."""
    content = [
        Header("My Assignments"),
        Paragraph(state.message),
        Button("Add Assignment", "add_task"),
        Button("Home", "index")
    ]

    if len(state.tasks) == 0:
        content.append(Paragraph("You have no assignments yet."))

    for task in state.tasks:
        if task.completed:
            content.append(
                Paragraph(task.name + " - " + task.course + " - Done")
            )
        else:
            content.append(
                Paragraph(
                    task.name + " - " + task.course +
                    " - " + str(task.minutes) + " minutes"
                )
            )
            content.append(
                Button(
                    "Mark Done: " + task.name,
                    "mark_complete",
                    [Argument("task_number", task.number)]
                )
            )

    return Page(state, content)


@route
def mark_complete(state: State, task_number: int) -> Page:
    """Mark one assignment as completed."""
    for task in state.tasks:
        if task.number == task_number:
            if not task.completed:
                task.completed = True
                state.message = "Assignment completed!"

    return task_list(state)


@route
def focus(state: State) -> Page:
    """Show assignments from a selected class."""
    content = [
        Header("Choose a Class"),
        Paragraph("Select a class to see its assignments."),
        SelectBox("course_choice", [
            "All",
            "CISC108",
            "ENGL110",
            "EGGG101",
            "THEA241",
            "THEA242",
            "Other"
        ], state.selected_course),
        Button("Show Assignments", "set_course"),
        Button("Home", "index"),
        Paragraph("Showing assignments for: " + state.selected_course)
    ]

    count = 0

    for task in state.tasks:
        if state.selected_course == "All" or task.course == state.selected_course:
            count = count + 1

            if task.completed:
                content.append(
                    Paragraph(task.name + " - Done")
                )
            else:
                content.append(
                    Paragraph(
                        task.name + " - " + str(task.minutes) + " minutes"
                    )
                )

    if count == 0:
        content.append(Paragraph("No assignments found."))

    return Page(state, content)


@route
def set_course(state: State, course_choice: str) -> Page:
    """Save the selected class."""
    state.selected_course = course_choice
    state.message = "Class changed."

    return focus(state)


@route
def goal(state: State) -> Page:
    """Show the daily study goal page."""
    return Page(state, [
        Header("Daily Study Goal"),
        Paragraph(state.message),
        Paragraph(
            "Your current goal is " +
            str(state.daily_goal_minutes) + " minutes per day."
        ),
        Paragraph("Enter your new daily study goal in minutes."),
        TextBox("goal_text", str(state.daily_goal_minutes)),
        Button("Save Goal", "save_goal"),
        Button("Progress Summary", "summary"),
        Button("Home", "index")
    ])


@route
def save_goal(state: State, goal_text: str) -> Page:
    """Save the daily study goal."""
    if not goal_text.isdigit():
        state.message = "Please enter a valid number."
        return goal(state)

    if int(goal_text) <= 0:
        state.message = "Your goal must be greater than zero."
        return goal(state)

    state.daily_goal_minutes = int(goal_text)
    state.message = "Daily study goal saved!"

    return goal(state)


@route
def summary(state: State, goal_text: str = "") -> Page:
    """Show assignment progress."""
    completed = 0
    remaining_minutes = 0
    completed_minutes = 0

    for task in state.tasks:
        if task.completed:
            completed = completed + 1
            completed_minutes = completed_minutes + task.minutes
        else:
            remaining_minutes = remaining_minutes + task.minutes

    content = [
        Header("Progress Summary"),
        Paragraph("Total Assignments: " + str(len(state.tasks))),
        Paragraph("Completed Assignments: " + str(completed)),
        Paragraph("Estimated Minutes Left: " + str(remaining_minutes)),
        Paragraph(
            "Estimated Minutes of Completed Work: " +
            str(completed_minutes)
        ),
        Paragraph(
            "Daily Study Goal: " +
            str(state.daily_goal_minutes) + " minutes"
        ),
        Button("View Assignments", "task_list"),
        Button("Change Goal", "goal"),
        Button("Home", "index")
    ]

    if len(state.tasks) > 0:
        if completed == len(state.tasks):
            content.append(
                Paragraph("Great job! You finished all your assignments!")
            )

    return Page(state, content)


assert_has(
    index(State([], 1, "All", 60, "")),
    Header("Campus Study Planner")
)

assert_has(
    add_task(State([], 1, "All", 60, "")),
    Header("Add Assignment")
)

assert_state(
    save_task(State([], 1, "All", 60, ""),
              "Math Homework", "CISC108", "30"),
    State(
        [Task(1, "Math Homework", "CISC108", 30, False)],
        2, "All", 60, "Assignment added successfully!"
    )
)

assert_has(
    task_list(State([], 1, "All", 60, "")),
    Header("My Assignments")
)

assert_state(
    mark_complete(
        State([Task(1, "Homework", "CISC108", 30, False)],
              2, "All", 60, ""),
        1
    ),
    State(
        [Task(1, "Homework", "CISC108", 30, True)],
        2, "All", 60, "Assignment completed!"
    )
)

assert_has(
    focus(State([], 1, "All", 60, "")),
    Header("Choose a Class")
)

assert_state(
    set_course(State([], 1, "All", 60, ""), "CISC108"),
    State([], 1, "CISC108", 60, "Class changed.")
)

assert_has(
    goal(State([], 1, "All", 60, "")),
    Header("Daily Study Goal")
)

assert_state(
    save_goal(State([], 1, "All", 60, ""), "90"),
    State([], 1, "All", 90, "Daily study goal saved!")
)

assert_has(
    summary(State([], 1, "All", 60, "")),
    Header("Progress Summary")
)


start_server(State([], 1, "All", 60, ""))
