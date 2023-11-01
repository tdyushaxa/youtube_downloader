import os

from pyrogram import Client,types,filters
from pytube import YouTube
from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton

app = Client(name='downloader',api_id=api_id,api_hash=api_hash,bot_token=bot_token)

@app.on_message(filters.command('start'))
async def CommandStart(client:app,msg:types.Message):
    chat_id  = msg.chat.id
    await app.send_message(chat_id,text=f'Salom {msg.from_user.first_name} {msg.from_user.last_name} hush kelibsiz '
                                f'!')
    await app.send_message(chat_id,text=f'Menga url yuboring. Men sizga videoni yuklab beraman ')

@app.on_message(filters.regex('https://youtu'))
async def get_url(client:app,msg:types.Message):
    global yt
    yt = YouTube(url=msg.text)
    title = yt.title
    auhtor = yt.author
    image = yt.thumbnail_url
    views  = yt.views
    s = yt.streaming_data.get('formats')[0].get('approxDurationMs')
    seconds, milliseconds = divmod(int(s), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    message = f"""
title - {title}
👁 - {views}
👤 - {auhtor}
🕒 - {time_string}
    """
    video = yt.streams.filter(progressive=True)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text=i.resolution,callback_data=str(i.itag))
            for i in yt.streams.filter(progressive=True)
        ]
    ])
    await app.send_photo(chat_id=msg.chat.id,photo=image,caption=message,reply_markup=keyboard)

@app.on_callback_query()
async def get_video(client:app,call:types.CallbackQuery):
    data = call.data
    await call.answer('vido yuklanmoqda',cache_time=60)
    message = f"""
📥 Downloading: ⏳
◻️ uploading to telegram...   
"""
    msg = await app.send_message(call.from_user.id,message)
    a = yt.streams.get_by_itag(itag=int(data)).download(output_path='users',filename=f'{call.from_user.id}.mp4')
    print(a)

    down_msg =  f"""
✅ Downloading: 
⏳ uploading to telegram...   
    
    """

    if a:
        s = await app.edit_message_text(call.from_user.id,msg.id,down_msg)
        path  = f'users/{call.message.chat.id}.mp4'
        async def progress(current, total):
            print(f"{current * 100 / total:.1f}%")
        await app.send_video(chat_id=call.from_user.id,video=path,progress=progress,has_spoiler=True)
        await app.delete_messages(call.from_user.id,s.id)
        os.remove(f'users/{call.from_user.id}.mp4')
app.run()