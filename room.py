import json
import tkinter as tk
from tkinter import scrolledtext

class GameOutput:
    """Класс для дублирования вывода в консоль и окно Tkinter"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Лесной Лабиринт")
        self.root.geometry("600x400")
        
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')
        self.text_area.configure(state='disabled')
        
    def print(self, text):
        """Вывод текста и в консоль, и в окно"""
        print(text)
        
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.configure(state='disabled')
        self.text_area.see(tk.END)
        self.root.update()

# Создаем глобальный объект для вывода
output = GameOutput()

class Player:
    """Класс игрока с показателями здоровья"""
    def __init__(self):
        self.max_health = 100
        self.health = 100
        self.is_alive = True
    
    def take_damage(self, amount):
        """Уменьшение здоровья персонажа"""
        if not self.is_alive:
            return
            
        self.health = max(0, self.health - amount)
        output.print(f"Вы получили {amount} урона! Здоровье: {self.health}/{self.max_health}")
        
        if self.health <= 0:
            self.die()
    
    def heal(self, amount):
        """Восстановление здоровья"""
        if not self.is_alive:
            return
            
        self.health = min(self.max_health, self.health + amount)
        output.print(f"Вы восстановили {amount} здоровья. Теперь у вас {self.health}/{self.max_health}")
    
    def die(self):
        """Обработка смерти персонажа"""
        self.is_alive = False
        output.print("\n=== ВЫ ПОГИБЛИ! ===")
        output.print("Игра завершена. Нажмите 0 для выхода.")
    
    def get_health_status(self):
        """Возвращает текстовое описание состояния здоровья"""
        if not self.is_alive:
            return "Мёртв"
        
        ratio = self.health / self.max_health
        if ratio > 0.8:
            return "Отличное состояние"
        elif ratio > 0.5:
            return "Лёгкие ранения"
        elif ratio > 0.2:
            return "Тяжело ранен"
        else:
            return "При смерти"

# Создаем глобальный объект игрока
player = Player()

class Room: # Класс с комнатами
    all = {} # Словарь для хранения комнат
    ENTRY = 1 # Константа с первой комнатой
    LEFT = 2
    RIGHT = 3
    RIGHT_EMPTY = 4  # Новая комната - пустая перед комнатой с сундуком

    @staticmethod # Создание функции которую можно вызвать напрямую из класса, без использования объекта
    def get(room_code):
        return Room.all[room_code]
    
    def __init__(self, description="??? нет описания ???", actions=[]):
        self.description = description
        self.actions = actions

    def enter(self):
        # Показываем состояние здоровья при входе в комнату
        health_status = player.get_health_status()
        output.print(f"[Состояние: {health_status}, Здоровье: {player.health}/{player.max_health}]")
        output.print(f">> {self.description}\n")
        output.print("Возможные действия:")
        for id, action in enumerate(self.actions):
            output.print(f"{id+1} {action.description}")
            
        while True:
            command = input("Ваше действие (0 - выход, s - сохранить, o - загрузить):")
            if command == 's':
                save_game()
                output.print("Игра сохранена!")
                continue
            elif command == 'o':
                load_game()
                output.print("Игра загружена!")
                return -1 # Специальный код для перезагрузки комнаты
            elif command.isnumeric():
                command = int(command)
                if command == 0:
                    output.print("\n")
                    return 0
                elif 0 < command <= len(self.actions):
                    # Случайный урон при выборе действия (для демонстрации)
                    if player.is_alive and current_room != Room.ENTRY and command != len(self.actions):
                        player.take_damage(5)
                    output.print("\n")
                    return self.actions[command-1].param

class Action:
    RIGHT_CHEST_OPEN = 1000
    LEFT_GIVE_ITEM = 1001

    def __init__(self, description, param, result=''):
        self.description = description
        self.param = param
        self.result = result

class EntryRoom(Room):
    def __init__(self):
        super().__init__('''Вход в лабиринт.
   Лестница вниз, от которой есть двери направо и налево''',
       [ Action("Пойти направо", Room.RIGHT_EMPTY),  # Теперь ведет сначала в пустую комнату
         Action("Пойти налево", Room.LEFT), ])

class RightEmptyRoom(Room):
    """Новая пустая комната перед комнатой с сундуком"""
    def __init__(self):
        super().__init__('''Пустая каменная комната с высокой потолком.
   В дальнем углу видна еще одна дверь.''',
       [ Action("Пойти дальше направо", Room.RIGHT),
         Action("Вернуться", Room.ENTRY), ])

class RightRoom(Room):
    def __init__(self):
        super().__init__('''Комната с закрытым сундуком''',
       [ Action("Открыть сундук", Action.RIGHT_CHEST_OPEN),
         Action("Вернуться", Room.RIGHT_EMPTY), ])  # Теперь возврат в пустую комнату

    def open_chest(self):
        output.print('''  Вы открыли сундук.
  В сундуке - ветвистая деревянная трость. Вы взяли ветвистую трость''')
        # Восстановление здоровья при нахождении предмета
        player.heal(30)
        self.description = '''Комната с открытым пустым сундуком'''
        self.actions.pop(0)

class LeftRoom(Room):
    def __init__(self):
        super().__init__('''В комнате сидит старый леший
   Леший: "Прииивееет...... Тыы хтоооо? Виииделлл мооою троооость?"''',
       [ Action("Нет не видел", Room.LEFT),
         Action("Вернуться", Room.ENTRY), ])

    def got_item(self):
        self.description = '''Старый леший с радостью смотрит на ветвистая деревянная трость
  Ооооооо.... Моооая трооость вернууууулась! Дааай!!!'''
        self.actions = [
            Action("Отдать трость", Action.LEFT_GIVE_ITEM),
            Action("Вернуться", Room.ENTRY),
        ]
    
    def give_item(self):
        output.print("  Радостный леший опираясь на свою трость, вприпрыжку ускакал в чащу леса")
        # Полное исцеление после помощи лешему
        player.heal(player.max_health)
        self.description = '''Тихая пустынная комната'''
        self.actions = [
            Action("Вернуться", Room.ENTRY),
        ]

def save_game():
    game_state = {
        'current_room': current_room,
        'right_empty_room': {
            'description': Room.get(Room.RIGHT_EMPTY).description,
            'actions': [a.description for a in Room.get(Room.RIGHT_EMPTY).actions]
        },
        'right_room': {
            'description': Room.get(Room.RIGHT).description,
            'actions': [a.description for a in Room.get(Room.RIGHT).actions]
        },
        'left_room': {
            'description': Room.get(Room.LEFT).description,
            'actions': [a.description for a in Room.get(Room.LEFT).actions]
        },
        'player': {
            'health': player.health,
            'max_health': player.max_health,
            'is_alive': player.is_alive
        }
    }
    with open('save.json', 'w', encoding='utf-8') as f:
        json.dump(game_state, f, ensure_ascii=False, indent=2)

def load_game():
    global current_room
    try:
        with open('save.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        current_room = data['current_room']
        
        # Восстанавливаем состояние игрока
        player.health = data['player']['health']
        player.max_health = data['player']['max_health']
        player.is_alive = data['player']['is_alive']
        
        # Восстанавливаем состояние пустой правой комнаты
        right_empty = Room.get(Room.RIGHT_EMPTY)
        right_empty.description = data['right_empty_room']['description']
        
        # Восстанавливаем состояние правой комнаты с сундуком
        right = Room.get(Room.RIGHT)
        right.description = data['right_room']['description']
        if 'Открыть сундук' not in data['right_room']['actions']:
            if hasattr(right, 'actions') and right.actions:
                right.actions.pop(0)
        
        # Восстанавливаем состояние левой комнаты
        left = Room.get(Room.LEFT)
        left.description = data['left_room']['description']
        if 'Отдать трость' in data['left_room']['actions']:
            left.actions = [
                Action("Отдать трость", Action.LEFT_GIVE_ITEM),
                Action("Вернуться", Room.ENTRY),
            ]
        elif 'Нет не видел' not in data['left_room']['actions']:
            left.actions = [
                Action("Вернуться", Room.ENTRY),
            ]
    except FileNotFoundError:
        output.print("Сохранение не найдено")

if __name__ == "__main__":
    Room.all = {
        Room.ENTRY: EntryRoom(),
        Room.LEFT: LeftRoom(),
        Room.RIGHT: RightRoom(),
        Room.RIGHT_EMPTY: RightEmptyRoom(),  # Добавляем новую комнату
    }
    current_room = Room.ENTRY
    
    try:
        while current_room and player.is_alive: # Добавили проверку на живой ли игрок
            action_id = Room.get(current_room).enter()
            if action_id == -1: # Перезагрузка комнаты после загрузки
                continue
            elif action_id == Action.RIGHT_CHEST_OPEN:
                Room.get(Room.RIGHT).open_chest()
                Room.get(Room.LEFT).got_item()
            elif action_id == Action.LEFT_GIVE_ITEM:
                Room.get(Room.LEFT).give_item()
            else:
                current_room = action_id
        
        # Если игрок умер, ждем завершения программы
        while not player.is_alive:
            output.root.update()
            
    except KeyboardInterrupt:
        output.root.destroy()