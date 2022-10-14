import bisect
import math

"""
Дефинирање на класа за структурата на проблемот кој ќе го решаваме со пребарување.
Класата Problem е апстрактна класа од која правиме наследување за дефинирање на основните 
карактеристики на секој проблем што сакаме да го решиме
"""


class Problem:
    def __init__(self, initial, goal=None):
        self.initial = initial
        self.goal = goal

    def successor(self, state):
        """За дадена состојба, врати речник од парови {акција : состојба}
        достапни од оваа состојба. Ако има многу следбеници, употребете
        итератор кој би ги генерирал следбениците еден по еден, наместо да
        ги генерирате сите одеднаш.
        :param state: дадена состојба
        :return:  речник од парови {акција : состојба} достапни од оваа
                  состојба
        :rtype: dict
        """
        raise NotImplementedError

    def actions(self, state):
        """За дадена состојба state, врати листа од сите акции што може да
        се применат над таа состојба
        :param state: дадена состојба
        :return: листа на акции
        :rtype: list
        """
        raise NotImplementedError

    def result(self, state, action):
        """За дадена состојба state и акција action, врати ја состојбата
        што се добива со примена на акцијата над состојбата
        :param state: дадена состојба
        :param action: дадена акција
        :return: резултантна состојба
        """
        raise NotImplementedError

    def goal_test(self, state):
        """Врати True ако state е целна состојба. Даденава имплементација
        на методот директно ја споредува state со self.goal, како што е
        специфицирана во конструкторот. Имплементирајте го овој метод ако
        проверката со една целна состојба self.goal не е доволна.
        :param state: дадена состојба
        :return: дали дадената состојба е целна состојба
        :rtype: bool
        """
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Врати ја цената на решавачкиот пат кој пристигнува во состојбата
        state2 од состојбата state1 преку акцијата action, претпоставувајќи
        дека цената на патот до состојбата state1 е c. Ако проблемот е таков
        што патот не е важен, оваа функција ќе ја разгледува само состојбата
        state2. Ако патот е важен, ќе ја разгледува цената c и можеби и
        state1 и action. Даденава имплементација му доделува цена 1 на секој
        чекор од патот.
        :param c: цена на патот до состојбата state1
        :param state1: дадена моментална состојба
        :param action: акција која треба да се изврши
        :param state2: состојба во која треба да се стигне
        :return: цена на патот по извршување на акцијата
        :rtype: float
        """
        return c + 1

    def value(self):
        """За проблеми на оптимизација, секоја состојба си има вредност.
        Hill-climbing и сличните алгоритми се обидуваат да ја максимизираат
        оваа вредност.
        :return: вредност на состојба
        :rtype: float
        """
        raise NotImplementedError


"""
Дефинирање на класата за структурата на јазел од пребарување.
Класата Node не се наследува
"""


class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Креирај јазол од пребарувачкото дрво, добиен од parent со примена
        на акцијата action
        :param state: моментална состојба (current state)
        :param parent: родителска состојба (parent state)
        :param action: акција (action)
        :param path_cost: цена на патот (path cost)
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0  # search depth
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node %s>" % (self.state,)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """Излистај ги јазлите достапни во еден чекор од овој јазол.
        :param problem: даден проблем
        :return: листа на достапни јазли во еден чекор
        :rtype: list(Node)
        """

        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """Дете јазел
        :param problem: даден проблем
        :param action: дадена акција
        :return: достапен јазел според дадената акција
        :rtype: Node
        """
        next_state = problem.result(self.state, action)
        return Node(next_state, self, action,
                    problem.path_cost(self.path_cost, self.state,
                                      action, next_state))

    def solution(self):
        """Врати ја секвенцата од акции за да се стигне од коренот до овој јазол.
        :return: секвенцата од акции
        :rtype: list
        """
        return [node.action for node in self.path()[1:]]

    def solve(self):
        """Врати ја секвенцата од состојби за да се стигне од коренот до овој јазол.
        :return: листа од состојби
        :rtype: list
        """
        return [node.state for node in self.path()[0:]]

    def path(self):
        """Врати ја листата од јазли што го формираат патот од коренот до овој јазол.
        :return: листа од јазли од патот
        :rtype: list(Node)
        """
        x, result = self, []
        while x:
            result.append(x)
            x = x.parent
        result.reverse()
        return result

    """Сакаме редицата од јазли кај breadth_first_search или 
    astar_search да не содржи состојби - дупликати, па јазлите што
    содржат иста состојба ги третираме како исти. [Проблем: ова може
    да не биде пожелно во други ситуации.]"""

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)


"""
Дефинирање на помошни структури за чување на листата на генерирани, но непроверени јазли
"""


class Queue:
    """Queue е апстрактна класа / интерфејс. Постојат 3 типа:
        Stack(): Last In First Out Queue (стек).
        FIFOQueue(): First In First Out Queue (редица).
        PriorityQueue(order, f): Queue во сортиран редослед (подразбирливо,од најмалиот кон
                                 најголемиот јазол).
    """

    def __init__(self):
        raise NotImplementedError

    def append(self, item):
        """Додади го елементот item во редицата
        :param item: даден елемент
        :return: None
        """
        raise NotImplementedError

    def extend(self, items):
        """Додади ги елементите items во редицата
        :param items: дадени елементи
        :return: None
        """
        raise NotImplementedError

    def pop(self):
        """Врати го првиот елемент од редицата
        :return: прв елемент
        """
        raise NotImplementedError

    def __len__(self):
        """Врати го бројот на елементи во редицата
        :return: број на елементи во редицата
        :rtype: int
        """
        raise NotImplementedError

    def __contains__(self, item):
        """Проверка дали редицата го содржи елементот item
        :param item: даден елемент
        :return: дали queue го содржи item
        :rtype: bool
        """
        raise NotImplementedError


class Stack(Queue):
    """Last-In-First-Out Queue."""

    def __init__(self):
        self.data = []

    def append(self, item):
        self.data.append(item)

    def extend(self, items):
        self.data.extend(items)

    def pop(self):
        return self.data.pop()

    def __len__(self):
        return len(self.data)

    def __contains__(self, item):
        return item in self.data


class FIFOQueue(Queue):
    """First-In-First-Out Queue."""

    def __init__(self):
        self.data = []

    def append(self, item):
        self.data.append(item)

    def extend(self, items):
        self.data.extend(items)

    def pop(self):
        return self.data.pop(0)

    def __len__(self):
        return len(self.data)

    def __contains__(self, item):
        return item in self.data


class PriorityQueue(Queue):
    """Редица во која прво се враќа минималниот (или максималниот) елемент
    (како што е определено со f и order). Оваа структура се користи кај
    информирано пребарување"""
    """"""

    def __init__(self, order=min, f=lambda x: x):
        """
        :param order: функција за подредување, ако order е min, се враќа елементот
                      со минимална f(x); ако order е max, тогаш се враќа елементот
                      со максимална f(x).
        :param f: функција f(x)
        """
        assert order in [min, max]
        self.data = []
        self.order = order
        self.f = f

    def append(self, item):
        bisect.insort_right(self.data, (self.f(item), item))

    def extend(self, items):
        for item in items:
            bisect.insort_right(self.data, (self.f(item), item))

    def pop(self):
        if self.order == min:
            return self.data.pop(0)[1]
        return self.data.pop()[1]

    def __len__(self):
        return len(self.data)

    def __contains__(self, item):
        return any(item == pair[1] for pair in self.data)

    def __getitem__(self, key):
        for _, item in self.data:
            if item == key:
                return item

    def __delitem__(self, key):
        for i, (value, item) in enumerate(self.data):
            if item == key:
                self.data.pop(i)


from sys import maxsize as infinity

"""
Информирано пребарување во рамки на граф
"""


def memoize(fn, slot=None):
    """ Запамети ја пресметаната вредност за која била листа од
    аргументи. Ако е специфициран slot, зачувај го резултатот во
    тој slot на првиот аргумент. Ако slot е None, зачувај ги
    резултатите во речник.
    :param fn: зададена функција
    :type fn: function
    :param slot: име на атрибут во кој се чуваат резултатите од функцијата
    :type slot: str
    :return: функција со модификација за зачувување на резултатите
    :rtype: function
    """
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        def memoized_fn(*args):
            if args not in memoized_fn.cache:
                memoized_fn.cache[args] = fn(*args)
            return memoized_fn.cache[args]

        memoized_fn.cache = {}
    return memoized_fn


def best_first_graph_search(problem, f):
    """Пребарувај низ следбениците на даден проблем за да најдеш цел. Користи
     функција за евалуација за да се одлучи кој е сосед најмногу ветува и
     потоа да се истражи. Ако до дадена состојба стигнат два пата, употреби
     го најдобриот пат.
    :param problem: даден проблем
    :type problem: Problem
    :param f: дадена функција за евалуација (проценка)
    :type f: function
    :return: Node or None
    :rtype: Node
    """
    f = memoize(f, 'f')
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = PriorityQueue(min, f)
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                incumbent = frontier[child]
                if f(child) < f(incumbent):
                    del frontier[incumbent]
                    frontier.append(child)
    return None


def greedy_best_first_graph_search(problem, h=None):
    """ Greedy best-first пребарување се остварува ако се специфицира дека f(n) = h(n).
    :param problem: даден проблем
    :type problem: Problem
    :param h: дадена функција за хевристика
    :type h: function
    :return: Node or None
    """
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, h)


def astar_search(problem, h=None):
    """ A* пребарување е best-first graph пребарување каде f(n) = g(n) + h(n).
    :param problem: даден проблем
    :type problem: Problem
    :param h: дадена функција за хевристика
    :type h: function
    :return: Node or None
    """
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))


def recursive_best_first_search(problem, h=None):
    """Recursive best first search - ја ограничува рекурзијата
    преку следење на f-вредноста на најдобриот алтернативен пат
    од било кој јазел предок (еден чекор гледање нанапред).
    :param problem: даден проблем
    :type problem: Problem
    :param h: дадена функција за хевристика
    :type h: function
    :return: Node or None
    """
    h = memoize(h or problem.h, 'h')

    def RBFS(problem, node, flimit):
        if problem.goal_test(node.state):
            return node, 0  # (втората вредност е неважна)
        successors = node.expand(problem)
        if len(successors) == 0:
            return None, infinity
        for s in successors:
            s.f = max(s.path_cost + h(s), node.f)
        while True:
            # Подреди ги според најниската f вредност
            successors.sort(key=lambda x: x.f)
            best = successors[0]
            if best.f > flimit:
                return None, best.f
            if len(successors) > 1:
                alternative = successors[1].f
            else:
                alternative = infinity
            result, best.f = RBFS(problem, best, min(flimit, alternative))
            if result is not None:
                return result, best.f

    node = Node(problem.initial)
    node.f = h(node)
    result, bestf = RBFS(problem, node, infinity)
    return result


# SEVER
def north(snake_head, snake_body):
    if (snake_head[1] + 1) < 10 and (snake_head[0], snake_head[1] + 1) not in snake_body:
        snake_body.pop()
        snake_body.insert(0, (snake_head[0], snake_head[1]))

        snake_head[1] += 1
        snake_head[2] = "north"

    return snake_head, snake_body


# ZAPAD
def west(snake_head, snake_body):
    if (snake_head[0] - 1) >= 0 and (snake_head[0] - 1, snake_head[1]) not in snake_body:
        snake_body.pop()
        snake_body.insert(0, (snake_head[0], snake_head[1]))

        snake_head[0] -= 1
        snake_head[2] = "west"

    return snake_head, snake_body


# JUG
def south(snake_head, snake_body):
    if (snake_head[1] - 1) >= 0 and (snake_head[0], snake_head[1] - 1) not in snake_body:
        snake_body.pop()
        snake_body.insert(0, (snake_head[0], snake_head[1]))

        snake_head[1] -= 1
        snake_head[2] = "south"
    return snake_head, snake_body


# ISTOK
def east(snake_head, snake_body):
    if (snake_head[0] + 1) < 10 and (snake_head[0] + 1, snake_head[1]) not in snake_body:
        snake_body.pop()
        snake_body.insert(0, (snake_head[0], snake_head[1]))

        snake_head[0] += 1
        snake_head[2] = "east"

    return snake_head, snake_body


#       north
# west        east
#       south

def ProdolzhiPravo(snake_head, snake_body):
    if snake_head[2] == "east":
        return east(snake_head, snake_body)
    elif snake_head[2] == "west":
        return west(snake_head, snake_body)
    elif snake_head[2] == "north":
        return north(snake_head, snake_body)
    elif snake_head[2] == "south":
        return south(snake_head, snake_body)


def SvrtiDesno(snake_head, snake_body):
    if snake_head[2] == "east":
        return south(snake_head, snake_body)
    elif snake_head[2] == "west":
        return north(snake_head, snake_body)
    elif snake_head[2] == "north":
        return east(snake_head, snake_body)
    elif snake_head[2] == "south":
        return west(snake_head, snake_body)


def SvrtiLevo(snake_head, snake_body):
    if snake_head[2] == "east":
        return north(snake_head, snake_body)
    elif snake_head[2] == "west":
        return south(snake_head, snake_body)
    elif snake_head[2] == "north":
        return west(snake_head, snake_body)
    elif snake_head[2] == "south":
        return east(snake_head, snake_body)


class Snake(Problem):
    def __init__(self, initial, goal=None):
        super().__init__(initial, goal)

    def successor(self, state):
        # ((head_x,head_y,head_dir), ((back1_x,back1_x),...), ((green1_x,green1_y),...))
        successors = dict()

        oldestPart = state[1][-1]
        snake_x, snake_y = state[0][0], state[0][1]
        green_apples = state[2]

        new_head, new_body = ProdolzhiPravo(list(state[0]), list(state[1]))
        if [new_head[0], new_head[1]] != [snake_x, snake_y]:
            food_len = len(green_apples)
            new_food_state = tuple([f for f in green_apples if (f[0], f[1]) != (new_head[0], new_head[1])])
            if food_len != len(new_food_state):
                new_body = list(new_body)
                new_body.append(oldestPart)
            new_body = tuple(new_body)
            successors["ProdolzhiPravo"] = (tuple(new_head), tuple(new_body), new_food_state)

        new_head, new_body = SvrtiDesno(list(state[0]), list(state[1]))
        if [new_head[0], new_head[1]] != [snake_x, snake_y]:
            food_len = len(green_apples)
            new_food_state = tuple([f for f in green_apples if (f[0], f[1]) != (new_head[0], new_head[1])])
            if food_len != len(new_food_state):
                new_body = list(new_body)
                new_body.append(oldestPart)
            new_body = tuple(new_body)
            successors["SvrtiDesno"] = (tuple(new_head), tuple(new_body), new_food_state)

        new_head, new_body = SvrtiLevo(list(state[0]), list(state[1]))
        if [new_head[0], new_head[1]] != [snake_x, snake_y]:
            food_len = len(green_apples)
            new_food_state = tuple([f for f in green_apples if (f[0], f[1]) != (new_head[0], new_head[1])])
            if food_len != len(new_food_state):
                new_body = list(new_body)
                new_body.append(oldestPart)
            new_body = tuple(new_body)
            successors["SvrtiLevo"] = (tuple(new_head), tuple(new_body), new_food_state)

        return successors

    def actions(self, state):
        return self.successor(state).keys()

    def result(self, state, action):
        return self.successor(state)[action]

    def goal_test(self, state):
        return len(state[2]) == 0

    def h(self, node):
        state = node.state

        snake_x = state[0][0]
        snake_y = state[0][1]
        green_apples = state[2]
        if len(green_apples) > 0:
            euc = math.sqrt((snake_x - green_apples[0][0]) ** 2 + (snake_y - green_apples[0][1]) ** 2)
            mnh = (abs(snake_x - green_apples[0][0]) + abs(snake_y - green_apples[0][1]))
            cheb = max(abs(snake_x - green_apples[0][0]), abs(snake_y - green_apples[0][1]))
            value = mnh
            for apple_x, apple_y in green_apples:
                euc = math.sqrt((snake_x - apple_x) ** 2 + (snake_y - apple_y) ** 2)
                mnh = abs(snake_x - apple_x) + abs(snake_y - apple_y)
                cheb = max(abs(snake_x - apple_x), abs(snake_y - apple_y))
                value = max(mnh, value)

            return value
            #return len(green_apples)
        else:
            return 0


if __name__ == '__main__':
    green_num = int(input())
    green_apples = []
    for i in range(green_num):
        green_apple = input().split(",")
        green_apples.append((int(green_apple[0]), int(green_apple[1])))

    snakeHead = (0, 7, "south")
    snakeBody1 = (0, 8)
    snakeBody2 = (0, 9)

    snake = Snake((snakeHead, (snakeBody1, snakeBody2), tuple(green_apples)))
    result = astar_search(snake)

    print(result.solution())
