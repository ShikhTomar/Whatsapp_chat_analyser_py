import re
import pandas as pd


def preprocess(data):
    pattern = r'\d{2}/\d{2}/\d{4},\s\d{2}:\d{2}\s-\s'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date to datetime objects
    df['message_date'] = pd.to_datetime(df['message_date'].str.replace(' - ', ''), format='%d/%m/%Y, %H:%M')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages_list = []

    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if len(entry) > 2:
            users.append(entry[1])
            messages_list.append(entry[2])
        else:
            users.append('group_notification')
            messages_list.append(entry[0])

    df['user'] = users
    df['message'] = messages_list
    df.drop(columns=['user_message'], inplace=True)

    # --- Corrected Date Extractions ---
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['only_date'] = df['date'].dt.date
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # FIX: Use .dt.day_name() instead of .dt.day
    df['day_name'] = df['date'].dt.day_name()

    # Create the Period column for the heatmap
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df