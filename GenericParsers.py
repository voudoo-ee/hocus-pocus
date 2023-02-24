import re

categories = [
    {"category": "Mahlad ja joogid", "sub-categories": ["Mahlad ja -kontsentraadid, siirupid", "Muud joogid",
                                                        "Alkoholivabad joogid", "Energiajoogid",
                                                        "Kakaod, kakaojoogid", "Karastusjoogid, toonikud", "Kohvid",
                                                        "Smuutid, värsked mahlad", "Spordijoogid"]},

    {"category": "Alkohoolsed joogid", "sub-categories": ["Long Drink", "Siider", "Ölled", "Kange Alkohol",
                                                          "Džinnid", "Konjakid, brändid", "Liköörid",
                                                          "Liköörveinid", "Muud kanged alkohoolsed joogid",
                                                          "Punased veinid", "Roosad veinid", "Rummid",
                                                          "Õlled, siidrid, segud, kokteilid",
                                                          "Šampanjad, vahuveinid"]},

    {"category": "Juust", "sub-categories": ["Juust", "Delikatessjuustud", "Juustud", "Määrdejuustud"]},
    {"category": "Külmutatud ja jahedad tooted", "sub-categories": ["KÜlmutatud Tooted",
                                                                    "Jahutatud valmistoidud",
                                                                    "Jogurtid, jogurtijoogid", "Jäätised",
                                                                    "Kohukesed", "Kohupiimad, kodujuustud",
                                                                    "Külmutatud liha- ja kalatooted",
                                                                    "Külmutatud köögiviljad, marjad, puuviljad",
                                                                    "Külmutatud tainad ja kondiitritooted",
                                                                    "Külmutatud valmistooted"]},

    {"category": "Kuivained", "sub-categories": ["Kuivained", "Hommikuhelbed, müslid, kiirpudrud", "Jahud",
                                                 "Kuivsupid ja -kastmed", "Leivad", "Maitseained", "Makaronid",
                                                 "Näkileivad", "Pähklid ja kuivatatud puuviljad", "Riisid", "Saiad",
                                                 "Saiakesed, stritslid, kringlid", "Sepikud, kuklid, lavašid",
                                                 "Sipsid"]},

    {"category": "Margariinid Ja õlid", "sub-categories": ["Margariinid Ja õlid", "Võid, margariinid",
                                                           "Õlid, äädikad"]},

    {"category": "Viljad ja muud värsked tooted", "sub-categories": ["Puu  Ja Juurviljad",
                                                                     "Köögiviljad, juurviljad",
                                                                     "Maitsetaimed, värsked salatid, piprad",
                                                                     "Salatid", "Seened", "Õunad, pirnid"]},

    {"category": "Munad", "sub-categories": ["Munad"]},

    {"category": "Piimatooted", "sub-categories": ["Piimatooted", "Suupisted (Piim)", "Piimad, koored"]},

    {"category": "Lihad ja kalatooted", "sub-categories": ["Grillvorstid, verivorstid", "Hakkliha",
                                                           "Keedu- ja suitsuvorstid, viinerid", "Linnuliha",
                                                           "Muud kalatooted", "Muud lihatooted", "Sealiha",
                                                           "Singid, rulaadid",
                                                           "Soolatud ja suitsutatud kalatooted",
                                                           "Sushi"]},

    {"category": "Hoidised", "sub-categories": ["Hoidised", "Ketšupid, tomatipastad, kastmed",
                                                "Majoneesid, sinepid"]},

    {"category": "Kommid ja muud magusad", "sub-categories": ["Kommikarbid", "Kommipakid",
                                                              "Koogid, rullbiskviidid, tainad", "Küpsised",
                                                              "Magusad hoidised", "Magustoidud",
                                                              "Maiustused, küpsised, näksid",
                                                              "Muud magustoidud", "Muud maiustused",
                                                              "Šokolaadid"]},

    {"category": "Lastetoidud", "sub-categories": ["Lastetoidud"]},

    {"category": "Maailma köök", "sub-categories": ["Maailma köök"]},

    {"category": "Paja- ja nuudliroad", "sub-categories": ["Paja- ja nuudliroad", "Puljongid"]}
]


def category_parser(prod_category) -> str:
    for item in categories:
        for category in item["sub-categories"]:
            if prod_category == category:
                return item["category"]
    return "N/A"


def image_parser(product, store) -> str:
    try:
        if store == "Selver":
            return f'https://www.selver.ee/img/800/800/resize{product["media_gallery"][0]["image"]}'
        elif store == "Prisma":
            return f'https://s3-eu-west-1.amazonaws.com/balticsimages/images/320x480/{product["image_guid"]}.png'
    except KeyError:
        return "https://www.prismamarket.ee/images/entry_no_image_170.png"


def name_parser(product_name):
    invalid_chars = {"´": "'", "`": "'", "  ": " ", "amp;": ""}
    regex = ",? \d{1,4}?\d? ?(g|kg|ml|l|/|tk|€|x|×|,)"

    for char in invalid_chars:
        product_name = product_name.replace(char, invalid_chars[char])
    if re.search(regex, product_name, flags=re.IGNORECASE):
        product_name = re.split(regex, product_name, flags=re.IGNORECASE)[0]
    return product_name.title()
