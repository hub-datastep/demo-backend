import sys

# Открываем файл для записи
file = open("syntetics_armatyres.txt", 'w', encoding='utf-8')

# Перенаправляем стандартный поток вывода (stdout) в файл
sys.stdout = file

# Исходные данные
let1 = ["А","А","А","А", "В"]  # // 9:1
num1 = ['240', '300', '400', '500']
let2 = ["", "","","","","C"]  # // 7:3
num2 = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 34, 36, 38, 40, 45]
num3 = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 30, 32, 34, 36, 38, 40, 45]
# Пропорции, которые нужно соблюсти
prop1 = (9, 1)  # let1
prop2 = (7, 3)  # let2



# Печать общего числа элементов
# print(len(let1)*len(let2)*len(num1)*len(num2))

# Переменные для счетчика
i = 0
cnt = 0
s = []
# Генерация и запись арматуры в файл
for a in let1:
    for b in num1:
        for c in let2:
            for d in num2:
                if cnt % 200 == 0:
                    f = f'''Арматура {a}{b}{c} стальная {d}мм'''
                elif cnt % 199 == 0:
                    f = f'''Арматура {a}{b}{c} {d}мм стальная'''
                else:
                    f = f'''Арматура стальная {a}{b}{c} {d}мм'''
                s.append(f)
                cnt += 1
def trim_list_by_step(input_list, target_size=130):
    # Если список уже меньше или равен целевому размеру, возвращаем его
    if len(input_list) <= target_size:
        return input_list
    
    # Определим шаг для выборки
    step = len(input_list) // target_size

    # Список для хранения результата
    result = []
    
    # Выбираем элементы с шагом
    deg = len(input_list) % target_size
    if deg > (target_size//2-1):
        for i in range(0, target_size*step//2, step):
            result.append(input_list[i])
        # step+=1
        for i in range(target_size*step//2+deg, len(input_list), step):
            result.append(input_list[i])

        print(len(result))
    else:
        for i in range(0, len(input_list), step):
            result.append(input_list[i])

    # Если количество выбранных элементов больше target_size, обрезаем
    if len(result) > target_size:
        result = result[:target_size]
    print("res: ", result)
    return result

s = trim_list_by_step(s)
lop = set()
for i in s:
    for n in i.split():
        if "мм" in n:
            lop.add(int(n.split("мм")[0]))
print()
print(lop)
print()
# Печать итогового количества элементов
print("s =",s)
print()
for i in s:
    print(i)