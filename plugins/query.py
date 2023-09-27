import asyncio, re, ast, math, logging, random, pyrogram

# pyrogram functions
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums 
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid


from Script import script
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_all_files
from database.filters_mdb import del_all, find_filter, get_filters
from database.gfilters_mdb import find_gfilter, get_gfilters
from plugins.helper.admin_check import admin_fliter

# image editor tools
from image.edit_1 import bright, mix, black_white, g_blur, normal_blur, box_blur
from image.edit_2 import circle_with_bg, circle_without_bg, sticker, edge_curved, contrast, sepia_mode, pencil, cartoon                             
from image.edit_3 import green_border, blue_border, black_border, red_border
from image.edit_4 import rotate_90, rotate_180, rotate_270, inverted, round_sticker, removebg_white, removebg_plain, removebg_sticker
from image.edit_5 import normalglitch_1, normalglitch_2, normalglitch_3, normalglitch_4, normalglitch_5, scanlineglitch_1, scanlineglitch_2, scanlineglitch_3, scanlineglitch_4, scanlineglitch_5

# configuration
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, PICS, IMDB, PM_IMDB, SINGLE_BUTTON, PROTECT_CONTENT, \
    SPELL_CHECK_REPLY, IMDB_TEMPLATE, IMDB_DELET_TIME, START_MESSAGE, PMFILTER, G_FILTER, BUTTON_LOCK, BUTTON_LOCK_TEXT, SHORT_URL, SHORT_API, HOW_TO_DOWNLOAD, SHORTNER_SITE, SHORTNER_API


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)



@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Tʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ!! Cᴏɴɴᴇᴄᴛ ᴛᴏ ꜱᴏᴍᴇ ɢʀᴏᴜᴘꜱ ғɪʀꜱᴛ.", quote=True)
                    return await query.answer(' ˆ°• ✰ мѕ ᴍᴏᴠᴠɪᴇꜱ࿐ •°ˆ ')
            else:
                await query.message.edit_text(
                    "Iᴀᴍ Nᴏᴛ Cᴏɴɴᴇᴄᴛᴇᴅ Tᴏ Aɴʏ Gʀᴏᴜᴩ \nCʜᴇᴄᴋ /connections Oʀ Cᴏɴɴᴇᴄᴛ Tᴏ Aɴʏ Gʀᴏᴜᴩ",
                    quote=True
                )
                return await query.answer(' ˆ°• ✰ мѕ ᴍᴏᴠᴠɪᴇꜱ࿐ •°ˆ ')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(' ˆ°• ✰ мѕ ᴍᴏᴠᴠɪᴇꜱ࿐ •°ˆ ')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Tʜᴀᴛ´s Nᴏᴛ Fᴏʀ Yᴏᴜ !!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("🚫 Dᴇʟᴇᴛᴇ 🚫", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("‹‹‹ Bᴀᴄᴋ", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(' ˆ°• ✰ мѕ ᴍᴏᴠᴠɪᴇꜱ࿐ •°ˆ ')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(' ˆ°• ✰ мѕ ᴍᴏᴠᴠɪᴇꜱ࿐ •°ˆ ')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Dɪsᴄᴏɴɴᴇᴄᴛᴇᴅ Fʀᴏᴍ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode="md")
        return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙷𝙰𝚁𝙴 𝙰𝙽𝙳 𝚂𝚄𝙿𝙿𝙾𝚁𝚃')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]        
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)       
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "galert" in query.data:
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]             
        reply_text, btn, alerts, fileid = await find_gfilter("gfilters", keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    
    if query.data.startswith("pmfile"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(mention=query.from_user.mention, file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)                                                                                                      
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"    
        try:                  
            if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.message.edit_text(
                f"Sᴏᴍᴇ Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(' ˆ°• ✰ мѕ ᴍᴏᴠᴠɪᴇꜱ࿐ •°ˆ ')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Sᴜᴄᴄᴇssғᴜʟʟʏ Cᴏɴɴᴇᴄᴛɪᴏɴ Dᴇʟᴇᴛᴇᴅ"
            )
        else:
            await query.message.edit_text(
                f"Sᴏᴍᴇ Eʀʀᴏʀ Oᴄᴄᴜʀᴇᴅ!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(' ˆ°• ✰ мѕ ᴍᴏᴠᴠɪᴇꜱ࿐ •°ˆ ')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer(' ˆ°• ✰ мѕ ᴍᴏᴠᴠɪᴇꜱ࿐ •°ˆ ')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                g = short_url(f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                await client.send_photo(chat_id=query.from_user.id, photo='https://graph.org/Thumbnail-08-25', caption = f"<b>📕Nᴀᴍᴇ ➠ : <code>{files.file_name}</code> \n\n🔗Sɪᴢᴇ ➠ : {get_size(files.file_size)}</b>", 
                                          reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('⁉️ Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ ⁉️', url=HOW_TO_DOWNLOAD)
                ],
                [
                    InlineKeyboardButton('📥 Dᴏᴡɴʟᴏᴀᴅ Nᴏᴡ 📥', url=g)
                ]]))
                await query.answer('Cʟɪᴄᴋ °Cʜᴇᴄᴋ Bᴏᴛ Pᴍ° Bᴜᴛᴛᴏɴ\n\nI Sᴇɴᴛᴇᴅ U ASᴋᴇᴅ Fɪʟᴇs', show_alert=True)
        except UserIsBlocked:
            await query.answer('Fɪʀsᴛ Sᴛᴀʀᴛ Mᴇ Tʜᴇɴ I Wɪʟʟ Sᴇɴᴅ Fɪʟᴇs !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("Fɪʀsᴛ Jᴏɪɴ Tʜᴇ Cʜᴀɴɴᴇʟ Aɴᴅ Cʟɪᴄᴋ Tʜɪs 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('Nᴏ Sᴜᴄʜ Fɪʟᴇ Exsɪsᴛ.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "pages":
        await query.answer()


    elif query.data == "removebg":
        await query.message.edit_text("**Select required mode**",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(text="ᴡɪᴛʜ ᴡʜɪᴛᴇ ʙɢ", callback_data="rmbgwhite"),
                InlineKeyboardButton(text="ᴡɪᴛʜᴏᴜᴛ ʙɢ", callback_data="rmbgplain"),
                ],[
                InlineKeyboardButton(text="ꜱᴛɪᴄᴋᴇʀ", callback_data="rmbgsticker"),
                ],[
                InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='photo')
             ]])
        )
    elif query.data == "stick":
        await query.message.edit("**Select a Type**",            
            reply_markup=InlineKeyboardMarkup( [[
               InlineKeyboardButton(text="ɴᴏʀᴍᴀʟ", callback_data="stkr"),
               InlineKeyboardButton(text="ᴇᴅɢᴇ ᴄᴜʀᴠᴇᴅ", callback_data="cur_ved"),
               ],[                    
               InlineKeyboardButton(text="ᴄɪʀᴄʟᴇ", callback_data="circle_sticker")
               ],[
               InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='photo')
               ]]                
           )
       )
    elif query.data == "rotate":
        await query.message.edit_text("**Select the Degree**",
            reply_markup=InlineKeyboardMarkup( [[
               InlineKeyboardButton(text="180", callback_data="180"),
               InlineKeyboardButton(text="90", callback_data="90")
               ],[
               InlineKeyboardButton(text="270", callback_data="270")
               ],[
               InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='photo')
               ]]
           )
       )
    elif query.data == "glitch":
        await query.message.edit_text("**Select required mode**",
            reply_markup=InlineKeyboardMarkup( [[
               InlineKeyboardButton(text="ɴᴏʀᴍᴀʟ", callback_data="normalglitch"),
               InlineKeyboardButton(text="ꜱᴄᴀɴ ʟᴀɪɴꜱ", callback_data="scanlineglitch")
               ],[
               InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='photo')
               ]]
           )
       )
    elif query.data == "normalglitch":
        await query.message.edit_text(text="**Select Glitch power level**",
           reply_markup=InlineKeyboardMarkup( [[
               InlineKeyboardButton(text="1", callback_data="normalglitch1"),
               InlineKeyboardButton(text="2", callback_data="normalglitch2"),
               InlineKeyboardButton(text="3", callback_data="normalglitch3"),
               ],[
               InlineKeyboardButton(text="4", callback_data="normalglitch4"),
               InlineKeyboardButton(text="5", callback_data="normalglitch5"),
               ],[
               InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='glitch')
               ]]
           )
       )
    elif query.data == "scanlineglitch":
        await query.message.edit_text("**Select Glitch power level**",
            reply_markup=InlineKeyboardMarkup( [[
               InlineKeyboardButton(text="1", callback_data="scanlineglitch1"),
               InlineKeyboardButton(text="2", callback_data="scanlineglitch2"),
               InlineKeyboardButton(text="3", callback_data="scanlineglitch3"),
               ],[
               InlineKeyboardButton(text="4", callback_data="scanlineglitch4"),
               InlineKeyboardButton(text="5", callback_data="scanlineglitch5"),
               ],[
               InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='glitch')
               ]]
           )
       )
    elif query.data == "blur":
        await query.message.edit("**Select a Type**",
            reply_markup=InlineKeyboardMarkup( [[
               InlineKeyboardButton(text="ʙᴏx", callback_data="box"),
               InlineKeyboardButton(text="ɴᴏʀᴍᴀʟ", callback_data="normal"),
               ],[
               InlineKeyboardButton(text="ɢᴀᴜꜱꜱɪᴏɴ", callback_data="gas")
               ],[
               InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='photo')
               ]]
           )
       )
    elif query.data == "circle":
        await query.message.edit_text("**Select required mode**",
            reply_markup=InlineKeyboardMarkup( [[
               InlineKeyboardButton(text="ᴡɪᴛʜ ʙɢ", callback_data="circlewithbg"),
               InlineKeyboardButton(text="ᴡɪᴛʜᴏᴜᴛ ʙɢ", callback_data="circlewithoutbg"),
               ],[
               InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='photo')
               ]]
           )
       )
    elif query.data == "border":
        await query.message.edit("**Select Border**",
            reply_markup=InlineKeyboardMarkup( [[
               InlineKeyboardButton(text="ʀᴇᴅ", callback_data="red"),
               InlineKeyboardButton(text="ɢʀᴇᴇɴ", callback_data="green"),
               ],[
               InlineKeyboardButton(text="ʙʟᴀᴄᴋ", callback_data="black"),
               InlineKeyboardButton(text="ʙʟᴜᴇ", callback_data="blue"),
               ],[                    
               InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='photo')   
               ]]                
           )
       )
    elif query.data == "bright":
        await bright(client, query.message)
    elif query.data == "mix":
        await mix(client, query.message)
    elif query.data == "b|w":
        await black_white(client, query.message)
    elif query.data == "circlewithbg":
        await circle_with_bg(client, query.message)
    elif query.data == "circlewithoutbg":
        await circle_without_bg(client, query.message)
    elif query.data == "green":
        await green_border(client, query.message)
    elif query.data == "blue":
        await blue_border(client, query.message)
    elif query.data == "red":
        await red_border(client, query.message)
    elif query.data == "black":
        await black_border(client, query.message)
    elif query.data == "circle_sticker":
        await round_sticker(client, query.message)
    elif query.data == "inverted":
        await inverted(client, query.message)
    elif query.data == "stkr":
        await sticker(client, query.message)
    elif query.data == "cur_ved":
        await edge_curved(client, query.message)
    elif query.data == "90":
        await rotate_90(client, query.message)
    elif query.data == "180":
        await rotate_180(client, query.message)
    elif query.data == "270":
        await rotate_270(client, query.message)
    elif query.data == "contrast":
        await contrast(client, query.message)
    elif query.data == "box":
        await box_blur(client, query.message)
    elif query.data == "gas":
        await g_blur(client, query.message)
    elif query.data == "normal":
        await normal_blur(client, query.message)
    elif query.data == "sepia":
        await sepia_mode(client, query.message)
    elif query.data == "pencil":
        await pencil(client, query.message)
    elif query.data == "cartoon":
        await cartoon(client, query.message)
    elif query.data == "normalglitch1":
        await normalglitch_1(client, query.message)
    elif query.data == "normalglitch2":
        await normalglitch_2(client, query.message)
    elif query.data == "normalglitch3":
        await normalglitch_3(client, query.message)
    elif query.data == "normalglitch4":
        await normalglitch_4(client, query.message)
    elif query.data == "normalglitch5":
        await normalglitch_5(client, query.message)
    elif query.data == "scanlineglitch1":
        await scanlineglitch_1(client, query.message)
    elif query.data == "scanlineglitch2":
        await scanlineglitch_2(client, query.message)
    elif query.data == "scanlineglitch3":
        await scanlineglitch_3(client, query.message)
    elif query.data == "scanlineglitch4":
        await scanlineglitch_4(client, query.message)
    elif query.data == "scanlineglitch5":
        await scanlineglitch_5(client, query.message)
    elif query.data == "rmbgwhite":
        await removebg_white(client, query.message)
    elif query.data == "rmbgplain":
        await removebg_plain(client, query.message)
    elif query.data == "rmbgsticker":
        await removebg_sticker(client, query.message)

    elif query.data == "pages":
        await query.answer("🤨 Wrong Click 🥴", show_alert=True)
    elif query.data == "howdl":
        try:
            await query.answer(script.HOW_TO_DOWNLOAD.format(query.from_user.first_name), show_alert=True)
        except:
            await query.message.edit(script.HOW_TO_DOWNLOAD.format(query.from_user.first_name))


    elif query.data == "start":                        
        buttons = [[
            InlineKeyboardButton("⭕  ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⭕", url=f"http://t.me/{temp.U_NAME}?startgroup=true")
            ],[
            InlineKeyboardButton("👑 ᴏᴡɴᴇʀ 👑", callback_data="owner_hun"), 
            InlineKeyboardButton("🛠️ sᴜᴘᴘᴏʀᴛ 🛠️", callback_data="support_karo")
            ],[      
            InlineKeyboardButton("⁉️ ʜᴇʟᴘ ⁉️", callback_data="help"),
            InlineKeyboardButton("📝 ᴀʙᴏᴜᴛ 📝", callback_data="about")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), START_MESSAGE.format(user=query.from_user.mention, bot=temp.B_LINK), enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    
    elif query.data == "photo":
        buttons = [[
            InlineKeyboardButton(text="ʙʀɪɢᴛʜ", callback_data="bright"),
            InlineKeyboardButton(text="ᴍɪxᴇᴅ", callback_data="mix"),
            InlineKeyboardButton(text="ʙ & ᴡ", callback_data="b|w"),
            ],[
            InlineKeyboardButton(text="ᴄɪʀᴄʟᴇ", callback_data="circle"),
            InlineKeyboardButton(text="ʙʟᴜʀ", callback_data="blur"),
            InlineKeyboardButton(text="ʙᴏʀᴅᴇʀ", callback_data="border"),
            ],[
            InlineKeyboardButton(text="ꜱᴛɪᴄᴋᴇʀ", callback_data="stick"),
            InlineKeyboardButton(text="ʀᴏᴛᴀᴛᴇ", callback_data="rotate"),
            InlineKeyboardButton(text="ᴄᴏɴᴛʀᴀꜱᴛ", callback_data="contrast"),
            ],[
            InlineKeyboardButton(text="ꜱᴇᴘɪᴀ", callback_data="sepia"),
            InlineKeyboardButton(text="ᴘᴇɴᴄɪʟ", callback_data="pencil"),
            InlineKeyboardButton(text="ᴄᴀʀᴛᴏᴏɴ", callback_data="cartoon"),
            ],[
            InlineKeyboardButton(text="ɪɴᴠᴇʀᴛ", callback_data="inverted"),
            InlineKeyboardButton(text="ɢʟɪᴛᴄʜ", callback_data="glitch"),
            InlineKeyboardButton(text="ʀᴇᴍᴏᴠᴇ ʙɢ", callback_data="removebg")
            ],[
            InlineKeyboardButton(text="❌✖️ ʟᴏᴄᴋ ✖️❌", callback_data="close_data")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)        
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), "Select your required mode from below!"),
            reply_markup=reply_markup,           
        )
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('😈 ᴀᴅᴍɪɴ 😈', callback_data='admin')            
            ],[
            InlineKeyboardButton('ᴍᴀɴᴜᴀʟ ꜰɪʟᴛᴇʀ', callback_data='manuelfilter'),
            InlineKeyboardButton('ᴀᴜᴛᴏ ꜰɪʟᴛᴇʀ', callback_data='autofilter'),
            InlineKeyboardButton('ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ', callback_data='coct')
            ],[                       
            InlineKeyboardButton('ᴛᴇʟᴇɢʀᴀᴘʜ', callback_data='tele'),
            InlineKeyboardButton('ꜱʜᴀʀᴇ-ᴛᴇxᴛ', callback_data='sharetxt'),
            InlineKeyboardButton('ꜰɪʟᴇ ꜱᴛᴏʀᴇ', callback_data='newdata')
            ],[           
            InlineKeyboardButton('ᴊꜱᴏɴᴇ', callback_data='son'),
            InlineKeyboardButton('ᴛᴛꜱ', callback_data='ttss'),           
            InlineKeyboardButton('ᴘᴜʀɢᴇ', callback_data='purges')
            ],[
            InlineKeyboardButton('ᴘᴀꜱᴛᴇ', callback_data='pastes'),
            InlineKeyboardButton("ɪᴍᴀɢᴇ", callback_data='image'),
            InlineKeyboardButton('ɪᴍᴀɢᴇ', callback_data='pings')                                   
            ],[                               
            InlineKeyboardButton('ᴍᴜᴛᴇ', callback_data='restric'),
            InlineKeyboardButton('ᴋɪᴄᴋ', callback_data='zombies'),
            InlineKeyboardButton('ᴘɪɴ', callback_data='pin')
            ],[
            InlineKeyboardButton('ᴄᴀʀʙᴏɴ', callback_data='carb'),
            InlineKeyboardButton('ꜰᴏɴᴅ', callback_data='fond'),
            InlineKeyboardButton('ʏᴛ-ᴅʟ', callback_data='ytdl')
            ],[
            InlineKeyboardButton('📊 ꜱᴛᴀᴛᴜꜱ 🔭', callback_data='stats')
            ],[
            InlineKeyboardButton('❌ ʟᴏᴄᴋ ❌', callback_data='close_data'),
            InlineKeyboardButton('🏡 ʜᴏᴍᴇ 🏡', callback_data='start')           
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)             
        await query.edit_message_media(  
            InputMediaPhoto(random.choice(PICS), script.EXTRAMOD_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,           
        )
    elif query.data == "about":
        buttons= [[
            InlineKeyboardButton('🔥 ᴍʏ ᴇɴᴇʀɢʏ 🔥', callback_data='source')
            ],[
            InlineKeyboardButton('🏡 ʜᴏᴍᴇ 🏡', callback_data='start'),
            InlineKeyboardButton('❌✖️ ʟᴏᴄᴋ ✖️❌', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)        
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.ABOUT_TXT.format(temp.B_NAME), enums.ParseMode.HTML),
            reply_markup=reply_markup,           
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('📞 ᴄᴏɴᴛᴀᴄᴛ 🐍', url='https://t.me/MS_Contact_RoBot')
            ],[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.SOURCE_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,            
        )
    elif query.data == "owner_hun":
        buttons = [[
            InlineKeyboardButton('📞 ᴄᴏɴᴛᴀᴄᴛ 🐍', url='https://t.me/MS_Contact_RoBot')
            ],[
            InlineKeyboardButton('🏡 ʜᴏᴍᴇ  🏡', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.OWNER_HUN, enums.ParseMode.HTML),
            reply_markup=reply_markup,            
        )
    elif query.data == "support_karo":
        buttons = [[
            InlineKeyboardButton('🔮ᴍᴀɪ ᴄʜᴀɴɴᴇʟ🔮', url='https://t.me/MS_Movvies')
            ],[
            InlineKeyboardButton('👥ɢʀᴏᴜᴘ👥', url='https://t.me/Movvies_Request')
            ],[
            InlineKeyboardButton('🏡 ʜᴏᴍᴇ  🏡', callback_data='start')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.SUPPORT_KARO, enums.ParseMode.HTML),
            reply_markup=reply_markup,            
        )
    elif query.data == "restric":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.RESTRIC_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,            
        )
    elif query.data == "image":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.IMAGE_TXT.format(temp.B_NAME), enums.ParseMode.HTML),            
            reply_markup=reply_markup,
        ) 
    elif query.data == "ytdl":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.YTDL, enums.ParseMode.HTML),            
            reply_markup=reply_markup,
        )  
    elif query.data == "sharetxt":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.SHARE_TXT, enums.ParseMode.HTML),           
            reply_markup=reply_markup,
        )      
    elif query.data == "zombies":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.ZOMBIES_TXT, enums.ParseMode.HTML),           
            reply_markup=reply_markup,
        )    
    elif query.data == "pin":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.PIN_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "son":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.JSON_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "pastes":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.PASTE_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "pings":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.PINGS_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "ttss":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.TTS_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "purges":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.PURGE_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "tele":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.TELE_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )             
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help'),
            InlineKeyboardButton('𝙱𝚄𝚃𝚃𝙾𝙽𝚂', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.MANUELFILTER_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.BUTTON_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.AUTOFILTER_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.CONNECTION_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )   

    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('𝙶𝙻𝙾𝙱𝙰𝙻 𝙵𝙸𝙻𝚃𝙴𝚁', callback_data='gfill'),
            InlineKeyboardButton('𝚄𝚂𝙴𝚁 & 𝙲𝙷𝙰𝚃', callback_data='uschat')
            ],[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        if query.from_user.id in ADMINS:
            await query.edit_message_media(InputMediaPhoto(random.choice(PICS), script.ADMIN_TXT, enums.ParseMode.HTML), reply_markup=reply_markup)
        else:
            await query.answer("ʏᴏᴜʀ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇʀ ⚠️", show_alert=True)

    elif query.data == "gfill":
        buttons = [[            
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)        
        await query.edit_message_media(InputMediaPhoto(random.choice(PICS), script.G_FIL_TXT, enums.ParseMode.HTML), reply_markup=reply_markup)
        
    elif query.data == "uschat":
        buttons = [[            
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)        
        await query.edit_message_media(InputMediaPhoto(random.choice(PICS), script.US_CHAT_TXT, enums.ParseMode.HTML), reply_markup=reply_markup)
       
    elif query.data == "carb":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.CARB_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )      
    elif query.data == "fond":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.FOND_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )       
    elif query.data == "newdata":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.FILE_TXT, enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help'),
            InlineKeyboardButton('♻️ ʀᴇꜰʀᴇꜱʜ ♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.STATUS_TXT.format(total, users, chats, monsize, free), enums.ParseMode.HTML),
            reply_markup=reply_markup,
        )
    elif query.data == "rfrsh":
        await query.answer("ꜰᴇᴛᴄʜɪɴɢ ᴅᴀᴛᴀ ꜰʀᴏᴍ ᴍʏ ʙᴏꜱꜱ ʜᴏᴍᴇ")
        buttons = [[
            InlineKeyboardButton('🔙 ʙᴀᴄᴋ 🔙', callback_data='help'),
            InlineKeyboardButton('♻️ ʀᴇꜰʀᴇꜱʜ ♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.edit_message_media(
            InputMediaPhoto(random.choice(PICS), script.STATUS_TXT.format(total, users, chats, monsize, free), enums.ParseMode.HTML),
            reply_markup=reply_markup,          
      )

    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))
        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return 
        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)
        settings = await get_settings(grpid)
        if settings is not None:
            buttons = [[
                InlineKeyboardButton('𝐅𝐈𝐋𝐓𝐄𝐑 𝐁𝐔𝐓𝐓𝐎𝐍', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                InlineKeyboardButton('𝐒𝐈𝐍𝐆𝐋𝐄' if settings["button"] else '𝐃𝐎𝐔𝐁𝐋𝐄',  callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('𝐁𝐎𝐓 𝐏𝐌', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["botpm"] else '❌ 𝐍𝐎', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],[                
                InlineKeyboardButton('𝐅𝐈𝐋𝐄 𝐒𝐄𝐂𝐔𝐑𝐄', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["file_secure"] else '❌ 𝐍𝐎',  callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('𝐈𝐌𝐃𝐁', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["imdb"] else '❌ 𝐍𝐎', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('𝐒𝐏𝐄𝐋𝐋 𝐂𝐇𝐄𝐂𝐊', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["spell_check"] else '❌ 𝐍𝐎', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],[
                InlineKeyboardButton('𝐖𝐄𝐋𝐂𝐎𝐌𝐄', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                InlineKeyboardButton('✅ 𝐘𝐄𝐒' if settings["welcome"] else '❌ 𝐍𝐎', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')               
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
