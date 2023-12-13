# Cellular Automata in Blender

### Description:

The project is a set of scripts in Python to run in [Blender](https://www.blender.org/) and is designed to implement three-dimensional cellular automata with various rules.

The main idea of the project is the possibility of combining three-dimensional [cellular automata](https://en.wikipedia.org/wiki/Cellular_automaton) with different rules in one space. For this purpose, it is possible to mark areas with such rules using primitive objects, which, after creation, are converted into three-dimensional matrices. These matrices dynamically recalculate their values when the primary object changes.

To make it easier to work with matrices, various functions have been implemented. You can combine and aggregate matrices using functions to combine, subtract, and produce a hollow object.

I would be glad if this project helps you create unique 3D cellular automata in Blender and opens up new possibilities for your creativity.

***

# Клеточные автоматы в Blender

### Описание:

Проект представляет собой набор скриптов на языке Python для запуска в [Blender](https://www.blender.org/) и предназначен для реализации трехмерных клеточных автоматов с различными правилами.

Основная идея проекта заключается в возможности комбинирования трехмерных [клеточных автоматов](https://ru.wikipedia.org/wiki/%D0%9A%D0%BB%D0%B5%D1%82%D0%BE%D1%87%D0%BD%D1%8B%D0%B9_%D0%B0%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D1%82) с различными правилами в одном пространстве. Для этого предусмотрена возможность разметки областей с такими правилами с помощью примитивных объектов, которые после создания преобразуются в **трехмерные матрицы**. Эти матрицы динамически пересчитывают свои значения при изменении первичного объекта.

Для удобства работы с матрицами реализованы различные функции. Вы можете сочетать и агрегировать матрицы, используя функции для объединения, вычитания и получения полого объекта.

Буду рад, если этот проект поможет вам создавать уникальные трехмерные клеточные автоматы в Blender и откроет новые возможности для вашего творчества.

***

### Функционал проекта:

- [tensor.py](tensor.py) - модуль для работы с трехмерными матрицами на основе `numpy`. [(Схема)](https://github.com/islesarev317/NumPy-Education/assets/78931652/b63a2a5c-01b2-4d98-90f2-40549df5325e)
- [virtual.py](virtual.py) - модуль для преобразования объектов в трехмерные матрицы с возможностью задавать формулу сочетания матриц и пересчитывать результат при изменении первичных объектов. [(Схема)](https://github.com/islesarev317/NumPy-Education/assets/78931652/29157797-a1e6-4f24-8c79-62d8ac8fa0c1)
- [rule.py](rule.py) - модуль для расчета правил клеточных автоматов и их применения
- [instance.py](instance.py) - модуль реализующий отображение трехмерных матриц в Blender, каждому ненулевому значению матрицы сопоставляется объект. Также предусмотрено переиспользование объектов в целях оптимизации при создании анимации.
- [utils.py](utils.py) - набор различных функций, инкапсулирующих логику работы с модулем `bpy`.

***

### TODO

- [ ] Добавление класса `VirtualProperty` связывающего заданный пользователем **параметр в Blender** и **Python объект**. Таким образом возможно будет динамически изменять некоторые параметры CA (например, правила CA) без необходимости редактирования и перезапуска управляющего скрипта
- [ ] Оптимизация функции `next_life`
  - [x] PR: [feature-next-life-optimization](https://github.com/islesarev317/Cellular-Automata-In-Blender/pull/1/commits/1477a69be686e9a066416326faa2b0ac1f7ad94c)
- [ ] Разработка интерфейса
- [ ] Методы для работы с правилами CA: поиск ближайших похожих; получение случайного по заданным коэффициентам выживаемости и рождаемости

***

### Галерея

#### 1. Growing-Sphere

[![Cellular Automata in Blender Python Scripting - YouTube](demos/demo-2312111224-Growing-Sphere/Pre-Screen-YouTube.png)](https://www.youtube.com/watch?v=s1DLh8MZMMQ)

![Growing-Sphere.gif](demos/demo-2312111224-Growing-Sphere/Growing-Sphere.gif)

![Growing-Sphere.png](demos/demo-2312111224-Growing-Sphere/Growing-Sphere.png)

- **Скрипт:** *[Growing-Sphere.py](demos/demo-2312111224-Growing-Sphere/Growing-Sphere.py)*
- **Blender файл:** *[Growing-Sphere.blend](demos/demo-2312111224-Growing-Sphere/Growing-Sphere.blend)*
- **Описание:**
  - Инициализируем сферу как **VirtualObject** экземпляр и заполняем значениями
    - `sphere = VirtualObject(bpy.data.objects["Sphere"], grain)`
    - `vf_init = sphere.fill(1)`
  - Получаем трехмерную матрицу заполненную **1** в местах пересечения со сферой и **0** в прилегающих областях
  - Аналогично инициализируем куб и заполняем случайным кодом клеточного автомата
    - `cube = VirtualObject(bpy.data.objects["Cube"], grain)`
    - `vf_rule = cube.fill(code_rand)`
  - Код случайного правила можно увидеть в окне **Outliner** в коллекции **Info**. Расшифровки кода в скрипте нет, но можно использовать вызов:
    - `CellRule.get_condition(code_rand)`
  - Создаем экземпляр клеточного автомата с данным правилом и начальными условиями в виде сферы
    - `vf_life = VirtualLife(vf_rule, vf_init)`
  - В целях оптимизации и уменьшения количества отображаемых кубов в Blender, убираем все внутренние клетки. Эта функция никак не влияет на расчет состояний клеточного автомата
    - `vf_life = vf_life.hollow()`
  - Время жизни клетки по умолчанию передается в `Custom Property` с именем `value`, используем этот параметр в материале объекта для покраски клетки в разные цвета.

***
#### 2. Basic-Cube

![Basic-Cube.gif](demos/demo-2312092116-Basic-Cube/Basic-Cube.gif)

![Basic-Cube.png](demos/demo-2312092116-Basic-Cube/Basic-Cube.png)

- **Скрипт:** *[Basic-Cube.py](demos/demo-2312092116-Basic-Cube/Basic-Cube.py)*
- **Blender файл:** *[Basic-Cube.blend](demos/demo-2312092116-Basic-Cube/Basic-Cube.blend)*
- **Описание:**
  - Куб заполняем случайным образом значениями **0** и **1** в соотношении **90:10**
    - `vf_init = cube.random_fill([0, 1], weights=[0.9, 0.1])`
  - Полученную трехмерную матрицу отзеркаливаем по всем осям для получения симметрии
    - `vf_init = vf_init.mirror()`
  - Тот же куб используем для создания матрицы заполненной кодом правила клеточного автомата
    - `vf_rule = cube.fill(code_maze)`
    - Код можно расшифровать вызовом `CellRule.get_condition(8259390827203093)`, получим:
      - B = `[1, 6, 7, 9, 10, 13, 21, 22]` (условия рождения)
      - S = `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 18, 24, 25, 26]` (условия выживания)
  - Создаем экземпляр клеточного автомата с данным правилом и случайными начальными условиями
    - `vf_life = VirtualLife(vf_rule, vf_init)`
  - В целях оптимизации и уменьшения количества отображаемых кубов в Blender, убираем все внутренние клетки. Эта функция никак не влияет на расчет состояний клеточного автомата
    - `vf_life = vf_life.hollow()`
  - Время жизни клетки по умолчанию передается в `Custom Property` с именем `value`, используем этот параметр в материале объекта для покраски клетки в разные цвета.

***

Также больше примеров можно увидеть в разделe: *[examples](examples)* 
