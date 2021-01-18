# coding: utf8
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import os, time, winreg, re, random, math, datetime, calendar, logging, pprint, winsound, keyboard, pandas as pd, sys
import traceback


global brauzer, var, Current_phone, last_element_html

def sleep_or_press_keyboard(seconds=10, wait_press_keyboard=None) -> bool:
    # пауза seconds секунд, прерывается нажатием клавиши

    print(f'Ожидание {seconds} секунд ', end= '')
    if wait_press_keyboard == None:
        wait_press_keyboard = {'esc':'прервать ожидание'}

    wait_press_keyboard['p']=' - пауза'
    pause_active = False


    for key in wait_press_keyboard:
        print(f'  {key} {wait_press_keyboard[key]}', end= '')
    print('') # на новую строку

    end_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    while ((left:=(end_time - datetime.datetime.now()).seconds) > 0) or pause_active: # datetime.timedelta(0)
        if pause_active:
            if keyboard.is_pressed('c'):
                end_time = datetime.datetime.now() + datetime.timedelta(seconds=left_after_pause)
                print(' конец паузы')
                pause_active = False
        else:
            for key in wait_press_keyboard:
                if keyboard.is_pressed(key):
                    if key == 'p':
                        left_after_pause = left
                        print(' пауза, c - прордолжить')
                        time.sleep(1)
                        pause_active = True
                        break
                    else:
                        print('')
                        log(f'Ожидания прервано {key}')
                        return key # возвращаем нажатую клавишу
        time.sleep(0.5)
        if not pause_active:
            print(f'\b\b\b\b{left}', end= '')

    print(f'\b\b\b\b', end='')
    return False

def log_start(file=__file__):
    logging.basicConfig(filename= file + ".log", format=u'%(asctime)s;  %(message)s',level=logging.INFO)
    log("----------------------------------------------------------")
    log("Program started. Python version " + sys.version.split(' ')[0])


def log(text): # no_new_line - без новой строки  , ОтправитьВТелеграмм = False
    new_line = ' '  #if no_new_line else '\n'
    print('%s : %s' %(time.strftime("%Y-%m-%d %H.%M.%S", time.localtime()), text), new_line)
    # if ОтправитьВТелеграмм:
    #     send_message_to_telegram(text)
    try:
        logging.info(text)
    except:
        a=1
    return ''

def wait_elements_xpath(xpath_elements, count_try_wait_max=60, find1=True, del_spec_char_from_text=True, true_if_exist_data=False):
    global last_element_html, xpath_last_element_html, xpath_last_element_text
    elements = {}
    for el in xpath_elements.split(';'):
        elements.update({el: False})
    #xpath_last_element_html = ''
    # поиск элементов на странице, пример elements = {'input[@id="S485857639177A485861480317"]':False}
    # find1 - поиск хотябы одного элемента это успех
    count_try_wait, count_find, xpath_last_element_text, count_el = 0, 0, '', len(elements)
    while (count_try_wait < count_try_wait_max):
        count_try_wait += 1

        for key_element in elements:
            if not elements[key_element]:
                if count_try_wait == count_try_wait_max:
                    begin_log = ("Поиск %s" % key_element) if count_el != 1 or count_try_wait == 1 else ''
                    begin_log += " попытка " + str(count_try_wait) + ' из ' + str(count_try_wait_max)
                    log(begin_log)
                elements[key_element]=False
                try:
                    elements[key_element]=brauzer.find_element_by_xpath(key_element)
                    xpath_last_element_text = elements[key_element].text
                    if del_spec_char_from_text:
                        xpath_last_element_text = re.sub(r'[^\x00-\x7f]', '', xpath_last_element_text)
                    if count_try_wait == count_try_wait_max:
                        log(' - найден, .text=' + xpath_last_element_text)
                    if xpath_last_element_text == ''  and true_if_exist_data:
                        log('Найденный тэг пустой, он считается как не найденный. Пауза 3 сек.')
                        elements[key_element] = False
                        time.sleep(3)
                    elif xpath_last_element_text != 'Недоступно' :
                        if find1 or (count_find==len(elements)):
                            last_element_html=elements[key_element]
                            xpath_last_element_html = key_element
                            return elements
                        count_find += 1
                except:
                    elements[key_element] = False
                    if count_try_wait == count_try_wait_max:
                        log(' - не найден!')
            else:
                log('elements[key_element] - истина')
        time.sleep(1)
        # if count_try_wait == 20:
        #     winsound.MessageBeep()

    return False

def Not_exist_Xpath(seek_xpath, wait_sec=10): # ожидает исчезновение seek_xpath
    if seek_xpath[0:2]!='//' and seek_xpath[0:1]!='(':
        seek_xpath = XPATH[seek_xpath]

    while wait_sec > 0:
        wait_sec -= 1
        if not isXpath(seek_xpath):
            # log (f'{seek_xpath} исчез')
            return True
        # log (f'{seek_xpath} есть')
        time.sleep(1)
    return False

def isXpath(xpath_): # проверяет наличие xpath_ на странице
    global last_element_html, xpath_last_element_html, xpath_last_element_text
    try:
        last_element_html = brauzer.find_element_by_xpath(xpath_)
        xpath_last_element_html=xpath_
        xpath_last_element_text = last_element_html.text
        return last_element_html
    except:
        last_element_html = None
        return False

def get_url(url_open):
    global brauzer
    count_try_wait, max_count_try_wait = 1, 3
    while count_try_wait <= max_count_try_wait:
        try:
            brauzer.get(url_open) # иногда ошибка
            if count_try_wait > 1:
                log('Успешное открытие %s попытка %d' % (url_open, count_try_wait))
            return True
        except:
            log(f'Ошибка открытия {url_open} попытка {count_try_wait} из {max_count_try_wait}')
            time.sleep(2)
            count_try_wait+=1
    return False

def Close_ather_programm()->None:
    os.system('chcp 65001>nul') # переключение кодировки консоли
    for process_for_kill in {'geckodriver.exe','firefox.exe'}:
        os.system(f"TASKKILL /F /IM {process_for_kill}")
    time.sleep(2)

def init_branch_reestr(name_branch=os.path.basename(__file__)): # запустить один раз перед использованием init_branch_reestr('SkorPay')
    global branch_reestr_config
    # if not ('branch_reestr_config' in globals()):
    try:
        branch_reestr_config = winreg.OpenKey(winreg.HKEY_CURRENT_USER, name_branch, winreg.KEY_READ | winreg.KEY_WRITE)
    except:
        branch_reestr_config = winreg.CreateKey(winreg.HKEY_CURRENT_USER, name_branch)


def get_value_by_key_reestr(key_reestr, value_default=False, type_value=0):
    global branch_reestr_config
    try:
        value_key = winreg.QueryValueEx(branch_reestr_config, key_reestr)[0]
        if type_value == float:
            return float(value_key)
        elif isinstance(value_default, list):
            return eval(value_key)
        elif type(value_default) is dict:
            # return eval('{' + value_key + '}')
            return eval(value_key)
        elif type_value == str:
            return str(value_key)
        return value_key # тип int и др.
    except:
        return value_default

def save_value_to_reestr(key_reestr, value_to_save, type_value_in_reestr=winreg.REG_SZ):
    # winreg.REG_DWORD    # 32-bit number.
    # winreg.REG_QWORD    # A 64-bit number.
    global branch_reestr_config
    # if isinstance(value_to_save, list) and type_value_in_reestr==winreg.REG_SZ:
    #     value_to_save = ДвумерныйСписокВСтроку(value_to_save) # преобразуем в строку
    # el
    if type(value_to_save) is dict:
        value_to_save = str(value_to_save)
    winreg.SetValueEx(branch_reestr_config, key_reestr, 0, type_value_in_reestr, value_to_save)

def restart_browser(profile=False):
    global brauzer
    brauzer = None

    FirefoxProfile = webdriver.FirefoxProfile()
    if profile:
        if profile == True:
            profile = __file__+'.Profiles_Firefox'
        else:
            profile = f'{os.getcwd()}\\{profile}'
        if os.path.exists(profile):
            log(f'Профиль Firefox={profile}')
            FirefoxProfile = webdriver.FirefoxProfile(profile)     #  profile - имя файла профиля из папки (%APPDATA%\Mozilla\Firefox\Profiles\) C://Users//SkorPay//AppData//Roaming//Mozilla//Firefox//Profiles//, например 'etc7988t.default-release'
        else:
            log(f'Нет папки профиля Firefox {profile}') # (скопировать из папки %APPDATA%\Mozilla\Firefox\Profiles\)')
            return None


    # открытие браузера
    cap = DesiredCapabilities().FIREFOX
    cap["unexpectedAlertBehaviour"] = "accept"  # для автозакрытия алертов

    # настройки firefox about:config
    Firefox_Config = {
                      # "geo.enabled": False,  # отключение geo запроса
                      'browser.cache.disk.enable': False,
                      'browser.sessionhistory.max_total_viewer':0, # по умолчанию Мозилла кеширует в оперативной памяти 5 страниц открытых последними в текущей вкладке.
                      'browser.sessionhistory.max_entries':1, #Уменьшить число запоминаемым шагов, по умолчанию 50
                      'network.prefetch-next':False,# Отключение предварительной загрузки страниц
                      'dom.webnotifications.enabled': False, 'dom.push.enabled': False,  # отключение PUSH
                      'layout.css.devPixelsPerPx':'0.8', # масштаб строкой
                      # 'media.peerconnection.enabled':False, # Отключение WebRTC (реального ip)
                      'app.update.enabled': False # отключение авто обновления
                      }
    for key in Firefox_Config:
        FirefoxProfile.set_preference(key, Firefox_Config[key])
    # FirefoxProfile.setEnableNativeEvents(true);

    for _try in range(2):
        try:
            brauzer = webdriver.Firefox(firefox_profile=FirefoxProfile, capabilities=cap)
            return brauzer
        except Exception: # selenium.common.exceptions.WebDriverException
            log(f'Ошибка: {traceback.format_exc()}')
            # Close_brauzers(dict_Profile_FireFox)
    exit

def open_url(new_url, wait_element, max_count_try=4, update=False, error_xpath=False): # открытие страницы оплаты
    global current_bank, brauzer
    # log('Открытие %s c ожиданием элементов %s' %(new_url, wait_element))
    count_try_wait = 0
    # wait_elements = wait_element.split(';')
    while count_try_wait<max_count_try:
        count_try_wait += 1
        str_log = 'Открытие %s попытка %s из %d' %(new_url, count_try_wait, max_count_try)
        if update or brauzer.current_url[0:len(new_url)] != new_url or count_try_wait > 1: # иногда ошибка
            get_url(new_url)
        seconds_wait = min(count_try_wait * 5, 10)
        sleep_or_press_keyboard(seconds_wait)

        if wait_elements_xpath(wait_element):
            return True
        # for element in wait_elements:
        #     if isXpath(element):
        #         if count_try_wait > 1:
        #             log(str_log + ' %s - успешно!' %element)
        #         if error_xpath and isXpath(error_xpath):
        #             log(f'Найден {error_xpath} будет обновление страницы через {seconds_wait} сек.')
        #             time.sleep(seconds_wait)
        #             continue
        #         return True
        #     if count_try_wait > 1:
        #         log(str_log + ' %s - Не успешно!' % element)

        log(f'Ошибка открытия url={new_url} попытка {count_try_wait} из {max_count_try}')

    return False

def click(xpath_el=None, count_try_wait_max=10):
    global xpath_last_element_html
    if xpath_el != None:
        xpath_last_element_html = xpath_el
    count_try_wait=1
    while (count_try_wait <= count_try_wait_max):
        try:
            el = WebDriverWait(brauzer, 8).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath_last_element_html)))
            el.click()
            if count_try_wait>1:
                log (f'Успех click {xpath_last_element_html}')
            return True
        except Exception as err:
            log(f' {count_try_wait}/{count_try_wait_max} Ошибка click {xpath_last_element_html} {err}')
        count_try_wait += 1
        time.sleep(2)
    log(f' Не удалось click {xpath_last_element_html}')
    return False


def Press_Button(xpath_Button, sleep_after=0.3, wait_sec=2, try_max=3):
    global brauzer, url, XPATH, last_element_html
    if xpath_Button != '':
        if xpath_Button[0:2]!='//' and xpath_Button[0:1]!='(':
            xpath_Button = XPATH[xpath_Button]

        while wait_sec > 0:
            wait_sec -= 1
            if isXpath(xpath_Button):
                time.sleep(0.1)
                break
            time.sleep(1)
    for number_try in range(try_max):
        try:
            if number_try>0:
                last_element_html = WebDriverWait(brauzer, 8).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath_last_element_html)))
                # el_xp(xpath_last_element_html).click()
            # else:
            last_element_html.click()
            #    wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[@class='blockUI blockOverlay']"))) and then el_xp("//input[@value='Save']").click()
            #  WebDriverWait(brauzer, 8).until(last_element_html.invisibility_of_element_located((By.XPATH, xpath_last_element_html))) and then el_xp("//input[@value='Save']").click()

            if number_try > 0:
                log (f' {number_try+1}/{try_max} успех')

            if sleep_after:
                time.sleep(sleep_after)
            return True
        except Exception as err:
            log(f' {number_try+1}/{try_max} Ошибка click {xpath_Button} {err}')
            time.sleep(5)
    return False

def sleep(sec):
    time.sleep(sec)
    return True

def Past_Value(xpath_Value, val, sleep=0.3):
    if xpath_Value[0:2]!='//':
        xpath_Value = XPATH[xpath_Value]
    for i in range(3):
        try:
            last_element_html = brauzer.find_element_by_xpath(xpath_Value)
            old_value = last_element_html.get_attribute('value')
            if old_value == val:
                # log(f'Вставка значения {val} в {xpath_Value} не требуется.')
                return True
            if old_value != "":
                # last_element_html.clear()
                last_element_html.send_keys(Keys.BACKSPACE*len(old_value))
                time.sleep(0.1)
            last_element_html.send_keys(val)  # иногда ошибка
            # log(f'Вставка значения {val} в {xpath_Value} успешно!')
            time.sleep(sleep)
            return True
        except Exception as err:
            log(f' Ошибка при {xpath_Value} send_keys(Value): {err}')
        time.sleep(1)
    return False

def del_all_lots(max_lots_for_del_by_resource=2):
    global brauzer, url, XPATH, Current_phone
    log (f'Удаление всех лотов до {max_lots_for_del_by_resource} шт. по {Current_phone}.')
    if not open_url(url['url_Мои_лоты'], XPATH['Сформировать_лот_Начало']):
        log (f'Не удалось удалить лоты {Current_phone}')
        sleep(60)
        return False

    exist_dleted_lots = False
    max_lots_for_del_by_resource = max_lots_for_del_by_resource//2
    for Resource_for_sale in ('Гб', 'минуты'):
        number_lot_for_del = 1
        while number_lot_for_del <= max_lots_for_del_by_resource and not isXpath(XPATH['Текст_нет_активных_лотов']):
            number_lot_for_del +=1
            # посменно удаляются лоты интеренет и минут
            if not isXpath(XPATH['Удаление_лота_количество_' + Resource_for_sale]):
                break
            count_for_del = str_to_int(xpath_last_element_text)
            if count_for_del > 0 and sleep(0.5) and Press_Button(XPATH['Удаление_лота_начало_' + Resource_for_sale], 1, 9) and Press_Button('Редактирования_лота_Отозвать', 1) \
                    and Press_Button('Редактирования_лота_Отозвать_Подтверждение') and Not_exist_Xpath('Кнопка_закрытия_окна'):
                # and isXpath(XPATH['Редактирования_лота_Отозвать_Подтверждение']) and sleep(0.5)

                var["Телефоны"][Current_phone][f'Остатки_{Resource_for_sale}'] += count_for_del
                log(f'Конец удаления {number_lot_for_del} лота {count_for_del} {Resource_for_sale} новый остаток {var["Телефоны"][Current_phone][f"Остатки_{Resource_for_sale}"]}')
                exist_dleted_lots = True
            else:
                log(f'Ошибка удаления лота {count_for_del} {Resource_for_sale}, будут обновлены остатки.')
                var["Телефоны"][Current_phone]['ОбновитьОстатки']=True
                if not open_url(url['url_Мои_лоты'], XPATH['Сформировать_лот_Начало']):
                    sleep(3)
                    return False
                break

        if xpath_last_element_html == XPATH['Текст_нет_активных_лотов']:
            log (f'Нет_активных_лотов {Current_phone}')
            save_value_to_reestr(Current_phone+'_Выставленное_количествo_Гб', 0, winreg.REG_DWORD)
            save_value_to_reestr(Current_phone+'_Выставленное_количествo_минуты', 0, winreg.REG_DWORD)
            var["Телефоны"][Current_phone]['Выставлно_Гб']=var["Телефоны"][Current_phone]['Выставлно_минуты']=0
            break

    return exist_dleted_lots

def str_to_int(str)->int: #строка в число
    match = re.search(r'\d+', str)
    return int(match[0]) if match else 0

def Получить_доступные_остатки(): # чтение остатков Гб и Минут
    global var, Current_phone, xpath_last_element_text

    if not open_url(url['url_lk'], XPATH['Остатки_lk_минуты']+';'+XPATH['Остатки_lk_Гб']+';//h2[text()="Доступно"]'):
        return False

    time.sleep(1)

    is_read_resource = False
    for Resource_for_sale in ['минуты', 'Гб']:
        key_остатки = f'Остатки_{Resource_for_sale}'
        if isXpath(XPATH[f'Остатки_lk_{Resource_for_sale}']):
            var["Телефоны"][Current_phone][key_остатки]= str_to_int(xpath_last_element_text.replace(' ', ''))
            is_read_resource = True
        else:
            if Resource_for_sale == 'Гб' and isXpath('//a[contains(text(),"Подключить пакет интернета")]'):
                is_read_resource = True
            var["Телефоны"][Current_phone].update({key_остатки:0})

    if is_read_resource:
        var["Телефоны"][Current_phone]['ОбновитьОстатки']=False

    log(f'Остатки {Current_phone} {var["Телефоны"][Current_phone]["Остатки_Гб"]} Гб {var["Телефоны"][Current_phone]["Остатки_минуты"]} Мин. Не продавать {var["Телефоны"][Current_phone]["Оставлять_Гб"]} Гб {var["Телефоны"][Current_phone]["Оставлять_минуты"]} Мин.' )
    return is_read_resource

def sell_lots(Resource_for_sale)->int:
    """
    Выставление лотов на продажу по ресурсу Resource_for_sale
    перед открытием уже должна быть открыта страница https://yar.tele2.ru/stock-exchange/my
    """

    global Current_phone, brauzer, var, _today
    ОставлятьРесурса = var["Телефоны"][Current_phone].get('Оставлять_'+Resource_for_sale, -1)
    if ОставлятьРесурса == -1:
        # log (f'Ресурс {Resource_for_sale} {Current_phone} не продается.')
        return 0
    Остатки_Ресурса = var["Телефоны"][Current_phone]['Остатки_'+Resource_for_sale]
    if ОставлятьРесурса >= Остатки_Ресурса:
        # log (f'Ресурс {Resource_for_sale} {Current_phone} не продается т к оставляется {ОставлятьРесурса} а остаток ресурса {Остатки_Ресурса}')
        return 0
    Остатки_Ресурса -= ОставлятьРесурса
    if Остатки_Ресурса < var['Min_count_for_sale_'+Resource_for_sale]:
        log (f'Пакет для продажи {Resource_for_sale} {Остатки_Ресурса} меньше минимального лота {var["Min_count_for_sale_"+Resource_for_sale]}')
        return 0

    if brauzer.current_url != url['url_Мои_лоты'] and not open_url(url['url_'+Resource_for_sale], XPATH['Сформировать_лот_Начало'], 2):
        sleep_or_press_keyboard(600) # time.sleep(600)
        return 0

    var["Телефоны"][Current_phone]['Выставлно_'+Resource_for_sale]=get_value_by_key_reestr(Current_phone+'_Выставленное_количествo_'+Resource_for_sale, 0, int)
    Подписаться = var["Телефоны"][Current_phone]['Подписаться']
    while  1:
        макс_количествo = Остатки_Ресурса-var["Телефоны"][Current_phone]['Выставлно_'+Resource_for_sale]
        if макс_количествo < var['Min_count_for_sale_'+Resource_for_sale]:
            log (f'Выставлено максимальное количество лотов по {Resource_for_sale}. Не продажный остаток {ОставлятьРесурса} {Resource_for_sale}')
            return True

        количество_для_продажи = random.randint(var['Min_count_for_sale_'+Resource_for_sale], var['Min_count_for_sale_'+Resource_for_sale] + var['Максимальное_увеличение_количества_на_продажу'])
        сумма_продажи = str(math.ceil(var['Стоимость_1_ед_'+Resource_for_sale]*количество_для_продажи))

        if Press_Button('Сформировать_лот_Начало', 1) \
                and (brauzer.current_url == url['url_'+Resource_for_sale] or (Press_Button('Выбор_типа_лота_'+Resource_for_sale) and Press_Button('Кнопка_Продолжить'))) \
                and Press_Button('Подготовка_к_вводу_количества', 1, 3) \
                and Past_Value('Сформировать_лот_Поле_количествo_'+Resource_for_sale, str(количество_для_продажи)) \
                and Press_Button('Подготовка_к_вводу_Суммы') \
                and Past_Value('Сформировать_лот_Поле_Сумма', сумма_продажи)  \
                and Press_Button('Кнопка_Продолжить', 3) \
                and ((not Подписаться) or Press_Button('Подписаться_как', sleep_after=0.1))\
                and Press_Button('Кнопка_Продолжить', sleep_after=1):
            # and Press_Button('Сформировать_лот_Smile2') and Press_Button('Сформировать_лот_Smile2')
            # and Press_Button('Сформировать_лот_Smile2', 0.5, 60)

            log (f'Выставлен лот {Resource_for_sale} {количество_для_продажи} осталось {макс_количествo-количество_для_продажи}')
            var["Телефоны"][Current_phone]['Выставлно_'+Resource_for_sale] += количество_для_продажи
            var["Всего_на_продажу_"+Resource_for_sale] += количество_для_продажи

            save_value_to_reestr(Current_phone+'_Выставленное_количествo_'+Resource_for_sale, var["Телефоны"][Current_phone]['Выставлно_'+Resource_for_sale], winreg.REG_DWORD)
            var["Телефоны"][Current_phone][f'Остатки_{Resource_for_sale}'] -= количество_для_продажи

            # сохранение кол-ва выставленных лотов в день
            key_reestr = _today+'_Выставлено_лотов'
            save_value_to_reestr(key_reestr, get_value_by_key_reestr(key_reestr, 0, int) + 1, winreg.REG_DWORD)
            key_reestr = Current_phone + key_reestr
            save_value_to_reestr(key_reestr, get_value_by_key_reestr(key_reestr, 0, int) + 1, winreg.REG_DWORD)
        else:
            log (f'Ошибка выставления лота {Resource_for_sale}')
            var["Телефоны"][Current_phone]['ОбновитьОстатки']=True
            return -1

def Подарить_ресурс_Гб():
    global Current_phone
    while len(var["Кому_дарить_Гб"])>0:
        КомуДарить = var["Кому_дарить_Гб"].pop()
        a = var["Телефоны"][Current_phone]["Остатки_Гб"]>=1 and Press_Button('Подарить_Гб_шаг1', 1)
        a = Past_Value('Подарить_Гб_ввод_телефона_получателя', КомуДарить, 1)
        a = Press_Button('Кнопка_Продолжить', 1)
        a = Press_Button('Кнопка_Подтвердить', 1)
        a = Press_Button('Кнопка_закрытия_окна', 1)

        if a:
            log('Удачное дарение 1 ГБ от {Current_phone} to {КомуДарить}.')
        else:
            break
def ВремяДоНачалаТоргов(ТекЧас, ЧасНачалаТорогв, ЧасКонцаТоргов):
    if ЧасНачалаТорогв <= ЧасКонцаТоргов:
        # print(f'ТекЧас={ТекЧас}')
        # торговля внутри одного дня, например с 6 до 23
        if ЧасНачалаТорогв <= ТекЧас < ЧасКонцаТоргов:
            return 0
        else:
            if ЧасКонцаТоргов <= ТекЧас:
                # тек время от ЧасКонцаТоргов до 24 часов
                return 24 + ЧасНачалаТорогв - ТекЧас
            else:
                return ЧасНачалаТорогв - ТекЧас
    else:
        # не торговое внутри внутри дня, например торговля с 6 до 1
        # print(f'ТекЧас = {ТекЧас}')
        if ЧасКонцаТоргов < ТекЧас < ЧасНачалаТорогв:
            return ЧасНачалаТорогв - ТекЧас
        else:
            return 0


def dict_phones_to_csv(name_csv_phones_cfg = 'phones_cfg.csv'):  # конвертирование словаря в pandas
    dict_for_save = var["Телефоны"]

    # no_save_colu = ['brauzer','Profile_FireFox','Остатки_минуты	Остатки_Гб','Выставлно_Гб','Выставлно_минуты']
    columns = ['Приоритет','Баланс','Баланс_дата','Абонплата','ПродаватьС','Активная_симка','Name','Оставлять_минуты','Оставлять_Гб','День_обновления_остатков','Описание','ЛС','Телефон_ЛК','ПродаватьДоБаланса','ЧасКонцаТорговли','ЧасНачалаТорговли','Подписаться','Остатки_минуты','Остатки_Гб','Выставлно_Гб','Выставлно_минуты']
               #list(dict_for_save['9535248000'].keys()) - no_save_columns

    data_phones = []
    for phone in dict_for_save:
        line_data = [phone]
        for key_data_phone in columns:
             line_data.append(dict_for_save[phone].get(key_data_phone, None))
        data_phones.append(line_data)
    columns.insert(0, 'Телефон')
    df = pd.DataFrame(data_phones, columns=columns)
    df.to_csv(name_csv_phones_cfg, index=False) # , sep=','

def Close_brauzers(dict_Profile_FireFox):
    log(f'Закрытие всех браузеров.')
    for Profile_FireFox, brauzer in dict_Profile_FireFox.items():
        try:
            brauzer.quit()
        except Exception as err:
            log(f'Ошибка при закрытии браузера {Profile_FireFox}! {err}')
        dict_Profile_FireFox[Profile_FireFox] = None

def to_str(var):
    return var

def to_bool(var):
    if type(var) != bool:
        return False
    return var

def to_int(var):
    if type(var) != int:
        return 0
    return var

def to_float(var):
    if type(var) != float:
        return 0
    return var

def load_cfg2():
    pass

def load_cfg(name_csv_phones_cfg='phones_cfg.csv')->None:
    # имя файла с настройками по телефонам
    # try:
    print(f'Начало загрухки {name_csv_phones_cfg}')
    # exit(0)
    df = pd.read_csv(name_csv_phones_cfg,  # sep=',',
                     dtype={'Телефон': str},
                     converters={'ЛС': to_str, 'ПродаватьС': to_str, 'Телефон_ЛК': to_str, 'Баланс_дата': to_str,
                                 'Подписаться': to_bool, 'ЧасКонцаТорговли': to_str, 'ЧасНачалаТорговли': to_str,
                                 'ПродаватьДоБаланса': to_int, 'Баланс': to_float, 'Остатки_минуты': to_int,
                                 'Остатки_Гб': to_int, 'Выставлно_Гб': to_int, 'Выставлно_минуты': to_int})
    print(f'{name_csv_phones_cfg} строк {len(df)}')
    print(df.head(100).to_string())
    df = df.sort_values(by=['Активная_симка', 'Приоритет', 'Телефон'])  #
    # except Exception:
    #     log(f'Ошибка загрузки файла {name_csv_phones_cfg} Ошибка: {traceback.format_exc()}')
    #     exit(0)
    df.set_index('Телефон', inplace=True)  # переназначение индекса
    df = df.sort_values(by=['Приоритет', 'Name'])  # .reset_index(drop = True)

    var["Телефоны"] = df.to_dict('index')


# Начало программы -------------------------------------------------------------------------------------------------------------------------------
#             Смнетить тариф можно только звонком в Теле2 или USSD-командой: *630*(количество минут)*(количество ГБ)#
# Условия текущего тарифа - *107#
# для ЯО "Мой онлайн" 250 руб, 25 ГБ, 800 минут *630*800*25#
            
log_start()

var ={'Min_count_for_sale_Гб':5, 'Min_count_for_sale_минуты':50, 'Максимальное_увеличение_количества_на_продажу':0,
      'Стоимость_1_ед_Гб':15, 'Стоимость_1_ед_минуты':0.8, 'ЧасНачалаТорговли':4, 'ЧасКонцаТорговли':1,
       'Пауза_между_выставлений_лотов_сек':500,
      "Откуда_дарить_Гб":["9535248000", "9012998490"], 'Кому_дарить_Гб':[],
      }


init_branch_reestr() # загрузка настроек

if __name__ == '__main__':
    Close_ather_programm()
    # load_cfg2()
    load_cfg() # загрузка настроек

    XPATH={'xpath_phone':'//input[@id="keycloakAuth.phone"]', 'xpath_next_login' : '//button[contains(text(),"Далее")]', 'xpath_login_with_password' : '//button[text()="Вход по паролю"]',
          'Текст_нет_активных_лотов':'//div[contains(text(), "У вас нет активных лотов в продаже.")]',
           'Сформировать_лот_Начало':'//span/a[contains(text(), "Сформировать лот")]',
           'Подготовка_к_вводу_количества':'(//div[@class="lot-setup__manual-input"])[1]', 'Подготовка_к_вводу_Суммы':'//div[@class="lot-setup__manual-input"][last()]',
           'Сформировать_лот_Поле_количествo_Гб':'(//input)[1]', 'Сформировать_лот_Поле_Сумма':'(//input)[2]',
           'Сформировать_лот_Поле_количествo_минуты':'(//input)[1]', 'Сформировать_лот_Поле_Сумма':'(//input)[2]',
           'Кнопка_Продолжить':'//div/a[contains(text(), "Продолжить")]', 'Подписаться_как':'//label',
           'Сформировать_лот_Smile1':'(//div[@class="emoji-field__available-values-block"]/img)[1]', 'Сформировать_лот_Smile2':'(//div[@class="emoji-field__available-values-block"]/img)[2]',
           'Сформировать_лот_Smile3':'(//div[@class="emoji-field__available-values-block"]/img)[3]', 'Сформировать_лот_Smile4':'(//div[@class="emoji-field__available-values-block"]/img)[4]',
           'Сформировать_лот_Smile5':'(//div[@class="emoji-field__available-values-block"]/img)[5]', 'Сформировать_лот_Smile6':'(//div[@class="emoji-field__available-values-block"]/img)[4]',
           'Сформировать_лот_Smile7':'(//div[@class="emoji-field__available-values-block"]/img)[7]', 'Сформировать_лот_Smile8':'(//div[@class="emoji-field__available-values-block"]/img)[4]',
           'Удаление_лота_количество_Гб':'(//div[@class="my-lot-item__info_specs" and contains(text(), "ГБ за")])[last()]',
           'Удаление_лота_количество_минуты':'(//div[@class="my-lot-item__info_specs" and contains(text(), "минут за")])[last()]',
           'Удаление_лота_начало_минуты':'(//div[@class="my-lot-item__info_specs" and contains(text(), "минут за")])[last()]/../../div/a/i',
           'Удаление_лота_начало_Гб':'(//div[@class="my-lot-item__info_specs" and contains(text(), "ГБ за")])[last()]/../../div/a/i',
           # 'Нет_активных_лотов':'//div[@class="exchange-block__message" and text()="У вас нет активных лотов в продаже. Разместите новый лот."]',
           'Редактирования_лота_Отозвать': '//div/a[contains(text(), "Отозвать лот")]', 'Редактирования_лота_Отозвать_Подтверждение': '//span/a[contains(text(), "Отозвать лот")]',
           'Мой_Tele2':'//span[@class="ico icon-profile"]', #//span[contains(text(), "Мой Tele2")]
           'Мой_Tele2_номер':'//span[contains(text(), "Мой Tele2")]/span', 'icon-profile':'//span[@class="ico icon-profile"]',
           'Войти':'(//span[contains(text(),"Войти")])[1]',  #//span[contains(text(),"Войти")]
           'Остатки_НаАватаре_минуты':'(//div[@class="profile-popup_rest"]/span/span)[1]', 'Остатки_НаАватаре_Гб':'(//div[@class="profile-popup_rest"]/span/span)[2]',
           'Остатки_lk_минуты':'//span[@class="remnant calls"]', 'Остатки_lk_Гб':'//span[@class="remnant internet"]',
           'Выбор_типа_лота_Гб':'(//span[@class="radio-label"])[1]', 'Выбор_типа_лота_минуты':'(//span[@class="radio-label"])[2]',
           'Кнопка_закрытия_окна':'//a[contains(@class, "icon-close")]',
           'Баланс':'//span[@class="number"]', 'Абонплата':'//p[@class="abonent-date"]',
           'Подарить_Гб_шаг1':'//span[contains(text(), "Подарить интернет")]',
           'Подарить_Гб_ввод_телефона_получателя':'//input[@id="receiverNumber"]', 'Кнопка_Подтвердить':'//div/a[contains(text(), "Подтвердить")]',
           # <div>Превышение лимита на размещение лотов в день. Повторите попытку завтра.</div>   //div[contains(text(), "Превышение лимита на размещение лотов в день")]
           }
    url={'url_Мои_лоты':'https://yar.tele2.ru/stock-exchange/my',
         'url_Гб':'https://yar.tele2.ru/stock-exchange/internet', #Гб
         'url_минуты':'https://yar.tele2.ru/stock-exchange/calls',           # минуты
         'url_lk':'https://yar.tele2.ru/lk'
         }

    Список_ЛС = {}
    _today = str(datetime.datetime.today())[:10]
    phone_lk_default = '' # list(var["Телефоны"].keys())[0] Первый телефон - логин авторизации

    for Current_phone in var["Телефоны"].keys():
        ПродаватьС = get_value_by_key_reestr(Current_phone+'ПродаватьС', "", str)
        if ПродаватьС <= _today:
            ПродаватьС = ''
        var["Телефоны"][Current_phone]['ПродаватьС'] = ПродаватьС
        log(f'{Current_phone} {var["Телефоны"][Current_phone]["Name"]} ПродаватьС={ПродаватьС}')

        # заполняем 'ПочиненныеНомера'
        ЛС = var["Телефоны"][Current_phone].get('ЛС', '')
        if ЛС == '' or not (ЛС in var["Телефоны"]):
            var["Телефоны"][Current_phone][ЛС]=ЛС=Current_phone

        if not ('ПочиненныеНомера' in var["Телефоны"][ЛС]):
            var["Телефоны"][ЛС]['ПочиненныеНомера'] = [Current_phone]
        else:
            var["Телефоны"][ЛС]['ПочиненныеНомера'].append(Current_phone)
        Список_ЛС.update({ЛС:var["Телефоны"][ЛС]['ПочиненныеНомера']})

        var["Телефоны"][Current_phone]['ОбновитьОстатки'] = get_value_by_key_reestr(Current_phone + 'ОбновитьОстаткиС', "") <= _today
        if var["Телефоны"][Current_phone]['ЧасКонцаТорговли'] == '':
            var["Телефоны"][Current_phone]['ЧасКонцаТорговли'] = '24'
        var["Телефоны"][Current_phone]['brauzer'] = None
        phone_lk = var["Телефоны"][Current_phone]['Телефон_ЛК'] = var["Телефоны"][Current_phone]['Телефон_ЛК']
        if phone_lk != phone_lk_default or phone_lk_default == '':
            phone_lk_default = phone_lk # если не задан 'Телефон_ЛК' то возьмется последний 'Телефон_ЛК'
        var["Телефоны"][Current_phone]['Profile_FireFox'] = name_Profile_FireFox = phone_lk + '.' + 'Profile_FireFox' # имя профиля FireFox
        var[name_Profile_FireFox] = None # очищаем ссылку на selenium
        if var["Телефоны"][Current_phone].get("Баланс", None) == None:
            var["Телефоны"][Current_phone]["Баланс"]=0

    while True:
        count_phone_for_sale = var["Всего_на_продажу_Гб"] = var["Всего_на_продажу_минуты"] = 0

        _today = str(datetime.datetime.today())[:19]
        hour_trade = _today[11:13]
        _today = _today[:10]
        До_начала = ВремяДоНачалаТоргов(int(hour_trade), var['ЧасНачалаТорговли'], var['ЧасКонцаТорговли'])
        if До_начала >  0:
             print(f"До начала торгов {round(До_начала, 2)} часов. Начало {var['ЧасНачалаТорговли']} конец {var['ЧасКонцаТорговли']} часов.")
             if brauzer != None:
                 brauzer.quit()
                 brauzer = None
             sleep_or_press_keyboard(До_начала*3600)
             continue

        dict_Profile_FireFox = {} #профиль - ссылка на браузер
        for Current_phone in var["Телефоны"].keys():

            # запуск браузера по профилю
            Profile_FireFox = var["Телефоны"][Current_phone]['Profile_FireFox']
            brauzer = dict_Profile_FireFox.get(Profile_FireFox, None)
            if brauzer == None:
                dict_Profile_FireFox[Profile_FireFox] = restart_browser(Profile_FireFox)
                if brauzer == None:
                    log(f'Для {Current_phone} не удалось открыть браузер с профилем {os.getcwd()}\\{Profile_FireFox}')
                    sleep_or_press_keyboard(300, wait_press_keyboard = {'esc':'для досрочного продолжения'})
                    continue

            phone_enable, sell_with=var["Телефоны"][Current_phone]['Активная_симка'] , var["Телефоны"][Current_phone].get('ПродаватьС', '')
            log(f'Начало переключения на номер {Current_phone} {var["Телефоны"][Current_phone]["Name"]} {var["Телефоны"][Current_phone]["Баланс"]}р Активность:{phone_enable} использовать с: {sell_with} ОбновитьОстатки={var["Телефоны"][Current_phone]["ОбновитьОстатки"]}')
            phone_enable = (phone_enable and (_today >= sell_with))\
                         and var["Телефоны"][Current_phone]['ЧасНачалаТорговли'] <= hour_trade <= var["Телефоны"][Current_phone]['ЧасКонцаТорговли']
            ЕстьКомуДаритьГб = len(var["Кому_дарить_Гб"])>0 and Current_phone in var["Откуда_дарить_Гб"] and var["Телефоны"][Current_phone].get("Остатки_Гб", -1) != 0
            if  not phone_enable and not var["Телефоны"][Current_phone]['ОбновитьОстатки'] and not ЕстьКомуДаритьГб:
                continue

            if not open_url(url['url_lk'], XPATH['Войти']+';' + XPATH['xpath_phone'] + ';' + XPATH['Мой_Tele2'], 2):
                sleep_or_press_keyboard(600, {'c':' -  скопировать с про'})

                continue

            if xpath_last_element_html in [XPATH['Войти'], XPATH['xpath_phone']]:                 #  авторизация
                log(f'Телефон для авторизации {var["Телефоны"][Current_phone]["Телефон_ЛК"]}')
                if (isXpath(XPATH['xpath_phone']) or Press_Button('Войти', 1)) \
                        and Past_Value('xpath_phone', var["Телефоны"][Current_phone]["Телефон_ЛК"], 0.5) \
                        and Press_Button('xpath_next_login', 5):
                    #         and Press_Button('//button[text()="Вход по паролю"]', 1) \
                    #         and Past_Value('//input[@id="keycloakAuth.password"]', password, 0.5):

                    #         ожидание входа человеком
                    log ('Ожидание входа человеком')
                    while not isXpath(XPATH['Мой_Tele2']):
                        sleep_or_press_keyboard(20)

            phone_format = Current_phone[0:3]+' '+Current_phone[3:6]+' '+Current_phone[6:8]+' '+Current_phone[8:10]
            if isXpath(f'//button/h1[contains(text(),"{phone_format}")]'):
                log(f'Номер {Current_phone} уже выбран из списка.') #  управляемых номеров
            elif open_url(url['url_lk'], '//span[contains(@class, "dashboard-number__icon")]', 2, error_xpath='//div[@class="data-unavailable-message lk-new error-message"]') and click() and sleep(0.8)\
                and click(f'//li/button/h3[contains(text(),"{phone_format}")]/..', 10) and wait_elements_xpath(f'//button/h1[contains(text(),"{phone_format}")]', 30) and wait_elements_xpath(XPATH['Баланс'], 30):
                var["Телефоны"][Current_phone]['Баланс']=float(xpath_last_element_text.replace(' ', '').replace(',', '.')) #.replace('₽', '')
                var["Телефоны"][Current_phone]['Баланс_дата'] = _today
                log(f'Успешное переключение на номер {Current_phone} баланс {xpath_last_element_text} руб.')

                # обновление Абонплата
                if var["Телефоны"][Current_phone].get('Абонплата', 0) <= 0 and isXpath(XPATH['Абонплата']):
                    rez_match = re.search('(Абонентская плата )(.+)( ₽ будет списана )(\d+)', xpath_last_element_text)
                    if rez_match:
                        var["Телефоны"][Current_phone]['Абонплата'] = float(rez_match.group(2))
                        var["Телефоны"][Current_phone]['День_обновления_остатков'] = int(rez_match.group(4))

            else:
                log(f'Неудалось переключиться на номер {Current_phone}. Переход к следущему номеру черех 3 минуты.')
                sleep_or_press_keyboard(180)
                continue

            if isXpath(XPATH['Мой_Tele2_номер']):
                Current_phone2 = last_element_html.text.replace(' ', '')
                if Current_phone2 != Current_phone:
                    log(f'Не корректное переключение на {Current_phone} на экране ЛК {Current_phone2}')
                    winsound.MessageBeep()
                    sleep_or_press_keyboard(200)
                    continue


            #     Обновление остатков
            if var["Телефоны"][Current_phone]['ОбновитьОстатки']:
                if not Получить_доступные_остатки():
                    log(f'По {Current_phone} не получены остатки! Переход к следущему номеру.')
                    sleep_or_press_keyboard(20)
                    continue
            else:
                log(f'Остатки {Current_phone} без обновления: {var["Телефоны"][Current_phone]["Остатки_Гб"]} Гб {var["Телефоны"][Current_phone]["Остатки_минуты"]} минут')

            if ЕстьКомуДаритьГб:
                Подарить_ресурс_Гб()
            else:
                Resource = "Гб"
                Пополнить_ресурс_кол = var["Телефоны"][Current_phone].get("Поддерживать_"+Resource, 0)
                if 0 < Пополнить_ресурс_кол > var["Телефоны"][Current_phone]["Остатки_"+Resource]:
                    Пополнить_ресурс_кол = max(1, int(Пополнить_ресурс_кол - var["Телефоны"][Current_phone]["Остатки_"+Resource]))
                    log(f'Требуется пополнить {Resource} на {Пополнить_ресурс_кол}.')
                    if not Current_phone in var["Кому_дарить_Гб"]:
                        var["Кому_дарить_Гб"].append(Current_phone)

            if not phone_enable:
                time.sleep(1)
                continue

            del_all_lots(40)



            #  Проверка есть ли что продавать и обновление "ПродаватьС"
            if (0 < var["Телефоны"][Current_phone].get('ПродаватьДоБаланса', -1) < var["Телефоны"][Current_phone]['Баланс'])\
                or\
                    ((((var["Телефоны"][Current_phone]['Остатки_Гб']-var["Телефоны"][Current_phone]['Оставлять_Гб']) < var['Min_count_for_sale_Гб']) or (var["Телефоны"][Current_phone]['Оставлять_Гб'])==-1) \
                    and (((var["Телефоны"][Current_phone]['Остатки_минуты']-var["Телефоны"][Current_phone]['Оставлять_минуты']) < var['Min_count_for_sale_минуты']) or (var["Телефоны"][Current_phone]['Оставлять_минуты']==-1)) \
                    and var["Телефоны"][Current_phone].get('Выставлно_Гб', 0) == var["Телефоны"][Current_phone].get('Выставлно_минуты', 0)==0):

                if var["Телефоны"][Current_phone].get('День_обновления_остатков', 0) == 0:
                    log(f'Не задан день обновления баланса.')
                else:
                    Сегодня = datetime.datetime.now()
                    ДатаОбновленияБаланса = datetime.datetime(Сегодня.year, Сегодня.month, int(var["Телефоны"][Current_phone]['День_обновления_остатков']))
                    if ДатаОбновленияБаланса < Сегодня: # обновление будет в следующем месяце
                        days_in_month = calendar.monthrange(ДатаОбновленияБаланса.year, ДатаОбновленияБаланса.month)[1]
                        ДатаОбновленияБаланса += datetime.timedelta(days=days_in_month)

                    var["Телефоны"][Current_phone]['ПродаватьС'] = sell_with = str(ДатаОбновленияБаланса)[:10] #int(time.mktime(ДатаОбновленияБаланса.timetuple()))
                    save_value_to_reestr(Current_phone+'ПродаватьС', sell_with) # , winreg.REG_DWORD
                    log(f'Новая дата ПродаватьС для {Current_phone}: {sell_with}') #time.ctime(ПродаватьС) .strftime("%d.%m.%Y")

                log(f'Нет ресурсов для продажи. Переход к следущему номеру.\n')
                continue

            count_phone_for_sale +=1

            if sell_lots('Гб') < 0:
                # переоткрываем страницу, чтобы скрыть открытые окна
                open_url(url['url_Мои_лоты'], XPATH['Сформировать_лот_Начало'])

            sell_lots('минуты')
            dict_phones_to_csv()
            time.sleep(2)

        log('Итоги:')
        pprint.pprint(var["Телефоны"])
        dict_phones_to_csv()

        log(f'Всего выставлено на продажу {var["Всего_на_продажу_минуты"]*var["Стоимость_1_ед_минуты"] + var["Всего_на_продажу_Гб"]*var["Стоимость_1_ед_Гб"]} руб. {var["Всего_на_продажу_минуты"]} минут {var["Всего_на_продажу_Гб"]} Гб')

        log('Проверка достаточности денег для абонплаты:')
        sell_with = ''
        for ЛС in Список_ЛС.keys():
            var["Телефоны"][ЛС]['Абонплата_ЛС'] = 0
            for Current_phone in var["Телефоны"][ЛС]['ПочиненныеНомера']:
                sell_with = min(sell_with, var["Телефоны"][Current_phone].get('ПродаватьС', ''))
                var["Телефоны"][ЛС]['Абонплата_ЛС'] += abs(var["Телефоны"][Current_phone].get('Абонплата', 0))
            text = f'ЛС {ЛС} {var["Телефоны"][ЛС]["Name"]} общий баланс: {var["Телефоны"][ЛС]["Баланс"]} общая абонплата: {var["Телефоны"][ЛС]["Абонплата_ЛС"]} подчиненные {var["Телефоны"][ЛС]["ПочиненныеНомера"]}'
            ИзлишекБаланса = var["Телефоны"][ЛС]['Абонплата_ЛС'] - var["Телефоны"][ЛС]["Баланс"]
            if  0 < ИзлишекБаланса:
                text = f'!!!! Недостаточно {int(abs(ИзлишекБаланса))} для ' +  text
            log(text)

        if count_phone_for_sale==0 and sell_with > str(datetime.datetime.now())[:10]:
            near_data='2999-01-01'
            for Current_phone in var["Телефоны"].keys():
                sell_with = var["Телефоны"][Current_phone].get('ПродаватьС', '')
                if var["Телефоны"][Current_phone].get('Активная_симка', False) and near_data > sell_with > '':
                    near_data = sell_with
            СекДоЗапуска = (datetime.datetime.strptime(near_data, '%Y-%m-%d')-datetime.datetime.now()).total_seconds()
            log(f'Все продано! Ближаящая работа {near_data} Закрытие браузера.')
            Close_brauzers(dict_Profile_FireFox)

        else:
            СекДоЗапуска = var["Пауза_между_выставлений_лотов_сек"]

        log(f'Пауза {СекДоЗапуска} сек. count_phone_for_sale={count_phone_for_sale}')
        sleep_or_press_keyboard(СекДоЗапуска)