
from dataclasses import dataclass
from drafter import *

set_website_title("Campus Study Planner")
set_site_information(
    author="Suhaib Ahmad",
    description="A website for organizing assignments and study goals.",
    sources="Drafter documentation and sources listed in the repository.",
    planning="Planning worksheets are in the repository.",
    links=["https://github.com/suhaib-lgtm/Cisc-108-deployment"]
)
hide_debug_information()
set_website_framed(False)


@dataclass
class Homework:
    number: int
    name: str
    course: str
    minutes: int
    done: bool


@dataclass
class State:
    homework: list[Homework]
    next_number: int
    selected_course: str
    goal: int
    message: str


@route
def index(state: State, name: str = "", course: str = "",
          minutes: str = "", class_choice: str = "",
          goal_minutes: str = "") -> Page:
    """Show the main page."""
    return Page(state, [
        Header("Campus Study Planner"),
        Paragraph("Keep track of your schoolwork."),
        Paragraph(state.message),
        Paragraph("Assignments: " + str(len(state.homework))),
        Button("Add Assignment", "add_task"),
        Button("My Assignments", "task_list"),
        Button("Choose Class", "class_page"),
        Button("Study Goal", "goal_page"),
        Button("Progress", "progress")
    ])


@route
def add_task(state: State) -> Page:
    """Show the form for adding homework."""
    return Page(state, [
        Header("Add Assignment"),
        Paragraph(state.message),
        Paragraph("Assignment name:"),
        TextBox("name"),
        Paragraph("Class:"),
        SelectBox("course", [
            "CISC108", "ENGL110", "EGGG101", "THEA241", "THEA242", "Other"
        ]),
        Paragraph("How many minutes will it take?"),
        TextBox("minutes", "30"),
        Button("Save Assignment", "save_task"),
        Button("Home", "index")
    ])


@route
def save_task(state: State, name: str, course: str,
              minutes: str) -> Page:
    """Add one assignment to the list."""
    if name.strip() == "":
        state.message = "Please type an assignment name."
        return add_task(state)

    if not minutes.isdigit():
        state.message = "Please enter a number of minutes."
        return add_task(state)

    if int(minutes) == 0:
        state.message = "Minutes must be more than zero."
        return add_task(state)

    hw = Homework(state.next_number, name.strip(), course,
                  int(minutes), False)

    state.homework.append(hw)
    state.next_number = state.next_number + 1
    state.message = "Assignment added!"

    return task_list(state)


@route
def task_list(state: State) -> Page:
    """Show all of the homework."""
    stuff = [
        Header("My Assignments"),
        Paragraph(state.message),
        Button("Add Assignment", "add_task"),
        Button("Home", "index")
    ]

    if len(state.homework) == 0:
        stuff.append(Paragraph("No assignments added yet."))

    for hw in state.homework:
        if hw.done:
            stuff.append(
                Paragraph(hw.name + " (" + hw.course + ") - Done")
            )
        else:
            stuff.append(
                Paragraph(hw.name + " (" + hw.course + ") - " +
                          str(hw.minutes) + " minutes")
            )
            stuff.append(
                Button("Mark Done: " + hw.name, "mark_done",
                       [Argument("number", hw.number)])
            )

    return Page(state, stuff)


@route
def mark_done(state: State, number: int) -> Page:
    """Mark the chosen assignment done."""
    for hw in state.homework:
        if hw.number == number:
            hw.done = True
            state.message = "Assignment marked done!"

    return task_list(state)


@route
def class_page(state: State) -> Page:
    """Show work from one class."""
    stuff = [
        Header("Choose Class"),
        Paragraph("Pick a class to see its assignments."),
        SelectBox("class_choice", [
            "All", "CISC108", "ENGL110", "EGGG101",
            "THEA241", "THEA242", "Other"
        ], state.selected_course),
        Button("Show Class", "choose_class"),
        Button("Home", "index"),
        Paragraph("Showing: " + state.selected_course)
    ]

    found = 0

    for hw in state.homework:
        if state.selected_course == "All" or hw.course == state.selected_course:
            found = found + 1

            if hw.done:
                stuff.append(Paragraph(hw.name + " - Done"))
            else:
                stuff.append(Paragraph(hw.name + " - Not done"))

    if found == 0:
        stuff.append(Paragraph("Nothing for this class yet."))

    return Page(state, stuff)


@route
def choose_class(state: State, class_choice: str) -> Page:
    """Remember which class was picked."""
    state.selected_course = class_choice
    state.message = "Class changed."

    return class_page(state)


@route
def goal_page(state: State) -> Page:
    """Show the daily study goal form."""
    return Page(state, [
        Header("Daily Study Goal"),
        Paragraph(state.message),
        Paragraph("Current goal: " + str(state.goal) + " minutes"),
        Paragraph("New goal in minutes:"),
        TextBox("goal_minutes", str(state.goal)),
        Button("Save Goal", "save_goal"),
        Button("Home", "index")
    ])


@route
def save_goal(state: State, goal_minutes: str) -> Page:
    """Change the daily goal."""
    if not goal_minutes.isdigit():
        state.message = "Type a number for your goal."
        return goal_page(state)

    if int(goal_minutes) == 0:
        state.message = "Your goal needs to be more than zero."
        return goal_page(state)

    state.goal = int(goal_minutes)
    state.message = "Goal saved!"

    return goal_page(state)


@route
def progress(state: State) -> Page:
    """Show how much homework is left."""
    finished = 0
    minutes_left = 0

    for hw in state.homework:
        if hw.done:
            finished = finished + 1
        else:
            minutes_left = minutes_left + hw.minutes

    stuff = [
        Header("Progress"),
        Paragraph("Total assignments: " + str(len(state.homework))),
        Paragraph("Finished: " + str(finished)),
        Paragraph("Estimated minutes left: " + str(minutes_left)),
        Paragraph("Daily goal: " + str(state.goal) + " minutes"),
        Button("View Assignments", "task_list"),
        Button("Change Goal", "goal_page"),
        Button("Home", "index")
    ]

    if len(state.homework) > 0 and finished == len(state.homework):
        stuff.append(Paragraph("All done!"))

    return Page(state, stuff)


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
              "Finish project", "CISC108", "45"),
    State([Homework(1, "Finish project", "CISC108", 45, False)],
          2, "All", 60, "Assignment added!")
)

assert_has(
    task_list(State([], 1, "All", 60, "")),
    Header("My Assignments")
)

assert_state(
    mark_done(
        State([Homework(1, "Quiz", "CISC108", 20, False),
               Homework(2, "Essay", "ENGL110", 50, False)],
              3, "All", 60, ""), 1),
    State([Homework(1, "Quiz", "CISC108", 20, True),
           Homework(2, "Essay", "ENGL110", 50, False)],
          3, "All", 60, "Assignment marked done!")
)

assert_has(
    class_page(State([], 1, "All", 60, "")),
    Header("Choose Class")
)

assert_state(
    choose_class(State([], 1, "All", 60, ""), "ENGL110"),
    State([], 1, "ENGL110", 60, "Class changed.")
)

assert_has(
    goal_page(State([], 1, "All", 60, "")),
    Header("Daily Study Goal")
)

assert_state(
    save_goal(State([], 1, "All", 60, ""), "90"),
    State([], 1, "All", 90, "Goal saved!")
)

assert_has(
    progress(State([], 1, "All", 60, "")),
    Header("Progress")
)


start_server(State([], 1, "All", 60, ""))
