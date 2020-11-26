# coding: utf8
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import os, time, winreg, re, random, time, math, datetime, calendar, logging, pprint, winsound, keyboard, pandas as pd
# pip3 install selenium keyboard pandas

global brauzer, var, Current_phone, last_element_html

def sleep_or_press_keyboard(seconds=10, wait_press_keyboard=None) -> None:
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
    logging.basicConfig(filename= file + ".log", format=u'%(asctime)s;  %(message)s',
                        level=logging.INFO)  # , level = logging.INFO DEBUG  LINE:%(lineno)d;
    log("----------------------------------------------------------")
    log("Program started")

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

def wait_elements_xpath(xpath_elements, count_try_wait_max=60, find1=True, УдалятьСпецСимволыИзТекста=True, УспехТолькоСЗаполненнымиДанными=False):
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
                    if УдалятьСпецСимволыИзТекста:
                        xpath_last_element_text = re.sub(r'[^\x00-\x7f]', '', xpath_last_element_text)
                    if count_try_wait == count_try_wait_max:
                        log(' - найден, .text=' + xpath_last_element_text)
                    if xpath_last_element_text == ''  and УспехТолькоСЗаполненнымиДанными:
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
        seek_xpath = xpath[seek_xpath]

    while wait_sec > 0:
        wait_sec -= 1
        if not isXpath(seek_xpath):
            # log (f'{seek_xpath} исчез')
            return True
        # log (f'{seek_xpath} есть')
        time.sleep(1)
    return False


def isXpath(xpath): # проверяет наличие xpath на странице
    global last_element_html, xpath_last_element_html, xpath_last_element_text
    try:
        last_element_html = brauzer.find_element_by_xpath(xpath)
        xpath_last_element_html=xpath
        xpath_last_element_text = last_element_html.text
        return last_element_html
    except:
        last_element_html = None
        return False

def get_url(url):
    global brauzer
    count_try_wait, max_count_try_wait = 1, 3
    while count_try_wait <= max_count_try_wait:
        try:
            brauzer.get(url) # иногда ошибка
            if count_try_wait > 1:
                log('Успешное открытие %s попытка %d' % (url, count_try_wait))
            return True
        except:
            log(f'Ошибка открытия {url} попытка {count_try_wait} из {max_count_try_wait}')
            time.sleep(2)
            count_try_wait+=1
    return False

def ЗакрытьВсеНенужноеПО():
    for key in {'geckodriver.exe','firefox.exe'}:
        cmd = "nircmd.exe execmd TASKKILL /F /IM "+key
        os.system(cmd)
    time.sleep(2)

def init_Ветка_Реестра(name_Ветки=os.path.basename(__file__)): # запустить один раз перед использованием init_Ветка_Реестра('SkorPay')
    global Ветка_Реестра_всех_настроек
    # if not ('Ветка_Реестра_всех_настроек' in globals()):
    try:
        Ветка_Реестра_всех_настроек = winreg.OpenKey(winreg.HKEY_CURRENT_USER, name_Ветки, winreg.KEY_READ | winreg.KEY_WRITE)
    except:
        Ветка_Реестра_всех_настроек = winreg.CreateKey(winreg.HKEY_CURRENT_USER, name_Ветки)


def ПолучитьЗначениеКлючаРеестра(КлючРеестра, ЗначениеПоУмолчанию=False, тип=0):
    global Ветка_Реестра_всех_настроек
    try:
        зн = winreg.QueryValueEx(Ветка_Реестра_всех_настроек, КлючРеестра)[0]
        if тип == float:
            return float(зн)
        elif isinstance(ЗначениеПоУмолчанию, list):
            return eval(зн)
        elif type(ЗначениеПоУмолчанию) is dict:
            # return eval('{' + зн + '}')
            return eval(зн)
        elif тип == str:
            return str(зн)
        return зн # тип int и др.
    except:
        return ЗначениеПоУмолчанию

def СохранитьЗначениеКлючаРеестра(КлючРеестра, Значение, тип_в_реестре=winreg.REG_SZ):
    # winreg.REG_DWORD    # 32-bit number.
    # winreg.REG_QWORD    # A 64-bit number.
    global Ветка_Реестра_всех_настроек
    if isinstance(Значение, list) and тип_в_реестре==winreg.REG_SZ:
        Значение = ДвумерныйСписокВСтроку(Значение) # преобразуем в строку
    elif type(Значение) is dict:
        Значение = str(Значение)
    winreg.SetValueEx(Ветка_Реестра_всех_настроек, КлючРеестра, 0, тип_в_реестре, Значение)

def Перезапуск_Браузера(profile=False):
    global brauzer
    ЗакрытьВсеНенужноеПО()
    brauzer = None

    FirefoxProfile = webdriver.FirefoxProfile()
    if profile:
        if profile == True:
            profile = __file__+'.Profiles_Firefox'
        if os.path.exists(profile):
            log(f'Профиль Firefox={profile}')
            FirefoxProfile = webdriver.FirefoxProfile(profile)     #  profile - имя файла профиля из папки (%APPDATA%\Mozilla\Firefox\Profiles\) C://Users//SkorPay//AppData//Roaming//Mozilla//Firefox//Profiles//, например 'etc7988t.default-release'
        else:
            log(f'Нет файла спрофилем Firefox {profile}') # (скопировать из папки %APPDATA%\Mozilla\Firefox\Profiles\)')
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

    brauzer = webdriver.Firefox(firefox_profile=FirefoxProfile, capabilities=cap)
    return brauzer

def open_url(new_url, wait_element, max_count_try=4, update=False, error_xpath=False): # открытие страницы оплаты
    global current_bank, brauzer
    # log('Открытие %s c ожиданием элементов %s' %(new_url, wait_element))
    count_try_wait = 0
    # wait_elements = wait_element.split(';')
    while count_try_wait<max_count_try:
        count_try_wait += 1
        str_log = 'Открытие %s попытка %s из %d' %(new_url, count_try_wait, max_count_try)
        if update or brauzer.current_url[0:len(new_url)] != new_url or count_try_wait > 1:
            get_url(new_url)
        сек_ожидания = min(count_try_wait * 5, 10)
        sleep_or_press_keyboard(сек_ожидания)

        if wait_elements_xpath(wait_element):
            return True
        # for element in wait_elements:
        #     if isXpath(element):
        #         if count_try_wait > 1:
        #             log(str_log + ' %s - успешно!' %element)
        #         if error_xpath and isXpath(error_xpath):
        #             log(f'Найден {error_xpath} будет обновление страницы через {сек_ожидания} сек.')
        #             time.sleep(сек_ожидания)
        #             continue
        #         return True
        #     if count_try_wait > 1:
        #         log(str_log + ' %s - Не успешно!' % element)

        # url=brauzer.current_url
        # if url[0:len(new_url)]==new_url:
        #     log(f'Ожидание элемента {wait_element}, пауза {сек_ожидания} сек.')
        #     time.sleep(сек_ожидания)
        #     continue

        # if count_try_wait>1:
        log(f'Ошибка открытия url={new_url} попытка {count_try_wait} из {max_count_try}')

    return False

def click(xpath_el=None, count_try_wait_max=10):
    global xpath_last_element_html
    if xpath_el != None:
        xpath_last_element_html = xpath_el
    count_try_wait=1
    while (count_try_wait <= count_try_wait_max):
        try:
            # if isinstance(xpath_last_element_html, str):
            el = WebDriverWait(brauzer, 8).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath_last_element_html)))
            el.click()
            if count_try_wait>1:
                log (f'Успех click {xpath_last_element_html}')
            return True
        except Exception as err:
            count_try_wait += 1
            log(f'Попытка {count_try_wait} Ошибка click {xpath_last_element_html} {err}')
            time.sleep(2)
    log(f'Не удалось click {xpath_last_element_html}')
    return False


def Press_Button(xpath_Button, sleep_after=0.3, wait_sec=2, Попыток=2):
    global brauzer, url, xpath, last_element_html
    if xpath_Button != '':
        if xpath_Button[0:2]!='//' and xpath_Button[0:1]!='(':
            xpath_Button = xpath[xpath_Button]

        while wait_sec > 0:
            wait_sec -= 1
            if isXpath(xpath_Button):
                time.sleep(0.1)
                break
            time.sleep(1)
    for Попытка in range(Попыток):
        try:
            if Попытка>0:
                last_element_html = WebDriverWait(brauzer, 8).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath_last_element_html)))
                # el_xp(xpath_last_element_html).click()
            # else:
            last_element_html.click()
            #    wait.until(EC.invisibility_of_element_located((By.XPATH, "//div[@class='blockUI blockOverlay']"))) and then el_xp("//input[@value='Save']").click()
            #  WebDriverWait(brauzer, 8).until(last_element_html.invisibility_of_element_located((By.XPATH, xpath_last_element_html))) and then el_xp("//input[@value='Save']").click()

            if Попытка > 0:
                log (f' {Попытка+1}/{Попыток} успех')

            if sleep_after:
                time.sleep(sleep_after)
            return True
        except Exception as err:
            log(f' {Попытка+1}/{Попыток} Ошибка click {xpath_Button} {err}')
            time.sleep(1)
    return False

def sleep(sec):
    time.sleep(sec)
    return True

def Past_Value(xpath_Value, val, sleep=0.3):
    if xpath_Value[0:2]!='//':
        xpath_Value = xpath[xpath_Value]
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

def Удаление_всех_лотов(МаксКолУдаляемыхЛотовПоРесурсу=2):
    global brauzer, url, xpath, Current_phone
    log (f'Удаление всех лотов до {МаксКолУдаляемыхЛотовПоРесурсу} шт. по {Current_phone}.')
    if not open_url(url['url_Мои_лоты'], xpath['Сформировать_лот_Начало']):
        log (f'Не удалось удалить лоты {Current_phone}')
        sleep(60)
        return False

    есть_удаленные_лоты = False
    МаксКолУдаляемыхЛотовПоРесурсу = МаксКолУдаляемыхЛотовПоРесурсу//2
    for Resource_for_sale in ('Гб', 'минуты'):
        НомерУдаляемогоЛота = 1
        while НомерУдаляемогоЛота <= МаксКолУдаляемыхЛотовПоРесурсу and not isXpath(xpath['Текст_нет_активных_лотов']):
            НомерУдаляемогоЛота +=1
            # посменно удаляются лоты интеренет и минут
            if not isXpath(xpath['Удаление_лота_количество_' + Resource_for_sale]):
                break
            УдаляемоеКол = Число(xpath_last_element_text)
            if УдаляемоеКол > 0 and sleep(0.5) and Press_Button(xpath['Удаление_лота_начало_' + Resource_for_sale], 1, 9) and Press_Button('Редактирования_лота_Отозвать', 1) \
                    and Press_Button('Редактирования_лота_Отозвать_Подтверждение') and Not_exist_Xpath('Кнопка_закрытия_окна'):
                # and isXpath(xpath['Редактирования_лота_Отозвать_Подтверждение']) and sleep(0.5)

                var["Телефоны"][Current_phone][f'Остатки_{Resource_for_sale}'] += УдаляемоеКол
                log(f'Конец удаления {НомерУдаляемогоЛота} лота {УдаляемоеКол} {Resource_for_sale} новый остаток {var["Телефоны"][Current_phone][f"Остатки_{Resource_for_sale}"]}')
                есть_удаленные_лоты = True
            else:
                log(f'Ошибка удаления лота {УдаляемоеКол} {Resource_for_sale}, будут обновлены остатки.')
                var["Телефоны"][Current_phone]['ОбновитьОстатки']=True
                if not open_url(url['url_Мои_лоты'], xpath['Сформировать_лот_Начало']):
                    sleep(3)
                    return False
                break

        if xpath_last_element_html == xpath['Текст_нет_активных_лотов']:
            log (f'Нет_активных_лотов {Current_phone}')
            СохранитьЗначениеКлючаРеестра(Current_phone+'_Выставленное_количествo_Гб', 0, winreg.REG_DWORD)
            СохранитьЗначениеКлючаРеестра(Current_phone+'_Выставленное_количествo_минуты', 0, winreg.REG_DWORD)
            var["Телефоны"][Current_phone]['Выставлное_количествo_Гб']=var["Телефоны"][Current_phone]['Выставлное_количествo_минуты']=0
            break

    return есть_удаленные_лоты

def Число(str): #строка в число
    match = re.search(r'\d+', str)
    return int(match[0]) if match else 0


def Получить_доступные_остатки(): # чтение остатков Гб и Минут
    global var, Current_phone, xpath_last_element_text

    if not open_url(url['url_lk'], xpath['Остатки_lk_минуты']+';'+xpath['Остатки_lk_Гб']+';//h2[text()="Доступно"]'):
        return False

    time.sleep(1)

    ОстакиПрочитаны = False
    for Resource_for_sale in ['минуты', 'Гб']:
        key_остатки = f'Остатки_{Resource_for_sale}'
        if isXpath(xpath[f'Остатки_lk_{Resource_for_sale}']):
            var["Телефоны"][Current_phone][key_остатки]= Число(xpath_last_element_text.replace(' ', ''))
            ОстакиПрочитаны = True
        else:
            if Resource_for_sale == 'Гб' and isXpath('//a[contains(text(),"Подключить пакет интернета")]'):
                ОстакиПрочитаны = True
            var["Телефоны"][Current_phone].update({key_остатки:0})

    if ОстакиПрочитаны:
        var["Телефоны"][Current_phone]['ОбновитьОстатки']=False

    log(f'Остатки {Current_phone} {var["Телефоны"][Current_phone]["Остатки_Гб"]} Гб {var["Телефоны"][Current_phone]["Остатки_минуты"]} Мин. Не продавать {var["Телефоны"][Current_phone]["Оставлять_Гб"]} Гб {var["Телефоны"][Current_phone]["Оставлять_минуты"]} Мин.' )
    return ОстакиПрочитаны

def ВыставитьЛоты(Resource_for_sale):

    global Current_phone, brauzer, var, _today
    ОставлятьРесурса = var["Телефоны"][Current_phone].get('Оставлять_'+Resource_for_sale, -1)
    if ОставлятьРесурса == -1:
        # log (f'Ресурс {Resource_for_sale} {Current_phone} не продается.')
        return False
    Остатки_Ресурса = var["Телефоны"][Current_phone]['Остатки_'+Resource_for_sale]
    if ОставлятьРесурса >= Остатки_Ресурса:
        # log (f'Ресурс {Resource_for_sale} {Current_phone} не продается т к оставляется {ОставлятьРесурса} а остаток ресурса {Остатки_Ресурса}')
        return False
    Остатки_Ресурса -= ОставлятьРесурса
    if Остатки_Ресурса < var['Min_count_for_sale_'+Resource_for_sale]:
        log (f'Пакет для продажи {Resource_for_sale} {Остатки_Ресурса} меньше минимального лота {var["Min_count_for_sale_"+Resource_for_sale]}')
        return False

    if brauzer.current_url != url['url_Мои_лоты'] and not open_url(url['url_'+Resource_for_sale], xpath['Сформировать_лот_Начало'], 2):
        sleep_or_press_keyboard(600) # time.sleep(600)
        return False

    var["Телефоны"][Current_phone]['Выставлное_количествo_'+Resource_for_sale]=ПолучитьЗначениеКлючаРеестра(Current_phone+'_Выставленное_количествo_'+Resource_for_sale, 0, int)
    Подписаться = var["Телефоны"][Current_phone].get('Подписаться', False)
    while  1:
        макс_количествo = Остатки_Ресурса-var["Телефоны"][Current_phone]['Выставлное_количествo_'+Resource_for_sale]
        if макс_количествo < var['Min_count_for_sale_'+Resource_for_sale]:
            log (f'Выставлено максимальное количество лотов по {Resource_for_sale}. Не продажный остаток {ОставлятьРесурса} {Resource_for_sale}')
            break

        количество_для_продажи = random.randint(var['Min_count_for_sale_'+Resource_for_sale], var['Min_count_for_sale_'+Resource_for_sale] + var['Максимальное_увеличение_количества_на_продажу'])
        сумма_продажи = str(math.ceil(var['Стоимость_1_ед_'+Resource_for_sale]*количество_для_продажи))

        if Press_Button('Сформировать_лот_Начало', 1) \
                and (brauzer.current_url == url['url_'+Resource_for_sale] or (Press_Button('Выбор_типа_лота_'+Resource_for_sale) and Press_Button('Кнопка_Продолжить'))) \
                and Press_Button('Подготовка_к_вводу_количества', 1, 2) \
                and Past_Value('Сформировать_лот_Поле_количествo_'+Resource_for_sale, str(количество_для_продажи)) \
                and Press_Button('Подготовка_к_вводу_Суммы') \
                and Past_Value('Сформировать_лот_Поле_Сумма', сумма_продажи)  \
                and Press_Button('Кнопка_Продолжить', 3) \
                and Press_Button('Кнопка_Продолжить', 3) :
            # and Press_Button('Сформировать_лот_Smile2') and Press_Button('Сформировать_лот_Smile2')
            # and Press_Button('Сформировать_лот_Smile2', 0.5, 60)  and ((not Подписаться) or Press_Button('Подписаться_как'))\

            log (f'Выставлен лот {Resource_for_sale} {количество_для_продажи} осталось {макс_количествo-количество_для_продажи}')
            var["Телефоны"][Current_phone]['Выставлное_количествo_'+Resource_for_sale] += количество_для_продажи
            var["Всего_на_продажу_"+Resource_for_sale] += количество_для_продажи

            СохранитьЗначениеКлючаРеестра(Current_phone+'_Выставленное_количествo_'+Resource_for_sale, var["Телефоны"][Current_phone]['Выставлное_количествo_'+Resource_for_sale], winreg.REG_DWORD)
            var["Телефоны"][Current_phone][f'Остатки_{Resource_for_sale}'] -= количество_для_продажи

            # сохранение кол-ва выставленных лотов в день
            КлючРеестра = _today+'_Выставлено_лотов'
            СохранитьЗначениеКлючаРеестра(КлючРеестра, ПолучитьЗначениеКлючаРеестра(КлючРеестра, 0, int) + 1, winreg.REG_DWORD)
            КлючРеестра = Current_phone + КлючРеестра
            СохранитьЗначениеКлючаРеестра(КлючРеестра, ПолучитьЗначениеКлючаРеестра(КлючРеестра, 0, int) + 1, winreg.REG_DWORD)
        else:
            log ('Ошибка выставления лота')
            var["Телефоны"][Current_phone]['ОбновитьОстатки']=True
            break

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


             # Начало программы -------------------------------------------------------------------------------------------------------------------------------
#             Смнетить тариф можно только звонком в Теле2 или USSD-командой: *630*(количество минут)*(количество ГБ)#
# Условия текущего тарифа - *107#
# для ЯО "Мой онлайн" 250 руб, 25 ГБ, 800 минут *630*800*25#
            
log_start()
log('Начало')
var ={'Min_count_for_sale_Гб':5, 'Min_count_for_sale_минуты':50, 'Максимальное_увеличение_количества_на_продажу':0,
      'Стоимость_1_ед_Гб':15, 'Стоимость_1_ед_минуты':0.8, 'ЧасНачалаТорговли':4, 'ЧасКонцаТорговли':1,
       'Пауза_между_выставлений_лотов_сек':500,
      "Откуда_дарить_Гб":["9535248000", "9012998490"], 'Кому_дарить_Гб':[],
      "Телефоны":{
      # '9535248000': {'Активная_симка': True, 'Name': 'Александр', 'Оставлять_минуты': 400, 'Оставлять_Гб': 14, 'День_обновления_остатков': 17, 'Абонплата': 500, 'Описание': 'Вологда 35ГБ, 700 минут', 'ЛС': '9535248000'},

      # '9019861431': {'Активная_симка': True, 'Name': 'Дима', 'Оставлять_минуты': 190, 'Оставлять_Гб': 19, 'День_обновления_остатков': 12, 'Абонплата': 300, 'Описание': 'Ярославль  40 ГБ, 800 минут', 'ПродаватьДоБаланса':0},
      # '9005093361': {'Активная_симка': True, 'Name': 'Александр', 'Оставлять_минуты': 300, 'Оставлять_Гб': 5, 'День_обновления_остатков': 12, 'Абонплата': 500, 'Описание': 'Вологда 35 ГБ, 700 минут', 'ЛС': '9535248000', 'ЧасКонцаТорговли':'23', 'ЧасНачалаТорговли':'19'},
      # '9005033469': {'Активная_симка': True, 'Name': 'Александр', 'Оставлять_минуты': 0, 'Оставлять_Гб': 0, 'День_обновления_остатков': 19, 'Абонплата': 500, 'Описание': 'Вологда 35 ГБ, 700 минут', 'ЛС': '9535248000'},
      # '9922874211': {'Активная_симка': True, 'Name': 'Александр', 'Оставлять_минуты': 300, 'Оставлять_Гб': 1, 'День_обновления_остатков': 26, 'Абонплата': 400, 'Описание': 'Вологда 25 ГБ, 600 минут', 'ЛС': '9535248000'},
      # '9005424360': {'Активная_симка': True, 'Name': 'Александр', 'Оставлять_минуты': 0, 'Оставлять_Гб': 5, 'День_обновления_остатков': 29, 'Абонплата': 500, 'Описание': 'поменять Вологда 35 ГБ, 700 минут', 'ЛС': '9535248000'},
      #
      #     #
      # '9012998490': {'Активная_симка': True, 'Name': 'Александр', 'Оставлять_минуты': 0, 'Оставлять_Гб': 0, 'День_обновления_остатков': 19, 'Абонплата': 300, 'Описание': 'Ярославль 40 ГБ, 800 минут'},
      # '9019861432': {'Активная_симка': True, 'Name': 'Александр', 'Оставлять_минуты': 0, 'Оставлять_Гб': 40, 'День_обновления_остатков': 12, 'Абонплата': 300, 'Описание': 'Ярославль  40 ГБ, 800 минут'},
      #
      # #
      # '9010452940':{'Активная_симка':True, 'Name':'Надежда личный2', 'Оставлять_минуты':40, 'Оставлять_Гб':1, 'День_обновления_остатков':30, 'Абонплата':250, 'Описание':'25 ГБ, 800 минут', 'Подписаться':True, 'ЛС': '9011720400'},
      # '9011720400':{'Активная_симка':True, 'Name':'Надежда личный', 'Оставлять_минуты':600, 'Оставлять_Гб':20, 'День_обновления_остатков':12, 'Абонплата':125, 'Описание':' 35 ГБ, 600 минут', 'Подписаться':True, 'ЛС': '9011720400', "Поддерживать_Гб":1},
      # # '9011720401':{'Активная_симка':True, 'Name':'Надежда мама', 'Оставлять_минуты':700, 'Оставлять_Гб':5, 'День_обновления_остатков':21, 'Абонплата':125, 'Описание':' 35 ГБ, 600 минут', 'Подписаться':True, 'ЛС': '9011720400'},
      # #
      # '9005034564': {'Активная_симка': True, 'Name': 'Евгения', 'Оставлять_минуты': 400, 'Оставлять_Гб': 25, 'День_обновления_остатков': 9, 'Абонплата': 337.5, 'Описание': 'Вологда  35 ГБ, 600 минут', 'ЛС': ''},
      # #
      # '9535202353': {'Активная_симка': True, 'Name': 'Руслан', 'Оставлять_минуты': 600, 'Оставлять_Гб': 5, 'День_обновления_остатков': 20, 'Абонплата': 400, 'Описание': 'Вологда  25ГБ,  600 минут', 'ЛС': ''},
      #
      '9005491033':{'Активная_симка':True, 'Name':'Орлов Стекольный modem', 'Оставлять_минуты':0, 'Оставлять_Гб':3, 'День_обновления_остатков':19, 'Абонплата':300, 'Описание':'Вологда 15 ГБ, 350 минут', 'ЛС': '9005072994', 'Телефон ЛК':'9535248000'},
      '9005507677':{'Активная_симка':True, 'Name':'Орлов Лакомка modem', 'Оставлять_минуты':0, 'Оставлять_Гб':5, 'День_обновления_остатков':25, 'Абонплата':500, 'Описание':'Вологда 35 ГБ, 700 минут', 'ЛС': '9005072994'},
      '9535208906':{'Активная_симка':True, 'Name':'Орлов Универма modem', 'Оставлять_минуты':0, 'Оставлять_Гб':5, 'День_обновления_остатков':25, 'Абонплата':500, 'Описание':'Вологда 35 ГБ, 700 минут +', 'ЛС': '9005072994'},

      '9535146404':{'Активная_симка':False, 'Name':'Орлов Универмаг phone', 'Оставлять_минуты':300, 'Оставлять_Гб':1, 'День_обновления_остатков':0, 'Абонплата':0, 'Описание':'Вологда 0 ГБ, 0 минут +', 'ЛС': '9005072994'},
      '9005490255': {'Активная_симка': False, 'Name': 'Орлов Лакомка phone', 'Оставлять_минуты': 300, 'Оставлять_Гб': 1, 'День_обновления_остатков': 0, 'Абонплата': 0, 'Описание': 'Вологда 0 ГБ, 0 минут +', 'ЛС': '9005072994'},
      '9005479262': {'Активная_симка': False, 'Name': 'Орлов Стекольный phone', 'Оставлять_минуты': 300, 'Оставлять_Гб': 1, 'День_обновления_остатков': 0, 'Абонплата': 0, 'Описание': 'Вологда 0 ГБ, 0 минут +', 'ЛС': '9005072994'},

      '9005072994':{'Активная_симка':True, 'Name':'Орлов Личный', 'Оставлять_минуты':400, 'Оставлять_Гб':5, 'День_обновления_остатков':23, 'Абонплата':500, 'Описание':'Вологда  35 ГБ, 700 минут', 'ЛС': '9005072994'}



          # '9005369460':{'Активная_симка':False, 'Name':'Дворецкая София Николаевна', 'Оставлять_минуты':150, 'Оставлять_Гб':3,'День_обновления_остатков':30},
      }
      }


#
# df = pd.concat({k: pd.Series(v) for k, v in data.items()}).reset_index()
# df.columns = ['dict_index', 'name','quantity']
# print(df)

init_Ветка_Реестра()
if __name__ == '__main__':
    xpath={'xpath_phone':'//input[@id="keycloakAuth.phone"]', 'xpath_next_login' : '//button[contains(text(),"Далее")]', 'xpath_login_with_password' : '//button[text()="Вход по паролю"]',
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

    # восстановление из реестра
    Список_ЛС = {}
    _today = str(datetime.datetime.today())[:10]
    phone_lk_default = list(var["Телефоны"].keys())[0] # Первый телефон - логин авторизации

    for Current_phone in var["Телефоны"].keys():
        ПродаватьС = ПолучитьЗначениеКлючаРеестра(Current_phone+'ПродаватьС', "", str)
        if ПродаватьС <= _today:
            ПродаватьС = ''
        var["Телефоны"][Current_phone]['ПродаватьС'] = ПродаватьС
        # else:
        #     ПродаватьС = time.strftime("%Y-%m-%d", time.gmtime(ПродаватьС))
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

        var["Телефоны"][Current_phone]['ОбновитьОстатки'] = ПолучитьЗначениеКлючаРеестра(Current_phone + 'ОбновитьОстаткиС', "") <= _today
        if var["Телефоны"][Current_phone].get('ЧасНачалаТорговли', None)  == None or var["Телефоны"][Current_phone].get('ЧасКонцаТорговли', None) == None:
            var["Телефоны"][Current_phone]['ЧасНачалаТорговли'] = ''
            var["Телефоны"][Current_phone]['ЧасКонцаТорговли'] = '24'
        var["Телефоны"][Current_phone]['brauzer'] = None
        phone_lk = var["Телефоны"][Current_phone]['Телефон ЛК'] = var["Телефоны"][Current_phone].get('Телефон ЛК', phone_lk_default)
        if phone_lk != phone_lk_default:
            phone_lk_default = phone_lk # если не задан 'Телефон ЛК' то возьмется последний 'Телефон ЛК'
        var["Телефоны"][Current_phone]['Profile_FireFox'] = name_Profile_FireFox = phone_lk + '.' + 'Profile_FireFox' # имя профиля FireFox
        var[name_Profile_FireFox] = None # очищаем ссылку на selenium
        if var["Телефоны"][Current_phone].get("Баланс", None) == None:
            var["Телефоны"][Current_phone]["Баланс"]=0


    while True:
        ВсегоНомеровСПродажей = var["Всего_на_продажу_Гб"] = var["Всего_на_продажу_минуты"] = 0

        _today = str(datetime.datetime.today())[:19]
        ЧасТорговли = _today[11:13]
        _today = _today[:10]
        До_начала = ВремяДоНачалаТоргов(int(ЧасТорговли), var['ЧасНачалаТорговли'], var['ЧасКонцаТорговли'])
        if До_начала >  0:
             print(f"До начала торгов {round(До_начала, 2)} часов. Начало {var['ЧасНачалаТорговли']} конец {var['ЧасКонцаТорговли']} часов.")
             if brauzer != None:
                 brauzer.quit()
                 brauzer = None
             sleep_or_press_keyboard(До_начала*3600)
             continue

        for Current_phone in var["Телефоны"].keys():

            # запуск браузера по профилю
            Profile_FireFox = var["Телефоны"][Current_phone]['Profile_FireFox']
            brauzer = var[Profile_FireFox]
            if brauzer == None:
                var[Profile_FireFox] = Перезапуск_Браузера(Profile_FireFox)
                if brauzer == None:
                    log(f'Для {Current_phone} не удалось открыть браузер с профилем {Profile_FireFox}')
                    sleep_or_press_keyboard(300, wait_press_keyboard = {'esc':'для досрочного продолжения'})
                    continue

            phone_enable, sell_with=var["Телефоны"][Current_phone]['Активная_симка'] , var["Телефоны"][Current_phone].get('ПродаватьС', '')
            log(f'Начало переключения на номер {Current_phone} {var["Телефоны"][Current_phone]["Name"]} {var["Телефоны"][Current_phone]["Баланс"]}р Активность:{phone_enable} использовать с: {sell_with} ОбновитьОстатки={var["Телефоны"][Current_phone]["ОбновитьОстатки"]}')
            phone_enable = (phone_enable and (_today >= sell_with))\
                         and var["Телефоны"][Current_phone]['ЧасНачалаТорговли'] <= ЧасТорговли <= var["Телефоны"][Current_phone]['ЧасКонцаТорговли']
            ЕстьКомуДаритьГб = len(var["Кому_дарить_Гб"])>0 and Current_phone in var["Откуда_дарить_Гб"] and var["Телефоны"][Current_phone].get("Остатки_Гб", -1) != 0
            if  not phone_enable and not var["Телефоны"][Current_phone]['ОбновитьОстатки'] and not ЕстьКомуДаритьГб:
                continue

            if not open_url(url['url_lk'], xpath['Войти']+';' + xpath['xpath_phone'] + ';' + xpath['Мой_Tele2'], 2):
                sleep_or_press_keyboard(600, {'c':' -  скопировать с про'})

                continue

            if xpath_last_element_html in [xpath['Войти'], xpath['xpath_phone']]:                 #  авторизация
                log(f'Телефон для авторизации {var["Телефоны"][Current_phone]["Телефон ЛК"]}')
                if (isXpath(xpath['xpath_phone']) or Press_Button('Войти', 1)) \
                        and Past_Value('xpath_phone', var["Телефоны"][Current_phone]["Телефон ЛК"], 0.5) \
                        and Press_Button('xpath_next_login', 5):
                    #         and Press_Button('//button[text()="Вход по паролю"]', 1) \
                    #         and Past_Value('//input[@id="keycloakAuth.password"]', password, 0.5):

                    #         ожидание входа человеком
                    log ('Ожидание входа человеком')
                    while not isXpath(xpath['Мой_Tele2']):
                        sleep_or_press_keyboard(20)

            phone_format = Current_phone[0:3]+' '+Current_phone[3:6]+' '+Current_phone[6:8]+' '+Current_phone[8:10]
            if isXpath(f'//button/h1[contains(text(),"{phone_format}")]'):
                log(f'Номер {Current_phone} уже выбран из списка.') #  управляемых номеров
            elif open_url(url['url_lk'], '//span[contains(@class, "dashboard-number__icon")]', 2, error_xpath='//div[@class="data-unavailable-message lk-new error-message"]') and click() and sleep(0.8)\
                and click(f'//li/button/h3[contains(text(),"{phone_format}")]/..', 10) and wait_elements_xpath(f'//button/h1[contains(text(),"{phone_format}")]', 30) and wait_elements_xpath(xpath['Баланс'], 30):
                var["Телефоны"][Current_phone]['Баланс']=float(xpath_last_element_text.replace(' ', '').replace(',', '.')) #.replace('₽', '')
                var["Телефоны"][Current_phone]['Баланс_дата'] = _today
                log(f'Успешное переключение на номер {Current_phone} баланс {xpath_last_element_text} руб.')

                # обновление Абонплата
                if var["Телефоны"][Current_phone].get('Абонплата', 0) <= 0 and isXpath(xpath['Абонплата']):
                    rez_match = re.search('(Абонентская плата )(.+)( ₽ будет списана )(\d+)', xpath_last_element_text)
                    if rez_match:
                        var["Телефоны"][Current_phone]['Абонплата'] = float(rez_match.group(2))
                        var["Телефоны"][Current_phone]['День_обновления_остатков'] = int(rez_match.group(4))

            else:
                log(f'Неудалось переключиться на номер {Current_phone}. Переход к следущему номеру черех 3 минуты.')
                sleep_or_press_keyboard(180)
                continue

            if isXpath(xpath['Мой_Tele2_номер']):
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

            Удаление_всех_лотов(40)



            #  Проверка есть ли что продавать и обновление "ПродаватьС"
            if (0 < var["Телефоны"][Current_phone].get('ПродаватьДоБаланса', -1) < var["Телефоны"][Current_phone]['Баланс'])\
                or\
                    ((((var["Телефоны"][Current_phone]['Остатки_Гб']-var["Телефоны"][Current_phone]['Оставлять_Гб']) < var['Min_count_for_sale_Гб']) or (var["Телефоны"][Current_phone]['Оставлять_Гб'])==-1) \
                    and (((var["Телефоны"][Current_phone]['Остатки_минуты']-var["Телефоны"][Current_phone]['Оставлять_минуты']) < var['Min_count_for_sale_минуты']) or (var["Телефоны"][Current_phone]['Оставлять_минуты']==-1)) \
                    and var["Телефоны"][Current_phone].get('Выставлное_количествo_Гб', 0) == var["Телефоны"][Current_phone].get('Выставлное_количествo_минуты', 0)==0):

                if var["Телефоны"][Current_phone].get('День_обновления_остатков', 0) == 0:
                    log(f'Не задан день обновления баланса.')
                else:
                    Сегодня = datetime.datetime.now()
                    ДатаОбновленияБаланса = datetime.datetime(Сегодня.year, Сегодня.month, var["Телефоны"][Current_phone]['День_обновления_остатков'])
                    if ДатаОбновленияБаланса < Сегодня: # обновление будет в следующем месяце
                        days_in_month = calendar.monthrange(ДатаОбновленияБаланса.year, ДатаОбновленияБаланса.month)[1]
                        ДатаОбновленияБаланса += datetime.timedelta(days=days_in_month)

                    var["Телефоны"][Current_phone]['ПродаватьС'] = sell_with = str(ДатаОбновленияБаланса)[:10] #int(time.mktime(ДатаОбновленияБаланса.timetuple()))
                    СохранитьЗначениеКлючаРеестра(Current_phone+'ПродаватьС', sell_with) # , winreg.REG_DWORD
                    log(f'Новая дата ПродаватьС для {Current_phone}: {sell_with}') #time.ctime(ПродаватьС) .strftime("%d.%m.%Y")

                log(f'Нет ресурсов для продажи. Переход к следущему номеру.\n')
                continue

            ВсегоНомеровСПродажей +=1

            ВыставитьЛоты('Гб')
            ВыставитьЛоты('минуты')
            time.sleep(2)

        log('Итоги:')
        pprint.pprint(var["Телефоны"])

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

        if ВсегоНомеровСПродажей==0 and sell_with > str(datetime.datetime.now())[:10]:
            near_data='2999-01-01'
            for Current_phone in var["Телефоны"].keys():
                sell_with = var["Телефоны"][Current_phone].get('ПродаватьС', '')
                if var["Телефоны"][Current_phone].get('Активная_симка', False) and near_data > sell_with > '':
                    near_data = sell_with
            СекДоЗапуска = (datetime.datetime.strptime(near_data, '%Y-%m-%d')-datetime.datetime.now()).total_seconds()
            log(f'Все продано! Ближаящая работа {near_data}')
            try:
                brauzer.quit()
            except:
                log('Ошибка при закрытии браузера!')
        else:
            СекДоЗапуска = var["Пауза_между_выставлений_лотов_сек"]

        log(f'Пауза {СекДоЗапуска} сек. ВсегоНомеровСПродажей={ВсегоНомеровСПродажей}')
        sleep_or_press_keyboard(СекДоЗапуска)