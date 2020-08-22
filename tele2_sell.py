from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import os, time, winreg, re, random, time, math, datetime, calendar, logging, pprint, winsound

global brauzer, var, Current_phone

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
        #log('wait %s' %count_try_wait)
        for key_element in elements:
            if not elements[key_element]:
                begin_log = ("Поиск %s" %key_element) if count_el!=1 or count_try_wait == 1 else ''
                begin_log += " попытка " + str(count_try_wait) + ' из ' + str(count_try_wait_max)
                log(begin_log)
                begin_log = ''
                elements[key_element]=False
                try:
                    elements[key_element]=brauzer.find_element_by_xpath(key_element)
                    xpath_last_element_text = elements[key_element].text
                    if УдалятьСпецСимволыИзТекста:
                        xpath_last_element_text = re.sub(r'[^\x00-\x7f]', '', xpath_last_element_text)
                    log(begin_log + ' - найден, .text=' + xpath_last_element_text)
                    if xpath_last_element_text == ''  and УспехТолькоСЗаполненнымиДанными:
                        log('Найденный тэг пустой, он считается как не найденный. Пауза 3 сек.')
                        elements[key_element] = False
                        time.sleep(3)
                    elif xpath_last_element_text != 'Недоступно' :
                        if find1 or (count_find==len(elements)):
                            last_element_html=elements[key_element]
                            xpath_last_element_html = key_element
                            return elements, xpath_last_element_text
                        count_find += 1
                except:
                    elements[key_element] = False
                    log(begin_log + ' - не найден!')
            else:
                log('elements[key_element] - истина')
        time.sleep(1)
        # if count_try_wait == 20:
        #     winsound.MessageBeep()

    return False, xpath_last_element_text
def Not_exist_Xpath(seek_xpath, wait_sec=10): # ожидает исчезновение seek_xpath
    if seek_xpath[0:2]!='//' and seek_xpath[0:1]!='(':
        seek_xpath = xpath[seek_xpath]

    while wait_sec > 0:
        wait_sec -= 1
        if not isXpath(seek_xpath):
            log (f'{seek_xpath} исчез')
            return True
        log (f'{seek_xpath} есть')
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
    count_try_wait = 0
    while count_try_wait < 3:
        try:
            brauzer.get(url) # иногда ошибка
            if count_try_wait>0:
                send_message_to_telegram('Успешное открытие %s попытка %d' % (url, count_try_wait))
            return True
        except:
            send_message_to_telegram('Ошибка открытия %s' %url, make_screenshot = True)
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

    FirefoxProfile = webdriver.FirefoxProfile()
    if profile:
        if profile == True:
            profile = __file__+'.Profiles_Firefox'
        if os.path.exists(profile):
            log(f'Профиль Firefox={profile}')
            FirefoxProfile = webdriver.FirefoxProfile(profile)     #  profile - имя файла профиля из папки (%APPDATA%\Mozilla\Firefox\Profiles\) C://Users//SkorPay//AppData//Roaming//Mozilla//Firefox//Profiles//, например 'etc7988t.default-release'
        else:
            log(f'Нет файла спрофилем Firefox {profile} (скопировать из папки %APPDATA%\Mozilla\Firefox\Profiles\)')

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

def open_url(new_url, wait_element, max_count_try=4, update=False, error_xpath=False): # открытие страницы оплаты
    global current_bank, brauzer
    log('Открытие %s c ожиданием элементов %s' %(new_url, wait_element))
    count_try_wait = 0
    wait_elements = wait_element.split(';')
    while count_try_wait<max_count_try:
        count_try_wait += 1
        str_log = 'Открытие %s попытка %s из %d' %(new_url, count_try_wait, max_count_try)
        if update or brauzer.current_url[0:len(new_url)] != new_url or count_try_wait > 1:
            get_url(new_url)
        сек_ожидания = min(count_try_wait * 2, 10)
        time.sleep(сек_ожидания)

        for element in wait_elements:
            if isXpath(element):
                log(str_log + ' %s - успешно!' %element)
                if error_xpath and isXpath(error_xpath):
                    log(f'Найден {error_xpath} будет обновление страницы.')
                    time.sleep(сек_ожидания)
                    continue
                return True
            log(str_log + ' %s - Не успешно!' % element)
        url=brauzer.current_url
        if url[0:len(new_url)]==new_url:
            log('Ожидание элемента %s, пауза %s сек.' %(wait_element, сек_ожидания))
            time.sleep(сек_ожидания)
            continue

        log('url=' + url)
    return False

def click(xpath_el, count_try_wait_max=10):
    count_try_wait=1
    while (count_try_wait <= count_try_wait_max):
        try:
            # if isinstance(xpath_el, str):
            el = WebDriverWait(brauzer, 8).until(expected_conditions.element_to_be_clickable((By.XPATH, xpath_el)))
            el.click()
            # if count_try_wait>1:
            log (f'Успех click {xpath_el}')
            return True
        except Exception as err:
            count_try_wait += 1
            log(f'Попытка {count_try_wait} Ошибка click {xpath_el} {err}')
            time.sleep(2)
    log(f'Не удалось click {xpath_el}')
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

            # log (f'Нажато {xpath_last_element_html}')
            if sleep_after:
                time.sleep(sleep_after)
            return True
        except Exception as err:
            log(f'Ошибка click {xpath_Button} {err} попытка {Попытка}')
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
    for Resource_for_sale in ('интернет', 'минуты'):
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

                var['Телефоны'][Current_phone][f'Остатки_{Resource_for_sale}'] += УдаляемоеКол
                log(f'Конец удаления {НомерУдаляемогоЛота} лота {УдаляемоеКол} {Resource_for_sale} новый остаток {var["Телефоны"][Current_phone][f"Остатки_{Resource_for_sale}"]}')
                есть_удаленные_лоты = True
            else:
                log(f'Ошибка удаления лота {УдаляемоеКол} {Resource_for_sale}, будут обновлены остатки.')
                var['Телефоны'][Current_phone]['ОбновитьОстатки']=True
                if not open_url(url['url_Мои_лоты'], xpath['Сформировать_лот_Начало']):
                    sleep(3)
                    return False
                break

        if xpath_last_element_html == xpath['Текст_нет_активных_лотов']:
            log (f'Нет_активных_лотов {Current_phone}')
            СохранитьЗначениеКлючаРеестра(Current_phone+'Выставлное_количествo_интернет', 0, winreg.REG_DWORD)
            СохранитьЗначениеКлючаРеестра(Current_phone+'Выставлное_количествo_минуты', 0, winreg.REG_DWORD)
            var["Телефоны"][Current_phone]['Выставлное_количествo_интернет']=var["Телефоны"][Current_phone]['Выставлное_количествo_минуты']=0
            break

    return есть_удаленные_лоты

def Число(str): #строка в число
    match = re.search(r'\d+', str)
    return int(match[0]) if match else 0


def Получить_доступные_остатки():
    global var, Current_phone, xpath_last_element_text

    ОстакиПрочитаны = False
    СпособыПолученяОстатков=['lk'] # ,'НаАватаре'
    for СпособПолученияОстатков in СпособыПолученяОстатков:
        if СпособПолученияОстатков == 'НаАватаре':
            if not isXpath(xpath['icon-profile']): # icon-profile Мой_Tele2_номер
                open_url(url['url_Мои_лоты'], xpath['Войти']+';'+xpath['Мой_Tele2'], 2, update=True)

            if not Press_Button(xpath['icon-profile']) :
                log ('Остатки Гб и Мин не прочитаны.')
                break

            ActionChains(brauzer).move_to_element(last_element_html).perform() # наведение
            time.sleep(0.1)

        elif СпособПолученияОстатков=='lk':
            if not open_url(url['url_lk'], xpath['Остатки_lk_минуты']+';'+xpath['Остатки_lk_интернет']+';//h2[text()="Доступно"]'):
                break
            time.sleep(3)
            if isXpath(xpath['Баланс'], 8):
                var["Телефоны"][Current_phone]['Баланс']=xpath_last_element_text
                var["Телефоны"][Current_phone]['Баланс_дата'] = str(datetime.datetime.today())[:10]

        for Resource_for_sale in ['минуты', 'интернет']:
            key_остатки = f'Остатки_{Resource_for_sale}'
            if isXpath(xpath[f'Остатки_{СпособПолученияОстатков}_{Resource_for_sale}']):
                var['Телефоны'][Current_phone][key_остатки]= Число(xpath_last_element_text)
                ОстакиПрочитаны = True
            else:
                if Resource_for_sale == 'интернет' and isXpath('//a[contains(text(),"Подключить пакет интернета")]'):
                    ОстакиПрочитаны = True
                var['Телефоны'][Current_phone].update({key_остатки:0})
                # log(f'Не удалось прочитать остатки {Current_phone} методом {СпособПолученияОстатков}')
                # break

        if ОстакиПрочитаны:
            var['Телефоны'][Current_phone]['ОбновитьОстатки']=False
            break

    log(f'Остатки {Current_phone} {var["Телефоны"][Current_phone]["Остатки_интернет"]} Гб {var["Телефоны"][Current_phone]["Остатки_минуты"]} Мин. Не продавать {var["Телефоны"][Current_phone]["Оставлять_интернет"]} Гб {var["Телефоны"][Current_phone]["Оставлять_минуты"]} Мин.' )
    return ОстакиПрочитаны

def ВыставитьЛоты(Resource_for_sale):
    global Current_phone, brauzer, var
    ОставлятьРесурса = var["Телефоны"][Current_phone].get('Оставлять_'+Resource_for_sale, -1)
    if ОставлятьРесурса == -1:
        log (f'Ресурс {Resource_for_sale} {Current_phone} не продается.')
        return False
    Остатки_Ресурса = var["Телефоны"][Current_phone]['Остатки_'+Resource_for_sale]
    if ОставлятьРесурса >= Остатки_Ресурса:
        log (f'Ресурс {Resource_for_sale} {Current_phone} не продается т к оставляется {ОставлятьРесурса} а остаток ресурса {Остатки_Ресурса}')
        return False
    Остатки_Ресурса -= ОставлятьРесурса
    if Остатки_Ресурса < var['Min_count_for_sale_'+Resource_for_sale]:
        log (f'Пакет для продажи {Resource_for_sale} {Остатки_Ресурса} меньше минимального лота {var["Min_count_for_sale_"+Resource_for_sale]}')
        return False

    if brauzer.current_url != url['url_Мои_лоты'] and not open_url(url['url_'+Resource_for_sale], xpath['Сформировать_лот_Начало'], 2):
        time.sleep(600)
        return False

    var["Телефоны"][Current_phone]['Выставлное_количествo_'+Resource_for_sale]=ПолучитьЗначениеКлючаРеестра(Current_phone+'Выставлное_количествo_'+Resource_for_sale, 0, int)
    Подписаться = var["Телефоны"][Current_phone].get('Подписаться', False)
    while  1:
        макс_количествo = Остатки_Ресурса-var["Телефоны"][Current_phone]['Выставлное_количествo_'+Resource_for_sale]
        if макс_количествo < var['Min_count_for_sale_'+Resource_for_sale]:
            log (f'Выставлено максимальное количество лотов по {Resource_for_sale}. Не продажный остаток {ОставлятьРесурса} {Resource_for_sale}')
            break

        количество_для_продажи = random.randint(var['Min_count_for_sale_'+Resource_for_sale], var['Min_count_for_sale_'+Resource_for_sale] + var['Максимальное_увеличение_количества_на_продажу'])
        сумма_продажи = str(math.ceil(var['Стоимость_1_ед_'+Resource_for_sale]*количество_для_продажи))

        if Press_Button('Сформировать_лот_Начало', 1) \
                and (brauzer.current_url == url['url_'+Resource_for_sale] or (Press_Button('Выбор_типа_лота_'+Resource_for_sale) and Press_Button('Сформировать_лот_Продолжить'))) \
                and Press_Button('Подготовка_к_вводу_количества', 1, 2) \
                and Past_Value('Сформировать_лот_Поле_количествo_'+Resource_for_sale, str(количество_для_продажи)) \
                and Press_Button('Подготовка_к_вводу_Суммы') \
                and Past_Value('Сформировать_лот_Поле_Сумма', сумма_продажи)  \
                and Press_Button('Сформировать_лот_Продолжить', 3) \
                and Press_Button('Сформировать_лот_Продолжить', 3) :
            # and Press_Button('Сформировать_лот_Smile2') and Press_Button('Сформировать_лот_Smile2')
            # and Press_Button('Сформировать_лот_Smile2', 0.5, 60)  and ((not Подписаться) or Press_Button('Подписаться_как'))\

            log (f'Выставлен лот {Resource_for_sale} {количество_для_продажи} осталось {макс_количествo-количество_для_продажи}')
            var["Телефоны"][Current_phone]['Выставлное_количествo_'+Resource_for_sale] += количество_для_продажи
            var["Всего_на_продажу_"+Resource_for_sale] += количество_для_продажи

            СохранитьЗначениеКлючаРеестра(Current_phone+'Выставлное_количествo_'+Resource_for_sale, var["Телефоны"][Current_phone]['Выставлное_количествo_'+Resource_for_sale], winreg.REG_DWORD)
            var["Телефоны"][Current_phone][f'Остатки_{Resource_for_sale}'] -= количество_для_продажи
        else:
            log ('Ошибка выставления лота')
            var["Телефоны"][Current_phone]['ОбновитьОстатки']=True
            break
# Начало программы -------------------------------------------------------------------------------------------------------------------------------
log_start()
log(f'{time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())} Начало')
var ={'Min_count_for_sale_интернет':5, 'Min_count_for_sale_минуты':100, 'Максимальное_увеличение_количества_на_продажу':0,
      'Стоимость_1_ед_интернет':15, 'Стоимость_1_ед_минуты':0.8,
       'Пауза_между_выставлений_лотов_сек':500,
      "Телефоны":{
      '9005034564': {'Активная_симка': True, 'Name': 'Евгения', 'Оставлять_минуты': 450, 'Оставлять_интернет': 25, 'День_обновления_остатков': 9, 'Абонентская плата': 337.5, 'Описание': 'Вологда  35 ГБ, 600 минут', 'Единый лицевой счет': ''},

      '9535248000':{'Активная_симка':True, 'Name':'Александр', 'Оставлять_минуты':600, 'Оставлять_интернет':15,'День_обновления_остатков':17, 'Абонентская плата':400, 'Описание':'Вологда 25ГБ, 600 минут'},
      '9005093361':{'Активная_симка':True, 'Name':'Александр', 'Оставлять_минуты':0, 'Оставлять_интернет':0,'День_обновления_остатков':12, 'Абонентская плата':400, 'Описание':'Вологда 25 ГБ, 600 минут', 'Единый лицевой счет':'9005424360'},
      '9005424360':{'Активная_симка':True, 'Name':'Александр', 'Оставлять_минуты':0, 'Оставлять_интернет':0,'День_обновления_остатков':12, 'Абонентская плата':250, 'Описание':'Вологда 5 ГБ, 200 минут', 'Единый лицевой счет':'9005424360'},
      '9005033469': {'Активная_симка': True, 'Name': 'Александр', 'Оставлять_минуты': 0, 'Оставлять_интернет': 30, 'День_обновления_остатков': 19, 'Абонентская плата': 500, 'Описание': 'Вологда 35 ГБ, 700 минут', 'Единый лицевой счет': ''},
      '9012998490': {'Активная_симка': True, 'Name': 'Александр', 'Оставлять_минуты': 0, 'Оставлять_интернет': 0, 'День_обновления_остатков': 11, 'Абонентская плата': 300, 'Описание': 'Ярославль 40 ГБ, 800 минут'},

      '9010452940':{'Активная_симка':True, 'Name':'Трапезина Надежда Сергеевна', 'Оставлять_минуты':0, 'Оставлять_интернет':60, 'День_обновления_остатков':11, 'Абонентская плата':300, 'Описание':'40 ГБ, 800 минут', 'Подписаться':True},
      # '9011720400':{'Активная_симка':False, 'Name':'Трапезина Надежда Сергеевна', 'Оставлять_минуты':300, 'Оставлять_интернет':5, 'День_обновления_остатков':12, 'Абонентская плата':125, 'Описание':' 35 ГБ, 600 минут', 'Подписаться':True},
      # '9011720401':{'Активная_симка':False, 'Name':'Трапезина Надежда Сергеевна мама', 'Оставлять_минуты':300, 'Оставлять_интернет':5, 'День_обновления_остатков':12, 'Абонентская плата':125, 'Описание':' 35 ГБ, 600 минут', 'Подписаться':True},

      '9535202353': {'Активная_симка': True, 'Name': 'Руслан', 'Оставлять_минуты': 500, 'Оставлять_интернет': 5, 'День_обновления_остатков': 20, 'Абонентская плата': 400, 'Описание': 'Вологда  25ГБ,  600 минут', 'Единый лицевой счет': ''}


          # '9005369460':{'Активная_симка':False, 'Name':'Дворецкая София Николаевна', 'Оставлять_минуты':150, 'Оставлять_интернет':3,'День_обновления_остатков':30},
      # '9005034564':{'Активная_симка':True, 'Name':'Евгения', 'Оставлять_минуты':500, 'Оставлять_интернет':25,'День_обновления_остатков':0}
      }
      }
init_Ветка_Реестра()
ГлаыныйНомер = '9535248000'
Перезапуск_Браузера(ГлаыныйНомер+'.Profiles_Firefox')

xpath={'xpath_phone':'//input[@id="keycloakAuth.phone"]', 'xpath_next_login' : '//button[contains(text(),"Далее")]', 'xpath_login_with_password' : '//button[text()="Вход по паролю"]',
      'Текст_нет_активных_лотов':'//div[contains(text(), "У вас нет активных лотов в продаже.")]',
       'Сформировать_лот_Начало':'//span/a[contains(text(), "Сформировать лот")]',
       'Подготовка_к_вводу_количества':'(//div[@class="lot-setup__manual-input"])[1]', 'Подготовка_к_вводу_Суммы':'//div[@class="lot-setup__manual-input"][last()]',
       'Сформировать_лот_Поле_количествo_интернет':'(//input)[1]', 'Сформировать_лот_Поле_Сумма':'(//input)[2]',
       'Сформировать_лот_Поле_количествo_минуты':'(//input)[1]', 'Сформировать_лот_Поле_Сумма':'(//input)[2]',
       'Сформировать_лот_Продолжить':'//div/a[contains(text(), "Продолжить")]', 'Подписаться_как':'//label',
       'Сформировать_лот_Smile1':'(//div[@class="emoji-field__available-values-block"]/img)[1]', 'Сформировать_лот_Smile2':'(//div[@class="emoji-field__available-values-block"]/img)[2]',
       'Сформировать_лот_Smile3':'(//div[@class="emoji-field__available-values-block"]/img)[3]', 'Сформировать_лот_Smile4':'(//div[@class="emoji-field__available-values-block"]/img)[4]',
       'Сформировать_лот_Smile5':'(//div[@class="emoji-field__available-values-block"]/img)[5]', 'Сформировать_лот_Smile6':'(//div[@class="emoji-field__available-values-block"]/img)[4]',
       'Сформировать_лот_Smile7':'(//div[@class="emoji-field__available-values-block"]/img)[7]', 'Сформировать_лот_Smile8':'(//div[@class="emoji-field__available-values-block"]/img)[4]',
       'Удаление_лота_количество_интернет':'(//div[@class="my-lot-item__info_specs" and contains(text(), "ГБ за")])[last()]',
       'Удаление_лота_количество_минуты':'(//div[@class="my-lot-item__info_specs" and contains(text(), "минут за")])[last()]',
       'Удаление_лота_начало_минуты':'(//div[@class="my-lot-item__info_specs" and contains(text(), "минут за")])[last()]/../../div/a/i',
       'Удаление_лота_начало_интернет':'(//div[@class="my-lot-item__info_specs" and contains(text(), "ГБ за")])[last()]/../../div/a/i',
       # 'Нет_активных_лотов':'//div[@class="exchange-block__message" and text()="У вас нет активных лотов в продаже. Разместите новый лот."]',
       'Редактирования_лота_Отозвать': '//div/a[contains(text(), "Отозвать лот")]', 'Редактирования_лота_Отозвать_Подтверждение': '//span/a[contains(text(), "Отозвать лот")]',
       'Мой_Tele2':'//span[contains(text(), "Мой Tele2")]', 'Мой_Tele2_номер':'//span[contains(text(), "Мой Tele2")]/span', 'icon-profile':'//span[@class="ico icon-profile"]',
       'Войти':'//span[contains(text(),"Войти")]',
       'Остатки_НаАватаре_минуты':'(//div[@class="profile-popup_rest"]/span/span)[1]', 'Остатки_НаАватаре_интернет':'(//div[@class="profile-popup_rest"]/span/span)[2]',
       'Остатки_lk_минуты':'//span[@class="remnant calls"]', 'Остатки_lk_интернет':'//span[@class="remnant internet"]',
       'Выбор_типа_лота_интернет':'(//span[@class="radio-label"])[1]', 'Выбор_типа_лота_минуты':'(//span[@class="radio-label"])[2]',
       'Кнопка_закрытия_окна':'//a[contains(@class, "icon-close")]',
       'Баланс_lk':'//span[@class="number"]'
       }
url={'url_Мои_лоты':'https://yar.tele2.ru/stock-exchange/my',
     'url_интернет':'https://yar.tele2.ru/stock-exchange/internet', #интернет
     'url_минуты':'https://yar.tele2.ru/stock-exchange/calls',           # минуты
     'url_lk':'https://yar.tele2.ru/lk'
     }


СохранитьЗначениеКлючаРеестра('login', '9535248000')
# СохранитьЗначениеКлючаРеестра('password', '')
phone = ПолучитьЗначениеКлючаРеестра('login', '9535248000')
# password = "" #ПолучитьЗначениеКлючаРеестра('password', '')


# восстановление из реестра
for Current_phone in var["Телефоны"].keys():
    var["Телефоны"][Current_phone]['ПродаватьС']=ПолучитьЗначениеКлючаРеестра(Current_phone+'ПродаватьС', 0, float)

while True:
    ВсегоНомеровСПродажей = var["Всего_на_продажу_интернет"] = var["Всего_на_продажу_минуты"] = 0

    for Current_phone in var["Телефоны"].keys():
        Акстивность, ПродаватьС=var["Телефоны"][Current_phone].get('Активная_симка', False), var["Телефоны"][Current_phone].get('ПродаватьС',0)
        log (f'\n{Current_phone} Активная_симка:{Акстивность} использовать с:{time.ctime(ПродаватьС)}')
        if  not Акстивность or not (time.time() > ПродаватьС):
            continue
        ВсегоНомеровСПродажей +=1
            
        log(f'Начало переключения на номер {Current_phone} {var["Телефоны"][Current_phone]["Name"]}')

        if not open_url(url['url_lk'], xpath['Войти']+';' + xpath['xpath_phone'] + ';' + xpath['Мой_Tele2'], 2):
            time.sleep(600)
            continue

        if xpath_last_element_html in [xpath['Войти'], xpath['xpath_phone']]:
            #  авторизация
            if (isXpath(xpath['xpath_phone']) or Press_Button('Войти', 1)) \
                    and Past_Value('xpath_phone', phone, 0.5) \
                    and Press_Button('xpath_next_login', 5):
                #         and Press_Button('//button[text()="Вход по паролю"]', 1) \
                #         and Past_Value('//input[@id="keycloakAuth.password"]', password, 0.5):

                #         ожидание входа человеком
                log ('Ожидание входа человеком')
                while not isXpath(xpath['Мой_Tele2']):
                    time.sleep(20)

        phone_format = Current_phone[0:3]+' '+Current_phone[3:6]+' '+Current_phone[6:8]+' '+Current_phone[8:10]
        if isXpath(f'//button/h1[contains(text(),"{phone_format}")]'):
            log(f'Номер {Current_phone} уже выбран из списка управляемых номеров!')
        elif open_url(url['url_lk'], xpath['Мой_Tele2'], 2, error_xpath='//div[@class="data-unavailable-message lk-new error-message"]') and click('//span[contains(@class, "dashboard-number__icon")]') and sleep(1)\
            and click(f'//li/button/h3[contains(text(),"{phone_format}")]/..', 10) and wait_elements_xpath(f'//button/h1[contains(text(),"{phone_format}")]', 30) and wait_elements_xpath(xpath['Баланс_lk'], 30):
            log(f'Успешное переключение на номер {Current_phone} баланс {xpath_last_element_text} руб.')
        else:
            log(f'Неудалось переключиться на номер {Current_phone}. Переход к следущему номеру черех 3 минуты.')
            time.sleep(180)
            continue

        if isXpath(xpath['Мой_Tele2_номер']):
            Current_phone2 = last_element_html.text.replace(' ', '')
            if Current_phone2 != Current_phone:
                log(f'Не корректное переключение на {Current_phone} на экране ЛК {Current_phone2}')
                winsound.MessageBeep()
                winsound.MessageBeep()
                time.sleep(200)
                continue


        #     Обновление остатков
        if var["Телефоны"][Current_phone].get('ОбновитьОстатки', True):
            if not Получить_доступные_остатки():
                log(f'По {Current_phone} не получены остатки! Переход к следущему номеру.')
                time.sleep(20)
                continue
        else:
            log(f'Остатки {Current_phone} без обновления: {var["Телефоны"][Current_phone]["Остатки_интернет"]} Гб {var["Телефоны"][Current_phone]["Остатки_минуты"]} минут')

        Удаление_всех_лотов(10)

        #  Проверка есть ли что продавать и обновление "ПродаватьС"
        if ((var['Телефоны'][Current_phone]['Остатки_интернет']<=var['Телефоны'][Current_phone]['Оставлять_интернет']) or (var['Телефоны'][Current_phone]['Оставлять_интернет'])==-1) \
                and ((var['Телефоны'][Current_phone]['Остатки_минуты']<=var['Телефоны'][Current_phone]['Оставлять_минуты']) or (var['Телефоны'][Current_phone]['Оставлять_минуты']==-1)) \
                and var["Телефоны"][Current_phone]['Выставлное_количествo_интернет']==var["Телефоны"][Current_phone]['Выставлное_количествo_минуты']==0:

            if var['Телефоны'][Current_phone].get('День_обновления_остатков', 0) == 0:
                log(f'Не задан день обновления баланса.')
            else:
                Сегодня = datetime.datetime.now()
                ДатаОбновленияБаланса = datetime.datetime(Сегодня.year, Сегодня.month, var['Телефоны'][Current_phone]['День_обновления_остатков'])
                if ДатаОбновленияБаланса < Сегодня: # обновление будет в следующем месяце
                    days_in_month = calendar.monthrange(ДатаОбновленияБаланса.year, ДатаОбновленияБаланса.month)[1]
                    ДатаОбновленияБаланса += datetime.timedelta(days=days_in_month)

                ДатаОбновленияБаланса_int=int(time.mktime(ДатаОбновленияБаланса.timetuple()))
                var["Телефоны"][Current_phone]['ПродаватьС'] = ДатаОбновленияБаланса_int
                СохранитьЗначениеКлючаРеестра(Current_phone+'ПродаватьС', ДатаОбновленияБаланса_int, winreg.REG_DWORD)
                log(f'Новая дата обновления баланса {Current_phone} {time.ctime(ДатаОбновленияБаланса_int)}')

            log(f'Нет ресурсов для продажи. Переход к следущему номеру.\n')
            continue

        ВыставитьЛоты('интернет')
        ВыставитьЛоты('минуты')
        time.sleep(2)

    log('Итоги:')
    pprint.pprint(var["Телефоны"])
    if ВсегоНомеровСПродажей==0:
        near_data=9999999999
        for Current_phone in var["Телефоны"].keys():
            ПродаватьС = var["Телефоны"][Current_phone].get('ПродаватьС', 0)
            if var["Телефоны"][Current_phone].get('Активная_симка', False) and near_data > ПродаватьС > 0:
                near_data = ПродаватьС
        log(f'Все продано! Ближаящая работа {time.ctime(near_data)}')
        brauzer.quit()
        time.sleep(near_data-time.localtime())
        Перезапуск_Браузера(ГлаыныйНомер+'.Profiles_Firefox')

    log(f'Всего выставлено на продажу {var["Всего_на_продажу_минуты"]*var["Стоимость_1_ед_минуты"] + var["Всего_на_продажу_интернет"]*var["Стоимость_1_ед_интернет"]} руб. {var["Всего_на_продажу_минуты"]} минут {var["Всего_на_продажу_интернет"]} Гб')
    log(f'{time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())} Пауза {var["Пауза_между_выставлений_лотов_сек"]} сек. ВсегоНомеровСПродажей={ВсегоНомеровСПродажей}')
    time.sleep(var['Пауза_между_выставлений_лотов_сек'])


            #  УДАЛИТЬ

            # if isXpath(xpath['Мой_Tele2_номер']):
            #     Current_phone = last_element_html.text.replace(' ', '')
            #     if not Current_phone in var:
            #         var.update({Current_phone:{}})
            #     if Current_phone == '':
            #         log (f'Не удалось найти "Мой_Tele2_номер" на странице {brauzer.current_url}')
            #         time.sleep(20)
            #         continue
            # else:
            #     log (f'Не удалось найти "Мой_Tele2_номер" на странице {brauzer.current_url}')
            #     time.sleep(20)
            #     continue
