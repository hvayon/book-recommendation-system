import re

from commands import *
from data import *
from preprocessing import process_tokens
from rules import *

likes = []
dislikes = []
filterEntity = FilterEntity()

debug = False

def _getAnswer():
    while True:
        answer = input().lower()
        if answer == "да":
            return True
        elif answer == "нет":
            return False
        cmd_yes_no_validation()


def isFound():
    cmd_was_found()
    return _getAnswer()


def isAdd():
    cmd_add_definition()
    return _getAnswer()

def isEnd():
    cmd_command_end()
    return _getAnswer()

def find_recommendation(likes, dislikes, filterEntity):
    result = get_recomendation(likes, dislikes, df)
    result = do_fliter(result, filterEntity)
    print_recommendation(result)

def print_recommendation(result):
    print("\n> Вам может понравиться:")
    print(result['Название'])
    print('\n')
    
def processDefinition(data):
     flag = 0
     for rule in RULE_ARR:
         regexp = re.compile(rule) # собираем правила
         match = regexp.match(data) # проверка совпадений
         if debug:
             print("match =", match)
         if match is not None:
             resDict = match.groupdict()

             if rule == NOT_SIMILAR_TO_BOOK or rule == I_DISLIKE_BOOK:
                 dislikes.append(resDict["similar_name"].capitalize())
             elif rule == SIMILAR_TO_BOOK or rule == I_LIKE_BOOK:
                 likes.append(resDict["similar_name"].capitalize())
             elif rule == LIKE_GENRE or rule == HELP_GENRE:
                 filterEntity.genre = resDict["genre"].capitalize()
             elif rule == SHOW_DURABILITY:
                 filterEntity.pages = resDict["durability"].capitalize()

             flag = 1
             break

     if flag == 0:
         cmd_missunderstanding()
     else:
         find_recommendation(likes, dislikes, filterEntity)


def dialog():
    #dictPrefer = initPrefer()

    while True:
        data = input()
        if (data == "Я ничего не знаю о книгах. Расскажи, какие жанры бывает?"):
                 print("> Существует множество жанров книг, но вот некоторые из наиболее распространенных:\n")
                 print("> Роман — длинное художественное произведение, в котором описывается история любви или другие человеческие отношения.")
                 print("> Детектив — жанр, в котором рассказывается о расследовании преступления.")
                 print("> Фантастика — жанр, в котором описываются вымышленные миры и события, часто с использованием научной фантастики.")
                 print("> Приключения — жанр, в котором описываются путешествия и приключения главных героев.")
                 print("> Исторический роман — жанр, в котором описывается история реальных людей или событий, произошедших в прошлом.")
                 break
        dataProcessed = process_tokens(data)
        processDefinition(dataProcessed)

        while True:
            if isFound():
                cmd_goodbye()
                return
            elif isAdd():
                break
            elif isEnd():
                return

def main():
    cmd_welcome()
    dialog()
    
if __name__ == "__main__":
    main()