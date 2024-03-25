import re
import time
from time import sleep
import requests
from imap_tools import MailBox, A


class Data:

    activate_linc = None
    imap_url = 'imap.gmail.com'
    email = 'alexandr@gmail.com'
    email_password = 'qqq qqq qqq qqq'
    password = 'password'
    key_in_header_email = 'api.service.com'
    wite_timeout = 90


    @staticmethod
    def reqular_findall(text, before_text, after_text):
        """Регулярное выражение, возвращает список элементов между двумя отрезками строк

            :param text: (str), исходный текст
            :param before_text: (str), фрагмент строки "до" искомого элемента
            :param after_text: (str), фрагмент строки "после" искомого элемента
            """
        return re.findall(fr'{before_text}(.*?){after_text}', text)


    def check_mail_and_activation(self,  check_frequency = 1):

        def deleting_mail_with_header_key(self, mesage = 'Письмо удалено'):
            email_name = self.email
            email_password = self.email_password

            with MailBox(self.imap_url).login(email_name, email_password) as mailbox:
                responce = mailbox.delete(
                    [msg.uid for msg in mailbox.fetch() if self.key_in_header_email in msg.html])
                if responce is not None:
                    status =  str(responce)
                    status = status.replace(')', '').split()[4]
                    print(f'\n{mesage}, статус:', status)
                    sleep(2)
                    return status

                else:
                    print('Старых писем для удаления нет\n')


        def check_mail(self):
            """Проверка получения письма по части названия и получение ссылки активации"""
            email_name = self.email
            email_password = self.email_password

            with MailBox(self.imap_url).login(email_name, email_password) as mailbox:
                for msg in mailbox.fetch(A(subject=self.key_in_header_email, seen=False, flagged=False), limit=1,
                                         reverse=True):
                    text = msg.text
                    text_without_spaces = re.sub(r"\s+", "", text)
                    self.activate_linc = self.reqular_findall(
                        text_without_spaces,
                        before_text='activateaccount:',
                        after_text='Thanks')[0]

        def wite_email_and_activation(self):
            """Ожидание письма по таймауту, и переход по ссылке активации"""
            start_time = time.time()

            while (time.time() - start_time) < self.wite_timeout:
                if self.activate_linc is None:
                    print('Ожидание письма | status:', self.activate_linc, time.strftime('%H:%M:%S'))
                    check_mail(self)
                    sleep(check_frequency)

                if self.activate_linc is None:
                    assert self.activate_linc == 'None', 'Ожидание письма завершено, ссылки на активацию нет'

                else:
                    print('Письмо пришло | status: OK', time.strftime('%H:%M:%S'))
                    print()
                    print('GET from:', self.activate_linc)
                    responce = requests.get(self.activate_linc)
                    print(f'Статус код активации E-mail по ссылке: {responce.status_code}')
                    assert responce.status_code == 200, 'Нет активации по ссылке'
                    break




        deleting_mail_with_header_key(self, 'Старые письма удалены')# Удаление старых писем, если будут
        wite_email_and_activation(self)
        deleting_mail_with_header_key(self, 'Письмо с сылкой активации удалено') # Удаление нового письма

