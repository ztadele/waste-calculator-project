from drafter import *
from dataclasses import dataclass
from bakery import assert_equal



@dataclass
class Waste:
    """Store information about one waste entry."""
    area: str
    waste_type: str
    waste_amount: int


@dataclass
class WasteCategory:
    """Store information about a waste category and its disposal method."""
    waste_category_name: str
    is_recyclable: bool
    disposable_method: str


@dataclass
class State:
    """Store the information used throughout the waste calculator."""
    area: str
    waste_list: list[Waste]
    waste_type: str
    waste_amount: int
    total_waste: int
    grade: str
    waste_categories: list[WasteCategory]


def create_initial_state():
    """Create the initial state with empty waste information."""
    return State("", [], "", 0, 0, "", [
        WasteCategory("Plastic", True, "Place in the recycling bin."),
        WasteCategory("Paper", True, "Place in the recycling bin."),
        WasteCategory("Glass", True, "Place in the recycling bin."),
        WasteCategory("Metal", True, "Place in the recycling bin."),
        WasteCategory("Other", False, "Dispose of according to local guidelines.")
    ])


def can_recycle(waste_type: str) -> bool:
    """Check whether a waste type is recyclable.

    Args:
        waste_type: The name of the waste category.

    Returns:
        True if the waste can be recycled, otherwise False.
    """
    waste_type = waste_type.lower()
    if waste_type == "plastic":
        return True
    elif waste_type == "glass":
        return True
    elif waste_type == "metal":
        return True
    elif waste_type == "paper":
        return True
    else:
        return False


def waste_present(waste_amount: int) -> str:
    """Describe the amount of waste recorded.

    Args:
        waste_amount: The total amount of waste in pounds.

    Returns:
        A message describing the waste amount.
    """
    if waste_amount == 0:
        return "No waste found, try again!"
    elif waste_amount > 50:
        return "high waste amount (greater than 50 lbs)"
    else:
        return "low waste count (less than 50 lbs)"


def save_waste_entry(state: State) -> State:
    """Add a new waste entry and update the total waste.

    Args:
        state: The current calculator state.

    Returns:
        The updated calculator state.
    """
    new_waste = Waste(
        state.area,
        state.waste_type,
        state.waste_amount
    )
    state.waste_list.append(new_waste)
    state.total_waste = 0
    for item in state.waste_list:
        state.total_waste += item.waste_amount
    return state


@route
def index(state: State) -> Page:
    """Display the welcome page and link to the input page."""
    return Page(state, [
        Header("Welcome to the Waste Calculator!"),
        Text("Hi! This is the home page for our waste calculator website."),
        Text("Enter your waste information."),
        Button("Go to Inputs Page", "add_waste")
    ])


@route
def add_waste(state: State) -> Page:
    """Display the input boxes for the user's area and waste amount."""
    return Page(state, [
        Header("Add Waste Page"),
        Text("Enter your waste information:"),
        Text("Enter Area:"),
        TextBox("area", state.area),
        Text("Enter Waste Amount (lbs):"),
        TextBox("waste_amount", state.waste_amount, "number"),
        Button("Submit Waste", "waste_categories"),
        Button("Back to Start", "index")
    ])


@route
def waste_categories(state: State, area: str, waste_amount: int) -> Page:
    """Save the user's information and display available waste categories.

    Args:
        area: The area where the waste was produced.
        waste_amount: The amount of waste in pounds.
    """
    state.area = area
    state.waste_amount = waste_amount

    category_text = []
    for category in state.waste_categories:
        category_text.append(
            Text(category.waste_category_name + ": " + category.disposable_method)
        )

    return Page(state, [
        Header("Waste Categories Page"),
        Text("Please select your waste type:"),
        *category_text,
        SelectBox("waste_type", ["Plastic", "Paper", "Glass", "Metal", "Other"]),
        Button("Submit Waste", "view_waste"),
        Button("Back to Add Waste", "add_waste")
    ])


@route
def view_waste(state: State, waste_type: str) -> Page:
    """Save the selected waste type and display the total waste amount.

    Args:
        waste_type: The waste category selected by the user.
    """
    state.waste_type = waste_type

    if state.area.strip() == "" or state.waste_amount <= 0:
        return Page(state, [
            Header("Invalid Waste Information"),
            Text("Please enter a valid area and a waste amount greater than zero."),
            Button("Back to Add Waste", "add_waste")
        ])

    state = save_waste_entry(state)

    return Page(state, [
        Header("Your Total Waste"),
        Text("Here is your waste calculation:"),
        Text(str(state.total_waste)),
        Text("Amount of total waste recorded (in pounds)."),
        Button("View Waste Grade", "return_grade")
    ])


@route
def return_grade(state: State) -> Page:
    """Calculate and save a letter grade based on total waste."""
    if state.total_waste <= 10:
        state.grade = "A"
    elif state.total_waste <= 25:
        state.grade = "B"
    elif state.total_waste <= 50:
        state.grade = "C"
    else:
        state.grade = "D"

    return Page(state, [
        Header("Waste Grade Calculation"),
        Text("Your waste grade has been calculated!"),
        Text("Your grade: " + state.grade),
        Button("Continue to Grade", "view_grade")
    ])


@route
def view_grade(state: State) -> Page:
    """Display the user's waste grade and feedback."""
    if state.grade == "A":
        feedback = "Excellent! You have a low amount of waste."
    elif state.grade == "B":
        feedback = "Good job! Your waste amount is pretty low."
    elif state.grade == "C":
        feedback = "Your waste amount is moderate. Consider recycling more or take a look at the advice on the next page."
    else:
        feedback = "Your waste amount is high. Try reducing and recycling waste and take a look at the advice on the next page."

    return Page(state, [
        Header("Your Waste Grade"),
        Text("Your final waste grade is:"),
        Text(state.grade),
        Text(feedback),
        Button("View Waste Advice", "view_advice")
    ])


@route
def view_advice(state: State) -> Page:
    """Display waste reduction advice based on the user's grade."""
    if state.grade == "A":
        advice = "Keep up the great work! Continue recycling and reducing waste."
    elif state.grade == "B":
        advice = "Try reusing containers and recycling paper, plastic, and metal."
    elif state.grade == "C":
        advice = "Consider composting food scraps and reducing single-use plastics."
    else:
        advice = "Start separating recyclable materials and look for ways to reuse items online."

    return Page(state, [
        Header("Waste Reduction Advice"),
        Text("Here is your personalized waste advice:"),
        Text(advice),
        Text("Recyclable: " + str(can_recycle(state.waste_type))),
        Text(waste_present(state.total_waste)),
        Button("Restart Calculator", "restart_calc")
    ])


@route
def restart_calc(state: State) -> Page:
    """Reset the user's waste information and display a confirmation page."""
    state.area = ""
    state.waste_list = []
    state.waste_type = ""
    state.waste_amount = 0
    state.total_waste = 0
    state.grade = ""

    return Page(state, [
        Header("Calculator Restarted"),
        Text("Your calculator has been reset!"),
        Text("You can now enter new waste information."),
        Button("Return to Start", "index")
    ])


import unittest

from finalproject import (
    create_initial_state,
    can_recycle,
    waste_present,
    save_waste_entry,
    index,
    add_waste,
    waste_categories,
    view_waste,
    return_grade,
    view_grade,
    view_advice,
    restart_calc
)


class TestWasteCalculator(unittest.TestCase):

    def test_create_initial_state(self):
        """Test that the initial state contains the correct values."""
        state = create_initial_state()

        self.assertEqual(state.area, "")
        self.assertEqual(state.waste_list, [])
        self.assertEqual(state.waste_type, "")
        self.assertEqual(state.waste_amount, 0)
        self.assertEqual(state.total_waste, 0)
        self.assertEqual(state.grade, "")
        self.assertEqual(len(state.waste_categories), 5)

    def test_can_recycle(self):
        """Test whether each waste type is recyclable."""
        self.assertEqual(can_recycle("plastic"), True)
        self.assertEqual(can_recycle("paper"), True)
        self.assertEqual(can_recycle("glass"), True)
        self.assertEqual(can_recycle("metal"), True)
        self.assertEqual(can_recycle("other"), False)

    def test_waste_present(self):
        """Test the messages returned for different waste amounts."""
        self.assertEqual(waste_present(0), "No waste found, try again!")
        self.assertEqual(
            waste_present(60),
            "high waste amount (greater than 50 lbs)"
        )
        self.assertEqual(
            waste_present(20),
            "low waste count (less than 50 lbs)"
        )

    def test_save_waste_entry(self):
        """Test that waste entries are saved and totals are calculated."""
        state = create_initial_state()
        state.area = "Kitchen"
        state.waste_type = "Plastic"
        state.waste_amount = 10

        result = save_waste_entry(state)

        self.assertEqual(result.total_waste, 10)
        self.assertEqual(len(result.waste_list), 1)
        self.assertEqual(result.waste_list[0].area, "Kitchen")
        self.assertEqual(result.waste_list[0].waste_type, "Plastic")
        self.assertEqual(result.waste_list[0].waste_amount, 10)

        state.area = "Bedroom"
        state.waste_type = "Paper"
        state.waste_amount = 5

        result = save_waste_entry(state)

        self.assertEqual(result.total_waste, 15)
        self.assertEqual(len(result.waste_list), 2)

    def test_index(self):
        """Test that the home route returns the correct page state."""
        state = create_initial_state()
        page = index(state)

        self.assertEqual(page.state, state)

    def test_add_waste(self):
        """Test that the add waste route returns the correct page state."""
        state = create_initial_state()
        page = add_waste(state)

        self.assertEqual(page.state, state)

    def test_waste_categories(self):
        """Test that the category route saves the area and waste amount."""
        state = create_initial_state()
        page = waste_categories(state, "Kitchen", 15)

        self.assertEqual(state.area, "Kitchen")
        self.assertEqual(state.waste_amount, 15)
        self.assertEqual(page.state, state)

    def test_view_waste(self):
        """Test that the waste route saves the selected waste information."""
        state = create_initial_state()
        state.area = "Kitchen"
        state.waste_amount = 15

        page = view_waste(state, "Plastic")

        self.assertEqual(state.waste_type, "Plastic")
        self.assertEqual(state.total_waste, 15)
        self.assertEqual(len(state.waste_list), 1)
        self.assertEqual(page.state, state)

    def test_return_grade(self):
        """Test that each waste amount receives the correct letter grade."""
        state = create_initial_state()

        state.total_waste = 5
        page = return_grade(state)
        self.assertEqual(state.grade, "A")
        self.assertEqual(page.state, state)

        state.total_waste = 20
        return_grade(state)
        self.assertEqual(state.grade, "B")

        state.total_waste = 40
        return_grade(state)
        self.assertEqual(state.grade, "C")

        state.total_waste = 60
        return_grade(state)
        self.assertEqual(state.grade, "D")

    def test_view_grade(self):
        """Test that the grade route displays the saved grade."""
        state = create_initial_state()
        state.grade = "A"

        page = view_grade(state)

        self.assertEqual(state.grade, "A")
        self.assertEqual(page.state, state)

    def test_view_advice(self):
        """Test that the advice route uses the saved grade and waste amount."""
        state = create_initial_state()
        state.grade = "B"
        state.waste_type = "Plastic"
        state.total_waste = 20

        page = view_advice(state)

        self.assertEqual(state.grade, "B")
        self.assertEqual(state.total_waste, 20)
        self.assertEqual(page.state, state)

    def test_restart_calc(self):
        """Test that restarting resets the user's waste information."""
        state = create_initial_state()
        state.area = "Kitchen"
        state.waste_type = "Plastic"
        state.waste_amount = 20
        state.total_waste = 20
        state.grade = "B"

        page = restart_calc(state)

        self.assertEqual(state.area, "")
        self.assertEqual(state.waste_list, [])
        self.assertEqual(state.waste_type, "")
        self.assertEqual(state.waste_amount, 0)
        self.assertEqual(state.total_waste, 0)
        self.assertEqual(state.grade, "")
        self.assertEqual(page.state, state)


if __name__ == "__main__":
    unittest.main()


start_server(create_initial_state())

