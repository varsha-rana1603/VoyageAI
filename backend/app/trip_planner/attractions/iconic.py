KYOTO_ICONIC = {

    "Fushimi Inari Shrine": 1.0,

    "Kiyomizu-dera": 1.0,

    "Arashiyama Bamboo Grove": 1.0,

    "Kinkaku-ji": 1.0,

}

def get_iconic_score(
    attraction_name,
    destination_name
):

    if destination_name == "Kyoto":

        return KYOTO_ICONIC.get(
            attraction_name,
            0.2
        )

    return 0.2