from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    main_menu = State()
    search = State()
    advert = State()
