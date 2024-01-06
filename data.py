import pandas as pd
import numpy as np
from zss import simple_distance, Node

df = pd.read_csv('data/books.csv')

# получаем массив тэгов
tags = np.array(df['Тэги'])

# функция, которая создает дерево жанров
def create_node(extra_node, object):
    extra = object.split(', ')
    new_list = []
    for element in extra:
        if ',' in element:
            new_list.append(element.split(', '))
        else:
            new_list.append(element)
    for item in new_list:
        if type(item) == list:
            next_node = Node(item[0])
            for i in range(1, len(item)):
                next_node.addkid(Node(item[i]))
            extra_node.addkid(next_node)
        else:
            extra_node.addkid(Node(item))
            
# Древесная мера близости по основному жанру
objects = tags
matrix_tree_main = np.zeros((objects.shape[0], objects.shape[0]))
for i in range(objects.shape[0]):
    for j in range(objects.shape[0]):
        main_tags_node_1 = Node("Основной")
        create_node(main_tags_node_1, objects[i])
        main_tags_node_2 = Node("Основной")
        create_node(main_tags_node_2, objects[j])
        matrix_tree_main[i, j] = simple_distance(main_tags_node_1, main_tags_node_2)
        
class YoungAdultLiterature:
    def __init__(self, name, par) -> None:
        self.name = name
        self.par = par
        self.children = []
        if par is not None:
            par.children.append(self)

bookRoot = YoungAdultLiterature('Юношесткая литература', None)
bookRoman = YoungAdultLiterature('Роман', bookRoot)
bookFantasy = YoungAdultLiterature('Фэнтези', bookRoot)
bookRomanLove = YoungAdultLiterature('Любовный роман', bookRoman)
bookRomanTriller = YoungAdultLiterature('Роман-триллер', bookRoman)
bookRomanFantasy = YoungAdultLiterature('Фантастический роман', bookRoman)
bookFantasyRoman = YoungAdultLiterature('Романтическое фэнтези', bookFantasy)

books = {
    'Юнашесткая литература': bookRoot,
    'Роман': bookRoman,
    'Фэнтези': bookFantasy,
    'Любовный роман': bookRomanLove,
    'Роман-триллер': bookRomanTriller,
	'Фантастический роман': bookRomanFantasy,
    'Романтическое фэнтези': bookFantasyRoman
}

# дерево
def metricTree(a, b):
    c1, c2 = books[a], books[b]

    if c1.name == c2.name:
        return 0

    anc1 = {}
    cur = c1
    cntr = 0
    while cur is not None:
        anc1[cur.name] = cntr
        cntr += 1
        cur = cur.par

    cur = c2
    cntr = 0
    while cur.name not in anc1.keys():
        cntr += 1
        cur = cur.par
        if cur is None:
            raise

    return (cntr + anc1[cur.name]) / 4.0

objects = np.array(df['Жанр'])
matrix_elem_kat = np.zeros((objects.shape[0], objects.shape[0]))
for i in range(objects.shape[0]):
    for j in range(objects.shape[0]):
        matrix_elem_kat[i, j] = metricTree(objects[i],objects[j])

# Функция для расчета евклидовой меры близости между объектами по количеству страниц
def similarity_measure(obj1, obj2):
    return np.linalg.norm(obj1 - obj2)

# получаем массив объектов по количеству страниц
objects = np.array(df['Количество страниц'])
matrix_evklid_time = np.zeros((objects.shape[0], objects.shape[0]))

# Расчет значений меры для каждой пары объектов
for i in range(objects.shape[0]):
    for j in range(objects.shape[0]):
        matrix_evklid_time[i, j] = similarity_measure(objects[i], objects[j])
        
# получаем массив объектов по году публикации
objects = np.array(df['Год первоначальной публикации'])
matrix_evklid_temp = np.zeros((objects.shape[0], objects.shape[0]))


# Расчет значений меры для каждой пары объектов
for i in range(objects.shape[0]):
    for j in range(objects.shape[0]):
        matrix_evklid_temp[i, j] = similarity_measure(objects[i], objects[j])

# Функция для расчета меры близости по коэффициенту Жаккара
def jaccard_similarity_measure(obj1, obj2):
    intersection = np.sum(np.logical_and(obj1, obj2))
    union = np.sum(np.logical_or(obj1, obj2))
    if intersection == 0 and union == 0:
        return 1
    else:
        return (intersection / union)

# получаем массив объектов по признаку бинарная ассоциативная
objects = np.array(df['Прочитана'].replace(to_replace=['False', 'True'], value=['0', '1'])).astype(int)
matrix_binary = np.zeros((objects.shape[0], objects.shape[0]))
for i in range(objects.shape[0]):
    for j in range(objects.shape[0]):
        matrix_binary[i, j] = jaccard_similarity_measure(objects[i], objects[j])

recomender_matrix = matrix_tree_main + matrix_elem_kat + matrix_evklid_temp * 0.01 + matrix_evklid_time * 0.01 + matrix_binary * 2

# рекомендация

def get_recomendation(likes, dislikes, data):
    def find(name):
        return data.loc[data['Название'] == name]

    recomendation = [0.5 for i in range(len(data))]
    for i in likes:
        book_i = find(i).index[0]
        recomendation[book_i] = None
        for j in range(len(recomender_matrix[book_i])):
            if recomendation[j] is None:
                continue

            recomendation[j] -= recomender_matrix[book_i][j] / len(likes) * 0.5

    for i in dislikes:
        book_i = find(i).index[0]
        recomendation[book_i] = None
        for j in range(len(recomender_matrix[book_i])):
            if recomendation[j] is None:
                continue

            recomendation[j] += recomender_matrix[book_i][j] / len(dislikes) * 0.5

    result = data
    result['Рекомендация'] = recomendation
    result = result.sort_values(by=['Рекомендация'], ascending=False)
	
    return result

def do_fliter(recomendation, filterEntity):

    term_to_pages = {
        'Очень маленький': lambda x: int(x) <= 50,
        'Маленький': lambda x: 50 < int(x) <= 200,
        'Средний': lambda x: 200 < int(x) <= 300,
        'Большой': lambda x: 300 < int(x) <= 500,
        'Очень большой': lambda x: int(x) > 1000,
    }

    if filterEntity.name is not None:
        recomendation = recomendation[recomendation['Название'].apply(lambda x: x.find(filterEntity.name) != -1)]

    if filterEntity.author is not None:
        recomendation = recomendation[recomendation['Автор'].apply(lambda x: x == filterEntity.author)]

    if filterEntity.year is not None:
        recomendation = recomendation[recomendation['Год первоначальной публикации'].apply(lambda x: x == filterEntity.year)]
        
    if filterEntity.pages is not None:
        recomendation = recomendation[recomendation['Количество страниц'].apply(term_to_pages[filterEntity.pages])]

    if filterEntity.was_read is not None:
        recomendation = recomendation[recomendation['Прочитана'].apply(lambda x: x == filterEntity.was_read)]

    if filterEntity.temp[0] is not None and filterEntity.temp[1] is not None:
        recomendation = recomendation[
            recomendation['Год первоначальной публикации'].apply(lambda x: filterEntity.temp[0] < int(x) <= filterEntity.temp[1])]

    if filterEntity.genre is not None:
         recomendation = recomendation[recomendation['Жанр'].apply(lambda x: x == filterEntity.genre)]
        
    if filterEntity.tags is not None:
        recomendation = recomendation[recomendation['Тэги'].apply(lambda x: x.find(filterEntity.name) != -1)]

    return recomendation

class FilterEntity:
    name=None
    author=None
    year=None
    pages=None
    was_read=None
    temp=[None, None]
    genre=None
    tags=None