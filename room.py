class Room: # Класс с комнатами
    all = {} # Словарь для хранения комнат
    ENTRY = 1 # Константа с первой комнатой
    LEFT = 2
    RIGHT = 3

    @staticmethod # Создание функции которую можно вызвать напрямую из класса, без использования объекта
    def get(room_code):
        return Room.all[room_code]
    
    def __init__(self,
       description="??? нет описания ???",
       actions=[]):
        self.description = description
        self.actions = actions

    def enter(self):
        print(f">> {self.description}\n")
        print("Возможные действия:")
        for id, action in enumerate(self.actions):
            print(f"{id+1}) {action.description}")
        while True:
            command = input("Ваше действие (0 - выход):")
            if command.isnumeric():
                command = int(command)
                if command == 0:
                    print("\n")
                    return 0
                elif 0 < command <= len(self.actions):
                    print("\n")
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
       [ Action ("Пойти направо", Room.RIGHT),
         Action ("Пойти налево", Room.LEFT), ])

class RightRoom(Room):
    def __init__(self):
        super().__init__('''Комната с закрытым сундуком''',
       [ Action ("Открыть сундук", Action.RIGHT_CHEST_OPEN),
         Action ("Вернуться", Room.ENTRY), ])

    def open_chest(self):
        print('''  Вы открыли сундук.
  В сундуке - ветвистая деревянная трость. Вы взяли ветвистую трость''')
        self.description = '''Комната с открытым пустым сундуком'''
        self.actions.pop(0)

class LeftRoom(Room):
    def __init__(self):
        super().__init__('''В комнате сидит старый леший
   Леший: "Прииивееет...... Тыы хтоооо? Виииделлл мооою троооость?"''',
       [ Action ("Нет не видел", Room.LEFT),
         Action ("Вернуться", Room.ENTRY), ])

    def got_item(self):
        self.description = '''Старый леший с радостью смотрит на ветвистая деревянная трость
  Ооооооо.... Моооая трооость вернууууулась! Дааай!!!'''
        self.actions = [
            Action ("Отдать трость", Action.LEFT_GIVE_ITEM),
            Action ("Вернуться", Room.ENTRY),
        ]
    
    def give_item(self):
        print("  Радостный леший опираясь на свою трость, вприпрыжку ускакал в чащу леса")
        self.description = '''Тихая пустынная комната'''
        self.actions = [
            Action ("Вернуться", Room.ENTRY),
        ] 

if __name__ == "__main__":
    Room.all = {
        Room.ENTRY: EntryRoom(),
        Room.LEFT: LeftRoom(),
        Room.RIGHT: RightRoom(),
    }
    current_room = Room.ENTRY
    while current_room: # Чтобы остановить бесконечный цикл нужно нажать сочитание клавиш "Ctrl + C"
        action_id = Room.get(current_room).enter()
        if action_id == Action.RIGHT_CHEST_OPEN:
            Room.get(Room.RIGHT).open_chest()
            Room.get(Room.LEFT).got_item()
        elif action_id == Action.LEFT_GIVE_ITEM:
            Room.get(Room.LEFT).give_item()
        else:
            current_room = action_id
        