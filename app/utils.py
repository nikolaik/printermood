
def top_emotion(emotions):
    if type(emotions) != dict or len(emotions) == 0:
        return None

    return sorted(emotions.items(), key=lambda x: x[1], reverse=True)[0]
