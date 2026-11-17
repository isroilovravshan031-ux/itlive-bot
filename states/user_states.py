from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    name = State()
    phone = State()
    age = State()
    region = State()
    course = State()
    time_preference = State()
    confirm = State()

class TrialLessonStates(StatesGroup):
    name = State()
    phone = State()
    course = State()
    confirm = State()

class FeedbackStates(StatesGroup):
    waiting_for_feedback = State()

class QuizStates(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()

class AdminCourseStates(StatesGroup):
    name = State()
    description = State()
    duration = State()
    price = State()
    technologies = State()

class AdminEditCourseStates(StatesGroup):
    select_field = State()
    new_value = State()

class AdminSalesStates(StatesGroup):
    enter_id = State()
    enter_name = State()
    enter_phone = State()

class AdminBroadcastStates(StatesGroup):
    waiting_for_message = State()
    confirm = State()

class AdminSettingStates(StatesGroup):
    waiting_for_value = State()

class SalesNoteStates(StatesGroup):
    lead_id = State()
    waiting_for_note = State()
