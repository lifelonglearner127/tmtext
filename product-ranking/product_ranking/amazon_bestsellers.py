# -*- coding: utf-8 -*-
#
# See http://bugzilla.contentanalyticsinc.com/show_bug.cgi?id=285
#

# list of departments and their categories
DEPARTMENTS_CATEGORIES = [
    'Books',
    'Home & Kitchen',
    'Electronics',
    'Sports & Outdoors',
    'Cell Phones & Accessories',
    'Collectibles & Fine Art',
    'Industrial & Scientific',
    'Automotive',
    'Clothing & Accessories',
    'Tools & Home Improvement',
    'Jewelry',
    'Office Products',
    'CDs & Vinyl',
    'Health & Personal Care',
    'Kindle Store',
    'Toys & Games',
    'Patio, Lawn & Garden',
    'Arts, Crafts & Sewing',
    'Beauty',
    'Movies & TV',
    'Grocery & Gourmet Food',
    'Pet Supplies',
    'Shoes',
    'Baby',
    'Musical Instruments',
    'Watches',
    'Appliances',
    'Software',
    'Video Games',
    'Apps & Games',
    'Kindle Accessories',
    'Gift Cards',
    #amazon.fr
    'Toutes nos boutiques', 
    'Animalerie', 
    'Applis & Jeux', 
    'Auto et Moto', 
    'Bagages', 
    'Beauté et Parfum', 
    'Bijoux', 
    'Boutique chèques-cadeaux', 
    'Boutique Kindle', 
    'Bricolage', 
    'Bébés & Puériculture', 
    'Chaussures et Sacs', 
    'Cuisine & Maison', 
    'DVD & Blu-ray', 
    'Fournitures de bureau', 
    'Gros électroménager', 
    'High-tech', 
    'Informatique', 
    'Instruments de musique & Sono', 
    'Jardin', 
    'Jeux et Jouets', 
    'Jeux vidéo', 
    'Livres anglais et étrangers', 
    'Livres en français', 
    'Logiciels', 
    'Luminaires et Eclairage', 
    'Montres', 
    'Musique : CD & Vinyles', 
    'Musique classique', 
    'Santé et Soins du corps', 
    'Sports et Loisirs', 
    'Téléchargement de musique', 
    'Vêtements et accessoires',
    'Téléchargement de musique', 
    'Amazon Cloud Drive', 
    'Liseuses Kindle & ebooks', 
    'Tablettes Fire', 
    'App-Shop pour Android', 
    'Jeux et Logiciels Digitaux', 
    'Livres', 
    'Musique, DVD et Blu-ray', 
    'Jeux vidéo et Consoles', 
    'High-Tech et Informatique', 
    'Jouets, Enfants et Bébés', 
    'Maison, Bricolage, Animalerie', 
    'Beauté, Santé, Alimentation', 
    'Vêtements et Chaussures', 
    'Montres et Bijoux', 
    'Sports et Loisirs', 
    'Auto et Moto',
]


def amazon_parse_department(cats):
    for r in cats:
        cat = r.get('category')
        rank = r.get('rank')
        # first, try to match the full category
        print('+'*50)
        print(cat)
        print(cat.lower() in [x.lower() for x in DEPARTMENTS_CATEGORIES])
        print('+'*50)
        if cat in DEPARTMENTS_CATEGORIES \
            or cat.lower() in [x.lower() for x in DEPARTMENTS_CATEGORIES]:
            return {cat: rank}
        cats = [_c.strip() for _c in cat.split('>')]
        if cats:
            if cats[0] in DEPARTMENTS_CATEGORIES:
                return {cats[0]: rank}
            if len(cats) > 1:
                if cats[1] in DEPARTMENTS_CATEGORIES:
                    return {cats[1]: rank}