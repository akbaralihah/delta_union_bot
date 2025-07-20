from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    main_menu = State()
    search_choice_menu = State()
    full_container = State()
    groupage_cargo = State()
    advert = State()
