"""Inline keyboards for all games."""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def main_menu_kb() -> InlineKeyboardMarkup:
    """Main menu with game selection."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Крестики-нолики", callback_data="game:tictactoe"),
            InlineKeyboardButton(text="🔢 Угадай число", callback_data="game:guess_number"),
        ],
        [
            InlineKeyboardButton(text="✊ Камень-Ножницы-Бумага", callback_data="game:rps"),
            InlineKeyboardButton(text="🔤 Виселица", callback_data="game:hangman"),
        ],
        [
            InlineKeyboardButton(text="⚡ Быстрый клик", callback_data="game:quick_click"),
        ],
    ])


def tictactoe_kb(board: list, game_active: bool = True) -> InlineKeyboardMarkup:
    """3x3 Tic-Tac-Toe board."""
    rows = []
    for i in range(3):
        row = []
        for j in range(3):
            idx = i * 3 + j
            cell = board[idx]
            symbol = "⬜"
            if cell == "X":
                symbol = "❌"
            elif cell == "O":
                symbol = "⭕"
            if not game_active and cell == "":
                symbol = "▪️"
            row.append(InlineKeyboardButton(
                text=symbol,
                callback_data=f"ttt:{idx}" if game_active else "noop"
            ))
        rows.append(row)
    if not game_active:
        rows.append([InlineKeyboardButton(text="🔄 Играть снова", callback_data="game:tictactoe")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tictactoe_back_kb() -> InlineKeyboardMarkup:
    """Back to menu button."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ В меню", callback_data="menu")]
    ])


def rps_kb() -> InlineKeyboardMarkup:
    """Rock-Paper-Scissors choices."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🪨 Камень", callback_data="rps:rock"),
            InlineKeyboardButton(text="✂️ Ножницы", callback_data="rps:scissors"),
            InlineKeyboardButton(text="📄 Бумага", callback_data="rps:paper"),
        ],
        [InlineKeyboardButton(text="◀️ В меню", callback_data="menu")],
    ])


def rps_result_kb() -> InlineKeyboardMarkup:
    """Play again or go back."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ещё раз", callback_data="game:rps")],
        [InlineKeyboardButton(text="◀️ В меню", callback_data="menu")],
    ])


def hangman_kb(letters: str = "АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ", guessed: set = None, word: str = None) -> InlineKeyboardMarkup:
    """Hangman letter keyboard (Russian)."""
    rows = []
    current_row = []
    for ch in letters:
        is_used = (guessed and ch in guessed) or (word and ch in word and guessed and ch in guessed)
        btn_text = f"{'✅' if ch in (guessed or set()) else ch}"
        btn = InlineKeyboardButton(
            text=btn_text,
            callback_data=f"hm:{ch}" if (guessed is None or ch not in guessed) else "noop"
        )
        current_row.append(btn)
        if len(current_row) == 8:
            rows.append(current_row)
            current_row = []
    if current_row:
        rows.append(current_row)
    rows.append([InlineKeyboardButton(text="◀️ В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def quick_click_kb(timer_started: bool = False, can_click: bool = False) -> InlineKeyboardMarkup:
    """Quick click game keyboard."""
    rows = []
    if timer_started and can_click:
        rows.append([InlineKeyboardButton(text="👆 ЖМИ СЕЙЧАС!", callback_data="qc:click")])
    elif timer_started:
        rows.append([InlineKeyboardButton(text="⏳ Жди...", callback_data="noop")])
    else:
        rows.append([InlineKeyboardButton(text="🚀 Начать игру", callback_data="qc:start")])
    rows.append([InlineKeyboardButton(text="◀️ В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ В меню", callback_data="menu")]
    ])
