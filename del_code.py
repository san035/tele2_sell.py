# path_FirefoxProfile = os.environ.get('APPDATA') +  os.path.join('\Mozilla\Firefox\Profiles')
# buttun = sleep_or_press_keyboard(500,
#                                  {'esc':f' - отмена, не использовать профиль {profile}',
#                                   '1':f' - скопировать профиль {profile} из {path_FirefoxProfile}'})
# if not buttun or buttun == 'esc':
#     return None
#
# #  копируем папку path_FirefoxProfile
# # поиск нужного профиля
# Profile_is_found = False
# for dir in os.listdir(path_FirefoxProfile):
#     dir = os.path.join(path_FirefoxProfile, dir)
#     if os.path.isdir(dir) and os.path.splitext(dir)[1] == '.default-release':
#         Profile_is_found = True
#         break
# if not Profile_is_found:
#     log(f'Не найден профиль Firefox {path_FirefoxProfile}*.default-release')
#     return None
#
# path_FirefoxProfile = dir
#
# log(f'Начало копирования профиля Firefox {path_FirefoxProfile} в {profile}')
# try:
#     shutil.copytree(path_FirefoxProfile, profile)
#     log('Профиль Firefox скопирован.')
# except Exception as err:
#     log(f'Ошибка копирования {err}.')
#     os.rmdir(path_FirefoxProfile)
#     return None


СпособыПолученяОстатков = ['lk']  # ,'НаАватаре'
for СпособПолученияОстатков in СпособыПолученяОстатков:
    if СпособПолученияОстатков == 'НаАватаре':
        if not isXpath(xpath['icon-profile']):  # icon-profile Мой_Tele2_номер
            open_url(url['url_Мои_лоты'], xpath['Войти'] + ';' + xpath['Мой_Tele2'], 2, update=True)

        if not Press_Button(xpath['icon-profile']):
            log('Остатки Гб и Мин не прочитаны.')
            break

        ActionChains(brauzer).move_to_element(last_element_html).perform()  # наведение
        time.sleep(0.1)

    elif СпособПолученияОстатков == 'lk':

