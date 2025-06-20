import json
import tkinter as tk
from tkinter import scrolledtext
import random  # Нужна для боя с монстром

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
        self.has_sword = False  # Флаг наличия меча для боя с монстром (меч увеличивает урон на +10)
        self.has_key = False  # Флаг наличия ключа от верхней комнаты
    
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
    LEFT = 2  # Комната с лешим
    RIGHT_SIGN = 3  # Комната с предупреждающей табличкой
    MONSTER_ROOM = 4  # Комната с монстром
    RIGHT_CHEST = 5  # Комната с сундуком
    SWORD_SIGN = 6  # Комната с информацией о мече
    SWORD_ROOM = 7  # Комната с мечом
    UPPER_ROOM = 8  # Верхняя комната с выходом из лабиринта

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
            else:
                output.print("Неизвестная команда. Попробуйте еще раз.")

class Action:
    RIGHT_CHEST_OPEN = 1000  # Действие - открытие сундука с сокровищами
    LEFT_GIVE_ITEM = 1001  # Действие - передача трости
    DEFEAT_MONSTER = 1002  # Действие - победа над монстром
    GET_SWORD = 1003  # Действие - получение меча
    UNLOCK_DOOR = 1004  # Действие - открытие двери в верхнюю комнату
    ESCAPE_LABYRINTH = 1005  # Действие - побег из лабиринта

    def __init__(self, description, param, result=''):
        self.description = description
        self.param = param
        self.result = result

class EntryRoom(Room):
    def __init__(self):
        super().__init__('''Вход в лабиринт.
   Лестница вниз, от которой есть двери направо и налево.
   Также есть темный проход вниз по скрипучей лестнице.''',
       [ Action("Пойти направо", Room.RIGHT_SIGN),  # Ведет в комнату с табличкой
         Action("Пойти налево", Room.LEFT),
         Action("Спуститься вниз", Room.SWORD_SIGN)])

class SwordSignRoom(Room):
    """Комната с информацией о мече"""
    def __init__(self):
        super().__init__(
            '''Маленькая каморка с низким потолком. На стене висит потрепанный пергамент.
            
   Надпись гласит:
   "Ищите меч света в комнате справа.
   Только он сможет победить тьму этого лабиринта!"''',
            [
                Action("Пойти направо", Room.SWORD_ROOM),
                Action("Вернуться наверх", Room.ENTRY)
            ]
        )

class SwordRoom(Room):
    """Комната с мечом"""
    def __init__(self):
        super().__init__(
            '''Крошечная комната, освещенная таинственным светом.
   В центре на каменном пьедестале лежит сияющий меч.''',
            [
                Action("Взять меч", Action.GET_SWORD),
                Action("Вернуться", Room.SWORD_SIGN)
            ]
        )
        self.sword_taken = False

    def enter(self):
        if self.sword_taken:
            self.description = '''Крошечная комната с пустым пьедесталом.
   Меч уже у вас!'''
            self.actions = [Action("Вернуться", Room.SWORD_SIGN)]
        
        return super().enter()

    def take_sword(self):
        """Логика взятия меча"""
        output.print('''  Вы берете меч в руки - он излучает тепло и свет.
  Чувствуете, как сила наполняет вас!''')
        player.has_sword = True
        self.sword_taken = True
        self.description = '''Крошечная комната с пустым пьедесталом.
   Меч уже у вас!'''
        self.actions = [Action("Вернуться", Room.SWORD_SIGN)]
        output.print("Теперь ваши атаки будут сильнее!")

class RightSignRoom(Room):
    """Комната с предупреждающей табличкой перед комнатой с монстром"""
    def __init__(self):
        super().__init__('''Каменная комната с высоким потолком. На стене висит старая табличка с надписью.
   В дальнем углу видна массивная дверь с железными скобами.

   Надпись на табличке гласит:
   "ОСТОРОЖНО! В следующей комнате обитает жуткий Упырь!
   Но смельчаков, что победят его, ждет невиданное сокровище!"''',
       [ Action("Пойти дальше вниз (рискнуть)", Room.MONSTER_ROOM),
         Action("Вернуться обратно", Room.ENTRY), ])

class MonsterRoom(Room):
    """Комната с монстром Упырем"""
    def __init__(self):
        super().__init__('''Темная сырая комната с костями на полу. В центре стоит жуткий Упырь!
   Его красные глаза горят в темноте, а длинные когти скребут по камням.''',
       [ Action("Атаковать монстра", Room.MONSTER_ROOM),  # Обрабатывается отдельно
         Action("Попытаться убежать", Room.RIGHT_SIGN), ])  # Бегство возвращает в комнату с табличкой
        self.monster_defeated = False

    def enter(self):
        """Особая логика enter для комнаты с монстром и обработки боя"""
        health_status = player.get_health_status()
        output.print(f"[Состояние: {health_status}, Здоровье: {player.health}/{player.max_health}]")
        output.print(f">> {self.description}\n")
        
        # Проверяем, жив ли монстр (если нет - пропускаем бой)
        if self.monster_defeated:
            output.print("Тело Упыря лежит на полу, издавая зловоние.")
            output.print("Возможные действия:")
            output.print("1 Пройти дальше в комнату с сокровищем")
            output.print("2 Вернуться")
            
            while True:
                cmd = input("Ваш выбор: ").strip().lower()
                if cmd == '1':
                    return Room.RIGHT_CHEST
                elif cmd == '2':
                    return Room.RIGHT_SIGN
                else:
                    output.print("Неверный ввод. Попробуйте еще раз.")
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
                    output.print(f"Вы бьете мечом и наносите {player_damage} урона! ({player_damage-10}+10)")
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
    """Комната с сундуком сокровищ"""
    def __init__(self):
        super().__init__('''Небольшая комната с массивным сундуком посередине.
   Сундук украшен замысловатой резьбой и выглядит очень старым.''',
       [ Action("Открыть сундук", Action.RIGHT_CHEST_OPEN),
         Action("Вернуться", Room.MONSTER_ROOM), ])
        self.chest_opened = False

    def open_chest(self):
        output.print('''  Вы открыли сундук.
  Внутри вы находите:
  - Ветвистая деревянная трость украшенная необычной резьбой
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
        self.door_unlocked = False  # Флаг открытия двери в верхнюю комнату
        self.has_given_key = False  # Флаг, что леший уже дал ключ

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
        output.print('''  Леший в благодарность, полностью излечивает игрока.''')
        
        # Леший дает ключ от верхней комнаты
        if not self.has_given_key:
            output.print('''\n  Перед тем как уйти, леший достает из кармана старинный ключ с таинственным узором, украшенный драгоценным рубином,
  и протягивает его вам со словами:
  "Возьмиии... Пригодииится..."''')
            player.has_key = True
            self.has_given_key = True

        output.print('''  После чего радостный леший с широкой улыбкой, опираясь на свою трость, вприпрыжку ускакивает в чащу леса.
  Когда леший ушел, вы замечаете старинную дверь в стене, которая раньше была скрыта за его спиной.
  На двери висит замок с затейливым узором.''')
        
        # Полное исцеление после помощи лешему
        player.heal(player.max_health)
        self.door_unlocked = True  # Дверь можно открыть
        
        self.description = '''Тихая пустынная комната. В стене видна старинная дверь с замком.'''
        self.actions = [
            Action("Попробовать открыть дверь", Action.UNLOCK_DOOR) if player.has_key else 
            Action("Осмотреть дверь (заперта)", Room.LEFT),
            Action("Вернуться", Room.ENTRY),
        ]

class UpperRoom(Room):
    """Верхняя комната с выходом из лабиринта"""
    def __init__(self):
        super().__init__('''Просторная светлая комната с высокими потолками. 
   В противоположной стене виден яркий свет, пробивающийся через выход наружу.
   
   Вы чувствуете свежий ветерок и слышите пение птиц - это точно выход из лабиринта!
   
   === ВЫ НАШЛИ ВЫХОД ИЗ ЛАБИРИНТА! ===
   
   Пройдя через выход, вы оказываетесь на солнечной поляне. 
   Лабиринт остался позади, а впереди вас ждут новые приключения!
   
   Поздравляем с успешным прохождением игры!''',
       [
           Action("Завершить игру", 0),  # Предлагается выйти из игры
           Action("Осмотреться вокруг", Room.UPPER_ROOM)  # Можно остаться и осмотреться
       ])
        self.escaped = False  # Флаг, что игрок нашел выход

    def enter(self):
        """Переопределяем enter, чтобы показать сообщение о победе только один раз"""
        if not self.escaped:
            output.print('''\n=== ВЫ НАШЛИ ВЫХОД ИЗ ЛАБИРИНТА! ===
            
  Пройдя через выход, вы оказываетесь на солнечной поляне. 
  Лабиринт остался позади, а впереди вас ждут новые приключения!
  
  Поздравляем с успешным прохождением игры!''')
            self.escaped = True
        
        # Показываем стандартное описание комнаты и действия
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
            else:
                output.print("Неизвестная команда. Попробуйте еще раз.")

def save_game():
    """Сохранение состояния игры"""
    game_state = {
        'current_room': current_room,
        'sword_sign_room': {
            'description': Room.get(Room.SWORD_SIGN).description,
            'actions': [a.description for a in Room.get(Room.SWORD_SIGN).actions]
        },
        'sword_room': {
            'description': Room.get(Room.SWORD_ROOM).description,
            'actions': [a.description for a in Room.get(Room.SWORD_ROOM).actions],
            'sword_taken': Room.get(Room.SWORD_ROOM).sword_taken
        },
        'right_sign_room': {
            'description': Room.get(Room.RIGHT_SIGN).description,
            'actions': [a.description for a in Room.get(Room.RIGHT_SIGN).actions]
        },
        'monster_room': {
            'description': Room.get(Room.MONSTER_ROOM).description,
            'actions': [a.description for a in Room.get(Room.MONSTER_ROOM).actions],
            'monster_defeated': Room.get(Room.MONSTER_ROOM).monster_defeated
        },
        'right_chest_room': {
            'description': Room.get(Room.RIGHT_CHEST).description,
            'actions': [a.description for a in Room.get(Room.RIGHT_CHEST).actions],
            'chest_opened': Room.get(Room.RIGHT_CHEST).chest_opened
        },
        'left_room': {
            'description': Room.get(Room.LEFT).description,
            'actions': [a.description for a in Room.get(Room.LEFT).actions],
            'door_unlocked': Room.get(Room.LEFT).door_unlocked
        },
        'upper_room': {
            'description': Room.get(Room.UPPER_ROOM).description,
            'actions': [a.description for a in Room.get(Room.UPPER_ROOM).actions],
            'escaped': Room.get(Room.UPPER_ROOM).escaped
        },
        'player': {
            'health': player.health,
            'max_health': player.max_health,
            'is_alive': player.is_alive,
            'has_sword': player.has_sword,
            'has_key': player.has_key
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
        player.has_key = data['player'].get('has_key', False)
        
        # Восстанавливаем состояние комнаты с мечем
        Room.get(Room.SWORD_SIGN).description = data['sword_sign_room']['description']
        sword_room = Room.get(Room.SWORD_ROOM)
        sword_room.description = data['sword_room']['description']
        sword_room.sword_taken = data['sword_room']['sword_taken']
        if sword_room.sword_taken:
            sword_room.actions = [Action("Вернуться", Room.SWORD_SIGN)]

        # Восстанавливаем состояние комнаты с табличкой
        Room.get(Room.RIGHT_SIGN).description = data['right_sign_room']['description']
        
        # Восстанавливаем состояние комнаты с монстром
        monster_room = Room.get(Room.MONSTER_ROOM)
        monster_room.description = data['monster_room']['description']
        monster_room.monster_defeated = data['monster_room']['monster_defeated']
        
        # Восстанавливаем состояние комнаты с сундуком
        right_chest = Room.get(Room.RIGHT_CHEST)
        right_chest.description = data['right_chest_room']['description']
        right_chest.chest_opened = data['right_chest_room']['chest_opened']
        if right_chest.chest_opened and len(right_chest.actions) > 0:
            right_chest.actions.pop(0)
        
        # Восстанавливаем состояние левой комнаты
        left_room = Room.get(Room.LEFT)
        left_room.description = data['left_room']['description']
        left_room.door_unlocked = data['left_room'].get('door_unlocked', False)
        
        if 'Отдать трость' in data['left_room']['actions']:
            left_room.actions = [
                Action("Отдать трость", Action.LEFT_GIVE_ITEM),
                Action("Вернуться", Room.ENTRY),
            ]
        elif left_room.door_unlocked:
            left_room.actions = [
                Action("Попробовать открыть дверь", Action.UNLOCK_DOOR) if player.has_key else 
                Action("Осмотреть дверь (заперта)", Room.LEFT),
                Action("Вернуться", Room.ENTRY),
            ]
        elif len(left_room.actions) > 1 and 'Нет не видел' not in data['left_room']['actions']:
            left_room.actions = [
                Action("Вернуться", Room.ENTRY),
            ]
        
        # Восстанавливаем состояние комнаты с выходом из лабиринта
        if Room.UPPER_ROOM in Room.all:
            upper_room = Room.get(Room.UPPER_ROOM)
            upper_room.description = data['upper_room']['description']
            upper_room.escaped = data['upper_room'].get('escaped', False)
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
        Room.MONSTER_ROOM: MonsterRoom(),  # Комната с монстром
        Room.RIGHT_CHEST: RightChestRoom(),
        Room.SWORD_SIGN: SwordSignRoom(),  # Комната с информацией о наличии меча
        Room.SWORD_ROOM: SwordRoom(),      # Комната с мечом
        Room.UPPER_ROOM: UpperRoom()       # Комната с выходом из лабиринта
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
            elif action_id == Action.LEFT_GIVE_ITEM:
                Room.get(Room.LEFT).give_item()
            elif action_id == Action.DEFEAT_MONSTER:
                Room.get(Room.MONSTER_ROOM).monster_defeated = True
            elif action_id == Action.GET_SWORD:
                Room.get(Room.SWORD_ROOM).take_sword()
            elif action_id == Action.UNLOCK_DOOR:
                if player.has_key:
                    output.print('''  Ключ идеально подошел к замку! Дверь со скрипом открывается, 
  обнажая узкую винтовую лестницу, ведущую наверх.''')
                    current_room = Room.UPPER_ROOM
                else:
                    output.print("У вас нет подходящего ключа для этой двери.")
            elif action_id == Action.ESCAPE_LABYRINTH:
                Room.get(Room.UPPER_ROOM).escape()
            else:
                current_room = action_id
        
        # Если игрок умер, ждем выхода из программы
        while not player.is_alive:
            output.root.update()
            
    except KeyboardInterrupt:
        output.root.destroy()