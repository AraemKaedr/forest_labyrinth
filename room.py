import json
import tkinter as tk
from tkinter import scrolledtext
import random  # Добавим для боя с монстром

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
        self.has_sword = False  # Добавим флаг наличия меча для боя с монстром (меч увеличивает урон на +10)
    
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
    all = {} # Словарь для хранения всех комнат
    ENTRY = 1  # Константа для начальной комнаты
    LEFT = 2
    RIGHT = 3
    RIGHT_SIGN = 4  # Комната с предупреждающей табличкой
    MONSTER_ROOM = 5  # Комната с монстром
    RIGHT_CHEST = 6  # Комната с сундуком

    @staticmethod # Создание функции которую можно вызвать напрямую из класса, без использования объекта
    def get(room_code):
        """Получение комнаты по коду"""
        return Room.all[room_code]
    
    def __init__(self, description="??? нет описания ???", actions=[]):
        self.description = description
        self.actions = actions

    def enter(self):
        """Вход в комнату - основная логика взаимодействия"""
        # Показываем состояние здоровья при входе в комнату
        health_status = player.get_health_status()
        output.print(f"[Состояние: {health_status}, Здоровье: {player.health}/{player.max_health}]")
        output.print(f">> {self.description}\n")
        output.print("Возможные действия:")
        for id, action in enumerate(self.actions):
            output.print(f"{id+1} {action.description}")
        
        # Обработка ввода пользователя
        while True:
            command = input("Ваше действие (0 - выход, s - сохранить, o - загрузить): ").strip().lower()
            if command == 's':
                save_game()
                output.print("Игра сохранена!")
                continue
            elif command == 'o':
                load_game()
                output.print("Игра загружена!")
                return -1 # Специальный код для перезагрузки комнаты
            elif command.isdigit():
                command = int(command)
                if command == 0:
                    output.print("\n")
                    return 0
                elif 1 <= command <= len(self.actions):
                    output.print("\n")
                    return self.actions[command-1].param

class Action:
    RIGHT_CHEST_OPEN = 1000
    LEFT_GIVE_ITEM = 1001
    DEFEAT_MONSTER = 1002  # Новое действие - победа над монстром

    def __init__(self, description, param, result=''):
        self.description = description
        self.param = param
        self.result = result

class EntryRoom(Room):
    def __init__(self):
        super().__init__('''Вход в лабиринт.
   Лестница вниз, от которой есть двери направо и налево''',
       [ Action("Пойти направо", Room.RIGHT_SIGN),  # Теперь ведет в комнату с табличкой
         Action("Пойти налево", Room.LEFT), ])

class RightSignRoom(Room):
    """Комната с предупреждающей табличкой перед комнатой с монстром"""
    def __init__(self):
        super().__init__('''Каменная комната с высоким потолком. На стене висит старая табличка с надписью.
   В дальнем углу видна массивная дверь с железными скобами.

   Надпись на табличке гласит:
   "ОСТОРОЖНО! В следующей комнате обитает жуткий Упырь!
   Но смельчаков, что победят его, ждет невиданное сокровище!"''',
       [ Action("Пойти дальше вниз (рискнуть)", Room.MONSTER_ROOM),
         Action("Вернуться обратно (поступить по-умному)", Room.ENTRY), ])

class MonsterRoom(Room):
    """Комната с монстром Упырем"""
    def __init__(self):
        super().__init__('''Темная сырая комната с костями на полу. В центре стоит жуткий Упырь!
   Его красные глаза горят в темноте, а длинные когти скребут по камням.''',
       [ Action("Атаковать монстра", Room.MONSTER_ROOM),  # Будем обрабатывать отдельно
         Action("Попытаться убежать", Room.RIGHT_SIGN), ])  # Бегство возвращает в комнату с табличкой

    def enter(self):
        """Особая логика enter для комнаты с монстром и обработки боя"""
        health_status = player.get_health_status()
        output.print(f"[Состояние: {health_status}, Здоровье: {player.health}/{player.max_health}]")
        output.print(f">> {self.description}\n")
        
        # Проверяем, жив ли монстр (если нет - пропускаем бой)
        if hasattr(self, 'monster_defeated') and self.monster_defeated:
            output.print("Тело Упыря лежит на полу, издавая зловоние.")
            output.print("Возможные действия:")
            output.print("1 Пройти дальше в комнату с сокровищем")
            output.print("2 Вернуться")
            
            while True:
                command = input("Ваше действие (0 - выход, s - сохранить, o - загрузить):").strip().lower()
                if command == 's':
                    save_game()
                    output.print("Игра сохранена!")
                    continue
                elif command == 'o':
                    load_game()
                    output.print("Игра загружена!")
                    return -1
                elif command.isnumeric():
                    command = int(command)
                    if command == 0:
                        output.print("\n")
                        return 0
                    elif command == 1:
                        return Room.RIGHT_CHEST  # После победы можно пройти к сундуку
                    elif command == 2:
                        return Room.RIGHT_SIGN
        else:
            # Если монстр жив - начинаем бой
            return self.fight_monster()

    def fight_monster(self):
        """Обработка боя с Упырем"""
        monster_health = 50  # Здоровье монстра
        
        output.print("=== БОЙ С УПЫРЕМ ===")
        output.print(f"Упырь: {monster_health} здоровья | Вы: {player.health} здоровья")
        
        while monster_health > 0 and player.is_alive:
            output.print("\n1. Атаковать")
            output.print("2. Попытаться убежать (50% шанс)")
            
            choice = input("Ваш выбор: ").strip().lower()
            if choice == '1':
                # Игрок атакует
                player_damage = random.randint(5, 15)
                if player.has_sword:
                    player_damage += 10  # Меч увеличивает урон
                    output.print(f"Вы бьете мечом и наносите {player_damage} урона! ({player_damage}+10)")
                else:
                    output.print(f"Вы бьете кулаками и наносите {player_damage} урона!")
                monster_health -= player_damage
                
                # Монстр атакует в ответ
                if monster_health > 0:
                    monster_damage = random.randint(8, 12)
                    player.take_damage(monster_damage)
                    output.print(f"Упырь царапает вас, нанося {monster_damage} урона!")
                
                output.print(f"Упырь: {max(0, monster_health)} здоровья | Вы: {player.health} здоровья")
            
            elif choice == '2':
                # Попытка убежать
                if random.random() < 0.5:  # 50% шанс побега
                    output.print("Вы успешно убежали от Упыря!")
                    return Room.RIGHT_SIGN
                else:
                    output.print("Упырь перехватил вас!")
                    monster_damage = random.randint(10, 15)
                    player.take_damage(monster_damage)
                    output.print(f"Упырь кусает вас, нанося {monster_damage} урона!")
            
            if player.health <= 0:
                return 0  # Игрок умер
        
        if monster_health <= 0:
            output.print("\n=== ВЫ ПОБЕДИЛИ УПЫРЯ! ===")
            output.print("Теперь вы можете пройти в комнату с сокровищем!")
            self.monster_defeated = True
            self.description = '''Темная комната с трупом Упыря. Дверь в следующую комнату теперь открыта.'''
            return -1  # Перезагрузить комнату

class RightChestRoom(Room):
    """Комната с сундуком, перенесенная справа от комнаты с монстром"""
    def __init__(self):
        super().__init__('''Небольшая комната с массивным сундуком посередине.
   Сундук украшен замысловатой резьбой и выглядит очень старым.''',
       [ Action("Открыть сундук", Action.RIGHT_CHEST_OPEN),
         Action("Вернуться", Room.MONSTER_ROOM), ])
        self.chest_opened = False

    def open_chest(self):
        output.print('''  Вы открыли сундук.
  Внутри вы находите:
  - Ветвистая деревянная трость украшенная необычной ресьбой
  - Целебное зелье (+30 здоровья)
  Вы выпиваете зелье.''')
        
        player.heal(30)
        self.chest_opened = True
        self.description = '''Комната с открытым пустым сундуком.'''
        self.actions.pop(0) # Убираем действие "Открыть сундук"
        # Даем игроку предмет для лешего
        Room.get(Room.LEFT).got_item()
        output.print("Вы получили ветвистую трость и немного подлечились зельем здоровья!")

class LeftRoom(Room):
    """Комната с лешим"""
    def __init__(self):
        super().__init__('''В комнате сидит старый леший
   Леший: "Прииивееет...... Тыы хтоооо? Виииделлл мооою троооость?"''',
       [ Action("Нет не видел", Room.LEFT),
         Action("Вернуться", Room.ENTRY), ])

    def got_item(self):
        """Обновляем комнату после получения трости"""
        self.description = '''Старый леший с радостью смотрит на ветвистая деревянная трость
  Ооооооо.... Моооая трооость вернууууулась! Дааай!!!'''
        self.actions = [
            Action("Отдать трость", Action.LEFT_GIVE_ITEM),
            Action("Вернуться", Room.ENTRY),
        ]
    
    def give_item(self):
        """Отдаем трость лешему"""
        output.print('''  Леший в благодарность, полностью излечивает игрока.
  После чего с широкой улыбкой радостный леший опираясь на свою трость, вприпрыжку ускакивает в чащу леса''')
        # Полное исцеление после помощи лешему
        player.heal(player.max_health)
        self.description = '''Тихая пустынная комната'''
        self.actions = [
            Action("Вернуться", Room.ENTRY),
        ]

def save_game():
    """Сохранение состояния игры"""
    game_state = {
        'current_room': current_room,
        'right_sign_room': {
            'description': Room.get(Room.RIGHT_SIGN).description,
            'actions': [a.description for a in Room.get(Room.RIGHT_SIGN).actions]
        },
        'monster_room': {
            'description': Room.get(Room.MONSTER_ROOM).description,
            'actions': [a.description for a in Room.get(Room.MONSTER_ROOM).actions],
            'monster_defeated': hasattr(Room.get(Room.MONSTER_ROOM), 'monster_defeated') and Room.get(Room.MONSTER_ROOM).monster_defeated
        },
        'right_chest_room': {
            'description': Room.get(Room.RIGHT_CHEST).description,
            'actions': [a.description for a in Room.get(Room.RIGHT_CHEST).actions],
            'chest_opened': Room.get(Room.RIGHT_CHEST).chest_opened
        },
        'left_room': {
            'description': Room.get(Room.LEFT).description,
            'actions': [a.description for a in Room.get(Room.LEFT).actions]
        },
        'player': {
            'health': player.health,
            'max_health': player.max_health,
            'is_alive': player.is_alive,
            'has_sword': player.has_sword
        }
    }
    with open('save.json', 'w', encoding='utf-8') as f:
        json.dump(game_state, f, ensure_ascii=False, indent=2)

def load_game():
    """Загрузка сохраненной игры"""
    global current_room
    try:
        with open('save.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        current_room = data['current_room']
        
        # Восстанавливаем состояние игрока
        player.health = data['player']['health']
        player.max_health = data['player']['max_health']
        player.is_alive = data['player']['is_alive']
        player.has_sword = data['player'].get('has_sword', False)
        
        # Восстанавливаем состояние комнаты с табличкой
        Room.get(Room.RIGHT_SIGN).description = data['right_sign_room']['description']
        
        # Восстанавливаем состояние комнаты с монстром
        monster_room = Room.get(Room.MONSTER_ROOM)
        monster_room.description = data['monster_room']['description']
        if data['monster_room'].get('monster_defeated', False):
            monster_room.monster_defeated = True
        
        # Восстанавливаем состояние комнаты с сундуком
        right_chest = Room.get(Room.RIGHT_CHEST)
        right_chest.description = data['right_chest_room']['description']
        right_chest.chest_opened = data['right_chest_room']['chest_opened']
        if right_chest.chest_opened and len(right_chest.actions) > 0:
            if hasattr(right_chest, 'actions') and right_chest.actions:
                right_chest.actions.pop(0)
        
        # Восстанавливаем состояние левой комнаты
        left_room = Room.get(Room.LEFT)
        left_room.description = data['left_room']['description']
        if 'Отдать трость' in data['left_room']['actions']:
            left_room.actions = [
                Action("Отдать трость", Action.LEFT_GIVE_ITEM),
                Action("Вернуться", Room.ENTRY),
            ]
        elif len(left_room.actions) > 1 and 'Нет не видел' not in data['left_room']['actions']:
            left_room.actions = [
                Action("Вернуться", Room.ENTRY),
            ]
    except FileNotFoundError:
        output.print("Сохранение не найдено")
    except Exception as e:
        output.print(f"Ошибка при загрузке: {str(e)}")

if __name__ == "__main__":
    # Инициализация всех комнат
    Room.all = {
        Room.ENTRY: EntryRoom(),
        Room.LEFT: LeftRoom(),
        Room.RIGHT_SIGN: RightSignRoom(),
        Room.MONSTER_ROOM: MonsterRoom(),  # Новая комната с монстром
        Room.RIGHT_CHEST: RightChestRoom(),
    }
    current_room = Room.ENTRY
    
    try:
        # Основной игровой цикл
        while current_room and player.is_alive: # Добавили проверку на живой ли игрок
            action_id = Room.get(current_room).enter()
            if action_id == -1: # Перезагрузка комнаты после загрузки
                continue
            elif action_id == Action.RIGHT_CHEST_OPEN:
                Room.get(Room.RIGHT_CHEST).open_chest()
                Room.get(Room.LEFT).got_item()
            elif action_id == Action.LEFT_GIVE_ITEM:
                Room.get(Room.LEFT).give_item()
            elif action_id == Action.DEFEAT_MONSTER:
                Room.get(Room.MONSTER_ROOM).monster_defeated = True
            else:
                current_room = action_id
        
        # Если игрок умер, ждем выхода из программы
        while not player.is_alive:
            output.root.update()
            
    except KeyboardInterrupt:
        output.root.destroy()