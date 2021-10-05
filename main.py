from telegram import ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import *
from Courses import Map_Courses
YEAR, SEMESTER, COURSE, WEEK = range(4)


# starts the conversation
def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = ['שנה א', 'שנה ב', 'שנה ג']  # start the conversation and ask the user about his year of study
    buttons = [[InlineKeyboardButton(text=value, callback_data=value) for value in reply_keyboard]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text="ברוך הבא " + update.message.from_user.first_name + "\n" + "בחר שנת לימודים",
                              reply_markup=keyboard)
    return YEAR


# after the user pressed on some year
def year_handler(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    reply_keyboard = ['סמסטר א', 'סמסטר ב']
    year_number = update.callback_query.data  # save the year that was pressed
    context.user_data[YEAR] = year_number
    buttons = [[InlineKeyboardButton(text=value, callback_data=value) for value in reply_keyboard]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text(text=year_number + ":", reply_markup=keyboard)
    return SEMESTER


# after the user pressed on some semester
def semester_handler(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    semester_number = update.callback_query.data  # save the semester that was pressed
    if semester_number == "שנה א" or semester_number == "שנה ב" or semester_number == "שנה ג":  # pressed on year button
        return year_handler(update, context)
    if semester_number == "syllabus" or semester_number == "drive":  # user pressed on syllabus or drive button
        return week_handler(update, context)
    if semester_number.isnumeric() and int(semester_number) <= 20:  # if user pressed on one of the weeks buttons
        return week_handler(update, context)
    context.user_data[SEMESTER] = semester_number
    year = context.user_data[YEAR]  # year will be the year the user chose
    semester = context.user_data[SEMESTER]  # semester will be the semester the user chose
    spec_map = {}  # initialize new map
    for k, v in Map_Courses.items():  # run over the Map_Courses items
        if v['year'] == year and v['semester'] == semester:
            spec_map[k] = v['name']  # put in spec_map the matching courses according to year and semester
    buttons = [[InlineKeyboardButton(text=value, callback_data=key)] for key, value in spec_map.items()]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text(text=semester_number + ":", reply_markup=keyboard)
    return COURSE


# after the user pressed on some course
def course_handler(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer()
    course_number = update.callback_query.data  # save the course that was pressed
    if course_number == "שנה א" or course_number == "שנה ב" or course_number == "שנה ג":  # user pressed on year button
        return year_handler(update, context)
    if course_number == "סמסטר א" or course_number == "סמסטר ב":  # if user pressed on semester button
        return semester_handler(update, context)
    if course_number == "syllabus" or course_number == "drive":  # if user pressed on syllabus or drive button
        return week_handler(update, context)
    if course_number.isnumeric() and int(course_number) <= 20:  # if user pressed on one of the weeks buttons
        return week_handler(update, context)
    context.user_data[COURSE] = course_number
    size = Map_Courses[course_number]['size']
    buttons = [[InlineKeyboardButton(text='שבוע ' + str(value), callback_data=(value)),
                InlineKeyboardButton(text='שבוע ' + str(value + 1), callback_data=(value + 1)),
                InlineKeyboardButton(text='שבוע ' + str(value + 2), callback_data=(value + 2))] for value in
               range(1, 3 * (size // 3) + 1, 3)]
    buttons.insert(size // 3, [InlineKeyboardButton(text='שבוע ' + str(value), callback_data=value) for value in
                               range(3 * (size // 3) + 1, size + 1)])
    buttons.insert(0, [InlineKeyboardButton(text='סילבוס', callback_data="syllabus")])
    buttons.insert(1, [InlineKeyboardButton(text='דרייב של הקורס', callback_data="drive")])
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text(text=Map_Courses[course_number]["name"] + ":", reply_markup=keyboard)
    return WEEK


# after the user pressed on some week
def week_handler(update: Update, context: CallbackContext) -> int:
    chat_id = update.callback_query.message.chat_id  # get the chat's id
    update.callback_query.answer()
    week_number = update.callback_query.data  # save the week number that was pressed in week_number
    course_number = context.user_data[COURSE]  # course_number will be the course the user chose
    if week_number == "שנה א" or week_number == "שנה ב" or week_number == "שנה ג":  # if user pressed on year button
        return year_handler(update, context)
    if week_number == "סמסטר א" or week_number == "סמסטר ב":  # if user pressed on semester button
        return semester_handler(update, context)
    if week_number == "syllabus":  # if user pressed on syllabus button
        context.bot.send_message(text='סילבוס:\n' + Map_Courses[course_number]['syllabus'], chat_id=chat_id)
    elif week_number == "drive":  # if user pressed on drive button
        context.bot.send_message(text='דרייב:\n' + Map_Courses[course_number]['drive'], chat_id=chat_id)
    elif int(week_number) > 20:  # if user pressed on course button
        return course_handler(update, context)
    else:  # user pressed on one of the weeks buttons
        context.bot.send_message(text="הקבצים של שבוע " + str(week_number) + " בהעלאה. רק שנייה...", chat_id=chat_id)
        try:  # upload the lecture of the chosen week
            context.bot.send_message(text="הרצאה:", chat_id=chat_id)
            with open("courses_summaries/" + course_number + "/l" + week_number + ".pdf", "rb") as file:
                context.bot.send_document(chat_id=chat_id, document=file,
                                          filename=Map_Courses[course_number]['name'] + ' הרצאה ' + week_number + ".pdf",
                                          timeout=1000)
        except FileNotFoundError:  # there was no lecture in the chosen week
            context.bot.send_message(text="לא הייתה הרצאה בשבוע זה", chat_id=chat_id)
        try:  # upload the exercise of the chosen week
            context.bot.send_message(text="תרגול:", chat_id=chat_id)
            with open("courses_summaries/" + course_number + "/e" + week_number + ".pdf", "rb") as file:
                context.bot.send_document(chat_id=chat_id, document=file,
                                          filename=Map_Courses[course_number]['name'] + ' תרגול ' + week_number + ".pdf",
                                          timeout=1000)
        except FileNotFoundError:  # there was no exercise in the chosen week
            context.bot.send_message(text="לא היה תרגול בשבוע זה", chat_id=chat_id)


# cancels and ends the conversation
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('להתראות.\nמקווה שעזרתי לך.\n', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END  # end conversation


# runs the bot
def main() -> None:
    updater = Updater('____confidential____')  # create updater and pass it the bot's token.
    dispatcher = updater.dispatcher  # the dispatcher handles the updates and dispatches them to the handlers
    conv_handler = ConversationHandler(  # add conversation handler with the states YEAR, COURSE, SEMESTER and WEEK
        entry_points=[CommandHandler('start', start)],
        states={
            YEAR: [CallbackQueryHandler(year_handler)],
            COURSE: [CallbackQueryHandler(course_handler)],
            SEMESTER: [CallbackQueryHandler(semester_handler)],
            WEEK: [CallbackQueryHandler(week_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True  # allows to restart the conversation in any time
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()  # starts polling updates from Telegram
    updater.idle()  # blocks until one of the signals are received and stops the updater (SIGINT, SIGTERM, SIGABRT)


if __name__ == "__main__":
    main()

