from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    main_menu = State()
    search_choice_menu = State()
    full_container = State()
    groupage_cargo_1 = State()
    groupage_cargo_2 = State()
    advert = State()
