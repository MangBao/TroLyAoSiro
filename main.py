import os
import playsound
import speech_recognition as sr
import time
import wikipedia
import datetime
import json
import webbrowser
import requests
import re
import operator
import subprocess
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from time import strftime
from gtts import gTTS
from wikipedia.wikipedia import languages
from youtube_search import YoutubeSearch
from difflib import get_close_matches
import json
from random import choice


wikipedia.set_lang('vi')
languages = 'vi'
path = ChromeDriverManager().install()
dataNormalChat = json.load(open('data/NormalChat.json', encoding='utf-8'))
dataApp = json.load(open('data/ListApplication.json', encoding='utf-8'))

# Dùng Google Cloud Text To Speech để chuyển văn bản thành âm thanh
def speak(txt):
    print('Siro: {}'.format(txt))
    tts = gTTS(text=txt, lang=languages, slow=False)
    filename = r"E:/TroLyAoSiro/sound.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

# Chuyển âm thanh thành văn bản
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Tôi: ", end='')
        audio = r.listen(source, phrase_time_limit=5)
        try:
            text = r.recognize_google(audio, language="vi-VN")
            print(text)
            return text
        except:
            print("...")
            return 0

def stop():
    speak("Hẹn gặp lại bạn sau!")

def get_text():
    for i in range(3):
        text = get_audio()
        if text:
            return text.lower()
        elif i < 2:
            speak("Siro không nghe rõ. Bạn nói lại được không!")
    time.sleep(2)
    stop()
    return 0

def hello(name):
    day_time = int(strftime('%H'))
    if day_time < 12:
        speak("Chào buổi sáng bạn {}. Chúc bạn một ngày tốt lành.".format(name))
    elif 12 <= day_time < 18:
        speak("Chào buổi chiều bạn {}. Bạn cần tôi giúp gì nhỉ?".format(name))
    else:
        speak("Chào buổi tối bạn {}. Bạn cần tôi giúp gì nhỉ?".format(name))

def get_time(text):
    now = datetime.datetime.now()
    if "giờ" in text:
        speak('Bây giờ là %d giờ %d phút' % (now.hour, now.minute))
    elif "ngày" in text:
        speak("Hôm nay là ngày %d tháng %d năm %d" % (now.day, now.month, now.year))    
    else:
        speak("Siro chưa hiểu ý của bạn. Bạn nói lại được không?")

def open_application(text):
    flag = False
    for key in dataApp:
        if key in text:
            flag = True
            speak("Đã mở " + key)
            subprocess.call('start ' + dataApp[key], shell = True)
            break
    if flag == False:
        speak("Ứng dụng chưa được cài đặt. Bạn hãy thử lại!")

def close_application(text):
    flag = False
    for key in dataApp:
        if key in text:
            flag = True
            temp = subprocess.call('taskkill /im ' + dataApp[key] + " >nul 2>&1", shell = True)
            if temp != 0:
                speak("Không có cửa số " + key + " đang mở. Bạn hãy thử lại!")
            else:
                speak("Đã đóng " + key)
            break
    if flag == False:
        speak("Ứng dụng chưa được cài đặt. Bạn hãy thử lại!")

def open_website(text):
    reg_ex = re.search('mở (.+)', text)
    if reg_ex:
        domain = reg_ex.group(1)
        url = 'https://www.' + domain
        webbrowser.open(url)
        speak("Trang web bạn yêu cầu đã được mở.")
        return True
    else:
        return False

def reply(text):
    if text in dataNormalChat:
        response =  dataNormalChat[text]
    else:
        text = get_close_matches(text, dataNormalChat.keys(), n=2, cutoff=0.6)
        if len(text)==0: return "None"
        speak(choice(dataNormalChat[text[0]]))
        return 1
    speak(choice(response))
    return 1

def open_google_and_search(text):
    search_for = text.split("kiếm", 1)[1]
    speak('Okay!')
    driver = webdriver.Chrome(path)
    driver.get("http://www.google.com")
    que = driver.find_element_by_xpath("//input[@name='q']")
    que.send_keys(str(search_for))
    que.send_keys(Keys.RETURN)

def current_weather():
    speak("Bạn muốn xem thời tiết ở đâu ạ.")
    ow_url = "http://api.openweathermap.org/data/2.5/weather?"
    city = get_text()
    if not city:
        pass
    api_key = "fe8d8c65cf345889139d8e545f57819a"
    call_url = ow_url + "appid=" + api_key + "&q=" + city + "&units=metric"
    response = requests.get(call_url)
    data = response.json()
    if data["cod"] != "404":
        city_res = data["main"]
        current_temperature = city_res["temp"]
        current_pressure = city_res["pressure"]
        current_humidity = city_res["humidity"]
        suntime = data["sys"]
        sunrise = datetime.datetime.fromtimestamp(suntime["sunrise"])
        sunset = datetime.datetime.fromtimestamp(suntime["sunset"])
        wthr = data["weather"]
        weather_description = wthr[0]["description"]
        now = datetime.datetime.now()
        content = """
        Hôm nay là ngày {day} tháng {month} năm {year}
        Mặt trời mọc vào {hourrise} giờ {minrise} phút
        Mặt trời lặn vào {hourset} giờ {minset} phút
        Nhiệt độ trung bình là {temp} độ C
        Áp suất không khí là {pressure} héc tơ Pascal
        Độ ẩm là {humidity}%
        Trời hôm nay quang mây. Dự báo mưa rải rác ở một số nơi.""".format(day=now.day, month=now.month, year=now.year,
                                                                            hourrise=sunrise.hour,
                                                                            minrise=sunrise.minute,
                                                                            hourset=sunset.hour, minset=sunset.minute,
                                                                            temp=current_temperature,
                                                                            pressure=current_pressure,
                                                                            humidity=current_humidity)
        speak(content)
        time.sleep(20)
    else:
        speak("Không tìm thấy địa chỉ của bạn")

def play_song():
    speak('Xin mời bạn chọn tên bài hát')
    mysong = get_text()
    while True:
        result = YoutubeSearch(mysong, max_results=1).to_json()
        if result:
            break
    data = json.loads(result)

    for i in data['videos']:
        print(i['id'])
        webbrowser.open('https://www.youtube.com/watch?v=' + i['id'])

    speak("Bài hát bạn yêu cầu đã được mở.")

def tell_me_about():
    try:
        speak("Bạn muốn nghe về gì ạ")
        text = get_text()
        contents = wikipedia.summary(text).split('\n')
        speak("Theo wikimedia " + contents[0])
        time.sleep(10)
        for content in contents[1:]:
            speak("Bạn muốn nghe thêm không")
            ans = get_text()
            if "có" not in ans:
                break
            speak(content)
            time.sleep(10)

        speak('Cảm ơn bạn đã lắng nghe!!!')
    except:
        speak("Siro không định nghĩa được thuật ngữ của bạn. Xin mời bạn nói lại")

def get_operator_fn(op):
    return {
        '+' : operator.add,
        '-' : operator.sub,
        'trừ' : operator.sub,
        'x' : operator.mul,
        'nhân' : operator.mul,
        '/' :operator.__truediv__,
        'chia' :operator.__truediv__,
        'mũ' : operator.pow,
        }[op]

def eval_binary_expr(op1, oper, op2):
    op1,op2 = float(op1), float(op2)
    return get_operator_fn(oper)(op1, op2)

def help_me():
    speak("""Siro có thể giúp bạn thực hiện các câu lệnh sau đây:
    1. Chào hỏi
    2. Hiển thị giờ
    3. Mở website
    4. Tìm kiếm trên Google
    5. Đóng/Mở ứng dụng
    6. Dự báo thời tiết
    7. Mở video nhạc
    8. Tính toán
    9. Kể bạn biết về thế giới""")

def assistant():
    speak("Xin chào, bạn tên là gì nhỉ?")
    name = get_text()
    if name:
        speak("Chào bạn {}".format(name))
        speak("Bạn cần Siro giúp gì ạ?")
        while True:
            text = get_text()
            if not text:
                break
            elif "dừng" in text or "tạm biệt" in text or "bye Siro" in text or "ngủ thôi" in text:
                stop()
                break
            elif "có thể làm gì" in text:
                help_me()
            elif "+" in text or "-" in text or "/" in text or " x " in text or " mũ " in text or " chia " in text or " nhân " in text or " trừ " in text:
                temp = text.split()
                arg = []
                arg.append(temp[0])
                arg.append(temp[1])
                arg.append(temp[2])
                if arg[0].isnumeric() == False and arg[2].isnumeric() == False:
                    speak("Xin lỗi, phép tính này tôi không thực hiện được.")
                else:
                    result = arg[0] + " " + arg[1] + " " + arg[2]
                    speak(result + " bằng " + str(eval_binary_expr(*(arg))))
            elif "chào trợ lý ảo" in text:
                hello(name)
            elif "hiện tại" in text:
                get_time(text)
            elif "mở" in text:
                if 'mở tìm kiếm' in text:
                    open_google_and_search(text)
                elif "." in text:
                    open_website(text)
                else:
                    open_application(text)
            elif "đóng" in text:
                close_application(text)
            elif "thời tiết" in text:
                current_weather()
            elif "chơi nhạc" in text:
                play_song()
            elif "cho tôi biết" in text:
                tell_me_about()
            else:
                if reply(text) != 1:
                    speak("Xin lỗi nhưng tôi chưa hiểu yêu cầu của bạn. Bạn có thể nói lại được không?")

assistant()