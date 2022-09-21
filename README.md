# mngcheck

Серверная часть построена на framework Django 3.2 с базой данных PostgreSQL на Python 3.8. Взаимодействие клиент-сервер по REST-API запросам.
В разработке сервиса задействован функционал Django REST framework.
<br>
Фронт сайта усилен JS вставками для удобства заполнения форм Django.
<p>
Клиентская, часть отвечающая за работу с кассовым оборудованием, представлена в проекте KKTAgent тоже разработан на Python 3.8. 
Для различных моделей оборудования разработана соответствующая работа с COM-объектами драйвера или обмен с API строннего сервера оборудования.
Конфигуратор KKTAgenta создан на языке С# для более простой установки и настройки клиентской службы на windows станциях. 
</p>
<p>
Работу проекта в действии можно оценить по ссылке 
https://kassbot.website/
</p>
<p>
Тестовый пользователь: test
<br>
Пароль: Test$1234
</p>

Развертывание на сервере реализуется через сервис DOKKU.
