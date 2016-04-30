from flask import render_template, session, redirect, url_for, current_app, request
from .. import db
from ..models import Post
from ..email import send_email
from . import main
from .forms import QueryForm
import random
from math import floor
from flask_paginate import Pagination
from datetime import date


@main.route('/')
def index():
    N = Post.query.count()
    return render_template('index.html', number=N)


@main.route('/random/')
def random_post():
    N = Post.query.count()
    randoffset = floor(random.random() * N)
    # print(randoffset)
    randpost = Post.query.limit(1).offset(randoffset).all()
    return render_template('random.html', post_id=randpost[0].id, date=randpost[0].date, country=randpost[0].country,
                           post_text=randpost[0].text)


@main.route('/queries/', methods=['GET', 'POST'])
def queries():
    form = QueryForm()
    page = request.args.get('page')
    if form.is_submitted():
        session["datefrom"] = date.isoformat(
            form.datefrom.data) + " 00:00:00.000000" if form.datefrom.data is not None else None
        session["dateto"] = date.isoformat(
            form.dateto.data) + " 00:00:00.000000" if form.dateto.data is not None else None
        session["country"] = form.country.data
        session["textq"] = form.text.data
        return redirect(url_for('main.results'))

    return render_template('queries.html', form=form)


@main.route('/results/', methods=['GET', 'POST'])
def results():
    page = request.args.get('page', 1, type=int)
    q = Post.query
    #print(session["datefrom"])
    #print(session["dateto"])
    #print(session["country"])
    #print(session["textq"])
    if session["country"]:
        q = q.filter(Post.country.in_(session["country"]))
    if session["textq"]:
        q = q.filter(Post.text.like("%" + session["textq"] + "%"))
    if session["datefrom"]:
        q = q.filter(Post.date >= session["datefrom"])
    if session["dateto"]:
        q = q.filter(Post.date < session["dateto"])
    allposts = q.all()
    geodata = {}
    chartgeodata = []
    timedata = {}
    charttimedata = []
    for post in allposts:
        country = post.country
        country = get_country_code(country)
        if country not in geodata.keys():
            geodata[country] = 1
        else:
            geodata[country] = geodata[country] + 1


        date = str(post.date).split(' ')[0]

        if date not in timedata.keys():
            timedata[date] = 1
        else:
            timedata[date] = timedata[date] + 1
    for country in geodata.keys():
        chartgeodata.append([country, geodata[country]])
    for date in sorted(timedata.keys()):
        charttimedata.append([date, timedata[date]])
    pagination = q.paginate(page, 20, False)
    posts = pagination.items
    # print(posts)
    #print(chartgeodata)
    return render_template('result.html', posts=posts, pagination=pagination, geodata=chartgeodata, timedata=charttimedata)


def get_country_code(country_name):
    #country_name = country_name.replace("\'", "")
    countries = {'Afghanistan': 'AF',
                 'Åland Islands': 'AX',
                 'Albania': 'AL',
                 'Algeria': 'DZ',
                 'American Samoa': 'AS',
                 'Andorra': 'AD',
                 'Angola': 'AO',
                 'Anguilla': 'AI',
                 'Antarctica': 'AQ',
                 'Antigua and Barbuda': 'AG',
                 'Argentina': 'AR',
                 'Australia': 'AU',
                 'Austria': 'AT',
                 'Azerbaijan': 'AZ',
                 'Bahamas': 'BS',
                 'Bahrain': 'BH',
                 'Bangladesh': 'BD',
                 'Barbados': 'BB',
                 'Belarus': 'BY',
                 'Belgium': 'BE',
                 'Belize': 'BZ',
                 'Benin': 'BJ',
                 'Bermuda': 'BM',
                 'Bhutan': 'BT',
                 'Bolivia': 'BO',
                 'Bosnia and Herzegovina': 'BA',
                 'Botswana': 'BW',
                 'Bouvet Island': 'BV',
                 'Brazil': 'BR',
                 'British Indian Ocean Territory': 'IO',
                 'Brunei Darussalam': 'BN',
                 'Bulgaria': 'BG',
                 'Burkina Faso': 'BF',
                 'Burundi': 'BI',
                 'Cambodia': 'KH',
                 'Cameroon': 'CM',
                 'Canada': 'CA',
                 'Cape Verde': 'CV',
                 'Cayman Islands': 'KY',
                 'Central African Republic': 'CF',
                 'Chad': 'TD',
                 'Chile': 'CL',
                 'China': 'CN',
                 'Christmas Island': 'CX',
                 'Cocos (Keeling) Islands': 'CC',
                 'Colombia': 'CO',
                 'Comoros': 'KM',
                 'Congo': 'CG',
                 'Zaire': 'CD',
                 'Cook Islands': 'CK',
                 'Costa Rica': 'CR',
                 'Côte D\'Ivoire': 'CI',
                 'Croatia': 'HR',
                 'Cuba': 'CU',
                 'Cyprus': 'CY',
                 'Czech Republic': 'CZ',
                 'Denmark': 'DK',
                 'Djibouti': 'DJ',
                 'Dominica': 'DM',
                 'Dominican Republic': 'DO',
                 'Ecuador': 'EC',
                 'Egypt': 'EG',
                 'El Salvador': 'SV',
                 'Equatorial Guinea': 'GQ',
                 'Eritrea': 'ER',
                 'Estonia': 'EE',
                 'Ethiopia': 'ET',
                 'Falkland Islands (Malvinas)': 'FK',
                 'Faroe Islands': 'FO',
                 'Fiji': 'FJ',
                 'Finland': 'FI',
                 'France': 'FR',
                 'French Guiana': 'GF',
                 'French Polynesia': 'PF',
                 'French Southern Territories': 'TF',
                 'Gabon': 'GA',
                 'Gambia': 'GM',
                 'Georgia': 'GE',
                 'Germany': 'DE',
                 'Ghana': 'GH',
                 'Gibraltar': 'GI',
                 'Greece': 'GR',
                 'Greenland': 'GL',
                 'Grenada': 'GD',
                 'Guadeloupe': 'GP',
                 'Guam': 'GU',
                 'Guatemala': 'GT',
                 'Guernsey': 'GG',
                 'Guinea': 'GN',
                 'Guinea-Bissau': 'GW',
                 'Guyana': 'GY',
                 'Haiti': 'HT',
                 'Heard Island and Mcdonald Islands': 'HM',
                 'Vatican City State': 'VA',
                 'Honduras': 'HN',
                 'Hong Kong': 'HK',
                 'Hungary': 'HU',
                 'Iceland': 'IS',
                 'India': 'IN',
                 'Indonesia': 'ID',
                 'Iran, Islamic Republic of': 'IR',
                 'Iraq': 'IQ',
                 'Ireland': 'IE',
                 'Isle of Man': 'IM',
                 'Israel': 'IL',
                 'Italy': 'IT',
                 'Jamaica': 'JM',
                 'Japan': 'JP',
                 'Jersey': 'JE',
                 'Jordan': 'JO',
                 'Kazakhstan': 'KZ',
                 'KENYA': 'KE',
                 'Kiribati': 'KI',
                 'Korea, Democratic People\'s Republic of': 'KP',
                 'Korea, Republic of': 'KR',
                 'Kuwait': 'KW',
                 'Kyrgyzstan': 'KG',
                 'Lao People\'s Democratic Republic': 'LA',
                 'Latvia': 'LV',
                 'Lebanon': 'LB',
                 'Lesotho': 'LS',
                 'Liberia': 'LR',
                 'Libyan Arab Jamahiriya': 'LY',
                 'Liechtenstein': 'LI',
                 'Lithuania': 'LT',
                 'Luxembourg': 'LU',
                 'Macao': 'MO',
                 'Macedonia, the Former Yugoslav Republic of': 'MK',
                 'Madagascar': 'MG',
                 'Malawi': 'MW',
                 'Malaysia': 'MY',
                 'Maldives': 'MV',
                 'Mali': 'ML',
                 'Malta': 'MT',
                 'Marshall Islands': 'MH',
                 'Martinique': 'MQ',
                 'Mauritania': 'MR',
                 'Mauritius': 'MU',
                 'Mayotte': 'YT',
                 'Mexico': 'MX',
                 'Micronesia, Federated States of': 'FM',
                 'Moldova, Republic of': 'MD',
                 'Monaco': 'MC',
                 'Mongolia': 'MN',
                 'Montenegro': 'ME',
                 'Montserrat': 'MS',
                 'Morocco': 'MA',
                 'Mozambique': 'MZ',
                 'Myanmar': 'MM',
                 'Namibia': 'NA',
                 'Nauru': 'NR',
                 'Nepal': 'NP',
                 'Netherlands': 'NL',
                 'Netherlands Antilles': 'AN',
                 'New Caledonia': 'NC',
                 'New Zealand': 'NZ',
                 'Nicaragua': 'NI',
                 'Niger': 'NE',
                 'Nigeria': 'NG',
                 'Niue': 'NU',
                 'Norfolk Island': 'NF',
                 'Northern Mariana Islands': 'MP',
                 'Norway': 'NO',
                 'Oman': 'OM',
                 'Pakistan': 'PK',
                 'Palau': 'PW',
                 'Palestinian Territory, Occupied': 'PS',
                 'Panama': 'PA',
                 'Papua New Guinea': 'PG',
                 'Paraguay': 'PY',
                 'Peru': 'PE',
                 'Philippines': 'PH',
                 'Pitcairn': 'PN',
                 'Poland': 'PL',
                 'Portugal': 'PT',
                 'Puerto Rico': 'PR',
                 'Qatar': 'QA',
                 'Réunion': 'RE',
                 'Romania': 'RO',
                 'Russian Federation': 'RU',
                 'Rwanda': 'RW',
                 'Saint Helena': 'SH',
                 'Saint Kitts and Nevis': 'KN',
                 'Saint Lucia': 'LC',
                 'Saint Pierre and Miquelon': 'PM',
                 'Saint Vincent and the Grenadines': 'VC',
                 'Samoa': 'WS',
                 'San Marino': 'SM',
                 'Sao Tome and Principe': 'ST',
                 'Saudi Arabia': 'SA',
                 'Senegal': 'SN',
                 'Serbia': 'RS',
                 'Seychelles': 'SC',
                 'Sierra Leone': 'SL',
                 'Singapore': 'SG',
                 'Slovakia': 'SK',
                 'Slovenia': 'SI',
                 'Solomon Islands': 'SB',
                 'Somalia': 'SO',
                 'South Africa': 'ZA',
                 'South Georgia and the South Sandwich Islands': 'GS',
                 'Spain': 'ES',
                 'Sri Lanka': 'LK',
                 'Sudan': 'SD',
                 'Suriname': 'SR',
                 'Svalbard and Jan Mayen': 'SJ',
                 'Swaziland': 'SZ',
                 'Sweden': 'SE',
                 'Switzerland': 'CH',
                 'Syrian Arab Republic': 'SY',
                 'Taiwan, Province of China': 'TW',
                 'Tajikistan': 'TJ',
                 'Tanzania, United Republic of': 'TZ',
                 'Thailand': 'TH',
                 'Timor-Leste': 'TL',
                 'Togo': 'TG',
                 'Tokelau': 'TK',
                 'Tonga': 'TO',
                 'Trinidad and Tobago': 'TT',
                 'Tunisia': 'TN',
                 'Turkey': 'TR',
                 'Turkmenistan': 'TM',
                 'Turks and Caicos Islands': 'TC',
                 'Tuvalu': 'TV',
                 'Uganda': 'UG',
                 'Ukraine': 'UA',
                 'United Arab Emirates': 'AE',
                 'United Kingdom': 'GB',
                 'United States': 'US',
                 'United States Minor Outlying Islands': 'UM',
                 'Uruguay': 'UY',
                 'Uzbekistan': 'UZ',
                 'Vanuatu': 'VU',
                 'Venezuela': 'VE',
                 'Viet Nam': 'VN',
                 'Virgin Islands, British': 'VG',
                 'Virgin Islands, U.S.': 'VI',
                 'Wallis and Futuna': 'WF',
                 'Western Sahara': 'EH',
                 'Yemen': 'YE',
                 'Zambia': 'ZM',
                 'Zimbabwe': 'ZW',
                 'Hyper-Israel': 'IL',
                 'Republic of Texas': 'US',
                 'Tringapore': 'SG',
                 'Free State of Bavaria': 'DE',
                 'Quebec': 'CA',
                 'Scotland': 'GB',
                 'England (St. George\\\'s Day)': 'GB',
                 'Catalonia': 'ES',
                 'Armenia': 'AM',
                 'Brazil (Indian Day)': 'BR',
                 'Spain (Anniversary of the Second Spanish Republic)': 'ES',
                 'Reunion': 'RE',
                 'Congo, The Democratic Republic of the': 'CG',
                 'The Illuminati': 'AQ',
                 '010011010110111101100100': 'AQ',
                 }
    try:
        country_code = countries[country_name]
    except:
        country_code = country_name
        #print(country_code)
    return country_code
