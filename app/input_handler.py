import re
import os

def handle_null_str(in_str):
    if in_str == '':
        return None
    else:
        return str(in_str)


def handle_null_int(in_str):
    if in_str == '':
        return None
    else:
        return int(in_str)


def email_checker(email):
    if email is not None:
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        return re.fullmatch(email_regex, email)
    else:
        return True


def phone_checker(phone):
    if phone is not None:
        phone_regex = "^\\+?\\d{1,4}?[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}$"
        return re.fullmatch(phone_regex, phone)
    else:
        return True


def images_path_handler(images):
    if images is not None:
        ad_image = []
        cwd = os.getcwd()
        # print(cwd)
        for image in images:
            # print(cwd + '/app/' + image[1])
            ad_image.append(str(image[1]))
        return ad_image
    else:
        return []

# [(20, 8, 0, 2, 'etiam justo etiam pretium', 67881.69, 'ligula sit amet', 'quam', 'Sarasota', '834 Old Gate Point', 196, datetime.datetime(2023, 6, 19, 12, 38, 40), datetime.datetime(2024, 1, 13, 20, 48, 47), 20, 'ads_imgs/32'),
#  (1, 22, 1, 0, 'cubilia curae nulla dapibus', 25467447.198, 'dapibus at diam nam', 'quam', 'Nashville', None, 188, datetime.datetime(2023, 7, 26, 4, 31, 46), datetime.datetime(2023, 7, 11, 12, 36, 7), 1, 'ads_imgs/6'),
#  (15, 26, 1, 1, 'ligula nec sem duis aliquam', 16567.817, None, 'et', 'Atlanta', '323 Eagle Crest Court', 126, datetime.datetime(2023, 7, 29, 11, 48, 39), datetime.datetime(2024, 6, 4, 18, 41, 22), 15, 'ads_imgs/54'),
#  (17, 9, 1, 1, 'quam pede lobortis ligula', 31531.58, 'interdum', 'aliquam', 'Arlington', '181 Pleasure Pass', 29, datetime.datetime(2023, 8, 2, 20, 49, 52), datetime.datetime(2024, 2, 17, 6, 55, 28), 17, 'ads_imgs/17'),
#  (17, 9, 1, 1, 'quam pede lobortis ligula', 31531.58, 'interdum', 'aliquam', 'Arlington', '181 Pleasure Pass', 29, datetime.datetime(2023, 8, 2, 20, 49, 52), datetime.datetime(2024, 2, 17, 6, 55, 28), 17, 'ads_imgs/26'), (17, 9, 1, 1, 'quam pede lobortis ligula', 31531.58, 'interdum', 'aliquam', 'Arlington', '181 Pleasure Pass', 29, datetime.datetime(2023, 8, 2, 20, 49, 52), datetime.datetime(2024, 2, 17, 6, 55, 28), 17, 'ads_imgs/29'), (17, 9, 1, 1, 'quam pede lobortis ligula', 31531.58, 'interdum', 'aliquam', 'Arlington', '181 Pleasure Pass', 29, datetime.datetime(2023, 8, 2, 20, 49, 52), datetime.datetime(2024, 2, 17, 6, 55, 28), 17, 'ads_imgs/56'), (17, 9, 1, 1, 'quam pede lobortis ligula', 31531.58, 'interdum', 'aliquam', 'Arlington', '181 Pleasure Pass', 29, datetime.datetime(2023, 8, 2, 20, 49, 52), datetime.datetime(2024, 2, 17, 6, 55, 28), 17, 'ads_imgs/30'), (17, 9, 1, 1, 'quam pede lobortis ligula', 31531.58, 'interdum', 'aliquam', 'Arlington', '181 Pleasure Pass', 29, datetime.datetime(2023, 8, 2, 20, 49, 52), datetime.datetime(2024, 2, 17, 6, 55, 28), 17, 'ads_imgs/51'), (22, 7, 0, 2, 'convallis morbi odio odio elementum', 30863.538, 'blandit ultrices', 'eros elementum', 'Cambridge', None, 107, datetime.datetime(2023, 8, 28, 1, 21, 14), datetime.datetime(2024, 2, 2, 5, 12, 25), 22, 'ads_imgs/22')]

# [(20, 8, 0, 2, 'etiam justo etiam pretium', 67881.69, 'ligula sit amet', 'quam', 'Sarasota', '834 Old Gate Point', 196, datetime.datetime(2023, 6, 19, 12, 38, 40), datetime.datetime(2024, 1, 13, 20, 48, 47)),
#  (1, 22, 1, 0, 'cubilia curae nulla dapibus', 25467447.198, 'dapibus at diam nam', 'quam', 'Nashville', None, 188, datetime.datetime(2023, 7, 26, 4, 31, 46), datetime.datetime(2023, 7, 11, 12, 36, 7)),
#  (15, 26, 1, 1, 'ligula nec sem duis aliquam', 16567.817, None, 'et', 'Atlanta', '323 Eagle Crest Court', 126, datetime.datetime(2023, 7, 29, 11, 48, 39), datetime.datetime(2024, 6, 4, 18, 41, 22)),
#  (17, 9, 1, 1, 'quam pede lobortis ligula', 31531.58, 'interdum', 'aliquam', 'Arlington', '181 Pleasure Pass', 29, datetime.datetime(2023, 8, 2, 20, 49, 52), datetime.datetime(2024, 2, 17, 6, 55, 28)),
#  (22, 7, 0, 2, 'convallis morbi odio odio elementum', 30863.538, 'blandit ultrices', 'eros elementum', 'Cambridge', None, 107, datetime.datetime(2023, 8, 28, 1, 21, 14), datetime.datetime(2024, 2, 2, 5, 12, 25)), (7, 31, 1, 0, 'convallis tortor risus dapibus augue', 81190.822, None, 'sed interdum', 'Greensboro', '5 Butternut Center', 89, datetime.datetime(2023, 9, 6, 0, 15, 40), datetime.datetime(2023, 12, 1, 16, 47, 48)), (29, 23, 1, 3, 'eget', 680391.318, 'nullam varius', 'scelerisque quam', 'Albany', '18 Glacier Hill Street', 150, datetime.datetime(2023, 9, 8, 9, 27, 23), datetime.datetime(2023, 7, 20, 2, 32, 2)), (25, 1, 0, 2, 'metus', 438621.312, 'orci luctus et ultrices', 'volutpat', 'El Paso', '26535 Lakeland Court', None, datetime.datetime(2023, 9, 23, 19, 0, 36), datetime.datetime(2023, 10, 20, 17, 2, 41)), (21, 3, 0, 2, 'vitae ipsum aliquam non mauris', 14055.744, 'nulla elit ac nulla sed', 'fermentum donec', 'Cambridge', '32 Emmet Crossing', 52, datetime.datetime(2023, 10, 28, 13, 34, 23), datetime.datetime(2023, 10, 7, 20, 53, 35)), (12, 26, 1, 1, 'nulla quisque', 374701.087, 'in leo maecenas', 'nam', 'Salt Lake City', '3799 Columbus Point', None, datetime.datetime(2023, 11, 15, 19, 4, 13), datetime.datetime(2023, 7, 16, 16, 34, 12))]