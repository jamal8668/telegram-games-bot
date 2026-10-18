"""Game handlers: Tic-Tac-Toe, Guess Number, Rock-Paper-Scissors, Hangman, Quick Click."""

import random
import asyncio
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards import (
    main_menu_kb,
    tictactoe_kb,
    tictactoe_back_kb,
    rps_kb,
    rps_result_kb,
    hangman_kb,
    quick_click_kb,
    back_menu_kb,
)

router = Router()

# ─── In-memory game state (per user) ─────────────────────────────
# NOTE: For production, use Redis. This is fine for a single-instance free Render.
ttt_boards: dict[int, list] = {}       # user_id -> board
guess_numbers: dict[int, int] = {}     # user_id -> secret number
hangman_state: dict[int, dict] = {}    # user_id -> {word, guessed, tries}
quick_click_state: dict[int, dict] = {}  # user_id -> {start_time, clicked}

# Russian words for Hangman
HANGMAN_WORDS = [
    "ПРОГРАММА", "ТЕЛЕФОН", "КОМПЬЮТЕР", "ИНТЕРНЕТ", "РОБОТ",
    "Галактика", "ПАРУСНИК", "МАРШРУТ", "БРИЛЛИАНТ", "КРОКОДИЛ",
    "МЕТЕОРИТ", "ПИРАМИДА", "ВЕЛОСИПЕД", "АВСТРАЛИЯ", "ГЕЙЗЕР",
    "ДЕЛЬФИН", "ЖИРАФ", "ЗВЕЗДОПАД", "ИГЛУ", "КАЛЕЙДОСКОП",
]


# ═══════════════════════════════════════════════════════════════════
# MENU
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "menu")
async def cb_menu(cb: CallbackQuery):
    await cb.message.edit_text(
        "🎮 <b>Игровой Бот</b>\n\nВыбери игру:",
        reply_markup=main_menu_kb()
    )
    await cb.answer()


# ═══════════════════════════════════════════════════════════════════
# TIC-TAC-TOE (Крестики-нолики)
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "game:tictactoe")
async def start_tictactoe(cb: CallbackQuery):
    user_id = cb.from_user.id
    ttt_boards[user_id] = [""] * 9
    await cb.message.edit_text(
        "❌⭕ <b>Крестики-нолики</b>\n\n"
        "Ты играешь за ❌. Ходи!",
        reply_markup=tictactoe_kb(ttt_boards[user_id])
    )
    await cb.answer()


def check_winner(board: list, player: str) -> bool:
    lines = [
        (0,1,2),(3,4,5),(6,7,8),  # rows
        (0,3,6),(1,4,7),(2,5,8),  # cols
        (0,4,8),(2,4,6)           # diags
    ]
    return any(board[a] == board[b] == board[c] == player for a, b, c in lines)


def bot_move(board: list) -> int:
    """Simple AI: try to win, then block, then center, then random."""
    # Try to win
    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            if check_winner(board, "O"):
                board[i] = ""
                return i
            board[i] = ""
    # Block player
    for i in range(9):
        if board[i] == "":
            board[i] = "X"
            if check_winner(board, "X"):
                board[i] = ""
                return i
            board[i] = ""
    # Center
    if board[4] == "":
        return 4
    # Corners
    for i in [0, 2, 6, 8]:
        if board[i] == "":
            return i
    # Any
    empty = [i for i in range(9) if board[i] == ""]
    return random.choice(empty) if empty else -1


@router.callback_query(F.data.startswith("ttt:"))
async def tictactoe_move(cb: CallbackQuery):
    user_id = cb.from_user.id
    idx = int(cb.data.split(":")[1])
    board = ttt_boards.get(user_id)

    if board is None:
        await cb.answer("Сначала начни игру!", show_alert=True)
        return

    if board[idx] != "":
        await cb.answer("Клетка занята!", show_alert=True)
        return

    # Player move
    board[idx] = "X"

    if check_winner(board, "X"):
        await cb.message.edit_text(
            "🎉 <b>Ты победил!</b> Поздравляю!",
            reply_markup=tictactoe_kb(board, game_active=False)
        )
        await cb.answer()
        return

    if all(cell != "" for cell in board):
        await cb.message.edit_text(
            "🤝 <b>Ничья!</b> Попробуй ещё раз.",
            reply_markup=tictactoe_kb(board, game_active=False)
        )
        await cb.answer()
        return

    # Bot move
    bot_idx = bot_move(board)
    if bot_idx >= 0:
        board[bot_idx] = "O"

    if check_winner(board, "O"):
        await cb.message.edit_text(
            "😔 <b>Бот победил!</b> Попробуй ещё раз.",
            reply_markup=tictactoe_kb(board, game_active=False)
        )
        await cb.answer()
        return

    await cb.message.edit_text(
        "❌⭕ <b>Крестики-нолики</b>\n\nТвой ход (❌):",
        reply_markup=tictactoe_kb(board)
    )
    await cb.answer()


# ═══════════════════════════════════════════════════════════════════
# GUESS NUMBER (Угадай число)
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "game:guess_number")
async def start_guess_number(cb: CallbackQuery):
    user_id = cb.from_user.id
    guess_numbers[user_id] = random.randint(1, 100)
    await cb.message.edit_text(
        "🔢 <b>Угадай число</b>\n\n"
        "Я загадал число от 1 до 100.\n"
        "Напиши своё предположение сообщением:",
        reply_markup=back_menu_kb()
    )
    await cb.answer()


@router.message(F.text, F.func(lambda m: m.from_user.id in guess_numbers))
async def process_guess(message: Message):
    user_id = message.from_user.id
    try:
        guess = int(message.text.strip())
    except ValueError:
        await message.answer("⚠️ Введи целое число!")
        return

    secret = guess_numbers[user_id]

    if guess < secret:
        await message.answer("📈 Больше! Попробуй ещё раз:")
    elif guess > secret:
        await message.answer("📉 Меньше! Попробуй ещё раз:")
    else:
        await message.answer(
            f"🎉 <b>Поздравляю! Ты угадал!</b>\nЧисло было: {secret}",
            reply_markup=main_menu_kb()
        )
        del guess_numbers[user_id]


# ═══════════════════════════════════════════════════════════════════
# ROCK-PAPER-SCISSORS (Камень-Ножницы-Бумага)
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "game:rps")
async def start_rps(cb: CallbackQuery):
    await cb.message.edit_text(
        "✊🪨📄 <b>Камень, Ножницы, Бумага!</b>\n\nВыбери:",
        reply_markup=rps_kb()
    )
    await cb.answer()


@router.callback_query(F.data.startswith("rps:"))
async def play_rps(cb: CallbackQuery):
    choice = cb.data.split(":")[1]
    bot_choice = random.choice(["rock", "scissors", "paper"])

    emoji = {"rock": "🪨", "scissors": "✂️", "paper": "📄"}
    name = {"rock": "Камень", "scissors": "Ножницы", "paper": "Бумага"}

    # Determine winner
    wins = {"rock": "scissors", "scissors": "paper", "paper": "rock"}

    if choice == bot_choice:
        result = "🤝 <b>Ничья!</b>"
    elif wins[choice] == bot_choice:
        result = "🎉 <b>Ты выиграл!</b>"
    else:
        result = "😔 <b>Бот выиграл!</b>"

    await cb.message.edit_text(
        f"✊🪨📄 <b>Камень, Ножницы, Бумага!</b>\n\n"
        f"Ты: {emoji[choice]} {name[choice]}\n"
        f"Бот: {emoji[bot_choice]} {name[bot_choice]}\n\n"
        f"{result}",
        reply_markup=rps_result_kb()
    )
    await cb.answer()


# ═══════════════════════════════════════════════════════════════════
# HANGMAN (Виселица)
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "game:hangman")
async def start_hangman(cb: CallbackQuery):
    user_id = cb.from_user.id
    word = random.choice(HANGMAN_WORDS).upper()
    hangman_state[user_id] = {
        "word": word,
        "guessed": set(),
        "tries": 6,
    }
    await render_hangman(cb)
    await cb.answer()


def hangman_display(word: str, guessed: set) -> str:
    """Show word with underscores for unguessed letters."""
    display = ""
    for ch in word:
        if ch in guessed:
            display += f"{ch} "
        else:
            display += "_ "
    return display.strip()


async def render_hangman(cb: CallbackQuery):
    user_id = cb.from_user.id
    state = hangman_state[user_id]
    word = state["word"]
    guessed = state["guessed"]
    tries = state["tries"]

    gallows = ["😈", "😟", "😐", "🙂", "😃", "🤩", "🎉"]
    face = gallows[6 - tries] if tries >= 0 else "💀"

    text = (
        f"🔤 <b>Виселица</b>\n\n"
        f"{face} Осталось попыток: <b>{tries}</b>\n\n"
        f"Слово: <code>{hangman_display(word, guessed)}</code>\n\n"
        f"Угаданные: {', '.join(sorted(guessed)) if guessed else '—'}\n\n"
        f"Выбери букву:"
    )

    await cb.message.edit_text(text, reply_markup=hangman_kb(guessed=guessed, word=word))


@router.callback_query(F.data.startswith("hm:"))
async def hangman_guess(cb: CallbackQuery):
    user_id = cb.from_user.id
    letter = cb.data.split(":")[1]
    state = hangman_state.get(user_id)

    if state is None:
        await cb.answer("Сначала начни игру!", show_alert=True)
        return

    word = state["word"]
    guessed = state["guessed"]

    if letter in guessed:
        await cb.answer("Уже угадано!", show_alert=True)
        return

    guessed.add(letter)

    if letter not in word:
        state["tries"] -= 1

    # Check win
    if all(ch in guessed for ch in word if ch.isalpha()):
        await cb.message.edit_text(
            f"🎉 <b>Поздравляю! Ты угадал слово: {word}!</b>",
            reply_markup=main_menu_kb()
        )
        del hangman_state[user_id]
        await cb.answer()
        return

    # Check loss
    if state["tries"] <= 0:
        await cb.message.edit_text(
            f"💀 <b>Игра окончена!</b>\nСлово было: <b>{word}</b>",
            reply_markup=main_menu_kb()
        )
        del hangman_state[user_id]
        await cb.answer()
        return

    await render_hangman(cb)
    await cb.answer(f"{'✅ Верно!' if letter in word else '❌ Мимо!'}")


# ═══════════════════════════════════════════════════════════════════
# QUICK CLICK (Быстрый клик)
# ═══════════════════════════════════════════════════════════════════
@router.callback_query(F.data == "game:quick_click")
async def start_quick_click_menu(cb: CallbackQuery):
    await cb.message.edit_text(
        "⚡ <b>Быстрый клик!</b>\n\n"
        "Правила: нажми «Начать», подожди 5 секунд, "
        "а потом ЖМИ как можно быстрее!\n\n"
        "Узнаешь свой результат в миллисекундах.",
        reply_markup=quick_click_kb()
    )
    await cb.answer()


@router.callback_query(F.data == "qc:start")
async def qc_start(cb: CallbackQuery):
    user_id = cb.from_user.id
    delay = random.uniform(2, 6)  # random wait 2-6 seconds

    quick_click_state[user_id] = {
        "start_time": None,
        "waiting": True,
        "clicked": False,
    }

    await cb.message.edit_text(
        "⚡ <b>Быстрый клик!</b>\n\n⏳ Жди зелёную кнопку...",
        reply_markup=quick_click_kb(timer_started=True, can_click=False)
    )
    await cb.answer()

    # Wait for random delay
    await asyncio.sleep(delay)

    # Check if user already clicked too early
    state = quick_click_state.get(user_id)
    if state is None or state.get("clicked"):
        return

    state["start_time"] = datetime.now()
    state["waiting"] = False

    try:
        await cb.message.edit_text(
            "⚡ <b>БЫСТРО! ЖМИ СЕЙЧАС!</b> 👇",
            reply_markup=quick_click_kb(timer_started=True, can_click=True)
        )
    except Exception:
        pass  # message might have been edited by user


@router.callback_query(F.data == "qc:click")
async def qc_click(cb: CallbackQuery):
    user_id = cb.from_user.id
    state = quick_click_state.get(user_id)

    if state is None:
        await cb.answer("Сначала начни игру!", show_alert=True)
        return

    if state.get("waiting"):
        # Too early!
        state["clicked"] = True
        await cb.message.edit_text(
            "🚫 <b>Слишком рано!</b> Ты нажал до появления кнопки.\n\n"
            "Попробуй ещё раз:",
            reply_markup=quick_click_kb()
        )
        await cb.answer("Рано!", show_alert=True)
        del quick_click_state[user_id]
        return

    if state.get("start_time"):
        elapsed = (datetime.now() - state["start_time"]).total_seconds() * 1000
        state["clicked"] = True

        if elapsed < 200:
            rating = "🏆 Невероятно!"
        elif elapsed < 400:
            rating = "⚡ Отлично!"
        elif elapsed < 600:
            rating = "👍 Хорошо!"
        else:
            rating = "🐌 Можно быстрее!"

        await cb.message.edit_text(
            f"⚡ <b>Быстрый клик!</b>\n\n"
            f"Твоё время: <b>{elapsed:.0f} мс</b>\n"
            f"{rating}\n\n"
            f"Попробуй ещё раз?",
            reply_markup=quick_click_kb()
        )
        await cb.answer()
        del quick_click_state[user_id]
    else:
        await cb.answer("Жди кнопку!", show_alert=True)


@router.callback_query(F.data == "noop")
async def noop(cb: CallbackQuery):
    await cb.answer()
